import copy
import datetime
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import f1lib
import session_results as results

NOW = datetime.datetime(2026, 9, 25, 11, 40, tzinfo=datetime.timezone.utc)
CTX = {
    "year": "2026", "dir": "test", "race_id": "1295", "results_slug": "test",
    "cal": {"sessions": [
        {"label": "Practice 3", "date": "2026-09-25", "time": "12:30", "gmt_offset": "+04:00"},
        {"label": "Qualifying", "date": "2026-09-25", "time": "16:00", "gmt_offset": "+04:00"},
        {"label": "Race", "date": "2026-09-26", "time": "15:00", "gmt_offset": "+04:00"},
    ]},
}


def table():
    headers = ["Pos.", "No.", "Driver", "Team", "Time / Gap", "Laps"]
    rows = [[str(i + 1), str(i + 1), f"Driver {i} AA{chr(65 + i)}",
             f"Team {i // 2}", "1:43.922" if i == 0 else "+0.099s", "21"]
            for i in range(22)]
    return headers, rows


def page(headers=None, rows=None):
    if headers is None:
        headers, rows = table()
    return ("<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in rows)
            + "</tbody></table>")


class Response:
    url = results.source_url(CTX, "practice/3")

    def __init__(self, body=None):
        self.body = body if body is not None else page()

    def read(self):
        return self.body.encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class ResultsTests(unittest.TestCase):
    def collect(self, old=None, response=None, error=None, now=NOW):
        with patch.object(results, "load", return_value=old or {}), patch.object(
                results.urllib.request, "urlopen", return_value=response or Response(),
                side_effect=error) as fetch:
            record = results.refresh(copy.deepcopy(CTX), now=now, persist=False)
        return record, fetch

    def test_full_table_identity_provenance_and_future_gate(self):
        record, fetch = self.collect()
        self.assertEqual(fetch.call_count, 1)
        block = record["sessions"][0]
        self.assertEqual(len(block["rows"]), 22)
        self.assertEqual(block["label"], "Practice 3")
        self.assertEqual(block["session_start"], "2026-09-25T12:30:00+04:00")
        self.assertEqual(block["fetched_at"], NOW.isoformat(timespec="seconds"))
        self.assertEqual(block["source_url"], Response.url)
        self.assertEqual(record["event"], results.identity(CTX))
        self.assertEqual(f1lib._split_driver(block["rows"][0][2]), ("Driver 0", "AAA"))

    def test_network_and_empty_or_partial_tables_retain_last_good(self):
        old, _ = self.collect()
        headers, rows = table()
        cases = [
            {"error": OSError("HTTP 503")},
            {"response": Response("<html>No results available</html>")},
            {"response": Response(page(headers, rows[:-1]))},
            {"response": Response(page(headers, rows[:5]))},
            {"response": Response(page() + page())},
        ]
        for case in cases:
            with self.subTest(case=case):
                current, _ = self.collect(old=old, **case)
                self.assertTrue(current["sessions"][0]["retained"])
                self.assertEqual(current["sessions"][0]["rows"], old["sessions"][0]["rows"])
                self.assertEqual(current["sessions"][0]["fetched_at"], old["sessions"][0]["fetched_at"])
                self.assertEqual(current["statuses"][0]["state"], "unavailable")
                self.assertTrue(current["statuses"][0]["error"])

    def test_missing_table_never_claims_no_running(self):
        record, _ = self.collect(error=OSError("timeout"))
        rendered = f1lib.render_results({"results": [], "results_status": record["statuses"]})
        self.assertIn("Practice 3", rendered)
        self.assertIn("does not mean the session has not run", rendered)
        self.assertNotIn("No sessions have been completed", rendered)

    def test_in_progress_missing_table_is_pending(self):
        now = NOW.replace(hour=8, minute=40)
        record, _ = self.collect(now=now, error=OSError("unpublished"))
        self.assertEqual(record["statuses"][0]["state"], "pending")

    def test_revised_classification_replaces_old_without_losing_status_rows(self):
        old, _ = self.collect()
        headers, rows = table()
        rows[0][4] = "1:43.900"
        rows[-2][4:6] = ["", "0"]
        rows[-1][0], rows[-1][4] = "DSQ", "DSQ"
        record, _ = self.collect(old=old, response=Response(page(headers, rows)))
        block = record["sessions"][0]
        self.assertEqual(block["rows"], rows)
        self.assertFalse(block["retained"])
        self.assertEqual(len(block["rows"]), 22)

    def test_duplicate_identities_and_positions_rejected(self):
        for column in (0, 1, 2):
            headers, rows = table()
            rows[1][column] = rows[0][column]
            with self.assertRaises(ValueError):
                results.parse_table(page(headers, rows))

    def test_wrong_event_year_source_or_session_cache_rejected(self):
        record, _ = self.collect()
        variants = []
        for key in ("year", "gp", "race_id", "results_slug"):
            changed = copy.deepcopy(record)
            changed["event"][key] = "wrong"
            variants.append(changed)
        for key in ("source_url", "session_start"):
            changed = copy.deepcopy(record)
            changed["sessions"][0][key] = "wrong"
            variants.append(changed)
        for changed in variants:
            with patch.object(Path, "exists", return_value=True), patch.object(
                    Path, "read_text", return_value=json.dumps(changed)):
                with self.assertRaises(ValueError):
                    results.load(CTX)

    def test_offline_build_uses_persisted_snapshot_and_latest_active_tab(self):
        record, _ = self.collect()
        ctx = copy.deepcopy(CTX)
        with patch.object(results, "load", return_value=record), patch.object(
                results.urllib.request, "urlopen", side_effect=AssertionError("No build refetch")):
            ctx["results"] = results.results(ctx, now=NOW)
        rendered = f1lib.render_results(ctx)
        self.assertIn('nav-link active" id="res-practice-3-tab"', rendered)
        self.assertEqual(rendered.count("<tr>"), 23)
        self.assertIn(Response.url, rendered)
        self.assertNotIn("Qualifying</button>", rendered)
        with patch.object(results, "load", return_value=record):
            self.assertEqual(results.results(ctx, now=NOW.replace(hour=7)), [])

    def test_starting_grid_does_not_displace_latest_completed_session(self):
        headers, rows = table()
        rendered = f1lib.render_results({"results": [
            {"label": "Qualifying", "headers": headers, "rows": rows},
            {"label": "Starting Grid", "headers": headers, "rows": rows},
        ]})
        self.assertIn('nav-link active" id="res-qualifying-tab"', rendered)
        self.assertIn('id="res-starting-grid-tab"', rendered)
        self.assertNotIn('nav-link active" id="res-starting-grid-tab"', rendered)

    def test_collector_precedes_persistence_and_build_in_deployment(self):
        workflow = Path(__file__).with_name(".github").joinpath("workflows/deploy.yml").read_text()
        self.assertLess(workflow.index("run: python3 session_results.py"),
                        workflow.index("- name: Persist enrichment data"))
        self.assertLess(workflow.index("- name: Persist enrichment data"),
                        workflow.index("- name: Build site"))


if __name__ == "__main__":
    unittest.main()
