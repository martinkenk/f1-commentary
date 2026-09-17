import copy
import unittest
from unittest.mock import patch

import build
import content_generic
import f1lib
import history_render


def driver(identity, name, wins, *, starts=5, best=1, season=True):
    return {
        "id": identity, "name": name, "code": identity.upper(), "season_driver": season,
        "starts": starts, "wins": wins, "podiums": wins, "poles": 0,
        "best_finish": best, "best_years": [2025] if best else [],
        "win_years": [2021, 2023] if wins else [],
    }


PROFILE = {
    "completed_races": 9, "venue_edition": 10,
    "grand_prix": {"id": "azerbaijan", "name": "Azerbaijan Grand Prix",
                   "completed_races": 8, "edition": 9},
    "names_at_venue": [
        {"name": "European Grand Prix", "count": 1, "years": [2016]},
        {"name": "Azerbaijan Grand Prix", "count": 8,
         "years": [2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025]},
    ],
    "drivers": [driver("per", "Sergio Perez", 2), driver("ver", "Max Verstappen", 2),
                driver("new", "New driver", 0, starts=0, best=None),
                driver("nc", "Unclassified driver", 0, best=None)],
    "constructors": [driver("red-bull", "Red Bull", 4)],
    "most_driver_wins": ["per", "ver"], "most_constructor_wins": ["red-bull"],
    "wins_from_pole": {"wins": 3, "races": 9},
    "recent_winners": [{
        "year": 2025, "name": "Azerbaijan Grand Prix", "driver": "Max Verstappen",
        "constructor": "Red Bull", "grid": 1, "pole": True,
        "url": "https://github.com/f1db/f1db/tree/main/src/data/seasons/2025/races/17-azerbaijan",
    }],
    "teammates": {
        "limit": 10, "races": 9, "pairs": [{
            "team": "Red Bull", "drivers": [{"name": "Sergio Perez"}, {"name": "Max Verstappen"}],
            "Qualifying": {"wins": [1, 2], "excluded": 1},
            "Race": {"wins": [2, 1], "excluded": 1},
            "events": [{
                "year": 2025, "name": "Azerbaijan Grand Prix",
                "url": "https://github.com/f1db/f1db/tree/main/src/data/seasons/2025/races/17-azerbaijan",
                "Qualifying": {"positions": [3, None], "statuses": ["classified", "no-time"],
                               "winner": None, "reason": "No qualifying time"},
                "Race": {"positions": [2, 1], "statuses": ["classified", "classified"],
                         "winner": 1, "reason": ""},
            }],
        }],
    },
}
RECORD = {
    "profile": PROFILE, "error": "",
    "source": {"release": "v2026.14.0", "release_url": "https://github.com/f1db/f1db/releases/tag/v2026.14.0"},
}


