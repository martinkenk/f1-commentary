"""Offline regression coverage for the published Madrid FIA material."""
import copy
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import build
import content_generic
import content_spain
import f1lib


class SpainContentTests(unittest.TestCase):
    def setUp(self):
        self.ctx = next(ctx for ctx in build.season_gps() if ctx["dir"] == "spain")
        self.ctx.update(status="future", results=[], weather={}, weather_ok=False)
        self.env = {
            "schedule_rows": lambda: "SCHEDULE_ROWS",
            "weather_cards": lambda: "WEATHER_CARDS",
            "weather_ok": False, "weather": {},
        }

    def pages(self):
        return content_spain.build_pages(self.ctx, self.env)

    def test_registered_and_preserves_unrelated_live_surfaces(self):
        self.assertIs(build.BESPOKE["spain"], content_spain.build_pages)
        generic = content_generic.build_pages(self.ctx, self.env)
        pages = self.pages()
        self.assertIn(generic["standings"]["body"], pages["standings"]["body"])
        self.assertIn("SCHEDULE_ROWS", pages["overview"]["body"])
        self.assertIn("SCHEDULE_ROWS", pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", pages["schedule"]["body"])

    def test_published_fia_material_renders_in_all_event_states(self):
        for state in ("future", "live", "past"):
            with self.subTest(state=state):
                self.ctx["status"] = state
                pages = self.pages()
                for slug in ("circuit", "powerunit", "tyres", "upgrades"):
                    self.assertIn("https://www.fia.com/", pages[slug]["body"])
                    self.assertNotIn("not published yet", pages[slug]["body"])
                self.assertNotIn("energy-map document for this event: awaiting",
                                 pages["powerunit"]["body"])
                self.assertNotIn("compound allocation and tyre-set breakdown: awaiting",
                                 pages["tyres"]["body"])

    def test_recharge_session_columns_match_fia_document(self):
        body = self.pages()["powerunit"]["body"]
        rows = re.findall(r"<tr><td>(.*?)</td><td class=\"num\">(.*?)</td></tr>", body)
        self.assertEqual(rows, [
            ("Race &mdash; Overtake not active", "8.5 MJ"),
            ("Race &mdash; Overtake active", "9.0 MJ"),
            ("Qualifying", "7.5 MJ"),
            ("Free practice", "9.0 MJ"),
            ("Out-laps other than in the race", "9.0 MJ"),
        ])
        for value in ("3206 m", "100 kW/s", "L24", "L25", "TBC"):
            self.assertIn(value, body)

    def test_tyre_axles_match_verified_fia_table(self):
        rows = re.findall(
            r"<tr><td>(.*?)</td><td>(.*?)</td><td class=\"num\">(.*?)</td>"
            r"<td class=\"num\">(.*?)</td><td class=\"num\">(.*?)</td></tr>",
            self.pages()["tyres"]["body"])
        self.assertEqual(rows, [
            ("Slick", "Front", "26.5 psi", "&ge;27.5 psi", "-2.75&deg;"),
            ("Slick", "Rear", "25.5 psi", "&ge;26.5 psi", "-1.5&deg;"),
            ("Intermediate", "Front", "28.0 psi", "&ge;29.0 psi", "-3&deg;"),
            ("Intermediate", "Rear", "26.5 psi", "&ge;27.5 psi", "-2&deg;"),
            ("Wet", "Front", "27.0 psi", "&ge;29.0 psi", "-3&deg;"),
            ("Wet", "Rear", "25.0 psi", "&ge;27.5 psi", "-2&deg;"),
        ])

    def test_both_aero_modes_and_source_discrepancy_are_explicit(self):
        before = copy.deepcopy(self.ctx["cal"])
        pages = self.pages()
        for metres in (100, 130):
            self.assertIn(f"{metres} m after T22", pages["circuit"]["body"])
        for metres in (40, 90):
            self.assertIn(f"{metres} m after T3", pages["circuit"]["body"])
        for slug in ("overview", "circuit", "powerunit", "facts", "notes"):
            self.assertIn("5.414 km", pages[slug]["body"])
            self.assertIn("5.416 km", pages[slug]["body"])
        self.assertEqual(self.ctx["cal"], before)

    def test_figures_are_local_zoomable_and_cited(self):
        assets = set()
        for page in self.pages().values():
            for figure in re.findall(r"<figure.*?</figure>", page["body"], re.S):
                src = re.search(r'src="\.\./assets/([^"]+)"', figure)[1]
                self.assertTrue((Path(build.ROOT) / "assets_src" / src).is_file(), src)
                self.assertIn('onclick="zoomImg(this)"', figure)
                self.assertIn('<a href="https://', figure)
                assets.add(src)
        self.assertTrue({
            "spain_fia_circuit_map_2026.png",
            "spain_fia_pit_lane_2026.png",
            "spain_fia_emergency_exits_2026.png",
            "spain_fia_power_unit_2026.png",
            "spain_fia_pirelli_prescriptions_2026.png",
            "spain_pirelli_tyres_2026.webp",
        }.issubset(assets))

    def test_future_penalties_remain_automatic(self):
        with patch.object(content_spain, "auto_penalties", return_value="LIVE_DECISION_TRACKER") as tracker:
            body = self.pages()["penalties"]["body"]
        tracker.assert_called_once_with(self.ctx)
        self.assertIn("LIVE_DECISION_TRACKER", body)
        self.assertIn("not penalties already imposed", body)

    def test_complete_friday_upgrade_submissions_replace_pending_notice(self):
        expected = {
            "McLaren": (2, 1), "Mercedes": (4, 3), "Red Bull": (6, 2),
            "Ferrari": (8, 1), "Williams": (10, 0), "Racing Bulls": (11, 0),
            "Aston Martin": (12, 0), "Haas": (13, 0), "Audi": (14, 0),
            "Alpine": (15, 1), "Cadillac": (17, 2),
        }
        self.assertEqual({
            team: (page, len(updates))
            for team, page, updates in content_spain.UPGRADE_SUBMISSIONS
        }, expected)
        for state in ("future", "live", "past"):
            with self.subTest(state=state):
                self.ctx["status"] = state
                page = self.pages()["upgrades"]
                body = page["body"]
                self.assertIn("FIA Document 11", page["kicker"])
                self.assertNotIn("awaiting", body.lower())
                self.assertNotIn("will be added", body)
                self.assertEqual(body.count("Filed reason:"), 10)
                self.assertEqual(body.count("Filed reason: Reliability."), 2)
                for team, (source_page, count) in expected.items():
                    self.assertIn(f'<tr><td>{team}</td><td class="num">{count}</td>', body)
                    self.assertIn(f"{content_spain.FIA_UPGRADES_URL}#page={source_page}", body)
                for item in ("Front drum", "Floor bib", "Diffuser vane", "Rear suspension"):
                    self.assertIn(item, body)
                self.assertIn("not independently", body)
                self.assertIn("Friday car presentation: confirmed procedure", body)

    def test_all_submission_pages_render_once_with_diagrams_and_nil_returns(self):
        body = self.pages()["upgrades"]["body"]
        for page in range(2, 19):
            asset = f"{content_spain.FIA_UPGRADES_ASSET}-p{page}.png"
            self.assertEqual(body.count(f'src="../assets/{asset}"'), 1)
            self.assertTrue((Path(build.ROOT) / "assets_src" / asset).is_file(), asset)
            self.assertIn(f"{content_spain.FIA_UPGRADES_URL}#page={page}", body)
        gallery = f1lib.render_fia_media(self.ctx, "upgrades", body)
        self.assertNotIn(content_spain.FIA_UPGRADES_ASSET, gallery)

    def test_published_pu_usage_no_longer_claimed_pending(self):
        body = self.pages()["powerunit"]["body"]
        self.assertIn("pu_elements_used_per_driver_up_to_now.pdf", body)
        self.assertNotIn("penalties remain awaiting", body)

    def test_upgrade_table_opens_team_reader_instead_of_downloading_pdf(self):
        body = self.pages()["upgrades"]["body"]
        table = re.search(r'<table class="data">.*?</table>', body, re.S)[0]
        self.assertNotIn(".pdf", table)
        for team, page, _ in content_spain.UPGRADE_SUBMISSIONS:
            self.assertIn(f'href="#upgrade-submission-{page}" data-document-reader', table)
            self.assertIn(f'data-reader-title="{team} - FIA Document 11"', table)
            self.assertIn(f'<details id="upgrade-submission-{page}">', body)
        self.assertEqual(table.count("data-document-reader"), 11)


if __name__ == "__main__":
    unittest.main()
