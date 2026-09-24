"""Offline content parity checks: verified event evidence, not borrowed GP facts."""
import unittest
from unittest.mock import patch

import build
import content_azerbaijan
import content_italy
import content_spain


class GPParityTests(unittest.TestCase):
    def setUp(self):
        self.contexts = {
            ctx["dir"]: ctx for ctx in build.season_gps()
            if ctx["dir"] in ("italy", "spain")
        }
        for slug, ctx in self.contexts.items():
            ctx.update(status="past", results=[], extra={}, weather={}, weather_ok=False)
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
        self.assertNotIn("Tyre sets available for the race (official)", body)
        self.assertFalse(hasattr(content_italy, "TYRES_AVAILABLE_FOR_RACE"))

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
            self.assertIn("not applicable before its debut", pages["facts"]["body"])
            self.assertIn("different-track", pages["facts"]["body"])
        self.assertNotIn("Past winners, polesitters and weekend-specific trivia: awaiting",
                         pages["facts"]["body"])
        self.assertIn("Antonelli won the Madring's inaugural Grand Prix", pages["moments"]["body"])
        self.assertIn("Measured long-run degradation and stint strategy: unavailable in this build",
                      pages["tyres"]["body"])
        self.assertIn("no Madrid Heat Hazard", pages["schedule"]["body"])
        self.assertIn("Hadjar", pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", pages["schedule"]["body"])

    def test_madrid_permutations_are_dated_and_do_not_reuse_old_scoring(self):
        body = self.spain()["standings"]["body"]
        self.assertIn("Madrid's effect on the title fight", body)
        self.assertIn("widened his lead, it did not narrow it", body)
        self.assertIn("Russell concedes the title fight", body)
        self.assertNotIn("10 September snapshot", body)
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
        self.assertIn("L24 at 5160 m", spain["powerunit"]["body"])
        self.assertIn("L25 at 5230 m", spain["powerunit"]["body"])
        self.assertIn("Document 25", spain["powerunit"]["body"])
        self.assertIn("Team-by-team car presentation submissions", spain["upgrades"]["body"])


class AzerbaijanParityTests(unittest.TestCase):
    def setUp(self):
        self.ctx = next(ctx for ctx in build.season_gps() if ctx["dir"] == "azerbaijan")
        self.ctx.update(status="live", results=[], extra={}, weather={}, weather_ok=False)
        self.env = {"schedule_rows": lambda: "SCHEDULE_ROWS",
                    "weather_cards": lambda: "WEATHER_CARDS", "weather_ok": False}
        self.pages = content_azerbaijan.build_pages(self.ctx, self.env)

    def test_seventeen_surfaces_preserve_automatic_feeds(self):
        automatic = {"results", "news", "h2h"}
        self.assertEqual({n[0] for n in self.ctx["nav"]}, set(self.pages) | automatic)
        with patch.object(content_azerbaijan.f1lib, "auto_reliability",
                          return_value="LIVE_PIT_TABLE"):
            pages = content_azerbaijan.build_pages(self.ctx, self.env)
        self.assertIn("LIVE_PIT_TABLE", pages["reliability"]["body"])

    def test_visually_reviewed_prescriptions_correct_old_errors(self):
        body = self.pages["tyres"]["body"]
        self.assertIn("C3 and C4", body)
        self.assertIn("not C5", body)
        self.assertIn("70&deg;C for slicks\nand intermediates", body)
        self.assertIn("40&deg;C for wets", body)
        self.assertIn("19.5-second", body)
        self.assertIn("not Pirelli", body)
        self.assertNotIn("after Friday practice", body)
        self.assertNotIn("mandatory race tyres alongside C5", body)
        self.assertIn(content_azerbaijan.PREVIEW_IMAGE, body)
        self.assertIn(content_azerbaijan.FIA_TYRES_ASSET, body)

    def test_complete_energy_sheet_and_qualifying_only_exceptions(self):
        body = self.pages["powerunit"]["body"]
        for value in ("3,796 m", "50 kW/s", "4,177 m", "4,270 m", "(TBC)",
                      "Outlaps other than in the race", "Base–Overtake",
                      "1,500–2,870 m", "[4,050–5,300 m]", "[5,600–6,000 m]",
                      "qualifying only", "1.0 s", "parts declaration or a confirmed penalty"):
            self.assertIn(value, body)
        self.assertNotIn("Sunday", body)
        self.assertNotIn("Manual Override", body)

    def test_circuit_map_notes_are_interpreted_not_just_linked(self):
        body = self.pages["circuit"]["body"]
        for value in ("45 m after T19", "45 m after T20", "110 m after T2",
                      "160 m after T2", "90 m after T16", "20 m before T17",
                      "2.033 / 2.025 / 1.945", "less than 100 seconds",
                      "during and after qualifying", "before T16", "80 km/h"):
            self.assertIn(value, body)
        self.assertNotIn("DRS-assisted", body)
        self.assertNotIn("statistical certainty", body)

    def test_all_teams_upgrades_and_rookie_context(self):
        body = self.pages["teams"]["body"]
        for team in ("Mercedes", "Ferrari", "McLaren", "Red Bull", "Racing Bulls",
                     "Alpine", "Haas", "Audi", "Williams", "Aston Martin", "Cadillac"):
            self.assertIn(team, body)
        self.assertNotIn("Team-by-team weekend storylines: awaiting", body)
        self.assertIn("10:00–11:00 Tallinn", self.pages["upgrades"]["body"])
        self.assertIn("No absent declaration is counted as a nil return",
                      self.pages["upgrades"]["body"])
        self.assertIn("Arvid Lindblad", self.pages["rookies"]["body"])
        self.assertIn("painful", body)

    def test_schedule_and_notes_follow_saturday_race(self):
        self.assertIn("SCHEDULE_ROWS", self.pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", self.pages["schedule"]["body"])
        for slug in ("overview", "notes"):
            self.assertIn("15:00 Baku / 14:00 Tallinn", self.pages[slug]["body"])
            self.assertIn(self.ctx["standings"]["summary"], self.pages[slug]["body"])
        self.assertIn("every other rival", self.pages["standings"]["body"])
        self.assertIn("no fastest-lap bonus", self.pages["standings"]["body"])
        self.assertNotIn("A curated moments list", self.pages["moments"]["body"])


if __name__ == "__main__":
    unittest.main()
