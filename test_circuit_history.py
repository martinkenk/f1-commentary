"""Deterministic offline tests for source-backed circuit history."""

import copy
from collections import defaultdict
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import uuid
import zipfile

import circuit_history as history


NOW = dt.datetime(2026, 9, 17, 8, tzinfo=dt.timezone.utc)
SOURCE = {"name": "F1DB", "release": "v2026.14.0", "sha256": "a" * 64}
RELEASE = {
    "tag_name": "v2026.14.0", "published_at": "2026-09-13T17:19:19Z",
    "html_url": "https://github.com/f1db/f1db/releases/tag/v2026.14.0",
    "assets": [{"name": name, "browser_download_url":
                f"https://github.com/f1db/f1db/releases/download/v2026.14.0/{name}"}
               for name in (history.ASSET, "checksums_sha256.txt")],
}


def race(identity, year, round_no, date, circuit, gp):
    return {"id": identity, "year": year, "round": round_no, "date": date,
            "circuitId": circuit, "grandPrixId": gp}


def result(event, driver, position, team="team", **extra):
    return {
        "raceId": event["id"], "year": event["year"], "round": event["round"],
        "driverId": driver, "constructorId": team, "driverNumber": driver.removeprefix("driver-"),
        "positionText": str(position) if isinstance(position, int) else position,
        "positionNumber": position if isinstance(position, int) else None,
        "sharedCar": False, "laps": 50, "polePosition": position == 1,
        "gridPositionNumber": position if isinstance(position, int) else 10, **extra,
    }


def complete_fixture(data):
    """Supply separate source-table fixtures after intentional valid edits."""
    groups = defaultdict(list)
    events = defaultdict(list)
    for row in data["races-race-results"]:
        groups[(row["year"], row["driverId"])].append(row)
        events[row["raceId"]].append(row)
    for rows in events.values():
        for order, row in enumerate(rows, 1):
            row["positionDisplayOrder"] = order
    totals = {(row["year"], row["driverId"]): row for row in data["seasons-drivers"]}
    for key in groups.keys() | totals.keys():
        rows = groups[key]
        totals[key] = {
            "year": key[0], "driverId": key[1],
            "totalRaceEntries": len({row["raceId"] for row in rows}),
            "totalRaceStarts": len({row["raceId"] for row in rows if history._started(row) is True}),
        }
    data["seasons-drivers"] = list(totals.values())
    data["races-starting-grid-positions"] = [
        {key: row[key] for key in ("raceId", "driverId", "constructorId", "driverNumber")}
        for row in data["races-race-results"] if row.get("gridPositionNumber")]


def fixture():
    old = [
        race(1, 2016, 1, "2016-06-19", "baku", "europe"),
        race(2, 2017, 1, "2017-06-25", "baku", "azerbaijan"),
        race(3, 2018, 1, "2018-04-29", "baku", "azerbaijan"),  # cancelled fixture
        race(4, 2020, 1, "2020-08-16", "catalunya", "spain"),
        race(5, 2021, 1, "2021-05-09", "jerez", "spain"),
        race(6, 2022, 1, "2022-10-02", "sepang", "malaysia"),
        race(7, 2023, 1, "2023-03-05", "sakhir", "bahrain"),
    ]
    current = [
        race(10, 2026, 14, "2026-09-13", "madring", "spain"),
        race(11, 2026, 15, "2026-09-26", "baku", "azerbaijan"),
        race(12, 2026, 16, "2026-10-04", "sepang", "bahrain"),
    ]
    data = {
        "races": old + current,
        "circuits": [{"id": identity, "name": identity, "fullName": identity}
                     for identity in ("baku", "catalunya", "jerez", "sepang", "sakhir", "madring")],
        "grands-prix": [{"id": identity, "fullName": name} for identity, name in (
            ("europe", "European Grand Prix"), ("azerbaijan", "Azerbaijan Grand Prix"),
            ("spain", "Spanish Grand Prix"), ("bahrain", "Bahrain Grand Prix"),
            ("malaysia", "Malaysian Grand Prix"))],
        "drivers": [{"id": f"driver-{i}", "name": f"Driver {i}", "fullName": f"Driver {i}",
                     "abbreviation": f"D{i:02}"} for i in range(22)],
        "constructors": [{"id": "team", "name": "Team"}, {"id": "other", "name": "Other"}],
        "seasons-drivers": [{"year": 2026, "driverId": f"driver-{i}"} for i in range(22)],
        "races-race-results": [], "races-qualifying-results": [], "races-starting-grid-positions": [],
    }
    for item in old:
        if item["id"] == 3:
            continue
        winner = 0 if item["id"] != 2 else 1
        for driver in range(2):
            row = result(item, f"driver-{driver}", 1 if driver == winner else 2)
            data["races-race-results"].append(row)
            data["races-qualifying-results"].append({**row, "time": "1:40.000"})
    for i in range(22):
        row = result(current[0], f"driver-{i}", i + 1, team="team" if i < 2 else "other")
        data["races-race-results"].append(row)
        data["races-qualifying-results"].append({**row, "q1": "1:20.000"})
    events = [{"slug": item["grandPrixId"], "round": item["round"], "race_date": item["date"],
               "location": location} for item, location in zip(current, ("Madrid", "Baku", "Kuala Lumpur"))]
    calendar = {"year": "2026", "events": events}
    standings = {"year": 2026, "drivers": [
        [i + 1, f"Driver {i}", f"D{i:02}", "Team", 0] for i in range(22)]}
    complete_fixture(data)
    return data, calendar, standings


