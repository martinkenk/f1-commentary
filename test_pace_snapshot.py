import unittest

from pace_snapshot import merge_completed_sessions


class PaceSnapshotTests(unittest.TestCase):
    def test_refresh_replaces_session_and_retains_failed_completed_session(self):
        existing = [
            {"session": "FP1", "value": "old-fp1"},
            {"session": "FP2", "value": "old-fp2"},
        ]
        refreshed = [{"session": "FP2", "value": "new-fp2"}]

        merged = merge_completed_sessions(
            existing, refreshed, {"FP1", "FP2"}, ["FP1", "FP2", "FP3"]
        )

        self.assertEqual(
            merged,
            [
                {"session": "FP1", "value": "old-fp1"},
                {"session": "FP2", "value": "new-fp2"},
            ],
        )

    def test_future_session_is_not_carried_before_completion(self):
        existing = [{"session": "FP3", "value": "unexpected"}]

        merged = merge_completed_sessions(
            existing, [], {"FP1", "FP2"}, ["FP1", "FP2", "FP3"]
        )

        self.assertEqual(merged, [])


if __name__ == "__main__":
    unittest.main()
