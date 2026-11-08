import datetime
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import standings


def table(kind, points=100):
    rows = []
    for index in range(1, 23 if kind == "drivers" else 12):
        if kind == "drivers":
            cells = [str(index), f"<span>Driver {index}</span><span>DRV</span>",
                     "GBR", f"Team {(index + 1) // 2}", str(points)]
        else:
            cells = [str(index), f"Team {index}", str(points)]
        rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    return "<table><thead><tr><th>Pos.</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def source_table(rows, kind):
    rendered = []
    for row in rows:
        if kind == "drivers":
            pos, name, code, team, points = row
            cells = [pos, f"{name} {code}", "GBR", team, points]
        else:
            pos, team, points = row
            cells = [pos, team, points]
        rendered.append("<tr>" + "".join(f"<td>{value}</td>" for value in cells) + "</tr>")
    return "<table><tbody>" + "".join(rendered) + "</tbody></table>"


class StandingsTests(unittest.TestCase):
    def test_official_order_and_half_points(self):
        rows = standings.parse_table(table("drivers", 12.5), "drivers")
        self.assertEqual(rows[0], [1, "Driver 1", "DRV", "Team 1", 12.5])
        self.assertEqual(len(rows), 22)
        self.assertEqual(rows[1][0], 2)

    def test_constructors_parsed_independently(self):
        rows = standings.parse_table(table("team"), "team")
        self.assertEqual(rows[0], [1, "Team 1", 100])

    def test_rejects_empty_partial_or_changed_markup(self):
        for markup in ("<html>Blocked</html>", "<table><tr><td>1</td></tr></table>",
                       table("team").replace("<td>11</td>", "<td>12</td>"),
                       table("team").replace("<td>100</td>", "<td>?</td>", 1)):
            with self.subTest(markup=markup[:50]), self.assertRaises(ValueError):
                standings.parse_table(markup, "team")
        for rows, kind in ((standings.DRIVERS[:20], "drivers"),
                           (standings.CONSTRUCTORS[:10], "team")):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                standings.validate_rows(rows, kind)

    def test_failed_second_fetch_preserves_entire_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            path.write_text("previous snapshot", encoding="utf-8")
            with patch.object(standings, "snapshot_path", return_value=path), patch(
                    "urllib.request.urlopen",
                    side_effect=[io.BytesIO(table("drivers").encode()),
                                 urllib.error.URLError("offline")]):
                with self.assertRaises(urllib.error.URLError):
                    standings.refresh()
            self.assertEqual(path.read_text(), "previous snapshot")
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_complete_refresh_writes_both_tables_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            with patch.object(standings, "snapshot_path", return_value=path), patch(
                    "urllib.request.urlopen",
                    side_effect=[io.BytesIO(table("drivers").encode()),
                                 io.BytesIO(table("team").encode())]):
                standings.refresh()
                data = standings.load_snapshot()
            self.assertEqual(data["year"], 2026)
            self.assertEqual(len(data["constructors"]), 11)
            self.assertIn("fetched_at", json.loads(path.read_text()))
            self.assertTrue(data["sources"]["drivers"].endswith("/2026/drivers"))

    def test_refresh_rejects_loss_of_previous_reserve_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            previous = {
                "year": 2026, "fetched_at": "2026-09-10T12:00:00+00:00",
                "drivers": standings.parse_table(table("drivers"), "drivers")
                           + [[23, "Reserve Driver", "RES", "Team 1", 0]],
                "constructors": standings.parse_table(table("team"), "team"),
            }
            path.write_text(json.dumps(previous), encoding="utf-8")
            with patch.object(standings, "snapshot_path", return_value=path), patch(
                    "urllib.request.urlopen",
                    side_effect=[io.BytesIO(table("drivers").encode()),
                                 io.BytesIO(table("team").encode())]):
                with self.assertRaisesRegex(ValueError, "Reserve Driver"):
                    standings.refresh()
            self.assertEqual(json.loads(path.read_text()), previous)

    def test_refresh_keeps_coherent_snapshot_when_driver_standings_lag_race(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            drivers = [
                [index, f"Driver {index}",
                 f"{chr(65 + (index - 1) // 26)}{chr(65 + (index - 1) % 26)}X",
                 f"Team {min((index + 1) // 2, 11)}", 101 - index]
                for index in range(1, 24)
            ]
            constructors = [[index, f"Team {index}", 101 - index] for index in range(1, 12)]
            previous = {
                "year": 2026,
                "fetched_at": "2026-09-26T13:11:49+00:00",
                "drivers": drivers,
                "constructors": constructors,
                "sources": {
                    "drivers": "https://www.formula1.com/en/results/2026/drivers",
                    "constructors": "https://www.formula1.com/en/results/2026/team",
                },
            }
            path.write_text(json.dumps(previous), encoding="utf-8")
            updated_constructors = [[pos, team, points + (35 if team == "Team 1" else 0)]
                                    for pos, team, points in constructors]
            race = {
                "round": 15,
                "slug": "azerbaijan",
                "name": "Azerbaijan Grand Prix",
                "fetched_at": "2026-09-26T13:13:19+00:00",
                "source_url": "https://www.formula1.com/en/results/2026/races/1295/azerbaijan/race-result",
                "driver_points": {"AAX": 25, "ABX": 10},
                "team_points": {"Team 1": 35},
                "driver_names": {"AAX": "Driver 1", "ABX": "Driver 2"},
            }
            with patch.object(standings, "snapshot_path", return_value=path), \
                    patch.object(standings, "_new_race_results", return_value=[race]), \
                    patch.object(standings, "_missing_race_checkpoints", return_value=[]), \
                    patch("urllib.request.urlopen",
                          side_effect=[
                              io.BytesIO(source_table(drivers, "drivers").encode()),
                              io.BytesIO(source_table(updated_constructors, "team").encode()),
                          ]):
                saved = standings.refresh()
                loaded = standings.load_snapshot()

            self.assertEqual(saved["fetched_at"], previous["fetched_at"])
            self.assertEqual(loaded["drivers"], previous["drivers"])
            self.assertEqual(loaded["constructors"], previous["constructors"])
            self.assertEqual(loaded["refresh_status"]["state"], "pending")
            self.assertIn("Driver 1 (AAX)", " ".join(loaded["refresh_status"]["mismatches"]))
            with patch.object(standings, "snapshot_path", return_value=path):
                context = standings.context(
                    now=datetime.datetime(2026, 9, 26, 14, tzinfo=datetime.timezone.utc))
            self.assertIn("Official post-race standings update pending", context["notice"])
            self.assertIn("not a post-race points table", context["notice"])

    def test_refresh_rejects_stale_lower_totals_after_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            previous = {
                "year": 2026,
                "fetched_at": "2026-11-08T19:04:07+00:00",
                "results_round": 20,
                "drivers": standings.parse_table(table("drivers", 100), "drivers"),
                "constructors": standings.parse_table(table("team", 100), "team"),
                "sources": {
                    "drivers": "https://www.formula1.com/en/results/2026/drivers",
                    "constructors": "https://www.formula1.com/en/results/2026/team",
                },
            }
            path.write_text(json.dumps(previous), encoding="utf-8")
            stale_constructors = standings.parse_table(table("team", 90), "team")
            with patch.object(standings, "snapshot_path", return_value=path), \
                    patch.object(standings, "_new_race_results", return_value=[]), \
                    patch.object(standings, "_missing_race_checkpoints", return_value=[]), \
                    patch("urllib.request.urlopen", side_effect=[
                        io.BytesIO(table("drivers", 100).encode()),
                        io.BytesIO(source_table(stale_constructors, "team").encode()),
                    ]):
                saved = standings.refresh()

            self.assertEqual(saved["drivers"], previous["drivers"])
            self.assertEqual(saved["constructors"], previous["constructors"])
            self.assertEqual(saved["results_round"], 20)
            self.assertEqual(saved["refresh_status"]["state"], "source_regression")
            self.assertIn("Team 1", " ".join(saved["refresh_status"]["mismatches"]))
            with patch.object(standings, "snapshot_path", return_value=path):
                context = standings.context(
                    now=datetime.datetime(2026, 11, 8, 20, tzinfo=datetime.timezone.utc))
            self.assertIn("Latest standings refresh rejected", context["notice"])
            self.assertIn("below the last coherent snapshot", context["notice"])

    def test_freshness_and_summary_follow_data(self):
        snapshot = {
            "fetched_at": "2026-09-10T12:00:00+00:00",
            "drivers": [[1, "Leader", "LED", "Mercedes", 267],
                        [2, "Second", "SEC", "Ferrari", 201]],
            "constructors": [[1, "Mercedes", 468]],
            "sources": {"drivers": "https://www.formula1.com/en/results/2026/drivers",
                        "constructors": "https://www.formula1.com/en/results/2026/team"},
        }
        with patch.object(standings, "load_snapshot", return_value=snapshot):
            fresh = standings.context(now=datetime.datetime(2026, 9, 10, 13, tzinfo=datetime.timezone.utc))
            stale = standings.context(now=datetime.datetime(2026, 9, 12, tzinfo=datetime.timezone.utc))
        self.assertIn("267 points, 66 ahead", fresh["summary"])
        self.assertIn('data-sort="468"', fresh["ctors"])
        self.assertNotIn("overdue", fresh["notice"])
        self.assertIn("overdue", stale["notice"])
        self.assertIn("10 Sep 2026", stale["as_of"])

    def test_race_checkpoint_not_fetch_timestamp_controls_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/test").mkdir(parents=True)
            event = {"round": 16, "slug": "test", "name": "Test GP", "race_date": "2026-10-04"}
            (root / "data/calendar_2026.json").write_text(json.dumps(
                {"year": 2026, "events": [event]}))
            (root / "data/test/session_results.json").write_text(json.dumps({
                "event": {"year": "2026", "gp": "test"},
                "sessions": [{
                    "label": "Race", "fetched_at": "2026-10-04T09:00:00+00:00",
                    "source_url": "https://www.formula1.com/results",
                    "headers": ["Driver", "Team", "Pts."],
                    "rows": [["Winner WIN", "Team", "25"]],
                }],
            }))
            previous = {"results_round": 15, "fetched_at": "2026-10-04T10:00:00+00:00"}
            with patch.object(standings, "ROOT", root):
                races = standings._new_race_results(previous, 2026)
                self.assertEqual(races[0]["driver_points"], {"WIN": 25})
                previous["results_round"] = 16
                self.assertEqual(standings._new_race_results(previous, 2026), [])

    def test_unclassified_race_blocks_changed_points_but_not_future_races(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/calendar_2026.json").write_text(json.dumps({
                "events": [{"round": 16, "name": "Test GP", "race_date": "2026-10-04",
                            "sessions": [{"label": "Race", "date": "2026-10-04",
                                          "time": "15:00", "gmt_offset": "+08:00"}]}],
            }))
            prior = {"results_round": 15, "fetched_at": "2026-10-03T10:00:00+00:00"}
            with patch.object(standings, "ROOT", root):
                before = datetime.datetime(2026, 10, 4, 6, tzinfo=datetime.timezone.utc)
                after = datetime.datetime(2026, 10, 4, 10, tzinfo=datetime.timezone.utc)
                self.assertEqual(standings._missing_race_checkpoints(prior, [], 2026, before), [])
                self.assertEqual(standings._missing_race_checkpoints(prior, [], 2026, after), ["Test GP"])
                self.assertEqual(standings._missing_race_checkpoints(
                    prior, [{"round": 16}], 2026, after), [])

    def test_refresh_refuses_new_totals_without_classification_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.json"
            prior = {"year": 2026, "fetched_at": "2026-10-04T06:00:00+00:00",
                     "results_round": 15,
                     "drivers": standings.parse_table(table("drivers"), "drivers"),
                     "constructors": standings.parse_table(table("team"), "team")}
            path.write_text(json.dumps(prior))
            with patch.object(standings, "snapshot_path", return_value=path), \
                    patch.object(standings, "_new_race_results", return_value=[]), \
                    patch.object(standings, "_missing_race_checkpoints", return_value=["Test GP"]), \
                    patch("urllib.request.urlopen", side_effect=[
                        io.BytesIO(table("drivers", 125).encode()), io.BytesIO(table("team", 125).encode())]):
                with self.assertRaisesRegex(ValueError, "Cannot checkpoint changed standings"):
                    standings.refresh()
            self.assertEqual(json.loads(path.read_text()), prior)

    def test_deployment_collects_classifications_before_standings(self):
        workflow = (Path(__file__).parent / ".github/workflows/deploy.yml").read_text()
        self.assertLess(workflow.index("python3 session_results.py"),
                        workflow.index("run: python3 standings.py"))

    def test_missing_snapshot_is_not_fabricated(self):
        with patch.object(standings, "load_snapshot", return_value={}):
            self.assertEqual(standings.context(), {})

    def test_rendering_escapes_names_and_preserves_ties(self):
        rows = [[1, "<Leader>", "ONE", "Mercedes", 20],
                [2, "Second", "TWO", "Ferrari", 20]]
        rendered = standings.driver_rows(rows)
        self.assertIn("&lt;Leader&gt;", rendered)
        self.assertIn("Level with P1", rendered)


if __name__ == "__main__":
    unittest.main()
