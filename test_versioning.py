import datetime
import unittest
from zoneinfo import ZoneInfo

import versioning


class VersionLabelTests(unittest.TestCase):
    def test_label_uses_the_tallinn_abbreviation_for_that_date(self):
        tallinn = ZoneInfo("Europe/Tallinn")
        cases = (
            (datetime.datetime(2026, 11, 11, 19, 53, tzinfo=tallinn),
             "11 Nov 2026, 19:53 EET"),
            (datetime.datetime(2026, 7, 10, 19, 53, tzinfo=tallinn),
             "10 Jul 2026, 19:53 EEST"),
        )
        for instant, expected_label in cases:
            with self.subTest(expected_label=expected_label):
                _version_id, label, _timestamp = versioning._now_ids(instant)
                self.assertEqual(expected_label, label)


if __name__ == "__main__":
    unittest.main()
