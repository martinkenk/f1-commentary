import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import enrich
import f1lib
import fia_media


URL = "https://www.fia.com/system/files/decision_-_car_77.pdf"
FILENAME = "decision_-_car_77.pdf"
CTX = {"dir": "test"}
TEXT = """Document 19
No / Driver 77 - Valtteri Bottas
Competitor Cadillac Formula 1 Team
Session Free Practice 1
Fact Overtaking under yellow flags
Decision No penalty is applied.
Reason The driver of Car 23 (Alexander Albon) was also heard.
"""


class DecisionIdentityTests(unittest.TestCase):
    def test_nbsp_fields_and_no_penalty_are_deterministic(self):
        with patch.object(enrich, "llm_json", return_value=None):
            record = enrich.structure_decision(TEXT.replace(" ", "\u00a0"), FILENAME)
        self.assertEqual(record["driver"], "Valtteri Bottas")
        self.assertEqual(record["no"], "77")
        self.assertEqual(record["team"], "Cadillac Formula 1 Team")
        self.assertEqual(record["session"], "Free Practice 1")
        self.assertEqual(record["kind"], "noaction")
        self.assertFalse(enrich._no_action("10-second penalty; no penalty points."))

    def test_multiple_subjects_and_replacement_use_document_not_current_roster(self):
        text = """Session Free Practice 1
No. Turn Car Driver Competitor Time of Day Lap Time
1 4 38\tOliver Bearman\tScuderia Ferrari\t12:12:12\t1:20.000
2 9 21\tNyck de Vries\tAlphaTauri\t12:13:13\t1:21.000
3 4 38\tOliver Bearman\tScuderia Ferrari\t12:14:14\t1:22.000
Decision Deletion of the lap times shown.
"""
        record = enrich.decision_identity(text)
        self.assertEqual(record["driver"], "Oliver Bearman; Nyck de Vries")
        self.assertEqual(record["no"], "")
        self.assertEqual(record["identity_status"], "named")
        no_turn = text.replace("No. Turn Car", "No. Car").replace("1 4 38", "1 38")
        self.assertIn("Oliver Bearman", enrich.decision_identity(no_turn)["driver"])

    def test_unknown_driver_is_not_guessed_and_general_and_team_are_distinct(self):
        self.assertEqual(enrich.decision_identity("No names", FILENAME)["identity_status"],
                         "unavailable")
        self.assertEqual(enrich.decision_identity("Unreadable subject")["identity_status"],
                         "unavailable")
        self.assertEqual(enrich.decision_identity("Session temporarily stopped")["identity_status"],
                         "general")
        record = enrich.decision_identity("Competitor Example Racing\nDecision Fine EUR 1000")
        self.assertEqual(record["identity_status"], "team")
        self.assertEqual(record["driver"], "")

    def test_legacy_backfill_preserves_summary_and_named_permission_subjects(self):
        original = {"driver": "", "outcome": "No\u00a0penalty\u00a0is\u00a0applied.",
                    "kind": "penalty", "fact": "Reviewed editorial summary"}
        enrich.repair_decision(original, TEXT, FILENAME)
        self.assertEqual(original["driver"], "Valtteri Bottas")
        self.assertEqual(original["fact"], "Reviewed editorial summary")
        self.assertEqual(original["kind"], "noaction")
        text = ("Cars eligible to start\n1. 87 - Oliver Bearman - Haas\n"
                "2. 18 - Lance Stroll - Aston Martin")
        self.assertEqual(enrich.decision_identity(text)["driver"], "Oliver Bearman; Lance Stroll")

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF renderer")
    def test_pdf_coordinates_separate_driver_from_team_and_merged_numbers(self):
        import pymupdf
        with pymupdf.open() as pdf:
            page = pdf.new_page()
            for x, text in ((40, "No."), (68, "Turn"), (100, "Car"),
                            (130, "Driver"), (235, "Competitor")):
                page.insert_text((x, 100), text, fontsize=10)
            for y, no, number, name, team in (
                    (120, "1", "38", "Oliver Bearman", "Scuderia Ferrari"),
                    (140, "2", "21", "Nyck de Vries", "AlphaTauri")):
                for x, text in ((40, no), (68, "13"), (100, number), (130, name), (235, team)):
                    page.insert_text((x, y), text, fontsize=10)
            page.insert_text((40, 165), "Decision Deletion of lap times.")
            text = enrich.pdf_text(pdf.tobytes())
        self.assertEqual(enrich.decision_identity(text)["driver"], "Oliver Bearman; Nyck de Vries")


class PenaltyReaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "assets_src").mkdir()
        (self.root / "data/test").mkdir(parents=True)
        for module, attr, value in (
                (f1lib, "ROOT", str(self.root)),
                (f1lib, "DATA_DIR", str(self.root / "data")),
                (fia_media, "DATA_DIR", self.root / "data"),
                (fia_media, "ASSETS_DIR", self.root / "assets_src")):
            mock = patch.object(module, attr, value)
            mock.start()
            self.addCleanup(mock.stop)
        self.penalty = {"doc": "Doc 19", "source_url": URL, "source_pdf": FILENAME,
                        "driver": "Valtteri Bottas", "no": "77", "kind": "noaction",
                        "outcome": "No penalty is applied."}
        self.document = {"url": URL, "filename": FILENAME, "categories": ["penalties"],
                         "pages": [{"page": 1, "asset": "fia-test-p1.png"},
                                   {"page": 2, "asset": "fia-test-p2.png"}]}
        for page in self.document["pages"]:
            (self.root / "assets_src" / page["asset"]).write_bytes(b"PNG")
        self.save("fia_media", {"documents": [self.document]})

    def save(self, name, value):
        (self.root / "data/test" / (name + ".json")).write_text(json.dumps(value))

    def test_all_pages_collapsed_in_same_row_and_source_reader_link(self):
        body = f1lib.render_penalties(CTX, [self.penalty])
        self.assertIn('<details class="penalty-document"', body)
        self.assertNotIn(" open", body)
        self.assertEqual(body.count("<figure"), 2)
        self.assertIn(URL + "#page=2", body)
        self.assertIn("data-document-reader", body)
        self.assertIn("loading=\"lazy\"", body)
        self.assertIn("Valtteri Bottas", body)
        self.assertEqual(body.count("<tr>"), 2)  # header + one sortable decision
        self.assertLess(body.index("</details>"), body.index("</tbody>"))
        self.assertIn('data-sort="No penalty is applied."', body)

    def test_exact_url_matching_and_pdf_fallback(self):
        self.document["url"] = URL + "?other=1"
        self.save("fia_media", {"documents": [self.document]})
        body = f1lib.render_penalties(CTX, [self.penalty])
        self.assertNotIn("<img", body)
        self.assertIn("screenshots unavailable", body)
        self.assertIn("Original FIA PDF", body)
        self.assertNotIn("data-document-reader", body)
        self.penalty.pop("source_url")
        self.assertIn("no verified original PDF", f1lib.render_penalties(CTX, [self.penalty]))

    def test_missing_assets_stale_refresh_and_revision_are_explicit(self):
        (self.root / "assets_src/fia-test-p2.png").unlink()
        self.document["revision"] = 1
        self.save("fia_media", {"documents": [self.document],
                                "errors": [{"url": URL, "error": "403"}]})
        body = f1lib.render_penalties(CTX, [self.penalty])
        self.assertEqual(body.count("<img"), 1)
        self.assertIn("Some page images are unavailable", body)
        self.assertIn("last successful images", body)
        self.assertIn("Revised PDF", body)
        (self.root / "assets_src/fia-test-p1.png").unlink()
        self.assertIn("screenshots unavailable", f1lib.render_penalties(CTX, [self.penalty]))

    def test_curated_html_and_auto_source_survive_merge_and_identities_are_escaped(self):
        self.save("penalties_auto", [self.penalty])
        body = f1lib.render_penalties(CTX, [{"doc": "Doc 19", "outcome": "<strong>Reviewed</strong>"}])
        self.assertIn("<strong>Reviewed</strong>", body)
        self.assertIn("Valtteri Bottas", body)
        self.assertIn("data-document-reader", body)
        self.assertEqual(body.count('<details class="penalty-document"'), 1)
        self.penalty["driver"] = '<script>alert("name")</script>'
        body = f1lib.render_penalties(CTX, [self.penalty])
        self.assertNotIn("<script>", body)
        self.assertIn("&lt;script&gt;", body)
        body = f1lib.render_penalties(CTX, [{"doc": "Doc 19", "source_url": URL + "?different=1"}])
        self.assertNotIn("data-document-reader", body)
        self.assertNotIn("Valtteri Bottas", body)

    def test_scoped_refresh_retains_other_document_errors(self):
        error = {"url": "https://www.fia.com/system/files/tyres.pdf", "error": "403"}
        self.save("fia_documents", {"documents": []})
        self.save("fia_media", {"documents": [], "errors": [error]})
        self.assertFalse(fia_media.refresh_gp(CTX, decisions_only=True))
        record = json.loads((self.root / "data/test/fia_media.json").read_text())
        self.assertIn(error, record["errors"])

    def test_no_number_only_or_silent_empty_identity(self):
        for name in ("", "77", "#77"):
            record = dict(self.penalty, driver=name)
            self.assertIn("Driver identity unavailable", f1lib.render_penalties(CTX, [record]))
        for status, label in (("general", "General ruling"), ("team", "Team ruling")):
            record = dict(self.penalty, driver="", no="", identity_status=status)
            self.assertIn(label, f1lib.render_penalties(CTX, [record]))

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF renderer")
    def test_refresh_backfills_seen_decisions_and_preserves_first_ruling_page(self):
        import pymupdf
        self.save("fia_documents", {"documents": [{"url": URL, "filename": FILENAME}]})
        self.save("penalties_auto", [dict(self.penalty, driver="", no="", kind="penalty")])
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((40, 40), TEXT + "\nTitle Ruling\nEnclosed evidence")
            pdf.new_page().insert_text((40, 40), "Remaining reasons and signatures")
            raw = pdf.tobytes()
        with patch.object(fia_media, "_download", return_value=raw):
            self.assertTrue(fia_media.refresh_gp(CTX, decisions_only=True))
        data = json.loads((self.root / "data/test/penalties_auto.json").read_text())
        self.assertEqual(data[0]["driver"], "Valtteri Bottas")
        self.assertEqual(data[0]["kind"], "noaction")
        media = json.loads((self.root / "data/test/fia_media.json").read_text())
        self.assertEqual([p["page"] for p in media["documents"][0]["pages"]], [1, 2])

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF renderer")
    def test_same_url_revision_replaces_reader_with_every_new_page(self):
        import pymupdf
        self.save("fia_documents", {"documents": [{"url": URL, "filename": FILENAME}]})
        self.save("penalties_auto", [self.penalty])
        versions = []
        for count in (2, 3):
            with pymupdf.open() as pdf:
                pdf.new_page().insert_text((40, 40), TEXT)
                for page in range(1, count):
                    pdf.new_page().insert_text((40, 40), f"Reasons and signatures {page}")
                versions.append(pdf.tobytes())
        with patch.object(fia_media, "_download", side_effect=versions):
            fia_media.refresh_gp(CTX, decisions_only=True)
            path = self.root / "data/test/fia_media.json"
            old = json.loads(path.read_text())["documents"][0]
            fia_media.refresh_gp(CTX, decisions_only=True)
            revised = json.loads(path.read_text())["documents"][0]
        self.assertEqual(revised["revision"], old.get("revision", 0) + 1)
        self.assertNotEqual(revised["sha256"], old["sha256"])
        self.assertEqual([p["page"] for p in revised["pages"]], [1, 2, 3])
        body = f1lib.render_penalties(CTX)
        for page in revised["pages"]:
            self.assertIn(page["asset"], body)
        for page in old["pages"]:
            self.assertNotIn(page["asset"], body)
            self.assertTrue((self.root / "assets_src" / page["asset"]).exists())


if __name__ == "__main__":
    unittest.main()
