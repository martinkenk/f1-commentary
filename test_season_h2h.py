import datetime
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import f1lib
import season_h2h as h2h

NOW = datetime.datetime(2026, 9, 10, 21, tzinfo=datetime.timezone.utc)


def driver(code, position, team="Team", status="classified"):
    return {"code": code, "name": "Driver " + code, "team": team,
            "position": position, "status": status,
            "raw_position": str(position) if position else "NC"}


def session(gp, label, drivers):
    return {"key": gp + "/" + label, "gp": gp, "name": gp, "label": label,
            "drivers": drivers, "date": "2026-09-06",
            "url": "https://www.formula1.com/" + gp + "/" + label}


def page(kind):
    headers = (["Pos.", "No.", "Driver", "Team", "Q1", "Q2", "Q3", "Laps"]
               if kind == "Qualifying" else
               ["Pos.", "No.", "Driver", "Team", "Laps", "Time / Retired", "Pts."])
    rows = []
    for index in range(20):
        cells = [str(index + 1), str(index + 1), f"Driver {index} AA{chr(65 + index)}", f"Team {index // 2}"]
        cells += ["1:22.000", "", "", "10"] if kind == "Qualifying" else ["53", "+1.000s", "0"]
        rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    return ("<table><thead><tr>" + "".join(f"<th>{header}</th>" for header in headers)
            + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def calendar_event(day="2026-09-06"):
    return {"slug": "test", "name": "Test Grand Prix", "round": 1,
            "race_id": "1234", "results_slug": "test", "sessions": [
                {"label": label, "date": day, "time": "15:00", "gmt_offset": "+02:00"}
                for label in ("Qualifying", "Race", "Sprint Qualifying", "Sprint")]}


class ComparisonTests(unittest.TestCase):
    def test_shared_parser_preserves_empty_qualifying_columns(self):
        headers, rows = f1lib._parse_result_table(page("Qualifying"))
        self.assertEqual(len(rows[0]), len(headers))
        self.assertEqual(rows[0][5:], ["", "", "10"])
        drivers = h2h.parse_classification(page("Qualifying"), "Qualifying")
        self.assertEqual(drivers[0]["status"], "classified")

    def test_partial_or_duplicate_source_is_rejected(self):
        source = page("Race")
        with self.assertRaises(ValueError):
            h2h.parse_classification(source.replace("<td>2</td>", "<td>1</td>"), "Race")
        with self.assertRaises(ValueError):
            h2h.parse_classification("<table><tbody></tbody></table>", "Race")

    def test_no_qualifying_time_is_not_a_win(self):
        parsed = h2h.parse_classification(page("Qualifying").replace("1:22.000", "", 1), "Qualifying")
        self.assertEqual(parsed[0]["status"], "no-time")
        self.assertIsNone(h2h.compare(parsed[0], parsed[1], "Qualifying")[0])

    def test_classifications_and_exclusions_are_explicit(self):
        self.assertEqual(h2h.compare(driver("AAA", 2), driver("BBB", 8), "Race")[0], 0)
        retired = driver("BBB", None, status="unclassified")
        self.assertEqual(h2h.compare(driver("AAA", 15), retired, "Race")[0], 0)
        self.assertIsNone(h2h.compare(retired, retired, "Race")[0])
        for state in ("dns", "dsq", "no-time"):
            self.assertIsNone(h2h.compare(driver("AAA", 1), driver("BBB", None, status=state), "Race")[0])

    def test_replacements_and_transfers_keep_distinct_pairings(self):
        record = {"sessions": [
            session("one", "Qualifying", [driver("AAA", 2), driver("BBB", 1)]),
            session("one", "Race", [driver("AAA", 1), driver("BBB", 2)]),
            session("two", "Qualifying", [driver("AAA", 1), driver("CCC", 2)]),
            session("two", "Race", [driver("AAA", 2), driver("CCC", 1),
                                    driver("BBB", 3, "Other"), driver("DDD", 4, "Other")]),
        ]}
        pairs = h2h.aggregate(record)
        self.assertEqual(len(pairs), 3)
        pair = next(pair for pair in pairs if [d["code"] for d in pair["drivers"]] == ["AAA", "BBB"])
        self.assertEqual(pair["Qualifying"]["wins"], [0, 1])
        self.assertEqual(pair["Race"]["wins"], [1, 0])
        self.assertEqual(pair["Race"]["excluded"], 0)

    def test_missing_qualifier_uses_race_pair_without_inventing_a_win(self):
        pairs = h2h.aggregate({"sessions": [
            session("one", "Qualifying", [driver("AAA", 1)]),
            session("one", "Race", [driver("AAA", 2), driver("BBB", 1)]),
        ]})
        self.assertEqual(pairs[0]["Qualifying"], {"wins": [0, 0], "excluded": 1})
        self.assertEqual(pairs[0]["Race"]["wins"], [0, 1])

    def test_sprints_and_future_sessions_are_not_selected(self):
        items = list(h2h.expected_sessions([calendar_event(), calendar_event("2026-09-13")], NOW))
        self.assertEqual([item[1] for item in items], ["Qualifying", "Race"])

    def test_session_due_time_respects_published_timezone(self):
        event = calendar_event("2026-09-10")
        now = datetime.datetime(2026, 9, 10, 14, 30, tzinfo=datetime.timezone.utc)
        self.assertEqual([item[1] for item in h2h.expected_sessions([event], now)], ["Qualifying"])

    def test_season_comparison_survives_no_local_sessions(self):
        with patch.object(h2h, "render", return_value="SEASON_SCORELINES"):
            body = f1lib.render_h2h({"year": "2026", "results": []}, tally_html="EXTRA_CONTEXT")
        self.assertIn("SEASON_SCORELINES", body)
        self.assertIn("EXTRA_CONTEXT", body)
        self.assertLess(body.index("SEASON_SCORELINES"), body.index("This Grand Prix"))


class RefreshTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        mock = patch.object(h2h, "ROOT", self.root)
        mock.start()
        self.addCleanup(mock.stop)
        h2h._write(self.root / "data/calendar_2026.json", {"events": [calendar_event()]})

    def populate(self):
        responses = [io.BytesIO(page(label).encode()) for label in ("Qualifying", "Race")]
        with patch.object(h2h.urllib.request, "urlopen", side_effect=responses):
            return h2h.refresh(now=NOW)

    def test_success_and_failed_refresh_preserve_last_good_sources(self):
        first = self.populate()
        self.assertEqual(len(first["sessions"]), 2)
        with patch.object(h2h.urllib.request, "urlopen", side_effect=OSError("HTTP 403")):
            failed = h2h.refresh(now=NOW + datetime.timedelta(hours=2))
        self.assertEqual(failed["sessions"], first["sessions"])
        self.assertEqual(len(failed["errors"]), 2)
        self.assertIn("Incomplete season refresh", h2h.render())

    def test_old_classifications_reused_until_weekly_refresh(self):
        h2h._write(self.root / "data/calendar_2026.json", {"events": [calendar_event("2026-09-01")]})
        self.populate()
        with patch.object(h2h.urllib.request, "urlopen") as fetch:
            # More than ten days after the race, but less than seven days since collection.
            h2h.refresh(now=NOW + datetime.timedelta(days=2))
        fetch.assert_not_called()

    def test_unknown_schema_does_not_overwrite_classifications(self):
        first = self.populate()
        with patch.object(h2h.urllib.request, "urlopen", side_effect=[
                io.BytesIO(b"<html>Access denied</html>"), io.BytesIO(b"<html>Access denied</html>")]):
            latest = h2h.refresh(now=NOW)
        self.assertEqual(latest["sessions"], first["sessions"])
        self.assertEqual(len(latest["errors"]), 2)

    def test_old_failed_session_retries_even_with_a_recent_cached_result(self):
        h2h._write(self.root / "data/calendar_2026.json", {"events": [calendar_event("2026-09-01")]})
        snapshot = self.populate()
        snapshot["errors"] = [{"key": "test/qualifying", "url": "https://www.formula1.com/", "error": "503"}]
        h2h._write(self.root / "data/season_h2h_2026.json", snapshot)
        with patch.object(h2h.urllib.request, "urlopen", return_value=io.BytesIO(page("Qualifying").encode())) as fetch:
            refreshed = h2h.refresh(now=NOW + datetime.timedelta(days=2))
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(refreshed["errors"], [])

    def test_calendar_omission_does_not_erase_past_results(self):
        first = self.populate()
        h2h._write(self.root / "data/calendar_2026.json", {"events": [calendar_event("2026-09-13")]})
        with patch.object(h2h.urllib.request, "urlopen") as fetch:
            latest = h2h.refresh(now=NOW)
        fetch.assert_not_called()
        self.assertEqual(latest["sessions"], first["sessions"])
        self.assertEqual(len(latest["errors"]), 2)

    def test_render_has_score_orientation_exclusions_and_source_evidence(self):
        self.populate()
        body = h2h.render()
        self.assertIn("Qualifying A&ndash;B", body)
        self.assertIn("Race A&ndash;B", body)
        self.assertIn("1 compared / 0 excluded", body)
        self.assertIn("round-by-round sources", body)
        self.assertIn("https://www.formula1.com/en/results/2026/races/1234/test/qualifying", body)


if __name__ == "__main__":
    unittest.main()
