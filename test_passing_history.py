import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import datetime as dt

import passing_history as ph


ARTICLE = """
<p>The 2024 Azerbaijan GP had <strong>47</strong> Overtakes.</p>
<h2>2024 Azerbaijan GP Overtakes</h2><ul><li>Lap 2 Example overtook Example for P 3</li></ul>
<h2>Numbers for the Season so far</h2><ul>
<li>China - 53 (Sprint - 21)</li><li>Azerbaijan - 47</li></ul>
<h2>Rules</h2>
<p>Only on track passes for position count; pitting, off track and major reliability exclusions.</p>
<p>Lapping and unlapping do not count. Overtakes on Lap 1 do not count.</p>
"""


class PassingContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "data").mkdir()
        self.ctx = {"dir": "azerbaijan", "race_date": "2026-09-26"}
        self.profile = {
            "completed_races": 3, "cutoff_date": "2026-09-26", "circuit": {"id": "baku"},
            "recent_winners": [
                {"race_id": year, "year": year, "date": f"{year}-06-01", "circuit_id": "baku",
                 "name": "European Grand Prix" if year == 2022 else "Azerbaijan Grand Prix",
                 "url": f"https://example.org/races/{year}"}
                for year in (2025, 2024, 2022)
            ],
        }
        self.snapshot = {
            "schema_version": 1, "checked_at": "2026-09-18T07:00:00Z",
            "sources": {"community": {
                "name": "Community counts", "url": "https://example.org/data",
                "methodology": "On-track passes excluding lap one and pit stops.",
                "attribution": "Independent count; not official FIA data.",
            }},
            "races": [
                {"series_id": "community", "race_id": year, "circuit_id": "baku",
                 "date": f"{year}-06-01", "overtakes": count,
                 "source_url": f"https://example.org/data/{year}"}
                for year, count in ((2024, 20), (2022, 0))
            ],
        }

    def save(self):
        (self.root / "data/passing_history.json").write_text(json.dumps(self.snapshot))

    def context(self):
        self.save()
        return ph.context(self.ctx, self.profile, root=self.root)

    def test_matches_same_venue_even_when_gp_name_changes_and_preserves_missing(self):
        result = self.context()
        self.assertEqual(result["error"], "")
        rows = result["series"][0]["races"]
        self.assertEqual([row["overtakes"] for row in rows], [None, 20, 0])
        self.assertEqual(rows[2]["name"], "European Grand Prix")
        self.assertEqual(rows[1]["source_url"], "https://example.org/data/2024")

    def test_never_borrows_another_circuit_or_invents_debut_counts(self):
        self.profile.update(completed_races=0, circuit={"id": "madring"}, recent_winners=[])
        self.ctx = {"dir": "spain", "race_date": "2026-09-13"}
        self.assertEqual(self.context()["series"], [])

    def test_identity_conflict_is_visible_not_silently_relabelled(self):
        self.snapshot["races"][0]["circuit_id"] = "catalunya"
        result = self.context()
        self.assertEqual(result["series"], [])
        self.assertIn("disagrees with the F1DB venue/date", result["error"])

    def test_current_and_future_races_are_excluded(self):
        for year in (2026, 2027):
            self.profile["recent_winners"].append({
                "race_id": year, "year": year, "date": f"{year}-09-26", "circuit_id": "baku",
                "name": "Azerbaijan Grand Prix", "url": f"https://example.org/races/{year}",
            })
            self.snapshot["races"].append({
                "series_id": "community", "race_id": year, "circuit_id": "baku",
                "date": f"{year}-09-26", "overtakes": 999, "source_url": "https://example.org/data",
            })
        rows = self.context()["series"][0]["races"]
        self.assertEqual([row["year"] for row in rows], [2025, 2024, 2022])

    def test_shared_winners_do_not_duplicate_one_race(self):
        self.profile["recent_winners"].append(copy.deepcopy(self.profile["recent_winners"][1]))
        self.assertEqual(len(self.context()["series"][0]["races"]), 3)

    def test_different_counting_methods_stay_in_separate_series(self):
        self.snapshot["sources"]["other"] = {
            **self.snapshot["sources"]["community"], "methodology": "Another definition.",
        }
        self.snapshot["races"].append({**self.snapshot["races"][0], "series_id": "other", "overtakes": 30})
        result = self.context()
        self.assertEqual(len(result["series"]), 2)
        self.assertEqual(result["series"][0]["races"][1]["overtakes"], 20)
        self.assertEqual(result["series"][1]["races"][1]["overtakes"], 30)

    def test_bad_count_and_duplicate_data_fail_explicitly(self):
        for count in (-1, True, "20", 1.5):
            with self.subTest(count=count):
                self.snapshot["races"][0]["overtakes"] = count
                result = self.context()
                self.assertEqual(result["series"], [])
                self.assertIn("Invalid sourced overtaking count", result["error"])
        self.snapshot["races"][0]["overtakes"] = 20
        self.snapshot["races"].append(copy.deepcopy(self.snapshot["races"][0]))
        self.assertIn("Duplicate overtaking count", self.context()["error"])

    def test_failed_refresh_retains_counts_with_warning(self):
        (self.root / "data/passing_history_status.json").write_text(json.dumps({
            "checked_at": "2026-09-18T07:30:00Z", "error": "Upstream unavailable", "ok": False,
        }))
        result = self.context()
        self.assertTrue(result["series"])
        self.assertEqual(result["error"], "Upstream unavailable")
        self.assertEqual(result["checked_at"], "2026-09-18T07:30:00Z")

    def test_no_snapshot_is_unknown_and_read_only(self):
        result = ph.context(self.ctx, self.profile, root=self.root)
        self.assertEqual(result["series"], [])
        self.assertFalse((self.root / "data/passing_history.json").exists())


class PassingCollectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "data").mkdir()
        self.url = "https://racingpass.net/published-race-report/"
        self.reviewed = {"articles": [{"url": self.url,
                                      "facts": [{"year": 2024, "gp": "Azerbaijan", "overtakes": 47}]}]}
        (self.root / "data/passing_history_reviewed.json").write_text(json.dumps(self.reviewed))
        self.data = {
            "grands-prix": [
                {"id": "azerbaijan", "name": "Azerbaijan", "fullName": "Azerbaijan Grand Prix"},
                {"id": "china", "name": "China", "fullName": "Chinese Grand Prix"},
                {"id": "europe", "name": "Europe", "fullName": "European Grand Prix"},
            ],
            "races": [
                {"id": 1118, "year": 2024, "date": "2024-09-15", "grandPrixId": "azerbaijan",
                 "circuitId": "baku"},
                {"id": 1106, "year": 2024, "date": "2024-04-21", "grandPrixId": "china",
                 "circuitId": "shanghai"},
                {"id": 901, "year": 2016, "date": "2016-06-19", "grandPrixId": "europe",
                 "circuitId": "baku"},
            ],
            "races-race-results": [{"raceId": identity} for identity in (1118, 1106, 901)],
        }
        self.now = dt.datetime(2026, 9, 18, 8, tzinfo=dt.timezone.utc)
        for name, result in (("_release", {"tag_name": "v2026.14.0"}),
                             ("_database", (self.data, {"release": "v2026.14.0"}))):
            patcher = patch.object(ph.circuit_history, name, return_value=result)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_parser_extracts_totals_not_pass_log_or_sprint_counts(self):
        rows = ph.parse_article(ARTICLE)
        self.assertIn({"year": 2024, "gp": "China", "overtakes": 53}, rows)
        self.assertNotIn(21, [row["overtakes"] for row in rows])
        joined = ph.join_facts([{"url": self.url, "facts": rows}], self.data, self.now.date())
        self.assertEqual(len(joined), 2)
        self.assertEqual(next(row for row in joined if row["circuit_id"] == "baku")["race_id"], 1118)
        self.assertNotIn(1137, [row["race_id"] for row in joined])  # Ergast is not F1DB.

    def test_changed_rules_or_aggregate_format_requires_review(self):
        for text in (ARTICLE.replace("Lap 1 do not count", "Lap 1 now counts"),
                     ARTICLE.replace("China - 53", "China: unknown"),
                     ARTICLE.replace("The 2024 Azerbaijan GP", "The 2024 Azerbaijan Sprint GP")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                ph.parse_article(text)

    def test_historical_venue_fact_can_use_another_named_gp(self):
        rows = ph.join_facts([{"url": self.url, "facts": [
            {"year": 2016, "circuit_id": "baku", "overtakes": 80},
        ]}], self.data, self.now.date())
        self.assertEqual(rows[0]["race_id"], 901)

    def test_ambiguous_or_unclassified_race_is_not_guessed(self):
        self.data["races-race-results"] = []
        with self.assertRaisesRegex(ValueError, "no unique completed"):
            ph.join_facts(self.reviewed["articles"], self.data, self.now.date())
        self.data["races-race-results"] = [{"raceId": 1118}, {"raceId": 2}]
        self.data["races"].append({**self.data["races"][0], "id": 2})
        with self.assertRaisesRegex(ValueError, "no unique completed"):
            ph.join_facts(self.reviewed["articles"], self.data, self.now.date())

    def test_primary_sources_must_agree_before_aggregation(self):
        other = {"url": "https://racingpass.net/other-report/", "facts": [
            {"year": 2024, "gp": "Azerbaijan", "overtakes": 48},
        ]}
        with self.assertRaisesRegex(ValueError, "Conflicting primary"):
            ph.join_facts(self.reviewed["articles"] + [other], self.data, self.now.date())

    def test_feed_discovers_actual_new_article_and_persists_counts(self):
        new_url = "https://racingpass.net/a-real-new-published-url/"
        feed = f"<rss><channel><item><title>Overtakes</title><link>{new_url}</link></item></channel></rss>"
        with patch.object(ph, "_fetch", side_effect=lambda url: feed if url == ph.FEED else ARTICLE):
            snapshot, status = ph.refresh(root=self.root, now=self.now)
        self.assertTrue(status["ok"])
        self.assertIn(new_url, snapshot["article_urls"])
        self.assertEqual(len(snapshot["races"]), 2)
        self.assertNotIn("Example", json.dumps(snapshot))
        with patch.object(ph, "_fetch", side_effect=AssertionError("Six-hour cache")):
            cached, _ = ph.refresh(root=self.root, now=self.now + dt.timedelta(hours=1))
        self.assertEqual(cached, snapshot)

    def test_source_block_does_not_clear_reviewed_counts_or_claim_success(self):
        with patch.object(ph, "_fetch", side_effect=OSError("HTTP 403")):
            snapshot, status = ph.refresh(root=self.root, now=self.now)
        self.assertFalse(status["ok"])
        self.assertEqual(snapshot["races"][0]["overtakes"], 47)
        self.assertIn("blocked or changed", status["error"])
        self.assertTrue(all("HTTP 403" in attempt["error"] for attempt in status["attempts"]))

    def test_bad_new_data_retains_previous_file(self):
        ph.refresh(root=self.root, now=self.now, reviewed_only=True)
        previous = (self.root / "data/passing_history.json").read_bytes()
        bad = ARTICLE.replace("47", "48")
        with patch.object(ph, "_fetch", side_effect=lambda url: "<rss><channel/></rss>"
                          if url == ph.FEED else bad), self.assertRaisesRegex(ValueError, "Conflicting"):
            ph.refresh(root=self.root, now=self.now, force=True)
        self.assertEqual((self.root / "data/passing_history.json").read_bytes(), previous)
        self.assertFalse(json.loads((self.root / "data/passing_history_status.json").read_text())["ok"])

    def test_other_hosts_and_redirects_are_rejected(self):
        for url in ("http://racingpass.net/a", "https://racingpass.net.evil.test/a",
                    "https://example.org/a", "https://racingpass.net:8443/a"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                ph._publisher_url(url)
        with self.assertRaises(ValueError):
            ph._Redirect().redirect_request(None, None, 302, "", {}, "https://example.org/a")


class PublishedPassingTests(unittest.TestCase):
    def test_primary_backfill_uses_real_venue_and_f1db_identities(self):
        history = json.loads((ph.ROOT / "data/circuit_history_2026.json").read_text())
        for gp, expected in {
            "azerbaijan": {2016: 80, 2019: 62, 2021: 27, 2022: 23, 2023: 23, 2024: 47},
            "hungary": {2021: 17, 2022: 61, 2023: 16, 2024: 33},
            "singapore": {2022: 16, 2023: 42, 2024: 30},
            "las-vegas": {2023: 99, 2024: 77},
        }.items():
            with self.subTest(gp=gp):
                profile = history["profiles"][gp]
                ctx = {"dir": gp, "race_date": profile["cutoff_date"]}
                record = ph.context(ctx, profile)
                self.assertTrue(record["series"])
                rows = {row["year"]: row for row in record["series"][0]["races"]}
                for year, count in expected.items():
                    self.assertEqual(rows[year]["overtakes"], count)
                if gp == "azerbaijan":
                    self.assertEqual(rows[2024]["race_id"], 1118)
                    self.assertEqual(rows[2016]["name"], "European Grand Prix")
        for gp in ("spain", "bahrain"):
            profile = history["profiles"][gp]
            ctx = {"dir": gp, "race_date": profile["cutoff_date"]}
            record = ph.context(ctx, profile)
            self.assertEqual(record["series"], [])


if __name__ == "__main__":
    unittest.main()
