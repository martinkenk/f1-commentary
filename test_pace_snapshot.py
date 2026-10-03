import unittest

from pace_snapshot import matching_session_articles, merge_completed_sessions


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

    def test_news_context_uses_current_session_not_older_report(self):
        articles = [
            {
                "title": "Antonelli expects a tough Bahrain weekend",
                "paragraphs": ["Mercedes prepared for practice."],
            },
            {
                "title": "FP2 report: Leclerc leads second practice",
                "paragraphs": ["Ferrari led Mercedes and the rest."],
            },
            {
                "title": "FP3 report: Antonelli leads final practice",
                "paragraphs": ["The Mercedes driver topped the session."],
            },
        ]

        matches = matching_session_articles(
            articles, "Kimi Antonelli", "Mercedes", "Practice 3"
        )

        self.assertEqual(
            [article["title"] for article in matches],
            ["FP3 report: Antonelli leads final practice"],
        )


if __name__ == "__main__":
    unittest.main()
