import unittest

from long_run_analysis import analyse_long_run_samples


def samples(times, start=10):
    return [
        {"lap_number": start + index, "lap_time": value,
         "tyre_life": index + 5}
        for index, value in enumerate(times)
    ]


class LongRunAnalysisTests(unittest.TestCase):
    def test_stable_continuous_run_reports_trend_and_confidence(self):
        runs = analyse_long_run_samples(samples(
            [104.2, 104.4, 104.5, 104.8, 105.0, 105.2, 105.4, 105.6]))
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["laps"], 8)
        self.assertEqual(runs[0]["confidence"], "high")
        self.assertGreater(runs[0]["pace_trend"], 0)
        self.assertEqual(runs[0]["tyre_life_start"], 5)
        self.assertEqual(runs[0]["tyre_life_end"], 12)

    def test_traffic_lap_is_excluded_but_run_survives(self):
        runs = analyse_long_run_samples(samples(
            [104.2, 104.4, 104.5, 109.8, 104.8, 105.0, 105.2]))
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["laps"], 6)
        self.assertEqual(runs[0]["excluded_laps"], 1)
        self.assertLess(runs[0]["avg_time"], 106)

    def test_push_cool_pattern_is_not_a_long_run(self):
        run = samples([99.4, 122.0, 99.2, 121.5, 99.1, 123.0, 99.0])
        self.assertEqual(analyse_long_run_samples(run), [])

    def test_scattered_sequence_is_not_presented_as_race_pace(self):
        run = samples([104.0, 110.0, 106.5, 113.0, 108.0, 115.0])
        self.assertEqual(analyse_long_run_samples(run), [])

    def test_missing_timed_laps_break_the_sequence(self):
        run = samples([104.0, 104.1, 104.2, 104.3])
        run += samples([104.4, 104.5, 104.6, 104.7], start=15)
        self.assertEqual(analyse_long_run_samples(run), [])


if __name__ == "__main__":
    unittest.main()
