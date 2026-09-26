import copy
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import zlib

import race_tyres as rt


SPAIN = {
    "year": "2026", "dir": "spain", "race_date": "2026-09-13",
    "name": "Spanish Grand Prix", "circuit": "Madring",
    "cal": {"location": "Madrid", "sessions": [
        {"label": "Race", "timezone": "Europe/Madrid"}]},
}
PAGE = rt.SEEDS[(2026, "spain")][0]
IMAGE = "https://coffeecornermotorsport.com/wp-content/uploads/2026/09/1920_14-es26-racesets.webp"


def png(red=0, width=1080, height=608):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(
            ">I", zlib.crc32(kind + data) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress((b"\0" + bytes([red, 0, 0]) * width) * height)) +
            chunk(b"IEND", b""))


def article(name="Spanish", venue="Madrid", published="2026-09-12T22:55:03+01:00",
            year=2026, image=IMAGE):
    return f"""<!doctype html><html><head>
    <meta property="og:title" content="F1 {name} Grand Prix {year} Tyre Strategy">
    <meta property="article:published_time" content="{published}">
    <link rel="alternate" type="application/rss+xml" href="{rt.SECONDARY_FEED}">
    </head><body><article>
    <figure><img src="https://coffeecornermotorsport.com/strategy-preview.png"
     alt="Pirelli tyre preview, pit-stop strategy windows for {name} Grand Prix"></figure>
    <figure class="size-full"><img data-src="{image}"
     src="data:image/gif;base64,placeholder" alt="{name} Grand Prix {year} race sets
     remaining new and used Hard Medium Soft tyres for all 22 drivers at {venue}. © Pirelli Motorsport">
    <noscript><img src="{image}" alt="{name} Grand Prix {year} race sets at {venue} © Pirelli"
     srcset="{image} 1080w, https://coffeecornermotorsport.com/racesets-small.webp 600w"></noscript>
    <figcaption>Pirelli Motorsport race sets graphic, full table and legend.</figcaption>
    </figure></article></body></html>"""


def feed(title="F1 Spanish Grand Prix 2026 Tyre Strategy", url=PAGE):
    return f"""<?xml version="1.0"?><rss version="2.0"><channel>
    <item><title>{title}</title><link>{url}</link><pubDate>Sat, 12 Sep 2026 21:55:03 +0000</pubDate>
    </item></channel></rss>""".encode()


LATEST = b'<a href="/en/latest/article/news-from-the-paddock.ABCD123">News</a>'
F1_GUIDE = ("https://www.formula1.com/en/latest/article/"
            "strategy-guide-what-are-the-tactical-options-for-the-spanish-gp.2BDFZFEsdYeeyJNgdk5R0R")
GATED = b"""<html><script type="application/ld+json">
{"@type":"NewsArticle","isAccessibleForFree":false,"datePublished":"2026-09-12T12:00:00Z"}
</script><script>{"isProtected":true,"isFreewallVisible":true}</script></html>"""