def add_leclerc_monaco_fixture(data, calendar):
    """Preserve the real pre-2026 Monaco entries, using a reduced other field."""
    data["drivers"].append({"id": "charles-leclerc", "name": "Charles Leclerc",
                            "abbreviation": "LEC"})
    data["constructors"].append({"id": "ferrari", "name": "Ferrari"})
    data["circuits"].append({"id": "monaco", "name": "Monaco", "fullName": "Circuit de Monaco"})
    data["grands-prix"].append({"id": "monaco", "fullName": "Monaco Grand Prix"})
    editions = [
        (982, 2018, 6, "2018-05-27", 18), (1003, 2019, 6, "2019-05-26", "DNF"),
        (1040, 2021, 5, "2021-05-23", "DNS"), (1064, 2022, 7, "2022-05-29", 4),
        (1085, 2023, 6, "2023-05-28", 6), (1109, 2024, 8, "2024-05-26", 1),
        (1133, 2025, 8, "2025-05-25", 2),
    ]
    for identity, year, round_no, date, position in editions:
        event = race(identity, year, round_no, date, "monaco", "monaco")
        data["races"].append(event)
        data["races-race-results"].extend([
            result(event, "driver-0", 2 if position == 1 else 1),
            result(event, "charles-leclerc", position, team="ferrari", driverNumber="16"),
        ])
    event = race(1155, 2026, 6, "2026-06-07", "monaco", "monaco")
    data["races"].append(event)
    data["races-race-results"].extend(result(event, f"driver-{i}", i + 1) for i in range(22))
    calendar["events"].append({"slug": "monaco", "round": 6, "race_date": event["date"],
                               "location": "Monte Carlo"})
    complete_fixture(data)


