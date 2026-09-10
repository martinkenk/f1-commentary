"""Offline FIA discovery, source rendering and extraction retry regression tests."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import urllib.error
import uuid

import enrich
import f1lib


CTX = {
    "dir": "italy", "flag": "IT", "name": "Italian Grand Prix",
    "year": 2026, "round": "Round 16", "nav": [], "keywords": {"monza"},
    "fia_url": "https://www.fia.com/events/f1/season-2026/event/italian-grand-prix",
}


def document(filename):
    return {"filename": filename,
            "url": "https://www.fia.com/system/files/documents/" + filename}


PU = document("2026_italian_grand_prix_-_power_unit_information.pdf")
MAP = document("2026_italian_grand_prix_-_competition_notes_-_circuit_map.pdf")
DECISION = document("2026_italian_grand_prix_-_decision_-_car_12.pdf")
ARTICLE = {"url": "https://www.the-race.com/formula-1/monza-test/",
           "title": "Monza report", "source": "The Race", "src_kind": "race",
           "body": "A race report.", "when": "6 Sep", "date": "2026-09-06"}
CARD = {"id": "news1", "url": ARTICLE["url"], "title": ARTICLE["title"],
        "paragraphs": ["A race report."]}
RULING = {"doc": "Doc 12", "outcome": "No further action", "kind": "noaction",
          "source_pdf": DECISION["filename"]}


class EnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path.cwd() / (".test-enrichment-" + uuid.uuid4().hex)
        self.directory.mkdir()
        self.addCleanup(shutil.rmtree, self.directory)
        for module in (enrich, f1lib):
            mock = patch.object(module, "DATA_DIR", str(self.directory))
            mock.start()
            self.addCleanup(mock.stop)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        enrich.FAILURES.clear()
        self.addCleanup(enrich.FAILURES.clear)
        for cache in (enrich._F1_PAGE_CACHE, enrich._F1_BODY_CACHE, enrich._F1_META_CACHE):
            cache.clear()
            self.addCleanup(cache.clear)

    def read(self, name):
        return json.loads((self.directory / "italy" / (name + ".json")).read_text())

    def save(self, name, data):
        enrich.save_json(str(self.directory / "italy" / (name + ".json")), data)

    def test_discovery_retains_all_documents_but_penalties_are_filtered(self):
        docs = [PU, MAP, DECISION,
                document("2026_car_presentation_submissions.pdf"),
                document("2026_final_classification.pdf"),
                document("2026_summons_alleged_infringement.pdf")]
        page = "".join(f'<a href="{d["url"]}">PDF</a>' for d in docs + [PU])
        with patch.object(enrich, "_get", return_value=page):
            found = enrich.fia_documents(CTX)
            decisions = enrich.fia_decision_pdfs(CTX)
        self.assertEqual(len(found), len(docs))
        self.assertEqual([d["filename"] for d in decisions], [DECISION["filename"]])
        self.assertEqual(found[0]["categories"], ["powerunit"])
        self.assertEqual(found[1]["categories"], ["circuit"])

    def test_categories_match_real_fia_subjects_not_generic_reports(self):
        subjects = {
            "pu_elements_used_per_driver_up_to_now": ["powerunit"],
            "new_pu_elements_for_this_competition_1": ["powerunit"],
            "race_directors_competition_notes_v2": ["circuit"],
            "race_director_notes_-_sc2_-_sc1_times": ["circuit"],
            "race_director_s_event_notes": ["circuit"],
            "competition_notes_-_pirelli_preview": ["tyres"],
            "available_tyres": ["tyres"],
            "car_presentation_submissions": ["upgrades"],
            "infringement_-_car_30_-_change_to_pu_elements": [],
            "race_scrutineering": [],
        }
        for subject, expected in subjects.items():
            with self.subTest(subject=subject):
                self.assertEqual(f1lib.fia_document_categories(subject + ".pdf"), expected)

    def test_event_failure_falls_back_to_matching_inline_event(self):
        page = ('<div class="event-title active">Italian Grand Prix</div>'
                f'<a href="{PU["url"]}">PDF</a>')
        with patch.object(enrich, "_get", side_effect=[OSError("403"), page]):
            self.assertEqual(enrich.fia_documents(CTX)[0]["url"], PU["url"])
        self.assertFalse(enrich.FAILURES)

    def test_event_failure_falls_back_to_ajax(self):
        index = ('<a href="/decision-document-list/nojs/123">Italian Grand Prix</a>'
                 '<a href="/decision-document-list/nojs/456">Dutch Grand Prix</a>')
        ajax = json.dumps([{"command": "insert", "data": f'<a href="{MAP["url"]}">PDF</a>'}])
        with patch.object(enrich, "_get", side_effect=[OSError("502"), index, ajax]) as get:
            self.assertEqual(enrich.fia_documents(CTX)[0]["url"], MAP["url"])
        self.assertEqual(get.call_args.args[0], "https://www.fia.com/decision-document-list/ajax/123")

    def test_invalid_http_success_uses_fallback(self):
        page = ('<div class="event-title active">Italian Grand Prix</div>'
                f'<a href="{PU["url"]}">PDF</a>')
        with patch.object(enrich, "_get", side_effect=["Access denied", page]):
            self.assertEqual(enrich.fia_documents(CTX)[0]["url"], PU["url"])

    def test_failed_discovery_retains_last_good_manifest(self):
        with patch.object(enrich, "fia_documents", return_value=[PU, MAP]):
            enrich.discover_fia(CTX)
        original = self.read("fia_documents")
        self.assertTrue(original["retrieved_at"])
        self.assertEqual(original["source_url"], CTX["fia_url"])
        with patch.object(enrich, "_get", side_effect=OSError("HTTP 500")):
            self.assertEqual(enrich.discover_fia(CTX), [])
        self.assertEqual(self.read("fia_documents"), original)
        self.assertFalse(self.read("fia_discovery_status")["ok"])
        rendered = f1lib.render_fia_documents(CTX, "powerunit")
        self.assertIn("Latest discovery attempt failed", rendered)
        self.assertIn(PU["url"], rendered)
        self.assertNotIn("not published documents for this event yet", rendered)
        self.assertTrue(enrich.FAILURES)

    def test_successful_empty_listing_is_recorded_without_publication_claim(self):
        with patch.object(enrich, "_get", return_value='<div class="document-list">No documents</div>'):
            self.assertEqual(enrich.discover_fia(CTX), [])
        self.assertEqual(self.read("fia_documents")["documents"], [])
        self.assertTrue(self.read("fia_discovery_status")["ok"])
        self.assertIn("not a statement of non-publication",
                      f1lib.render_fia_documents(CTX, "powerunit"))

    def test_shell_injects_sources_and_preserves_curated_content(self):
        docs = [PU, MAP, document("available_tyres.pdf"),
                document("car_presentation_submissions.pdf")]
        with patch.object(enrich, "fia_documents", return_value=docs):
            enrich.discover_fia(CTX)
        for category, doc in zip(("powerunit", "circuit", "tyres", "upgrades"), docs):
            with self.subTest(category=category):
                rendered = f1lib.shell(CTX, category, "Title", "Kicker", "Title",
                                       "Subtitle", '<p id="curated">Reviewed data: 42.</p>')
                self.assertIn(doc["url"], rendered)
                self.assertIn("Official source; curated transcription may await review.", rendered)
                self.assertIn('<p id="curated">Reviewed data: 42.</p>', rendered)
                self.assertIn("retrieval time, not issue time", rendered)
        self.assertEqual(f1lib.render_fia_documents(CTX, "news"), "")

    def test_unsafe_document_urls_are_not_rendered(self):
        self.save("fia_documents", {"retrieved_at": "2026-09-06",
                  "documents": [{"filename": PU["filename"], "url": "javascript:alert(1)"}]})
        self.assertNotIn("javascript:", f1lib.render_fia_documents(CTX, "powerunit"))

    def test_unrecorded_discovery_is_not_claimed_unpublished(self):
        rendered = f1lib.render_fia_documents(CTX, "circuit")
        self.assertIn("Automatic discovery has not yet been recorded", rendered)
        self.assertIn(CTX["fia_url"], rendered)

    def test_corrupt_discovery_is_not_silently_treated_as_missing(self):
        self.save("fia_documents", [])
        with self.assertRaisesRegex(ValueError, "Invalid FIA discovery record"):
            f1lib.render_fia_documents(CTX, "circuit")

    def test_failed_extractions_retry_and_reconcile_legacy_seen(self):
        self.save("_seen", {"articles": [ARTICLE["url"]], "fia": [DECISION["filename"]]})
        with patch.object(enrich, "fia_documents", return_value=[PU, DECISION]), \
                patch.object(enrich, "the_race_articles", return_value=[ARTICLE]), \
                patch.object(enrich, "f1_articles", return_value=[]), \
                patch.object(enrich, "summarise_article", side_effect=[None, CARD]) as summary, \
                patch.object(enrich, "_pdf_text", side_effect=["", "Document 12"]) as pdf, \
                patch.object(enrich, "structure_decision", return_value=RULING):
            self.assertEqual(enrich.enrich_gp(CTX), 0)
            self.assertEqual(self.read("_seen"), {"articles": [], "fia": []})
            self.assertEqual(enrich.enrich_gp(CTX), 2)
            self.assertEqual(self.read("_seen")["articles"], [ARTICLE["url"]])
            self.assertEqual(self.read("_seen")["fia"], [DECISION["filename"]])
            self.assertEqual(self.read("penalties_auto")[0]["source_url"], DECISION["url"])
            self.assertEqual(enrich.enrich_gp(CTX), 0)
            self.assertEqual(summary.call_count, 2)
            self.assertEqual(pdf.call_count, 2)
        self.assertEqual(len(self.read("fia_documents")["documents"]), 2)

    def test_incomplete_ruling_is_retryable(self):
        with patch.object(enrich, "fia_documents", return_value=[DECISION]), \
                patch.object(enrich, "the_race_articles", return_value=[]), \
                patch.object(enrich, "f1_articles", return_value=[]), \
                patch.object(enrich, "_pdf_text", return_value="Document 12"), \
                patch.object(enrich, "structure_decision", return_value={"doc": "Doc 12"}):
            enrich.enrich_gp(CTX)
        self.assertEqual(self.read("_seen")["fia"], [])
        self.assertEqual(self.read("penalties_auto"), [])
        self.assertTrue(enrich.FAILURES)

    def test_source_http_failures_are_visible(self):
        error = urllib.error.HTTPError("https://example.test", 503, "Unavailable", {}, None)
        self.addCleanup(error.close)
        with patch.object(enrich, "_get", side_effect=error):
            self.assertEqual(enrich.the_race_articles(), [])
            self.assertEqual(enrich.f1_articles(), [])
            self.assertEqual(enrich._f1_page(ARTICLE["url"]), "")
        self.assertEqual(len(enrich.FAILURES), 3)

    def test_main_exits_nonzero_but_continues_after_gp_exception(self):
        with patch.object(enrich, "load_gps", return_value=[CTX, CTX]), \
                patch.object(enrich, "enrich_gp", side_effect=[OSError("HTTP 503"), 1]) as run, \
                patch("sys.argv", ["enrich.py", "--all"]):
            self.assertEqual(enrich.main(), 1)
        self.assertEqual(run.call_count, 2)

    def test_main_exits_nonzero_after_recorded_source_failure(self):
        def failed_source(*args, **kwargs):
            enrich._failure("Source unavailable")
            return 0
        with patch.object(enrich, "load_gps", return_value=[CTX]), \
                patch.object(enrich, "enrich_gp", side_effect=failed_source), \
                patch("sys.argv", ["enrich.py", "--all"]):
            self.assertEqual(enrich.main(), 1)

    def test_main_success_resets_previous_failure_state(self):
        enrich.FAILURES.append("previous run")
        with patch.object(enrich, "load_gps", return_value=[CTX]), \
                patch.object(enrich, "enrich_gp", return_value=1), \
                patch("sys.argv", ["enrich.py", "--all"]):
            self.assertEqual(enrich.main(), 0)


if __name__ == "__main__":
    unittest.main()
