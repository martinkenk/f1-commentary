"""Offline content parity checks: verified event evidence, not borrowed GP facts."""
import unittest
from unittest.mock import patch

import build
import content_italy
import content_spain


class GPParityTests(unittest.TestCase):
    def setUp(self):
        self.contexts = {
            ctx["dir"]: ctx for ctx in build.season_gps()
            if ctx["dir"] in ("italy", "spain")
        }
        for slug, ctx in self.contexts.items():
            ctx.update(status="past" if slug == "italy" else "future",
                       results=[], extra={}, weather={}, weather_ok=False)
        self.env = {
            "schedule_rows": lambda: "SCHEDULE_ROWS",
            "weather_cards": lambda: "WEATHER_CARDS",
            "weather": {}, "weather_ok": False,
        }

    def italy(self):
        return content_italy.build_pages(self.contexts["italy"], self.env)

    def spain(self):
        return content_spain.build_pages(self.contexts["spain"], self.env)

    def test_all_seventeen_surfaces_are_authored_or_engine_provided(self):
        engine_pages = {"results", "news", "h2h", "reliability", "penalties"}
        for slug, pages in (("italy", self.italy()), ("spain", self.spain())):
            nav = {row[0] for row in self.contexts[slug]["nav"]}
            self.assertEqual(len(nav), 17)
            self.assertFalse(nav - set(pages) - engine_pages)
            self.assertTrue(all(page["body"].strip() for page in pages.values()))

    def test_completed_italy_leads_with_sourced_race_chronology(self):
        pages = self.italy()
        self.assertIn("Completed 6 September", pages["overview"]["kicker"])
        for slug in ("overview", "notes", "teams"):
            body = pages[slug]["body"]
            self.assertIn("6 September: Antonelli wins from P19", body)
            self.assertIn(content_italy.RACE_REPORT_URL, body)
            self.assertLess(body.index("Qualifying and grid"), body.index("Opening laps"))
            self.assertLess(body.index("Opening laps"), body.index("Strategy split"))
            self.assertLess(body.index("Strategy split"), body.index("Finish:"))
        self.assertIn("Pre-race briefing archive", pages["overview"]["body"])
        self.assertIn("Antonelli wins at Monza from P19", pages["news"]["body"])
        self.assertNotIn("Session-by-session commentary notes: awaiting", pages["notes"]["body"])

    def test_italy_practice_data_and_actual_strategy_replace_stale_placeholder(self):
        body = self.italy()["tyres"]["body"]
        self.assertIn('href="results.html">FP2 clean-lap long runs', body)
        self.assertIn("not a fitted degradation curve", body)
        self.assertIn("fresh mediums under the later VSC", body)
        self.assertNotIn("Long-run degradation data: awaiting", body)
        self.assertNotIn("every driver must use both compounds", body)
        self.assertNotIn("top-10 runners who start on their Q2 time", body)
        self.assertIn("no requirement for top-ten qualifiers", body)
        self.assertIn("Tyres Available for Race", body)

    def test_italian_home_win_history_is_not_frozen_before_race(self):
        pages = self.italy()
        for slug in ("overview", "facts", "moments"):
            self.assertNotIn("No Italian driver has won", pages[slug]["body"])
            self.assertNotIn("No Italian has won", pages[slug]["body"])
        self.assertIn("2026 — Antonelli wins", pages["moments"]["body"])
        self.assertIn("2021–2025", pages["facts"]["body"])
        self.assertIn("Current-grid track-history", pages["facts"]["body"])

    def test_automatic_comparisons_and_pit_data_are_preserved(self):
        with patch.object(content_italy, "auto_h2h", return_value="EVENT_H2H"), \
             patch.object(content_italy, "render_reliability", return_value="PIT_DATA") as pits:
            pages = self.italy()
        self.assertIn("EVENT_H2H", pages["h2h"]["body"])
        self.assertNotIn("No audited season-long", pages["h2h"]["body"])
        self.assertEqual(pages["reliability"]["body"], "PIT_DATA")
        self.assertIn("suspected car damage", pits.call_args.kwargs["intro_html"])
        self.assertIn("not establish medical clearance", pits.call_args.kwargs["intro_html"])

    def test_madrid_confirmed_replacements_are_not_pending(self):
        pages = self.spain()
        for slug in ("overview", "notes", "rookies", "teams"):
            self.assertIn("Liam Lawson", pages[slug]["body"])
            self.assertIn("Yuki Tsunoda", pages[slug]["body"])
            self.assertIn(content_spain.LINEUP_URL, pages[slug]["body"])
        self.assertNotIn("Reserve or replacement driver changes: awaiting",
                         pages["rookies"]["body"])
        self.assertIn("Rookie FP1 line-ups", pages["rookies"]["body"])
        self.assertNotIn("Team-by-team weekend storylines: awaiting", pages["teams"]["body"])

    def test_madrid_history_and_unknowns_are_explicit(self):
        pages = self.spain()
        for slug in ("facts", "moments"):
            self.assertIn("not applicable before its debut", pages[slug]["body"])
            self.assertIn("different-track", pages[slug]["body"])
        self.assertNotIn("Past winners, polesitters and weekend-specific trivia: awaiting",
                         pages["facts"]["body"])
        self.assertIn("No Madrid F1 practice or race sample exists", pages["tyres"]["body"])
        self.assertIn("no Madrid Heat Hazard", pages["schedule"]["body"])
        self.assertIn("Hadjar", pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", pages["schedule"]["body"])

    def test_madrid_permutations_are_dated_and_do_not_reuse_old_scoring(self):
        body = self.spain()["standings"]["body"]
        self.assertIn("10 September snapshot", body)
        self.assertIn("41 points", body)
        self.assertIn("countback", body)
        self.assertIn("No fastest-lap bonus", body)
        self.assertNotIn("26 points", body)
        self.assertIn(self.contexts["spain"]["standings"]["drivers"], body)

    def test_event_specific_fia_cautions_and_values_survive(self):
        italy, spain = self.italy(), self.spain()
        self.assertIn("5.0 MJ", italy["powerunit"]["body"])
        self.assertIn("Pre-running snapshot, not final post-Monza totals", italy["powerunit"]["body"])
        self.assertIn("Document 33", italy["powerunit"]["body"])
        self.assertIn("1:42.0 between the Safety Car lines", italy["circuit"]["body"])
        self.assertIn("during and after qualifying", italy["circuit"]["body"])
        self.assertIn(content_italy.FIA_SC_TIME_URL, italy["circuit"]["body"])
        for slug in ("overview", "facts", "notes", "circuit", "powerunit"):
            self.assertIn("5.414 km", spain[slug]["body"])
            self.assertIn("5.416 km", spain[slug]["body"])
        self.assertIn("7.5 MJ", spain["powerunit"]["body"])
        self.assertIn("values remain <strong>TBC", spain["powerunit"]["body"])
        self.assertIn("Team-by-team car presentation submissions", spain["upgrades"]["body"])


if __name__ == "__main__":
    unittest.main()