class SourceEvidenceTests(unittest.TestCase):
    def bellof(self):
        # F1DB v2026.14.0: all 12 1984 starts were retrospectively excluded;
        # 1985 has ten entries, nine starts, including a Monaco DNQ.
        rows = []
        rounds = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13)
        for round_no in rounds:
            event = race(388 + round_no, 1984, round_no, "1984-06-03", "monaco", "monaco")
            rows.append(result(event, "stefan-bellof", "DSQ", team="tyrrell", driverNumber="4",
                               laps=None, gridPositionNumber=None, sharedCar=False,
                               positionDisplayOrder=1))
        for identity, position in zip(range(406, 416), (6, "DNF", "DNQ", 11, 4, 13, 11, 8, 7, "DNF")):
            event = race(identity, 1985, identity - 404, "1985-05-19", "monaco", "monaco")
            rows.append(result(event, "stefan-bellof", position, team="tyrrell", driverNumber="4",
                               positionDisplayOrder=1))
        return {"races-race-results": rows, "races-starting-grid-positions": [],
                "seasons-drivers": [
                    {"year": 1984, "driverId": "stefan-bellof", "totalRaceEntries": 12, "totalRaceStarts": 12},
                    {"year": 1985, "driverId": "stefan-bellof", "totalRaceEntries": 10, "totalRaceStarts": 9},
                ]}

    def test_bellof_1984_retrospective_exclusions_restore_21_career_starts(self):
        data = self.bellof()
        rows = history.reconcile_results(data)
        self.assertEqual(sum(history._started(row) for row in rows), 21)
        monaco = next(row for row in rows if row["raceId"] == 394)
        self.assertTrue(history._started(monaco))
        self.assertEqual(history._state(monaco), "dsq")
        self.assertIsNone(monaco["positionNumber"])
        self.assertIsNone(history._started(data["races-race-results"][0]))
        indexed = {
            "drivers": {"stefan-bellof": {"name": "Stefan Bellof", "abbreviation": "BEL"}},
            "constructors": {"tyrrell": {"name": "Tyrrell"}},
            "circuits": {"monaco": {"fullName": "Circuit de Monaco"}},
            "grands-prix": {"monaco": {"fullName": "Monaco Grand Prix"}},
        }
        prior = race(394, 1984, 6, "1984-06-03", "monaco", "monaco")
        event = race(1155, 2026, 6, "2026-06-07", "monaco", "monaco")
        profile = history.make_profile(
            {"slug": "monaco", "race_date": "2026-06-07"}, event, [prior],
            {394: [monaco]}, {}, indexed, [])
        self.assertEqual(profile["drivers"][0]["starts"], 1)
        self.assertEqual(profile["drivers"][0]["history_status"], "unclassified")
        self.assertIsNone(profile["drivers"][0]["best_finish"])

    def test_ambiguous_participation_is_not_published_as_zero(self):
        data = self.bellof()
        data["seasons-drivers"][0]["totalRaceStarts"] = 6
        with self.assertRaisesRegex(ValueError, "Unresolved participation"):
            history.reconcile_results(data)

    def test_pre_race_exclusion_dns_and_allocated_grid_are_not_automatic_starts(self):
        event = race(517, 1992, 1, "1992-03-01", "kyalami", "south-africa")
        data = {
            "races-race-results": [
                result(event, "alex-caffi", "EX", laps=None, gridPositionNumber=None,
                       positionDisplayOrder=1),
                result(event, "driver-0", "DSQ", laps=0, gridPositionNumber=4,
                       positionDisplayOrder=2),
                result(event, "driver-1", "DNS", laps=0, gridPositionNumber=5,
                       positionDisplayOrder=3),
            ],
            "races-starting-grid-positions": [],
            "seasons-drivers": [{"year": 1992, "driverId": identity,
                                "totalRaceEntries": 1, "totalRaceStarts": 0}
                               for identity in ("alex-caffi", "driver-0", "driver-1")],
        }
        self.assertEqual([history._started(row) for row in history.reconcile_results(data)],
                         [False, False, False])

    def test_missing_independent_start_totals_fail_closed(self):
        data = self.bellof()
        del data["seasons-drivers"][0]["totalRaceStarts"]
        with self.assertRaisesRegex(ValueError, "independent season"):
            history.reconcile_results(data)

    def test_shared_disqualified_car_uses_same_car_participation(self):
        event = race(99, 1961, 5, "1961-07-15", "aintree", "great-britain")
        rows = [
            result(event, "stirling-moss", "DNF", team="lotus", driverNumber="28",
                   laps=44, positionDisplayOrder=1),
            result(event, "jack-fairman", "DNF", team="ferguson", driverNumber="26",
                   laps=13, positionDisplayOrder=2),
            result(event, "stirling-moss", "DSQ", team="ferguson", driverNumber="26",
                   laps=None, gridPositionNumber=None, sharedCar=True, positionDisplayOrder=3),
        ]
        data = {"races-race-results": rows, "races-starting-grid-positions": [],
                "seasons-drivers": [{"year": 1961, "driverId": identity,
                                    "totalRaceEntries": 1, "totalRaceStarts": 1}
                                   for identity in ("stirling-moss", "jack-fairman")]}
        self.assertTrue(history._started(history.reconcile_results(data)[2]))

    def test_first_refresh_missing_leclerc_monaco_2025_is_detected(self):
        data, calendar, standings = fixture()
        add_leclerc_monaco_fixture(data, calendar)
        good = history.build_snapshot(data, calendar, standings, SOURCE, NOW)
        driver = next(row for row in good["profiles"]["monaco"]["drivers"]
                      if row["id"] == "charles-leclerc")
        self.assertEqual((driver["starts"], driver["podiums"]), (6, 2))
        data["races-race-results"] = [row for row in data["races-race-results"]
                                      if not (row["raceId"] == 1133 and row["driverId"] == "charles-leclerc")]
        with self.assertRaisesRegex(ValueError, "starting-grid entrant missing"):
            history.build_snapshot(data, calendar, standings, SOURCE, NOW)
        # Independent season-entry counts still detect the loss without grid data.
        data["races-starting-grid-positions"] = []
        with self.assertRaisesRegex(ValueError, "season-entry total mismatch"):
            history.build_snapshot(data, calendar, standings, SOURCE, NOW)

    def test_independently_consistent_classification_correction_is_allowed(self):
        data, calendar, standings = fixture()
        add_leclerc_monaco_fixture(data, calendar)
        leclerc = next(row for row in data["races-race-results"]
                       if row["raceId"] == 1133 and row["driverId"] == "charles-leclerc")
        leclerc["positionNumber"], leclerc["positionText"] = 4, "4"
        record = history.build_snapshot(data, calendar, standings, SOURCE, NOW)
        driver = next(row for row in record["profiles"]["monaco"]["drivers"]
                      if row["id"] == "charles-leclerc")
        self.assertEqual((driver["starts"], driver["podiums"]), (6, 1))


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.data, self.calendar, self.standings = fixture()

    def snapshot(self):
        return history.build_snapshot(self.data, self.calendar, self.standings, SOURCE, NOW)

    def test_baku_venue_and_gp_identity_are_separate(self):
        profile = self.snapshot()["profiles"]["azerbaijan"]
        self.assertEqual(profile["completed_races"], 2)
        self.assertEqual(profile["venue_edition"], 3)
        self.assertEqual(profile["grand_prix"]["completed_races"], 1)
        self.assertEqual(profile["grand_prix"]["edition"], 2)
        self.assertEqual([(n["id"], n["years"]) for n in profile["names_at_venue"]],
                         [("europe", [2016]), ("azerbaijan", [2017])])
        self.assertEqual(profile["first_race"]["year"], 2016)
        self.assertEqual(profile["last_race"]["year"], 2017)

    def test_madrid_not_barcelona_and_named_gp_across_venues(self):
        profile = self.snapshot()["profiles"]["spain"]
        self.assertEqual(profile["circuit"]["id"], "madring")
        self.assertEqual(profile["completed_races"], 0)
        self.assertEqual(profile["grand_prix"]["completed_races"], 2)
        self.assertEqual({v["id"] for v in profile["grand_prix"]["venues"]}, {"catalunya", "jerez"})
        self.assertEqual(profile["venue_edition"], 1)
        self.assertEqual(profile["grand_prix"]["edition"], 3)
        self.assertIsNone(profile["last_race"])

    def test_sepang_not_sakhir(self):
        profile = self.snapshot()["profiles"]["bahrain"]
        self.assertEqual(profile["circuit"]["id"], "sepang")
        self.assertEqual(profile["completed_races"], 1)
        self.assertEqual(profile["names_at_venue"][0]["id"], "malaysia")
        self.assertEqual(profile["grand_prix"]["venues"][0]["id"], "sakhir")

    def test_conflicting_or_unknown_calendar_venues_fail_closed(self):
        for location in ("Barcelona", "Unknown"):
            with self.subTest(location=location):
                self.calendar["events"][0]["location"] = location
                with self.assertRaisesRegex(ValueError, "venue"):
                    self.snapshot()
        self.calendar["events"][0]["location"] = "Madrid"
        self.data["races"][-1]["circuitId"] = "sakhir"
        with self.assertRaisesRegex(ValueError, "venue"):
            self.snapshot()

    def test_ambiguous_round_or_wrong_gp_is_rejected(self):
        self.data["races"].append({**self.data["races"][-1], "id": 99})
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.snapshot()
        self.data["races"].pop()
        self.data["races"][-1]["grandPrixId"] = "malaysia"
        with self.assertRaisesRegex(ValueError, "Grand Prix identity"):
            self.snapshot()

    def test_strict_event_cutoff_future_rows_cancelled_races_and_sprints(self):
        future = self.data["races"][-2]
        self.data["races-race-results"].append(result(future, "driver-0", 1))
        self.data["races-sprint-race-results"] = [result(self.data["races"][2], "driver-0", 1)]
        pre_championship = race(90, 1949, 1, "1949-01-01", "baku", "europe")
        self.data["races"].append(pre_championship)
        self.data["races-race-results"].append(result(pre_championship, "driver-0", 1))
        complete_fixture(self.data)
        profiles = self.snapshot()["profiles"]
        self.assertEqual(profiles["azerbaijan"]["completed_races"], 2)
        # The completed current year's Madrid race must not count itself.
        self.assertEqual(profiles["spain"]["completed_races"], 0)

    def test_local_date_crosscheck_uses_actual_utc_race_session(self):
        event = {"slug": "las-vegas", "round": 21, "location": "Las Vegas",
                 "race_date": "2026-11-21", "sessions": [
                     {"label": "Race", "date": "2026-11-21", "time": "20:00", "gmt_offset": "-08:00"}]}
        source = race(90, 2026, 21, "2026-11-22", "las-vegas", "las-vegas")
        self.assertEqual(history.map_events([event], [source], 2026)["las-vegas"], source)
        source["date"] = "2026-11-23"
        with self.assertRaisesRegex(ValueError, "date mismatch"):
            history.map_events([event], [source], 2026)

    def test_new_season_driver_no_start_and_tied_leaders(self):
        profile = self.snapshot()["profiles"]["azerbaijan"]
        self.assertEqual(set(profile["most_driver_wins"]), {"driver-0", "driver-1"})
        self.assertEqual(profile["most_constructor_wins"], ["team"])
        self.assertEqual(len([r for r in profile["drivers"] if r["season_driver"]]), 22)
        debutant = next(r for r in profile["drivers"] if r["id"] == "driver-21")
        self.assertEqual(debutant["starts"], 0)
        self.assertIsNone(debutant["best_finish"])
        self.assertEqual(debutant["history_status"], "no-start")
        self.assertEqual(profile["wins_from_pole"], {"wins": 2, "races": 2})

    def test_all_time_driver_retained_and_classified_best_finish_only(self):
        self.data["drivers"].append({"id": "retired", "name": "Retired Driver", "abbreviation": "RET"})
        for item in self.data["races"][:2]:
            self.data["races-race-results"].append(result(item, "retired", "DNF"))
        complete_fixture(self.data)
        profile = self.snapshot()["profiles"]["azerbaijan"]
        driver = next(row for row in profile["drivers"] if row["id"] == "retired")
        self.assertFalse(driver["season_driver"])
        self.assertEqual(driver["starts"], 2)
        self.assertIsNone(driver["best_finish"])
        self.assertEqual(driver["history_status"], "unclassified")

    def test_pole_is_official_flag_not_grid_or_qualifying_order(self):
        rows = [r for r in self.data["races-race-results"] if r["raceId"] == 1]
        rows[0]["polePosition"] = False
        rows[1]["polePosition"] = True
        rows[0]["gridPositionNumber"] = 1
        profile = self.snapshot()["profiles"]["azerbaijan"]
        self.assertEqual(profile["wins_from_pole"], {"wins": 1, "races": 2})
        self.assertEqual(next(d for d in profile["drivers"] if d["id"] == "driver-0")["poles"], 0)
        for row in rows:
            row["polePosition"] = None
        self.assertEqual(self.snapshot()["profiles"]["azerbaijan"]["wins_from_pole"], {"wins": 1, "races": 1})

    def test_shared_drive_constructor_awards_are_not_double_counted(self):
        first = self.data["races-race-results"][0]
        self.data["races-race-results"].append(
            {**first, "driverId": "driver-2", "sharedCar": True})
        first["sharedCar"] = True
        complete_fixture(self.data)
        profile = self.snapshot()["profiles"]["azerbaijan"]
        team = profile["constructors"][0]
        self.assertEqual(team["wins"], 2)
        self.assertEqual(team["starts"], 4)
        self.assertEqual(profile["teammates"]["excluded_events"][0]["reason"], "Shared drive")

    def test_constructor_identities_and_no_start_statuses(self):
        for row in self.data["races-race-results"]:
            if row["raceId"] == 2:
                row["constructorId"] = "other"
        self.data["races-race-results"].append(
            result(self.data["races"][0], "driver-2", "DNS", laps=0, gridPositionNumber=None))
        complete_fixture(self.data)
        profile = self.snapshot()["profiles"]["azerbaijan"]
        self.assertEqual(set(profile["most_constructor_wins"]), {"team", "other"})
        no_start = next(row for row in profile["drivers"] if row["id"] == "driver-2")
        self.assertEqual(no_start["starts"], 0)
        self.assertIsNone(no_start["best_finish"])
        self.assertIsNone(history._started(result(self.data["races"][0], "driver-2", "DSQ",
                                                  laps=0, gridPositionNumber=None)))
        self.assertTrue(history._started(result(self.data["races"][0], "driver-2", "DSQ",
                                                laps=3, gridPositionNumber=4)))

    def test_classification_identity_and_missing_winner_fail_closed(self):
        self.data["races-race-results"][0]["year"] = 1950
        with self.assertRaisesRegex(ValueError, "totals|total mismatch|season/round"):
            self.snapshot()
        self.data["races-race-results"][0]["year"] = 2016
        self.data["races-race-results"][0]["positionNumber"] = None
        with self.assertRaisesRegex(ValueError, "no winner"):
            self.snapshot()

    def test_partial_or_stale_current_results_fail(self):
        for remove_all in (False, True):
            with self.subTest(remove_all=remove_all):
                data = copy.deepcopy(self.data)
                data["races-race-results"] = (
                    [r for r in data["races-race-results"] if r["raceId"] != 10] if remove_all
                    else data["races-race-results"][:-1])
                with self.assertRaisesRegex(ValueError, "Partial|Stale/partial"):
                    history.build_snapshot(data, self.calendar, self.standings, SOURCE, NOW)

    def test_partial_roster_and_reused_code_name_mismatch_fail(self):
        self.standings["drivers"][0][1] = "Different Person"
        with self.assertRaisesRegex(ValueError, "name mismatch"):
            self.snapshot()
        self.standings["drivers"] = self.standings["drivers"][1:]
        with self.assertRaisesRegex(ValueError, "standings"):
            self.snapshot()