class RaceTyresTests(unittest.TestCase):
    def setUp(self):
        # All test artifacts stay inside the repository, never the system temp directory.
        directory = tempfile.TemporaryDirectory(prefix=".race-tyres-test-", dir=rt.ROOT)
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.data = self.directory / "data"
        self.assets = self.directory / "assets"
        self.data.mkdir()
        self.assets.mkdir()
        for key, value in (("DATA_DIR", self.data), ("ASSET_DIR", self.assets)):
            patcher = patch.object(rt, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.responses = {
            rt.F1_LATEST: LATEST, rt.SECONDARY_FEED: feed(),
            PAGE: article().encode(), IMAGE: png(),
        }
        self.requests = []

    def fetch(self, url, image=False):
        rt.safe_url(url, image)
        self.requests.append((url, image))
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response

    def collect(self, ctx=SPAIN):
        with patch.object(rt, "fetch", side_effect=self.fetch):
            return rt.collect(ctx)

    def save(self, filename, obj, slug="spain"):
        directory = self.data / slug
        directory.mkdir(exist_ok=True)
        (directory / filename).write_text(json.dumps(obj))

    def test_secondary_attribution_and_full_image_not_preview_or_counts(self):
        result = self.collect()
        snapshot = result["snapshot"]
        self.assertEqual(result["status"]["state"], "available")
        self.assertEqual(snapshot["chart"]["provenance"], "secondary-reproduction")
        self.assertEqual(snapshot["source"]["publisher"], "Coffee Corner Motorsport")
        self.assertEqual(snapshot["chart"]["credit"], "Pirelli Motorsport")
        self.assertEqual(snapshot["chart"]["url"], IMAGE)
        self.assertEqual((snapshot["chart"]["width"], snapshot["chart"]["height"]), (1080, 608))
        self.assertNotIn("drivers", snapshot)
        self.assertNotIn("counts", snapshot)
        self.assertEqual([url for url, is_image in self.requests if is_image], [IMAGE])
        self.assertEqual((self.assets / snapshot["chart"]["asset"]).read_bytes(), png())

    def test_actual_raster_format_not_url_suffix(self):
        snapshot = self.collect()["snapshot"]
        self.assertTrue(snapshot["chart"]["url"].endswith(".webp"))
        self.assertTrue(snapshot["chart"]["asset"].endswith(".png"))
        self.assertEqual(snapshot["chart"]["sha256"], hashlib.sha256(png()).hexdigest())

    def test_live_feed_discovers_next_gp_without_registry_seed(self):
        ctx = {**SPAIN, "dir": "azerbaijan", "name": "Azerbaijan Grand Prix",
               "race_date": "2026-09-26", "circuit": "Baku City Circuit",
               "cal": {"location": "Baku", "sessions": [{"label": "Race", "timezone": "Asia/Baku"}]}}
        page = "https://coffeecornermotorsport.com/a-new-editorial-slug-no-template/"
        image = "https://coffeecornermotorsport.com/race-sets-baku.png"
        self.responses[rt.SECONDARY_FEED] = feed("Azerbaijan Grand Prix 2026 Tyre Strategy", page)
        self.responses[page] = article("Azerbaijan", "Baku", "2026-09-25T19:00:00Z", image=image).encode()
        self.responses[image] = png()
        with patch.object(rt, "SEEDS", {}):
            result = self.collect(ctx)
        self.assertEqual(result["status"]["state"], "available")
        self.assertEqual(result["snapshot"]["source"]["url"], page)
        self.assertEqual(result["snapshot"]["gp"], "azerbaijan")
        self.assertNotIn((PAGE, False), self.requests)

    def test_no_borrowed_spain_inventory_for_pending_baku(self):
        self.collect()
        ctx = {**SPAIN, "dir": "azerbaijan", "name": "Azerbaijan Grand Prix",
               "race_date": "2026-09-26", "cal": {"location": "Baku"}}
        result = self.collect(ctx)
        self.assertEqual(result["snapshot"], {})
        self.assertEqual(result["status"]["state"], "not_found")
        self.assertFalse((self.data / "azerbaijan/race_tyres.json").exists())

    def test_accented_calendar_names_match_public_ascii_titles(self):
        ctx = {**SPAIN, "dir": "brazil", "name": "São Paulo Grand Prix",
               "race_date": "2026-11-08", "circuit": "Interlagos",
               "cal": {"location": "São Paulo"}}
        page = "https://coffeecornermotorsport.com/published-sao-paulo-strategy/"
        image = "https://coffeecornermotorsport.com/sao-paulo-racesets.png"
        self.responses[rt.SECONDARY_FEED] = feed("Sao Paulo Grand Prix 2026 Tyre Strategy", page)
        self.responses[page] = article("Sao Paulo", "Sao Paulo", "2026-11-07T19:00:00Z",
                                       image=image).encode()
        self.responses[image] = png()
        with patch.object(rt, "SEEDS", {}):
            result = self.collect(ctx)
        self.assertEqual(result["status"]["state"], "available")
        self.assertEqual(result["snapshot"]["gp"], "brazil")

    def test_article_metadata_cannot_validate_another_events_chart(self):
        text = article().replace(
            "</head>", '<meta property="og:description" content="Spanish GP at Madrid"></head>')
        text = text.replace("at Madrid", "at Monza")
        text = text.replace('content="Spanish GP at Monza"', 'content="Spanish GP at Madrid"')
        with self.assertRaisesRegex(rt.SourceError, "venue evidence"):
            rt.chart_links(SPAIN, PAGE, text)
        text = article().replace("Spanish Grand Prix 2026 race sets",
                                 "Italian Grand Prix 2026 race sets")
        with self.assertRaisesRegex(rt.SourceError, "event evidence"):
            rt.chart_links(SPAIN, PAGE, text)

    def test_gated_f1_is_recorded_even_with_secondary_success(self):
        self.save("news_auto.json", [{"url": F1_GUIDE, "title": "Strategy guide Spanish GP"}])
        self.responses[F1_GUIDE] = GATED
        result = self.collect()
        self.assertEqual(result["status"]["state"], "available")
        self.assertIn("access-restricted", result["status"]["error"])
        self.assertTrue(any(a["state"] == "access_restricted" and a["url"] == F1_GUIDE
                            for a in result["status"]["attempts"]))
        self.assertEqual([u for u, _ in self.requests if "formula1.com" in u],
                         [rt.F1_LATEST, F1_GUIDE])

    def test_gated_only_is_not_false_not_found(self):
        self.responses[rt.SECONDARY_FEED] = feed(
            "General paddock news", "https://coffeecornermotorsport.com/general-news/")
        self.responses[rt.F1_LATEST] = f'<a href="{F1_GUIDE}">Spanish GP strategy guide</a>'.encode()
        self.responses[F1_GUIDE] = GATED
        with patch.object(rt, "SEEDS", {}):
            result = self.collect()
        self.assertEqual(result["status"]["state"], "access_restricted")
        self.assertEqual(result["snapshot"], {})
        self.assertFalse(any(image for _, image in self.requests))

    def test_public_latest_links_are_not_gated_by_embedded_card_flags(self):
        self.responses[rt.F1_LATEST] = (
            f'<script>{{"isAccessibleForFree":false}}</script><a href="{F1_GUIDE}">Guide</a>').encode()
        self.responses[F1_GUIDE] = GATED
        result = self.collect()
        latest = next(a for a in result["status"]["attempts"] if a["url"] == rt.F1_LATEST)
        self.assertEqual(latest["state"], "available")
        self.assertIn((F1_GUIDE, False), self.requests)

    def test_public_first_party_chart_is_preferred_with_creator_preserved(self):
        primary_image = "https://media.formula1.com/image/upload/public-racesets.png"
        self.responses[rt.F1_LATEST] = f'<a href="{F1_GUIDE}">Guide</a>'.encode()
        self.responses[F1_GUIDE] = article(image=primary_image).encode()
        self.responses[primary_image] = png()
        snapshot = self.collect()["snapshot"]
        self.assertEqual(snapshot["source"]["publisher"], "Formula1.com")
        self.assertEqual(snapshot["chart"]["provenance"], "first-party")
        self.assertEqual(snapshot["chart"]["credit"], "Pirelli Motorsport")

    def test_revision_redownloads_and_changes_hashed_asset(self):
        first = self.collect()["snapshot"]
        old_data = (self.data / "spain/race_tyres.json").read_bytes()
        self.responses[IMAGE] = png(100)
        second = self.collect()["snapshot"]
        self.assertNotEqual(first["chart"]["asset"], second["chart"]["asset"])
        self.assertNotEqual(first["chart"]["sha256"], second["chart"]["sha256"])
        self.assertNotEqual(old_data, (self.data / "spain/race_tyres.json").read_bytes())
        self.assertEqual(self.requests.count((PAGE, False)), 2)
        self.assertEqual(self.requests.count((IMAGE, True)), 2)
        self.assertTrue((self.assets / first["chart"]["asset"]).exists())

    def test_missing_caption_venue_can_reuse_identical_verified_image(self):
        first = self.collect()["snapshot"]
        self.responses[PAGE] = article(venue="").encode()
        result = self.collect()
        self.assertEqual(result["status"]["state"], "available")
        self.assertEqual(result["snapshot"]["chart"], first["chart"])
        self.assertEqual(self.requests.count((IMAGE, True)), 2)
        self.assertEqual(self.collect()["snapshot"]["chart"], first["chart"])

    def test_missing_caption_venue_cannot_reuse_evidence_for_changed_bytes(self):
        first = self.collect()["snapshot"]
        self.responses[PAGE] = article(venue="").encode()
        self.responses[IMAGE] = png(100)
        result = self.collect()
        self.assertEqual(result["status"]["state"], "error")
        self.assertIn("previous visual venue evidence", result["status"]["error"])
        self.assertEqual(result["snapshot"], first)

    def test_missing_caption_venue_cannot_borrow_another_source_or_image(self):
        first = self.collect()["snapshot"]
        other = "https://coffeecornermotorsport.com/other-racesets.webp"
        self.responses[PAGE] = article(venue="", image=other).encode()
        self.responses[other] = png()
        result = self.collect()
        self.assertEqual(result["status"]["state"], "error")
        self.assertEqual(result["snapshot"], first)
        self.assertNotIn((other, True), self.requests)
        with self.assertRaisesRegex(rt.SourceError, "venue"):
            rt.chart_links(SPAIN, "https://coffeecornermotorsport.com/another-article/",
                           article(venue=""), previous=first)

    def test_cached_venue_evidence_does_not_override_event_or_access_checks(self):
        first = self.collect()["snapshot"]
        for body in (article(name="Italian", venue="").encode(), GATED):
            with self.subTest(body=body):
                self.responses[PAGE] = body
                result = self.collect()
                self.assertNotEqual(result["status"]["state"], "available")
                self.assertEqual(result["snapshot"], first)
        self.assertEqual(self.requests.count((IMAGE, True)), 1)

    def test_missing_asset_is_repaired_from_saved_source_without_seeds(self):
        first = self.collect()["snapshot"]
        asset = self.assets / first["chart"]["asset"]
        asset.unlink()
        self.assertEqual(rt.context(SPAIN)["status"]["state"], "error")
        self.responses[rt.SECONDARY_FEED] = feed(
            "General news", "https://coffeecornermotorsport.com/general-news/")
        with patch.object(rt, "SEEDS", {}):
            result = self.collect()
        self.assertTrue(asset.exists())
        self.assertEqual(result["status"]["state"], "available")
        self.assertEqual(result["snapshot"]["chart"]["sha256"], first["chart"]["sha256"])

    def test_failed_image_retains_last_good_snapshot_and_file(self):
        first = self.collect()["snapshot"]
        before = (self.data / "spain/race_tyres.json").read_bytes()
        self.responses[IMAGE] = rt.SourceError("Connection failed")
        result = self.collect()
        self.assertEqual(result["snapshot"], first)
        self.assertEqual(result["status"]["state"], "error")
        self.assertEqual((self.data / "spain/race_tyres.json").read_bytes(), before)
        self.assertTrue((self.assets / first["chart"]["asset"]).exists())
        self.assertIn("Connection failed", result["status"]["error"])

    def test_failed_page_retains_last_good(self):
        first = self.collect()["snapshot"]
        self.responses[PAGE] = rt.SourceError("Page unavailable")
        result = self.collect()
        self.assertEqual(result["snapshot"], first)
        self.assertEqual(result["status"]["state"], "error")

    def test_discovery_failures_surface_with_and_without_fallback(self):
        for content in (b"<html>changed feed format</html>", b"<rss><channel/></rss>"):
            with self.subTest(content=content):
                self.responses[rt.SECONDARY_FEED] = content
                result = self.collect()
                self.assertEqual(result["status"]["state"], "available")
                self.assertIn("Unsupported publisher feed format", result["status"]["error"])
                with patch.object(rt, "SEEDS", {}):
                    # Remove the cached URL too, to test genuinely unavailable fallback.
                    (self.data / "spain/race_tyres.json").unlink()
                    result = self.collect()
                self.assertEqual(result["status"]["state"], "error")
                self.assertEqual(result["snapshot"], {})
        self.responses[rt.F1_LATEST] = b"<html>No recognised article links</html>"
        self.assertIn("Unsupported Formula1 latest format", self.collect()["status"]["error"])

    def test_event_year_date_and_venue_guards(self):
        cases = [
            article(name="Italian", venue="Monza"),
            article(year=2025),
            article(published="2025-09-12T12:00:00Z"),
            article(published="2026-08-12T12:00:00Z"),
            article(published="2026-09-14T12:00:00Z"),
            article(venue="Barcelona"),
            article(venue="Sakhir"),
            article(published="not-a-date"),
        ]
        for text in cases:
            with self.subTest(text=text[:200]), self.assertRaises(rt.SourceError):
                rt.chart_links(SPAIN, PAGE, text)
        # A current article cannot rescue an old chart embedded within it.
        text = article().replace("Spanish Grand Prix 2026 race sets", "Spanish Grand Prix 2025 race sets")
        with self.assertRaisesRegex(rt.SourceError, "another season"):
            rt.chart_links(SPAIN, PAGE, text)

    def test_relocated_bahrain_requires_sepang_not_sakhir(self):
        ctx = {**SPAIN, "dir": "bahrain", "name": "Bahrain Grand Prix",
               "race_date": "2026-10-04", "cal": {"location": "Kuala Lumpur"}}
        for venue, valid in (("Sepang", True), ("Kuala Lumpur", True), ("Sakhir", False)):
            text = article("Bahrain", venue, "2026-10-03T12:00:00Z")
            if valid:
                self.assertTrue(rt.chart_links(ctx, PAGE, text)[1])
            else:
                with self.assertRaisesRegex(rt.SourceError, "venue"):
                    rt.chart_links(ctx, PAGE, text)

    def test_las_vegas_utc_next_day_is_still_local_race_day(self):
        ctx = {**SPAIN, "dir": "las-vegas", "name": "Las Vegas Grand Prix",
               "race_date": "2026-11-21", "cal": {"location": "Las Vegas", "sessions": [
                   {"label": "Race", "timezone": "America/Los_Angeles"}]}}
        text = article("Las Vegas", "Las Vegas", "2026-11-22T02:00:00Z")
        self.assertTrue(rt.chart_links(ctx, PAGE, text)[1])
        with self.assertRaisesRegex(rt.SourceError, "date window"):
            rt.chart_links(ctx, PAGE, article("Las Vegas", "Las Vegas", "2026-11-22T12:00:00Z"))

    def test_full_linked_original_is_selected_without_guessing(self):
        full = "https://coffeecornermotorsport.com/original-racesets.png"
        text = article().replace('<img data-src=', f'<a href="{full}"><img data-src=', 1)
        text = text.replace("<noscript>", "</a><noscript>", 1)
        self.assertEqual(rt.chart_links(SPAIN, PAGE, text)[1][0]["url"], full)

    def test_race_available_wording_without_racesets_filename(self):
        text = article(image="https://coffeecornermotorsport.com/inventory.png")
        text = text.replace("race sets", "tyres available for the race")
        self.assertTrue(rt.chart_links(SPAIN, PAGE, text)[1])

    def test_preview_and_postrace_are_not_inventory(self):
        for phrase in ("tyre preview", "strategy windows", "post-race stint summary",
                       "qualifying summary"):
            text = article(image="https://coffeecornermotorsport.com/summary.png")
            text = text.replace("race sets", phrase).replace("racesets-small", "summary-small")
            self.assertEqual(rt.chart_links(SPAIN, PAGE, text)[1], [])

    def test_unsupported_linked_inventory_is_explicit_error(self):
        text = article().split("<figure>")[0] + (
            '<a href="https://coffeecornermotorsport.com/racesets.pdf">'
            'Race sets available at Madrid © Pirelli</a></article></body></html>')
        with self.assertRaisesRegex(rt.SourceError, "Unsupported linked/embedded"):
            rt.chart_links(SPAIN, PAGE, text)

    def test_bad_public_urls_and_redirects_rejected_before_fetch(self):
        urls = ["http://coffeecornermotorsport.com/image.png", "https://127.0.0.1/a",
                "https://coffeecornermotorsport.com.evil.test/a",
                "https://coffeecornermotorsport.com@evil.test/a",
                "https://user:secret@coffeecornermotorsport.com/a",
                "https://coffeecornermotorsport.com:8443/a",
                "file:///etc/passwd", "https://coffeecornermotorsport.com/\nfoo",
                "https://coffeecornermotorsport.com\\@evil.test/a", None, [], 123]
        for url in urls:
            with self.subTest(url=url), self.assertRaises(rt.SourceError):
                rt.safe_url(url, image=True)
        redirect = rt._PublicRedirect(True)
        with self.assertRaises(rt.SourceError):
            redirect.redirect_request(None, None, 302, "", {}, "https://evil.test/chart.png")
        text = article(image="https://evil.test/racesets.png")
        with self.assertRaises(rt.SourceError):
            rt.chart_links(SPAIN, PAGE, text)

    def test_wrong_image_types_and_corruption_are_errors(self):
        for data in (b"<html>Login page</html>" * 5, b"%PDF-1.7" * 10, b"<svg/>" * 20,
                     "not bytes", png(width=1, height=1), png()[:100]):
            with self.subTest(data=str(data)[:50]), self.assertRaises(rt.SourceError):
                rt.raster_info(data)
        self.responses[IMAGE] = b"<html>not an image</html>"
        result = self.collect()
        self.assertEqual(result["status"]["state"], "error")
        self.assertEqual(result["snapshot"], {})
        self.assertFalse((self.data / "spain/race_tyres.json").exists())

    def test_jpeg_and_webp_decoding(self):
        from PIL import Image
        jpeg = io.BytesIO()
        with Image.open(io.BytesIO(png())) as image:
            image.save(jpeg, format="JPEG")
        self.assertEqual(rt.raster_info(jpeg.getvalue()), ("jpg", 1080, 608))
        # Real public WebP artifacts are checked when present; no network needed.
        for path in (rt.ROOT / "assets_src").glob("race-tyres-2026-*.webp"):
            with self.subTest(path=path.name):
                self.assertEqual(rt.raster_info(path.read_bytes()), ("webp", 1080, 608))

    def test_no_cache_context_is_readonly_and_unknown_not_zero(self):
        with patch.object(rt, "fetch", side_effect=AssertionError("No network")), \
                patch.object(rt, "_atomic", side_effect=AssertionError("No build writes")):
            result = rt.context(SPAIN)
        self.assertEqual(result["snapshot"], {})
        self.assertEqual(result["status"]["state"], "not_found")
        self.assertNotIn("drivers", result)
        self.assertFalse((self.data / "spain").exists())

    def test_cached_context_is_readonly_and_does_not_require_decoder_or_timing(self):
        first = self.collect()["snapshot"]
        with patch.object(rt, "fetch", side_effect=AssertionError("No network")), \
                patch.object(rt, "_atomic", side_effect=AssertionError("No writes")), \
                patch.dict("sys.modules", {"pymupdf": None, "PIL": None, "fastf1": None}):
            self.assertEqual(rt.context(SPAIN)["snapshot"], first)

    def test_explicit_root_isolates_both_data_and_assets_without_writes(self):
        snapshot = self.collect()["snapshot"]
        root = self.directory / "offline-repository"
        (root / "data/spain").mkdir(parents=True)
        (root / "assets_src").mkdir()
        for name in ("race_tyres.json", "race_tyres_status.json"):
            (root / "data/spain" / name).write_bytes((self.data / "spain" / name).read_bytes())
        asset = snapshot["chart"]["asset"]
        (root / "assets_src" / asset).write_bytes((self.assets / asset).read_bytes())
        with patch.object(rt, "DATA_DIR", self.directory / "wrong-data"), \
                patch.object(rt, "ASSET_DIR", self.directory / "wrong-assets"), \
                patch.object(rt, "fetch", side_effect=AssertionError("No network")), \
                patch.object(rt, "_atomic", side_effect=AssertionError("No writes")):
            for supplied_root in (root, str(root)):
                with self.subTest(root=supplied_root):
                    result = rt.context(SPAIN, root=supplied_root)
                    self.assertEqual(result["snapshot"], snapshot)
                    self.assertEqual(result["status"]["state"], "available")
            (root / "assets_src" / asset).unlink()
            result = rt.context(SPAIN, root=root)
            self.assertEqual(result["snapshot"], {})
            self.assertIn("cached chart asset", result["status"]["error"])
        missing = self.directory / "nonexistent"
        self.assertEqual(rt.context(SPAIN, root=missing)["status"]["state"], "not_found")
        self.assertFalse(missing.exists())

    def test_cross_event_year_date_cache_is_hidden_with_warning(self):
        valid = self.collect()["snapshot"]
        for key, value in (("year", 2025), ("year", True), ("gp", "italy"),
                           ("race_date", "2026-09-06")):
            with self.subTest(key=key, value=value):
                self.save("race_tyres.json", {**valid, key: value})
                result = rt.context(SPAIN)
                self.assertEqual(result["snapshot"], {})
                self.assertEqual(result["status"]["state"], "error")
                self.assertTrue(result["status"]["error"])

    def test_invalid_cache_objects_do_not_crash_or_show_wrong_data(self):
        valid = self.collect()["snapshot"]
        bad = [[], None, True, {"year": 2026}]
        for field, value in (("width", True), ("height", "608"), ("asset", "../secret.png"),
                             ("url", "https://evil.test/image.png"), ("sha256", "wrong")):
            obj = copy.deepcopy(valid)
            obj["chart"][field] = value
            bad.append(obj)
        for obj in bad:
            with self.subTest(obj=obj):
                self.save("race_tyres.json", obj)
                result = rt.context(SPAIN)
                self.assertEqual(result["snapshot"], {})
                self.assertEqual(result["status"]["state"], "error")
        self.save("race_tyres.json", valid)
        (self.assets / valid["chart"]["asset"]).write_bytes(png(1))
        self.assertIn("hash mismatch", rt.context(SPAIN)["status"]["error"])

    def test_invalid_status_surfaces_warning(self):
        for obj in ([], None, {}, {"state": "available", "attempts": "bad"},
                    {"state": [], "attempts": []}):
            with self.subTest(obj=obj):
                self.save("race_tyres_status.json", obj)
                result = rt.context(SPAIN)
                self.assertEqual(result["status"]["state"], "error")
                self.assertIn("Invalid cached", result["status"]["error"])

    def test_network_size_bound_and_http_access_status(self):
        class Response:
            headers = {"Content-Length": str(rt.MAX_IMAGE + 1)}
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def geturl(self):
                return IMAGE
            def read(self, limit):
                raise AssertionError("Oversized declared response must not be read")
        with patch("urllib.request.OpenerDirector.open", return_value=Response()):
            with self.assertRaisesRegex(rt.SourceError, "size limit"):
                rt.fetch(IMAGE, image=True)
        error = urllib.error.HTTPError(PAGE, 403, "Forbidden", {}, None)
        with patch("urllib.request.OpenerDirector.open", side_effect=error):
            with self.assertRaises(rt.AccessRestricted):
                rt.fetch(PAGE)
        error.close()


if __name__ == "__main__":
    unittest.main()