class HistoryRenderTests(unittest.TestCase):
    def setUp(self):
        self.ctx = next(ctx for ctx in build.season_gps() if ctx["dir"] == "azerbaijan")
        self.ctx.update(status="future", results=[], weather={}, weather_ok=False)
        self.record = copy.deepcopy(RECORD)
        self.mock = patch.object(history_render.circuit_history, "context", return_value=self.record)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_venue_and_named_gp_editions_are_separate_and_future_labelled(self):
        body = history_render.render(self.ctx, "circuit")
        for value in ("10th", "9th Azerbaijan Grand Prix", "European Grand Prix", "2016",
                      "is scheduled to be", "all venues", "v2026.14.0", "CC BY 4.0",
                      "before 2026-09-26"):
            self.assertIn(value, body)
        self.assertEqual([history_render.ordinal(n) for n in (1, 2, 3, 11, 12, 13, 21)],
                         ["1st", "2nd", "3rd", "11th", "12th", "13th", "21st"])

    def test_driver_records_keep_ties_and_distinct_empty_states(self):
        body = history_render.render(self.ctx, "facts")
        for value in ("Sergio Perez", "Max Verstappen", "No previous start",
                      "No classified finish", "history-all-drivers", "filterable",
                      "Constructor record book"):
            self.assertIn(value, body)
        self.assertNotIn("PNone", body)
        self.assertNotIn("P0", body)
        self.assertIn('data-sort=""', body)
        self.assertIn("Source provenance", body)

    def test_historical_comparisons_show_exclusions_and_evidence(self):
        body = history_render.render(self.ctx, "h2h")
        for value in ("1 &ndash; 2", "2 &ndash; 1", "1 excluded", "No qualifying time",
                      "2025", "last 10", "9 editions", "not pure pace"):
            self.assertIn(value, body)
        self.assertIn("https://github.com/f1db/f1db/tree/main/src/data/seasons/2025/races/17-azerbaijan",
                      body)

    def test_winner_grid_context_and_pole_denominator_remain_separate(self):
        body = history_render.render(self.ctx, "facts")
        for value in ("3 / 9", "known official polesitter", "Recent winners",
                      "Starting grid is race", "Car starts"):
            self.assertIn(value, body)

    def test_retained_snapshot_keeps_records_but_shows_refresh_failure(self):
        self.record["error"] = "F1DB unavailable; retained last-good snapshot"
        body = history_render.render(self.ctx, "circuit")
        self.assertIn("F1DB unavailable", body)
        self.assertIn("10th", body)
        self.assertIn("Pre-weekend record book", body)

    def test_missing_snapshot_is_not_treated_as_zero_history(self):
        self.record["profile"] = None
        self.record["error"] = "Download failed <unsafe>"
        body = history_render.render(self.ctx, "circuit")
        self.assertIn("Download failed &lt;unsafe&gt;", body)
        self.assertIn("Missing data is not evidence", body)
        self.assertNotIn("1st", body)
        self.assertNotIn("debut venue:", body)

    def test_debut_is_explicit_but_gp_can_have_history_elsewhere(self):
        self.record["profile"].update(completed_races=0, venue_edition=1, names_at_venue=[])
        body = history_render.render(self.ctx, "circuit")
        self.assertIn("A debut venue", body)
        self.assertIn("1st", body)
        self.assertIn("9th Azerbaijan Grand Prix", body)

    def test_markup_from_data_and_unsafe_links_are_not_executed(self):
        self.record["profile"]["grand_prix"]["name"] = '<img src=x onerror="bad()">'
        self.record["source"]["release_url"] = "javascript:alert(1)"
        body = history_render.render(self.ctx, "overview")
        self.assertIn("&lt;img", body)
        self.assertNotIn("<img", body)
        self.assertNotIn("javascript:", body)

    def test_shared_shell_preserves_curated_content_and_injects_once(self):
        for page in ("overview", "circuit", "facts", "h2h"):
            with self.subTest(page=page):
                body = f1lib.shell(self.ctx, page, "Title", "Kicker", "Title", "Sub", "CURATED_BODY")
                self.assertEqual(body.count('id="circuit-history"'), 1)
                self.assertIn("CURATED_BODY", body)
        self.assertEqual(history_render.render(self.ctx, "upgrades"), "")

    def test_generic_page_does_not_claim_published_history_is_awaiting(self):
        env = {"schedule_rows": lambda: "", "weather_cards": lambda: "", "weather_ok": False}
        pages = content_generic.build_pages(self.ctx, env)
        self.assertNotIn("Past winners, polesitters and weekend-specific trivia: awaiting",
                         pages["facts"]["body"])
        self.record["profile"] = None
        pages = content_generic.build_pages(self.ctx, env)
        self.assertIn("Past winners, polesitters and weekend-specific trivia: awaiting",
                      pages["facts"]["body"])


class PublishedHistoryIntegrationTests(unittest.TestCase):
    def test_all_registered_gps_have_sourced_history_on_relevant_surfaces(self):
        for ctx in build.season_gps():
            for page in ("overview", "circuit", "facts", "h2h"):
                with self.subTest(gp=ctx["dir"], page=page):
                    body = history_render.render(ctx, page)
                    self.assertEqual(body.count('id="circuit-history"'), 1)
                    self.assertNotIn("Historical circuit records are unavailable", body)
                    self.assertIn("CC BY 4.0", body)
                    self.assertIn(ctx["race_date"], body)

    def test_baku_madrid_and_sepang_have_different_venue_and_gp_editions(self):
        examples = {
            "azerbaijan": ("10th", "9th Azerbaijan Grand Prix", "European Grand Prix"),
            "spain": ("1st", "56th Spanish Grand Prix", "A debut venue"),
            "bahrain": ("20th", "22nd Bahrain Grand Prix", "Malaysian Grand Prix"),
        }
        for ctx in build.season_gps():
            if ctx["dir"] not in examples:
                continue
            body = history_render.render(ctx, "circuit")
            for marker in examples[ctx["dir"]]:
                self.assertIn(marker, body)


if __name__ == "__main__":
    unittest.main()