class TeammateTests(unittest.TestCase):
    def setUp(self):
        self.data, self.calendar, self.standings = fixture()
        self.race = self.data["races"][0]

    def compare(self, a, b, qualifying=False, **extra):
        return history.compare(result(self.race, "driver-0", a, **extra),
                               result(self.race, "driver-1", b, **extra), qualifying)

    def test_classification_comparability(self):
        self.assertEqual(self.compare(12, "DNF")["winner"], 0)
        self.assertEqual(self.compare("DNF", 12)["winner"], 1)
        self.assertIsNone(self.compare("DNF", "NC")["winner"])
        self.assertIsNone(self.compare(1, 1)["winner"])
        for excluded in ("DNS", "DSQ", "EX", "DNQ"):
            self.assertIsNone(self.compare(1, excluded)["winner"])
        self.assertIsNone(history.compare(None, result(self.race, "driver-0", 1))["winner"])

    def test_qualifying_requires_time_and_never_uses_grid(self):
        self.assertIsNone(self.compare(1, 2, qualifying=True)["winner"])
        self.assertEqual(self.compare(2, 1, qualifying=True, q1="1:22.000")["winner"], 1)
        no_time = self.compare(1, 2, qualifying=True)
        self.assertEqual(no_time["statuses"], ["no-time", "no-time"])

    def test_grouped_pair_evidence_and_exclusions(self):
        # Q leader differs from grid/official pole; missing driver excludes only Q.
        qrows = self.data["races-qualifying-results"]
        qrows[0]["positionNumber"], qrows[1]["positionNumber"] = 2, 1
        qrows[:] = [r for r in qrows if not (r["raceId"] == 2 and r["driverId"] == "driver-1")]
        profile = history.build_snapshot(self.data, self.calendar, self.standings, SOURCE, NOW)["profiles"]["azerbaijan"]
        pair = profile["teammates"]["pairs"][0]
        self.assertEqual(pair["Qualifying"], {"wins": [0, 1], "excluded": 1})
        self.assertEqual(pair["Race"], {"wins": [1, 1], "excluded": 0})
        self.assertIn("2016/races/01-europe", pair["events"][0]["url"])
        self.assertEqual(pair["events"][1]["Qualifying"]["statuses"], ["classified", "absent"])

    def test_more_than_two_entrants_not_forced_into_pairs(self):
        self.data["races-race-results"].append(result(self.race, "driver-2", 3))
        complete_fixture(self.data)
        profile = history.build_snapshot(self.data, self.calendar, self.standings, SOURCE, NOW)["profiles"]["azerbaijan"]
        self.assertEqual(len(profile["teammates"]["pairs"][0]["events"]), 1)
        self.assertIn("More than two", profile["teammates"]["excluded_events"][0]["reason"])

    def test_last_ten_completed_editions_not_ten_years(self):
        for number in range(20, 32):
            item = race(number, 1980 + number, 1, f"{1980 + number}-01-01", "baku", "europe")
            self.data["races"].append(item)
            for driver in range(2):
                self.data["races-race-results"].append(result(item, f"driver-{driver}", driver + 1))
        complete_fixture(self.data)
        profile = history.build_snapshot(self.data, self.calendar, self.standings, SOURCE, NOW)["profiles"]["azerbaijan"]
        scope = profile["teammates"]
        self.assertEqual(scope["races"], 10)
        self.assertEqual(scope["first_year"], 2004)
        self.assertEqual(scope["last_year"], 2017)
        self.assertEqual(len(profile["recent_winners"]), 10)


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.root = history.ROOT / "__pycache__" / f"history-tests-{uuid.uuid4().hex}"
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.data, self.calendar, self.standings = fixture()
        history._write(self.root / "data/calendar_2026.json", self.calendar)
        history._write(self.root / "data/standings_2026.json", self.standings)
        self.path = self.root / "data/circuit_history_2026.json"
        self.status = self.root / "data/circuit_history_2026_status.json"

    def refresh(self, **kwargs):
        return history.refresh(root=self.root, now=NOW, **kwargs)

    def test_success_cache_and_input_invalidation(self):
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)) as database:
            self.refresh()
            self.refresh()
            self.assertEqual(database.call_count, 1)
            self.assertTrue(history._read(self.status)["cached"])
            changed = copy.deepcopy(self.calendar)
            changed["events"][0]["new_relevant_input"] = True
            history._write(self.root / "data/calendar_2026.json", changed)
            self.refresh()
            self.assertEqual(database.call_count, 2)

    def test_invalid_partial_or_network_refresh_retains_exact_last_good(self):
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)):
            self.refresh()
        original = self.path.read_bytes()
        partial = copy.deepcopy(self.data)
        partial["races-race-results"] = partial["races-race-results"][:-1]
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(partial, SOURCE)):
            with self.assertRaisesRegex(ValueError, "last good retained"):
                self.refresh(force=True)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse(history._read(self.status)["ok"])
        with patch.object(history, "_release", side_effect=OSError("offline")):
            with self.assertRaisesRegex(ValueError, "offline"):
                self.refresh(force=True)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertTrue(history._read(self.status)["retained_last_good"])

    def test_failed_first_refresh_does_not_publish_empty_profile(self):
        with patch.object(history, "_release", side_effect=ValueError("invalid source")):
            with self.assertRaises(ValueError):
                self.refresh()
        self.assertFalse(self.path.exists())
        self.assertFalse(history._read(self.status)["retained_last_good"])

    def test_losing_historical_race_keeps_previous_snapshot(self):
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)):
            self.refresh()
        original = self.path.read_bytes()
        self.data["races-race-results"] = [
            row for row in self.data["races-race-results"] if row["raceId"] != 1]
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)):
            with self.assertRaisesRegex(ValueError, "Partial race classification|lost recorded venue races"):
                self.refresh(force=True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_missing_leclerc_monaco_result_retains_last_good(self):
        add_leclerc_monaco_fixture(self.data, self.calendar)
        history._write(self.root / "data/calendar_2026.json", self.calendar)
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)):
            self.refresh()
            original = self.path.read_bytes()
            self.data["races-race-results"] = [
                row for row in self.data["races-race-results"]
                if not (row["raceId"] == 1133 and row["driverId"] == "charles-leclerc")]
            with self.assertRaisesRegex(ValueError, "starting-grid entrant missing"):
                self.refresh(force=True)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse(history._read(self.status)["ok"])
        self.assertTrue(history._read(self.status)["retained_last_good"])

    def test_context_is_read_only_and_rejects_wrong_cutoff(self):
        with patch.object(history, "_release", return_value=RELEASE), patch.object(
                history, "_database", return_value=(self.data, SOURCE)):
            self.refresh()
        before = self.path.stat().st_mtime_ns
        with patch.object(history, "ROOT", self.root), patch.object(history, "_fetch",
                                                                  side_effect=AssertionError("network")):
            ctx = {"year": "2026", "dir": "spain", "race_date": "2026-09-13", "round_no": 14}
            self.assertEqual(history.load_profile(ctx)["completed_races"], 0)
            bad = history.context({**ctx, "race_date": "2026-09-14"})
            self.assertFalse(bad["profile"])
            self.assertIn("cutoff", bad["error"])
            history._write(self.status, {"ok": False, "error": "Source temporarily unavailable"})
            self.assertEqual(history.context(ctx)["error"], "Source temporarily unavailable")
        self.assertEqual(self.path.stat().st_mtime_ns, before)

    def test_checksum_verification_and_license_provenance(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for name in history.TABLES:
                archive.writestr(f"f1db-{name}.json", json.dumps(self.data[name]))
        payload = buffer.getvalue()
        digest = hashlib.sha256(payload).hexdigest()
        manifest = f"{digest}  {history.ASSET}\n".encode()
        with patch.object(history, "_fetch", side_effect=[manifest, payload]):
            _, source = history._database(RELEASE, self.root / "cache")
        self.assertEqual(source["sha256"], digest)
        self.assertEqual(source["license"], "CC-BY-4.0")
        with patch.object(history, "_fetch", side_effect=AssertionError("downloaded cached archive")):
            history._database(RELEASE, self.root / "cache")
        bad_cache = self.root / "bad"
        with patch.object(history, "_fetch", side_effect=[manifest, b"corrupt archive"]):
            with self.assertRaisesRegex(ValueError, "SHA256"):
                history._database(RELEASE, bad_cache)
        self.assertFalse(bad_cache.exists())

    def test_latest_release_metadata_cache(self):
        cache = self.root / "metadata"
        with patch.object(history, "_fetch", return_value=json.dumps(RELEASE).encode()) as fetch:
            self.assertEqual(history._release(cache, NOW), RELEASE)
            history._release(cache, NOW + dt.timedelta(hours=1))
            self.assertEqual(fetch.call_count, 1)
            history._release(cache, NOW + dt.timedelta(hours=7))
            self.assertEqual(fetch.call_count, 2)

    def test_asset_url_must_be_from_expected_release(self):
        bad = copy.deepcopy(RELEASE)
        bad["assets"][0]["browser_download_url"] = "https://example.com/database.zip"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            history._asset_url(bad, history.ASSET)


if __name__ == "__main__":
    unittest.main()
