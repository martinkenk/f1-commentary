import copy
import datetime as dt
import json
import unittest

import passing_fantasy as pf


class FantasyTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 9, 18, tzinfo=dt.timezone.utc)
        self.session = {
            "RaceId": 7384, "TourId": 4, "Season": "2026", "SessionType": "Race",
            "MatchStatus": "4", "CircuitOfficialName": "Madring",
            "SessionStartDateISO8601": "2026-09-13T15:00:00+02:00",
            "SessionEndDateISO8601": "2026-09-13T17:00:00+02:00",
        }
        self.record = {
            "RaceDayId": 7384, "Season": "2026", "SessionType": "Race", "MatchStatus": "4",
            "IsPlayed": 1, "CircuitOfficialName": "Madring",
            "SessionStartDate": "2026-09-13T15:00:00+02:00",
            "StatsWise": [
                {"Event": "Total", "Value": 69, "Frequency": "-"},
                {"Event": "Race Position", "Value": 25, "Frequency": "1st"},
                {"Event": "Race position gained", "Value": 18, "Frequency": "18"},
                {"Event": "race overtake bonus", "Value": 26, "Frequency": "26"},
            ],
        }
        self.data = {
            "races": [{"id": 1163, "year": 2026, "date": "2026-09-13", "circuitId": "madring"}],
            "races-race-results": [{"raceId": 1163, "driverId": "kimi-antonelli"},
                                   {"raceId": 1163, "driverId": "carlos-sainz-jr"}],
            "circuits": [{"id": "madring", "name": "Madring", "fullName": "Circuito de Madring"}],
            "drivers": [{"id": "kimi-antonelli", "name": "Kimi Antonelli"},
                        {"id": "carlos-sainz-jr", "name": "Carlos Sainz Jr."}],
        }
        self.stats_url = pf.BASE + "/feeds/statistics/drivers_4.json"
        self.player_url = pf.BASE + "/feeds/popup/playerstats_11161.json"
        self.other_url = pf.BASE + "/feeds/popup/playerstats_125.json"
        self.feeds = {
            pf.CONFIG: {"tourId": 4},
            pf.RULES: {"rules_title_9_intro_5": pf.RULE},
            pf.SCHEDULE: {"Data": {"Value": [self.session]}},
            self.stats_url: {"Data": {"season": "2026", "statistics": [{
                "config": {"key": "overTakepoints"},
                "participants": [{"playerid": "11161", "playername": "Kimi Antonelli"},
                                 {"playerid": "125", "playername": "Carlos Sainz"}],
            }]}},
            self.player_url: {"Value": {"PlayerId": 11161, "PlayerSkill": 1, "MatchWiseStats": [
                {"TourId": 4, "RaceDayWise": [self.record]},
            ]}},
        }
        zero = copy.deepcopy(self.record)
        zero["StatsWise"] = [
            {"Event": "Total", "Value": 25, "Frequency": "-"},
            {"Event": "Race Position", "Value": 25, "Frequency": "1st"},
        ]
        self.feeds[self.other_url] = {"Value": {"PlayerId": 125, "PlayerSkill": 1,
                                               "MatchWiseStats": [
                                                   {"TourId": 4, "RaceDayWise": [zero]}]}}

    def collect(self):
        return pf.collect(lambda url: json.dumps(self.feeds[url]), self.data, self.now)

    def test_frequency_not_positions_gained_and_scored_zero(self):
        rows, evidence = self.collect()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["overtakes"], 26)
        self.assertEqual(rows[0]["participants"], 2)
        self.assertEqual(rows[0]["race_id"], 1163)
        self.assertEqual(rows[0]["session_id"], 7384)
        self.assertEqual(len(evidence["feeds"]), 6)
        self.assertTrue(all(len(feed["sha256"]) == 64 for feed in evidence["feeds"]))

    def test_sprints_and_historical_tours_are_not_counted(self):
        sprint = {**self.record, "RaceDayId": 9000, "SessionType": "Sprint"}
        self.feeds[self.player_url]["Value"]["MatchWiseStats"][0]["RaceDayWise"].append(sprint)
        self.feeds[self.player_url]["Value"]["MatchWiseStats"].append({
            "TourId": 3, "RaceDayWise": [self.record],
        })
        self.assertEqual(self.collect()[0][0]["overtakes"], 26)

    def test_completed_breakdown_without_bonus_is_zero_but_missing_score_is_not(self):
        zero = self.feeds[self.other_url]["Value"]["MatchWiseStats"][0]["RaceDayWise"][0]
        self.assertEqual(pf._score(zero), 0)
        for stats in ([], [{"Event": "Total", "Value": 0, "Frequency": "-"}],
                      [{"Event": "Race Position", "Value": 25, "Frequency": "1st"}]):
            with self.subTest(stats=stats), self.assertRaises(ValueError):
                pf._score({**zero, "StatsWise": stats})

    def test_feed_omits_total_for_zero_sum_not_for_incomplete_nonzero_scores(self):
        for stats, expected in (
            ([{"Event": "Race Position", "Value": 0, "Frequency": "14th"}], 0),
            ([{"Event": "Race Position", "Value": 0, "Frequency": "13th"},
              {"Event": "Race Position lost", "Value": -1, "Frequency": "1"},
              {"Event": "race overtake bonus", "Value": 1, "Frequency": "1"}], 1),
            ([{"Event": "Race Position", "Value": 4, "Frequency": "8th"},
              {"Event": "Race Position lost", "Value": -6, "Frequency": "6"},
              {"Event": "race overtake bonus", "Value": 2, "Frequency": "2"}], 2),
        ):
            with self.subTest(stats=stats):
                self.assertEqual(pf._score({"StatsWise": stats}), expected)
                incomplete = copy.deepcopy(stats)
                incomplete[0]["Value"] += 1
                with self.assertRaisesRegex(ValueError, "unreconciled"):
                    pf._score({"StatsWise": incomplete})

    def test_missing_driver_feed_or_record_cannot_produce_partial_total(self):
        self.feeds[self.other_url]["Value"]["MatchWiseStats"] = []
        with self.assertRaisesRegex(ValueError, "Incomplete Fantasy entrants"):
            self.collect()
        del self.feeds[self.other_url]
        with self.assertRaises(KeyError):
            self.collect()

    def test_player_discovery_does_not_omit_replaced_drivers_or_double_count_them(self):
        participants = self.feeds[self.stats_url]["Data"]["statistics"][0]["participants"]
        participants.append({"playerid": "99", "playername": "Kimi Antonelli"})
        replacement_url = pf.BASE + "/feeds/popup/playerstats_99.json"
        self.feeds[replacement_url] = {"Value": {"PlayerId": 99, "PlayerSkill": 1,
                                                "MatchWiseStats": []}}
        self.assertEqual(self.collect()[0][0]["participants"], 2)
        self.feeds[replacement_url]["Value"]["MatchWiseStats"] = [
            {"TourId": 4, "RaceDayWise": [self.record]},
        ]
        with self.assertRaisesRegex(ValueError, "Duplicate Fantasy entries"):
            self.collect()

    def test_unplayed_expected_entrant_is_not_zero(self):
        self.record["IsPlayed"] = 0
        with self.assertRaisesRegex(ValueError, "Incomplete Fantasy entrants"):
            self.collect()

    def test_duplicate_session_record_and_schedule_rejected(self):
        self.feeds[self.player_url]["Value"]["MatchWiseStats"][0]["RaceDayWise"].append(self.record)
        with self.assertRaisesRegex(ValueError, "Duplicate Fantasy player race"):
            self.collect()
        self.feeds[pf.SCHEDULE]["Data"]["Value"].append(self.session)
        with self.assertRaisesRegex(ValueError, "Duplicate Fantasy race session"):
            self.collect()

    def test_new_definition_or_season_requires_review(self):
        self.feeds[pf.RULES]["rules_title_9_intro_5"] += " Includes pit stops."
        with self.assertRaisesRegex(ValueError, "definition changed"):
            self.collect()
        self.feeds[pf.RULES]["rules_title_9_intro_5"] = pf.RULE
        self.feeds[self.stats_url]["Data"]["season"] = "2025"
        with self.assertRaisesRegex(ValueError, "current season"):
            self.collect()

    def test_wrong_venue_date_player_or_completion_is_rejected(self):
        for target, field, value in (
            (self.session, "CircuitOfficialName", "Circuit de Barcelona-Catalunya"),
            (self.session, "SessionStartDateISO8601", "2026-09-12T15:00:00+02:00"),
            (self.session, "MatchStatus", "0"),
            (self.record, "MatchStatus", "0"),
            (self.record, "CircuitOfficialName", "Circuit de Barcelona-Catalunya"),
            (self.record, "SessionStartDate", "2026-09-12T15:00:00+02:00"),
            (self.feeds[self.player_url]["Value"], "PlayerId", 999),
        ):
            with self.subTest(field=field, value=value):
                old = target[field]
                target[field] = value
                with self.assertRaises(ValueError):
                    self.collect()
                target[field] = old

    def test_future_and_unclassified_races_cannot_be_published(self):
        self.now = dt.datetime(2026, 9, 13, 13, tzinfo=dt.timezone.utc)
        with self.assertRaisesRegex(ValueError, "future race"):
            self.collect()
        self.now = dt.datetime(2026, 9, 18, tzinfo=dt.timezone.utc)
        self.data["races-race-results"] = []
        with self.assertRaisesRegex(ValueError, "No unique completed"):
            self.collect()

    def test_frequency_schema_and_score_reconciliation(self):
        for frequency in ("-", "-1", "1.5", 26, True):
            with self.subTest(frequency=frequency), self.assertRaises(ValueError):
                record = copy.deepcopy(self.record)
                record["StatsWise"][-1]["Frequency"] = frequency
                pf._score(record)
        for field, value in (("Event", "new overtake bonus"), ("Value", 27)):
            record = copy.deepcopy(self.record)
            record["StatsWise"][-1][field] = value
            with self.assertRaises(ValueError):
                pf._score(record)

    def test_las_vegas_joins_utc_date_not_local_calendar_day(self):
        self.session.update(
            CircuitOfficialName="Las Vegas Strip Circuit",
            SessionStartDateISO8601="2026-11-21T20:00:00-08:00",
            SessionEndDateISO8601="2026-11-21T22:00:00-08:00")
        self.now = dt.datetime(2026, 11, 23, tzinfo=dt.timezone.utc)
        self.data["races"][0].update(date="2026-11-22", circuitId="las-vegas")
        self.data["circuits"] = [{"id": "las-vegas", "name": "Las Vegas",
                                  "fullName": "Las Vegas Street Circuit"}]
        for url in (self.player_url, self.other_url):
            record = self.feeds[url]["Value"]["MatchWiseStats"][0]["RaceDayWise"][0]
            record.update(CircuitOfficialName=self.session["CircuitOfficialName"],
                          SessionStartDate=self.session["SessionStartDateISO8601"])
        self.assertEqual(self.collect()[0][0]["date"], "2026-11-22")


if __name__ == "__main__":
    unittest.main()
