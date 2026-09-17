import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build
import f1lib


class TyreAvailabilityTests(unittest.TestCase):
    def test_official_inventory_does_not_require_fastf1(self):
        ctx = {"name": "Spanish Grand Prix", "year": "2026", "dir": "spain", "results": []}
        with patch.object(f1lib, "_load_pace", side_effect=AssertionError("Official counts must not load FastF1")):
            body = f1lib.render_tyre_availability(
                ctx, official={"NOR": (1, 2, 3, 0, 1, 1)},
                compounds=("C2", "C3", "C4"), source_url="https://www.fia.com/example.pdf")
        self.assertIn("Tyre sets available for the race (official)", body)
        self.assertIn("Hard (C2)", body)
        self.assertIn("Soft (C4)", body)
        self.assertIn("Spanish Grand Prix", body)
        self.assertNotIn("Italian Grand Prix", body)
        self.assertIn("https://www.fia.com/example.pdf", body)

    def test_no_data_does_not_fabricate_inventory(self):
        with patch.object(f1lib, "_load_pace", return_value=[]):
            self.assertEqual(f1lib.render_tyre_availability({"dir": "spain"}), "")

    def test_invalid_official_counts_fail_explicitly(self):
        with patch.object(f1lib, "_load_pace", return_value=[]):
            for counts in (None, 1, (1, 2), (1, 2, 3, 4, 5, -1), (True, 0, 0, 0, 0, 0)):
                with self.subTest(counts=counts), self.assertRaises(ValueError):
                    f1lib.render_tyre_availability({"dir": "spain"}, official={"NOR": counts})

    def test_estimate_uses_event_compounds_without_claiming_official_inventory(self):
        sessions = [{"tyre_stints": [{"fresh": True, "code": "NOR", "compound": "SOFT"}]}]
        with patch.object(f1lib, "_load_pace", return_value=sessions):
            body = f1lib.render_tyre_availability({"dir": "spain"}, compounds=("C2", "C3", "C4"))
        self.assertIn("Hard (C2)", body)
        self.assertIn("Soft (C4)", body)
        self.assertNotIn("C5", body)
        self.assertIn("not an official inventory", body)


class PublishedRaceTyreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data = Path(temporary.name)
        (self.data / "spain").mkdir()
        self.ctx = {"dir": "spain", "name": "Spanish Grand Prix", "year": 2026, "results": []}
        self.snapshot = {
            "year": 2026, "gp": "spain", "race_date": "2026-09-13",
            "source": {"url": "https://coffeecornermotorsport.com/example/",
                       "publisher": "Coffee Corner Motorsport"},
            "chart": {"asset": "race-tyres-spain.webp", "sha256": "a" * 64,
                      "credit": "Pirelli Motorsport", "provenance": "secondary-reproduction"},
        }
        self.verified = {
            "year": 2026, "gp": "spain", "race_date": "2026-09-13",
            "source_sha256": "a" * 64, "reviewed_at": "2026-09-17T10:53:31Z",
            "review_method": "Visual review", "entrants": 2, "compounds": ["C2", "C3", "C4"],
            "drivers": {"HUL": [1, 4, 1, 0, 1, 0], "VER": [0, 3, 0, 1, 2, 0]},
        }

    def save(self, verified=None):
        (self.data / "spain/race_tyres_verified.json").write_text(
            json.dumps(self.verified if verified is None else verified), encoding="utf-8")

    def render(self, snapshot=None, state="available", error=""):
        with patch("race_tyres.context", return_value={
            "snapshot": self.snapshot if snapshot is None else snapshot,
            "status": {"state": state, "error": error, "checked_at": "2026-09-17T11:00:00Z"},
        }), patch.object(f1lib, "DATA_DIR", str(self.data)), \
                patch.object(f1lib, "_load_pace", side_effect=AssertionError("Not a timing inventory")):
            return f1lib.render_race_tyres(self.ctx)

    def test_verified_table_and_full_source_chart_without_timing(self):
        self.save()
        body = self.render()
        self.assertIn("Hard (C2)", body)
        self.assertIn("Medium (C3)", body)
        self.assertIn("Soft (C4)", body)
        self.assertIn("4 used", body)
        self.assertIn("reproduced by", body)
        self.assertIn("Coffee Corner Motorsport", body)
        self.assertIn('src="../assets/race-tyres-spain.webp"', body)
        self.assertIn('onclick="zoomImg(this)"', body)
        self.assertIn('onkeydown=', body)
        self.assertIn("not tyres remaining after the finish", body)
        self.assertNotIn("estimated from FastF1", body)

    def test_new_chart_publishes_before_numeric_review(self):
        body = self.render()
        self.assertIn("Full-resolution chart", body)
        self.assertIn("not yet been visually verified", body)
        self.assertNotIn("tyre-avail filterable", body)

    def test_changed_image_or_weekend_never_reuses_old_numeric_rows(self):
        for field, value in (("source_sha256", "b" * 64), ("year", 2025),
                             ("gp", "italy"), ("race_date", "2026-09-06")):
            with self.subTest(field=field):
                verified = {**self.verified, field: value}
                self.save(verified)
                body = self.render()
                self.assertIn("Full-resolution chart", body)
                self.assertIn("awaits renewed visual review", body)
                self.assertNotIn("tyre-avail filterable", body)

    def test_missing_or_restricted_chart_does_not_become_zero_counts(self):
        self.save()
        for state, error in (("not_found", ""), ("access_restricted", "Source requires login"),
                             ("error", "Missing chart asset")):
            with self.subTest(state=state):
                body = self.render(snapshot={}, state=state, error=error)
                self.assertIn("normally appear after qualifying", body)
                self.assertIn("not proof of non-publication", body)
                self.assertNotIn("tyre-avail filterable", body)
                self.assertNotIn("0 new", body)
                if error:
                    self.assertIn(error, body)

    def test_retained_chart_and_table_have_explicit_refresh_warning(self):
        self.save()
        body = self.render(state="error", error="HTTP 503")
        self.assertIn("last successfully collected chart", body)
        self.assertIn("HTTP 503", body)
        self.assertIn("Hard (C2)", body)

    def test_invalid_reviewed_data_fails_before_rendering(self):
        invalid = [
            {**self.verified, "entrants": 22},
            {**self.verified, "compounds": ["C2", "C2", "C4"]},
            {**self.verified, "compounds": ["C4", "C3", "C2"]},
            {**self.verified, "reviewed_at": "2026-09-17"},
            {**self.verified, "drivers": {"HUL": [True, 4, 1, 0, 1, 0], "VER": [0, 3, 0, 1, 2, 0]}},
        ]
        missing = copy.deepcopy(self.verified)
        del missing["drivers"]["VER"]
        invalid.append(missing)
        for verified in invalid:
            with self.subTest(verified=verified):
                self.save(verified)
                with self.assertRaises(ValueError):
                    self.render()

    def test_every_registered_tyre_page_uses_shared_inventory_once(self):
        with patch.object(f1lib, "render_race_tyres", return_value="SHARED_RACE_TYRES"), \
                patch.object(f1lib, "render_fia_documents", return_value=""), \
                patch.object(f1lib, "render_fia_media", return_value=""), \
                patch("history_render.render", return_value=""):
            for ctx in build.season_gps():
                with self.subTest(gp=ctx["dir"]):
                    page = f1lib.shell(ctx, "tyres", "Tyres", "Tyres", "Tyres", "", "CURATED_TYRES")
                    self.assertEqual(page.count("SHARED_RACE_TYRES"), 1)
                    self.assertLess(page.index("SHARED_RACE_TYRES"), page.index("CURATED_TYRES"))

    def test_backfilled_reviews_have_all_22_entrants(self):
        for gp in ("italy", "spain"):
            with self.subTest(gp=gp):
                verified = json.loads((Path(f1lib.DATA_DIR) / gp / "race_tyres_verified.json").read_text())
                snapshot = {key: verified[key] for key in ("year", "gp", "race_date")}
                snapshot["chart"] = {"sha256": verified["source_sha256"]}
                review = f1lib.reviewed_race_tyres({"dir": gp}, snapshot)
                self.assertEqual(review["state"], "verified")
                self.assertEqual(len(review["drivers"]), 22)
                if review["race_date"] == "2026-09-13":
                    self.assertEqual(review["drivers"]["HUL"], [1, 4, 1, 0, 1, 0])
                    self.assertEqual(review["drivers"]["VER"], [0, 3, 0, 1, 2, 0])
                    self.assertNotIn("HAD", review["drivers"])


if __name__ == "__main__":
    unittest.main()
