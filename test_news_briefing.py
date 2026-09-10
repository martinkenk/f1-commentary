import copy
import datetime
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build
import f1lib
import news_briefing as briefing

NOW = datetime.datetime(2026, 9, 10, 20, 30, tzinfo=datetime.timezone.utc)
CTX = {"dir": "spain", "race_date": "2026-09-13", "results": []}


def article(title="Lawson stays as injury recovery continues", url="https://example.org/lineup",
            date="2026-09-10"):
    return {"title": title, "url": url, "date": date, "source": "Primary report"}


class BriefingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.feed = [article()]
        self.record = {
            "reviewed_at": "2026-09-10T20:00:00Z", "expires_at": "2026-09-11T02:00:00Z",
            "through_session": None, "feed_fingerprint": briefing.fingerprint(self.feed, CTX, NOW),
            "items": [{"topic": "Line-up", "title": "Confirmed replacements",
                       "date": "2026-09-10", "summary": "A collated summary.",
                       "why_it_matters": "Check the race seats.",
                       "sources": [{"label": "Source", "url": "https://example.org/lineup"}]}],
        }
        self.write()

    def write(self):
        (self.directory / "news_auto.json").write_text(json.dumps(self.feed))
        (self.directory / "news_highlights.json").write_text(json.dumps(self.record))

    def test_current_reviewed_synthesis_is_first_choice(self):
        selected = briefing.select(CTX, self.directory, NOW)
        self.assertEqual(selected["mode"], "Editor-collated")
        self.assertEqual(selected["items"][0]["summary"], "A collated summary.")

    def test_expiry_and_new_session_unpin_the_editorial_selection(self):
        for now, ctx in ((NOW + datetime.timedelta(days=1), CTX),
                         (NOW, dict(CTX, results=[{"label": "Practice 1"}]))):
            with self.subTest(now=now, ctx=ctx):
                selected = briefing.select(ctx, self.directory, now)
                self.assertEqual(selected["mode"], "Automatic priority selection")
                self.assertTrue(selected["notice"])
                self.assertNotEqual(selected["items"][0]["title"], "Confirmed replacements")

    def test_new_important_reporting_invalidates_review_but_promotions_do_not(self):
        self.feed.append(article("Win Grand Prix tickets", "https://example.org/promo"))
        self.write()
        self.assertEqual(briefing.select(CTX, self.directory, NOW)["mode"], "Editor-collated")
        self.feed.append(article("Driver handed grid penalty", "https://example.org/penalty"))
        self.write()
        selected = briefing.select(CTX, self.directory, NOW)
        self.assertIn("feed has changed", selected["notice"])
        self.assertIn("Driver handed grid penalty", [item["title"] for item in selected["items"]])

    def test_automatic_selection_groups_sources_excludes_promos_and_wrong_dates(self):
        feed = [
            article(), article(url="https://example.org/second"),
            article("Best betting tips for pole", "https://example.org/bets"),
            article("Driver wins", "https://example.org/old", "2026-08-01"),
            article("Driver wins", "https://example.org/future", "2026-09-14"),
        ]
        items = briefing.automatic_items(feed, CTX, NOW)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items[0]["sources"]), 2)
        self.assertEqual(items[0]["summary"], "")

    def test_feed_order_changes_do_not_invalidate_a_review(self):
        feed = [article(), article("New tyre compounds", "https://example.org/tyres")]
        self.assertEqual(briefing.fingerprint(feed, CTX, NOW),
                         briefing.fingerprint(list(reversed(feed)), CTX, NOW))

    def test_practice_reports_and_contract_news_are_priority_candidates(self):
        items = briefing.automatic_items([
            article("FP1: Driver tops the opening session", "https://example.org/fp1"),
            article("Driver signs new contract", "https://example.org/contract")],
            dict(CTX, results=[{"label": "Practice 1"}]), NOW)
        self.assertEqual(items[0]["topic"], "Session outcome")
        self.assertEqual(len(items), 2)

    def test_completed_event_does_not_promote_the_next_gp_preview(self):
        ctx = dict(CTX, race_date="2026-09-06", results=[{"label": "Race"}])
        items = briefing.automatic_items([
            article("Driver wins Italian GP", date="2026-09-06"),
            article("Madrid circuit challenges", "https://example.org/madrid")], ctx, NOW)
        self.assertEqual([item["title"] for item in items], ["Driver wins Italian GP"])

    def test_bad_curated_data_is_not_silently_replaced(self):
        self.record["items"][0]["sources"][0]["url"] = "javascript:alert(1)"
        self.write()
        with self.assertRaisesRegex(ValueError, "source"):
            briefing.select(CTX, self.directory, NOW)
        (self.directory / "news_highlights.json").write_text("{broken")
        with self.assertRaises(json.JSONDecodeError):
            briefing.select(CTX, self.directory, NOW)

    def test_review_contract_rejects_duplicate_topics_and_unbounded_expiry(self):
        for change in ("duplicate", "expiry", "grid"):
            with self.subTest(change=change):
                record = copy.deepcopy(self.record)
                if change == "duplicate":
                    record["items"].append(copy.deepcopy(record["items"][0]))
                elif change == "expiry":
                    record["expires_at"] = "2026-09-12T20:00:00Z"
                else:
                    record["through_session"] = "Starting Grid"
                with self.assertRaises(ValueError):
                    briefing.validate(record)

    def test_no_editorial_record_still_produces_an_automatic_briefing(self):
        (self.directory / "news_highlights.json").unlink()
        selected = briefing.select(CTX, self.directory, NOW)
        self.assertEqual(selected["mode"], "Automatic priority selection")
        self.assertEqual(len(selected["items"]), 1)

    def test_render_escapes_copy_and_preserves_multiple_source_links(self):
        selected = {"items": copy.deepcopy(self.record["items"]), "mode": "Editor-collated",
                    "reviewed_at": self.record["reviewed_at"], "notice": ""}
        selected["items"][0]["summary"] = '<script>alert("bad")</script>'
        with patch.object(briefing, "select", return_value=selected):
            body = briefing.render(CTX, self.directory)
        self.assertIn("&lt;script&gt;", body)
        self.assertNotIn("<script>", body)
        self.assertIn('href="https://example.org/lineup"', body)
        self.assertIn("Why it matters:", body)

    def test_shared_shell_puts_briefing_before_overview_and_news_only(self):
        ctx = next(gp for gp in build.season_gps() if gp["dir"] == "spain")
        with patch.object(briefing, "render", return_value="TOP_STORIES") as render:
            for slug in ("overview", "news", "notes"):
                body = f1lib.shell(ctx, slug, "Page", "Kicker", "Title", "Subtitle", "ORIGINAL_BODY")
                if slug in ("overview", "news"):
                    self.assertLess(body.index("TOP_STORIES"), body.index("ORIGINAL_BODY"))
                else:
                    self.assertNotIn("TOP_STORIES", body)
        self.assertEqual(render.call_count, 2)

    def test_committed_editorial_records_follow_the_contract(self):
        for path in (Path(build.ROOT) / "data").glob("*/news_highlights.json"):
            with self.subTest(path=path):
                briefing.validate(json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main()
