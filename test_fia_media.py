import io
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fia_media
import f1lib


URL = "https://www.fia.com/system/files/documents/power_unit_information.pdf"
CTX = {"dir": "spain", "fia_url": "https://www.fia.com/documents/spain"}


class FiaMediaTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for module, attribute, value in (
                (fia_media, "DATA_DIR", self.root / "data"),
                (fia_media, "ASSETS_DIR", self.root / "assets"),
                (f1lib, "DATA_DIR", str(self.root / "data"))):
            mock = patch.object(module, attribute, value)
            mock.start()
            self.addCleanup(mock.stop)
        self.manifest = self.root / "data/spain/fia_documents.json"
        fia_media._write(self.manifest, {
            "retrieved_at": "2026-09-10T12:00:00+00:00",
            "documents": [{"url": URL, "filename": "power_unit_information.pdf"}],
        })

    def render(self, raw, prefix):
        fia_media.ASSETS_DIR.mkdir(exist_ok=True)
        asset = prefix + "-p2.png"
        (fia_media.ASSETS_DIR / asset).write_bytes(b"\x89PNG\r\n\x1a\n")
        return [{"page": 2, "asset": asset}]

    def record(self):
        return fia_media._read(self.root / "data/spain/fia_media.json")

    def test_first_fetch_renders_and_repeat_fetch_reuses_images(self):
        with patch.object(fia_media, "_download", return_value=b"%PDF-first"), \
                patch.object(fia_media, "_render", side_effect=self.render) as render:
            self.assertTrue(fia_media.refresh_gp(CTX))
            self.assertTrue(fia_media.refresh_gp(CTX))
        self.assertEqual(render.call_count, 1)
        self.assertEqual(self.record()["documents"][0]["pages"][0]["page"], 2)
        self.assertEqual(self.record()["errors"], [])

    def test_same_url_revision_gets_new_asset_without_overwriting_history(self):
        with patch.object(fia_media, "_download", side_effect=[b"%PDF-first", b"%PDF-revised"]), \
                patch.object(fia_media, "_render", side_effect=self.render):
            fia_media.refresh_gp(CTX)
            old_asset = self.record()["documents"][0]["pages"][0]["asset"]
            fia_media.refresh_gp(CTX)
        new_asset = self.record()["documents"][0]["pages"][0]["asset"]
        self.assertNotEqual(old_asset, new_asset)
        self.assertTrue((fia_media.ASSETS_DIR / old_asset).exists())
        self.assertTrue((fia_media.ASSETS_DIR / new_asset).exists())
        self.assertEqual(self.record()["documents"][0]["revision"], 1)
        old_figure = f'<figure><img src="old.png"><a href="{URL}#page=2">PDF</a></figure>'
        body = f1lib.render_fia_media(CTX, "powerunit", old_figure)
        self.assertIn(new_asset, body)
        self.assertIn("Revised at the same source URL", body)
        current_figure = f'<figure><img src="../assets/{new_asset}"></figure>'
        self.assertEqual(f1lib.render_fia_media(CTX, "powerunit", current_figure), "")

    def test_failed_fetch_retains_previous_images_and_records_error(self):
        with patch.object(fia_media, "_download", side_effect=[b"%PDF-first", OSError("HTTP 403")]), \
                patch.object(fia_media, "_render", side_effect=self.render):
            fia_media.refresh_gp(CTX)
            original = self.record()["documents"]
            self.assertFalse(fia_media.refresh_gp(CTX))
        self.assertEqual(self.record()["documents"], original)
        self.assertIn("403", self.record()["errors"][0]["error"])
        self.assertIn("could not be refreshed", f1lib.render_fia_media(CTX, "powerunit"))

    def test_missing_asset_is_rebuilt_even_when_pdf_hash_is_unchanged(self):
        with patch.object(fia_media, "_download", return_value=b"%PDF-first"), \
                patch.object(fia_media, "_render", side_effect=self.render) as render:
            fia_media.refresh_gp(CTX)
            asset = self.record()["documents"][0]["pages"][0]["asset"]
            (fia_media.ASSETS_DIR / asset).unlink()
            fia_media.refresh_gp(CTX)
        self.assertEqual(render.call_count, 2)

    def test_new_pdf_pages_are_visible_without_bespoke_content_edits(self):
        with patch.object(fia_media, "_download", return_value=b"%PDF-first"), \
                patch.object(fia_media, "_render", side_effect=self.render):
            fia_media.refresh_gp(CTX)
        body = f1lib.render_fia_media(CTX, "powerunit")
        self.assertIn('onclick="zoomImg(this)"', body)
        self.assertIn(URL + "#page=2", body)
        self.assertIn("automatic screenshot", body)
        self.assertEqual(f1lib.render_fia_media(CTX, "circuit"), "")

    def test_curated_page_figures_are_not_duplicated(self):
        with patch.object(fia_media, "_download", return_value=b"%PDF-first"), \
                patch.object(fia_media, "_render", side_effect=self.render):
            fia_media.refresh_gp(CTX)
        for citation in (f'<a href="{URL}#page=2">PDF</a>',
                         f'<a href="{URL}">PDF, page 2</a>'):
            with self.subTest(citation=citation):
                curated = '<figure><img src="existing.png">' + citation + "</figure>"
                self.assertEqual(f1lib.render_fia_media(CTX, "powerunit", curated), "")
        # A prose citation alone does not make a missing screenshot complete.
        self.assertIn("<img", f1lib.render_fia_media(CTX, "powerunit", f'<a href="{URL}">PDF</a>'))

    def test_download_rejects_html_and_non_fia_hosts(self):
        response = io.BytesIO(b"<html>Access denied</html>")
        response.url = URL
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "did not return a PDF"):
                fia_media._download(URL)
        with self.assertRaisesRegex(ValueError, "Not an official"):
            fia_media._download("https://example.test/doc.pdf")

    def test_absent_discovery_is_reported_not_success_shaped(self):
        self.manifest.unlink()
        self.assertFalse(fia_media.refresh_gp(CTX))
        self.assertEqual(self.record()["documents"], [])
        self.assertIn("No saved FIA", self.record()["errors"][0]["error"])

    def test_corrupt_manifest_fails_explicitly(self):
        self.manifest.write_text("invalid json")
        with self.assertRaises(json.JSONDecodeError):
            fia_media.refresh_gp(CTX)

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF renderer not installed")
    def test_real_renderer_skips_cover_but_preserves_substantive_pages(self):
        import pymupdf
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((40, 40), "Document 3\nTitle Power unit\nEnclosed report")
            pdf.new_page().insert_text((40, 40), "Race 8.5 MJ\nQualifying 7.5 MJ")
            pages = fia_media._render(pdf.tobytes(), "fia-test")
        self.assertEqual([page["page"] for page in pages], [2])
        with pymupdf.open(fia_media.ASSETS_DIR / pages[0]["asset"]) as image:
            pixmap = image[0].get_pixmap()
            self.assertEqual(pixmap.pixel(0, 0), (255, 255, 255))

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "optional PDF renderer not installed")
    def test_real_renderer_preserves_first_content_page_and_rejects_oversize(self):
        import pymupdf
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((40, 40), "Official circuit map")
            pages = fia_media._render(pdf.tobytes(), "fia-map")
            self.assertEqual(pages[0]["page"], 1)
        with pymupdf.open() as pdf:
            pdf.new_page(width=4000, height=4000)
            with self.assertRaisesRegex(ValueError, "render-size"):
                fia_media._render(pdf.tobytes(), "fia-too-large")


if __name__ == "__main__":
    unittest.main()
