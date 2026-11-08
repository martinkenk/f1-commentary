"""Offline content parity checks: verified event evidence, not borrowed GP facts."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from unittest.mock import mock_open, patch

import build
import content_azerbaijan
import content_bahrain
import content_brazil
import content_generic
import content_italy
import content_mexico
import content_singapore
import content_spain
import f1lib


class GPParityTests(unittest.TestCase):
    def setUp(self):
        self.contexts = {
            ctx["dir"]: ctx for ctx in build.season_gps()
            if ctx["dir"] in ("italy", "spain", "bahrain", "singapore", "brazil", "mexico")
        }
        for slug, ctx in self.contexts.items():
            ctx.update(status="past", results=[], extra={}, weather={}, weather_ok=False)
        self.env = {
            "schedule_rows": lambda: "SCHEDULE_ROWS",
            "weather_cards": lambda: "WEATHER_CARDS",
            "weather": {}, "weather_ok": False,
        }

    def italy(self):
        return content_italy.build_pages(self.contexts["italy"], self.env)

    def spain(self):
        return content_spain.build_pages(self.contexts["spain"], self.env)

    def bahrain(self):
        ctx = self.contexts["bahrain"].copy()
        ctx["status"] = "future"
        return content_bahrain.build_pages(ctx, self.env)

    def singapore(self):
        ctx = self.contexts["singapore"].copy()
        ctx["status"] = "live"
        return content_singapore.build_pages(ctx, self.env)

    def test_mexico_post_race_replaces_stale_event_page_placeholders(self):
        self.assertIs(build.BESPOKE["mexico"], content_mexico.build_pages)
        ctx = dict(
            self.contexts["mexico"],
            status="past",
            results=[{"label": "Race"}],
        )
        pages = content_mexico.build_pages(ctx, self.env)
        for slug in ("teams", "notes"):
            self.assertNotIn("awaiting a verified update", pages[slug]["body"])
        moments = pages["moments"]["body"]
        self.assertNotIn("A curated moments list", moments)
        for year, source in (
            ("2019", content_mexico.MOMENT_2019),
            ("2021", content_mexico.MOMENT_2021),
            ("2024", content_mexico.MOMENT_2024),
        ):
            self.assertIn(year, moments)
            self.assertIn(source, moments)
        self.assertIn("Antonelli", pages["teams"]["body"])
        self.assertIn("630–504", pages["teams"]["body"])
        self.assertIn("Piastri's ten-second", pages["teams"]["body"])
        self.assertIn("Pirelli", pages["teams"]["body"])
        self.assertIn("0.799 seconds", pages["notes"]["body"])
        self.assertIn("final classification", pages["notes"]["body"])
        self.assertIn(content_mexico.RACE_RESULT, pages["notes"]["body"])
        self.assertIn("Turn 12 entry to the", pages["notes"]["body"])
        self.assertIn("Turn 14 apex", pages["notes"]["body"])
        self.assertIn("one and four", pages["notes"]["body"])
        for source in (
            content_mexico.FIA_VERSTAPPEN_LAWSON_DECISION,
            content_mexico.FIA_LAWSON_VERSTAPPEN_DECISION,
            content_mexico.FIA_VERSTAPPEN_LAWSON_SUMMONS,
            content_mexico.FIA_LAWSON_VERSTAPPEN_SUMMONS,
        ):
            self.assertIn(source, pages["notes"]["body"])

        rookies = pages["rookies"]["body"]
        self.assertNotIn("awaiting a verified update", rookies)
        for driver in (
            "Frederik Vesti", "Ayumu Iwasa", "Nikola Tsolov",
            "Gabriele Mini", "Leonardo Fornaroli", "Jak Crawford",
            "Luke Browning", "Freddie Slater", "Colton Herta",
        ):
            self.assertIn(driver, rookies)
        self.assertIn("George Russell", rookies)
        self.assertIn("Valtteri Bottas", rookies)
        self.assertIn(content_mexico.FP1_RESULT, rookies)
        self.assertIn(content_mexico.RACE_RESULT, rookies)

        upgrades = pages["upgrades"]["body"]
        self.assertIn("9", upgrades)
        self.assertIn("6", upgrades)
        self.assertIn("5", upgrades)
        self.assertIn(content_mexico.FIA_CAR_PRESENTATION, upgrades)
        self.assertNotIn("Published source; event-specific interpretation pending", upgrades)
        self.assertNotIn("FIA car presentation submissions for this round: awaiting", upgrades)
        for team in ("McLaren", "Mercedes", "Red Bull", "Ferrari", "Williams",
                     "Racing Bulls", "Aston Martin", "Haas", "Audi", "Alpine", "Cadillac"):
            self.assertIn(team, upgrades)
        self.assertIn("No updates submitted", upgrades)
        self.assertIn("Larger cooling-exit louvres", upgrades)
        self.assertIn("rear brake-duct deflector", upgrades)
        for team, page, updates in content_mexico.UPGRADE_SUBMISSIONS:
            pages_to_show = (page, page + 1) if updates else (page,)
            self.assertIn(f'href="#upgrade-submission-{page}" data-document-reader', upgrades)
            for source_page in pages_to_show:
                asset = (
                    f"{content_mexico.FIA_CAR_PRESENTATION_ASSET}"
                    f"-p{source_page}.png"
                )
                self.assertIn(f"../assets/{asset}", upgrades)
                self.assertTrue((Path(__file__).parent / "assets_src" / asset).is_file())

        powerunit = pages["powerunit"]["body"]
        self.assertNotIn("Published source; event-specific interpretation pending", powerunit)
        self.assertIn(content_mexico.FIA_POWER_UNIT, powerunit)
        self.assertIn(content_mexico.FIA_PU_NEW_ELEMENTS, powerunit)
        self.assertIn(content_mexico.FIA_PU_USAGE, powerunit)
        self.assertIn(content_mexico.FIA_BOTTAS_PU_PENALTY, powerunit)
        self.assertIn("8.5 / 9.0 MJ", powerunit)
        self.assertIn("2,101 m", powerunit)
        self.assertIn("100 kW/s", powerunit)
        self.assertIn("3,871 m", powerunit)
        self.assertIn("4,051 m", powerunit)
        self.assertIn("250 km/h", powerunit)
        self.assertIn("fifth ICE and turbocharger", powerunit)
        self.assertIn("fourth MGU-K, energy store and control electronics", powerunit)
        self.assertIn("50-place drop", powerunit)
        self.assertIn("Straight Mode markings are active-aero zones", powerunit)
        for asset in (
            f"{content_mexico.FIA_POWER_UNIT_ASSET}-p2.png",
            f"{content_mexico.FIA_PU_NEW_ELEMENTS_ASSET}-p2.png",
            f"{content_mexico.FIA_PU_NEW_ELEMENTS_ASSET}-p3.png",
            f"{content_mexico.FIA_PU_USAGE_ASSET}-p2.png",
        ):
            self.assertIn(f"../assets/{asset}", powerunit)
            self.assertTrue((Path(__file__).parent / "assets_src" / asset).is_file())
        review = json.loads(
            (Path(__file__).parent / "data/mexico/coverage_review.json").read_text()
        )
        media = json.loads(
            (Path(__file__).parent / "data/mexico/fia_media.json").read_text()
        )
        media_hashes = {doc["url"]: doc["sha256"] for doc in media["documents"]}
        for source in (
            content_mexico.FIA_CAR_PRESENTATION,
            content_mexico.FIA_POWER_UNIT,
            content_mexico.FIA_PU_NEW_ELEMENTS,
            content_mexico.FIA_PU_USAGE,
            content_mexico.FIA_BOTTAS_PU_PENALTY,
        ):
            self.assertEqual(review["fia_sha256"].get(source), media_hashes[source])

        future = content_mexico.build_pages(
            dict(ctx, status="future", results=[]), self.env
        )
        self.assertIn("awaiting a verified update", future["teams"]["body"])
        self.assertIn("awaiting a verified update", future["notes"]["body"])
        self.assertIn("awaiting a verified update", future["rookies"]["body"])
        self.assertIn("awaiting a verified update", future["upgrades"]["body"])
        self.assertIn("awaiting a verified update", future["powerunit"]["body"])

    def test_brazil_published_lineup_replaces_pending_placeholders(self):
        ctx = dict(self.contexts["brazil"], status="live")
        self.assertIs(build.BESPOKE["brazil"], content_brazil.build_pages)
        pages = content_brazil.build_pages(ctx, self.env)
        for slug in ("rookies", "overview", "teams", "notes"):
            self.assertIn("Rafael Camara", pages[slug]["body"])
            for name in (
                "Leonardo Fornaroli", "Oscar Piastri", "Dino Beganovic",
                "Charles Leclerc", "Luke Browning", "Carlos Sainz",
                "Freddie Slater", "Nico Hulkenberg", "Gabriele Mini",
                "Pierre Gasly", "Colton Herta", "Sergio Perez",
            ):
                self.assertIn(name, pages[slug]["body"])
        self.assertNotIn("awaiting a verified update", pages["rookies"]["body"])
        self.assertIn("whole Sao Paulo weekend", pages["rookies"]["body"])
        self.assertIn("picked up his final Super Licence point", pages["rookies"]["body"])
        self.assertIn("does not confirm a 2027 seat", pages["rookies"]["body"])
        self.assertNotIn("Herta needs at least 100 km", pages["rookies"]["body"])
        self.assertIn(content_brazil.FP1_LINEUP, pages["rookies"]["body"])
        self.assertIn(content_brazil.FP1_RESULT, pages["rookies"]["body"])
        self.assertIn(content_brazil.THE_RACE_FP1, pages["rookies"]["body"])
        self.assertIn("100 km", pages["rookies"]["body"])

    def test_brazil_notes_link_to_published_session_coverage(self):
        body = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )["notes"]["body"]
        self.assertIn("Official classifications are published for FP1, FP2, FP3 and Qualifying", body)
        self.assertIn('href="results.html">Results</a>', body)
        self.assertIn('href="news.html">Weekend News</a>', body)
        self.assertNotIn("Session-by-session commentary notes: awaiting", body)

    def test_brazil_post_qualifying_strategy_is_surfaced_on_overview_and_notes(self):
        pages = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )
        for slug in ("overview", "notes"):
            body = " ".join(pages[slug]["body"].split())
            self.assertIn("two Soft", body)
            self.assertIn("one Medium", body)
            self.assertIn("three seconds", body)
            self.assertIn("ten seconds slower", body)
            self.assertIn("not a live update", body)
            self.assertIn("laps 17–23 and 42–48", body)
            self.assertIn(content_brazil.CCM_BRAZIL_STRATEGY, body)
            self.assertIn(content_brazil.PIRELLI_POST_QUALI_STRATEGY, body)

    def test_brazil_revised_power_unit_sheet_and_curfew_are_interpreted(self):
        pages = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )
        powerunit = pages["powerunit"]["body"]
        self.assertIn("240 km/h", powerunit)
        self.assertIn("2870–2970 m", powerunit)
        self.assertIn("3250 m on timing loop L17", powerunit)
        self.assertIn("3411 m on L18", powerunit)
        self.assertNotIn("3250 m (TBC)", powerunit)
        self.assertIn(
            "fia-brazil-8181546ca72d-ac646baaf86f1a4c-p2.png", powerunit
        )
        self.assertIn("power_unit_information_v2.pdf#page=2", powerunit)
        schedule = pages["schedule"]["body"]
        self.assertIn("Oracle Red Bull Racing and Aston Martin", schedule)
        self.assertIn(
            "Oracle Red Bull Racing's second and Aston Martin's third", schedule
        )
        self.assertIn("no action should be taken", schedule)
        self.assertIn("curfew_0.pdf", schedule)
        self.assertIn("FIA Document 47", schedule)
        self.assertIn("19:27 local time", schedule)
        self.assertIn("covers-on_time.pdf", schedule)
        self.assertIn(
            "FIA Competition Notes, Document 2, version 5 issue A",
            pages["tyres"]["body"],
        )
        self.assertNotIn("00:16 UTC", pages["tyres"]["body"])
        self.assertIn("FIA Technical Delegate Document 49", powerunit)
        self.assertIn("all listed items complied", powerunit)
        self.assertIn("fp3_and_qualifying_scrutineering.pdf", powerunit)

    def test_brazil_russell_penalty_is_attributed_and_not_mistaken_for_upgrade(self):
        body = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )["overview"]["body"]
        body = " ".join(body.split())
        self.assertIn("five-place drop", body)
        self.assertIn(content_brazil.RUSSELL_PENALTY, body)
        self.assertIn(content_brazil.FIA_NEW_PU_URL, body)
        self.assertIn(content_brazil.RUSSELL_FIA_PENALTY, body)
        self.assertIn("sixth against four allowed", body)
        self.assertIn("season-to-date usage report (Document 8)", body)
        self.assertIn("not an event-specific parts declaration", body)
        self.assertIn("do not establish whether the planned ADUO", body)
        self.assertIn(content_brazil.HAMILTON_F1_UPDATE, body)
        self.assertIn(content_brazil.FIA_HAMILTON_NEW_PU_URL, body)
        self.assertIn(content_brazil.FIA_HAMILTON_ADDITIONAL_PENALTY_URL, body)
        self.assertIn("further 65-place drop", body)
        self.assertIn("75-place penalty", body)
        self.assertIn("Car 44 qualified 11th", body)
        self.assertIn("official Formula1.com Starting Grid now also lists him 20th", body)
        self.assertNotIn("that position is not confirmed", body)
        self.assertNotIn("check the FIA event page", body)
        self.assertNotIn("14:00 UTC targeted FIA check", body)
        self.assertNotIn("12:46 UTC", body)
        powerunit = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )["powerunit"]["body"]
        self.assertIn("brazil-new-pu-elements", powerunit)
        self.assertIn(content_brazil.FIA_NEW_PU_ASSET, powerunit)
        self.assertIn("Rafael Câmara", powerunit)
        self.assertIn(content_brazil.RUSSELL_FIA_PENALTY, powerunit)
        self.assertIn("Document 15 imposes a five-place", powerunit)
        self.assertIn(content_brazil.HAMILTON_F1_UPDATE, powerunit)
        self.assertIn(content_brazil.FIA_HAMILTON_NEW_PU_URL, powerunit)
        self.assertIn("Sixth of four; not compliant", powerunit)
        self.assertIn("Seventh of six; not compliant", powerunit)
        self.assertIn("FIA document</th>", powerunit)
        self.assertIn("additional 65-place penalty", powerunit)
        self.assertNotIn("check the FIA event page", powerunit)
        notes = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )["notes"]["body"]
        notes = " ".join(notes.split())
        self.assertIn(content_brazil.FIA_HAMILTON_ADDITIONAL_PENALTY_URL, notes)
        self.assertIn("75 places cumulatively", notes)
        self.assertIn("penalty-adjusted official Starting Grid", notes)
        self.assertNotIn("still-pending official Starting Grid", notes)
        schedule = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )["schedule"]["body"]
        self.assertIn("lists all 22 qualifiers", schedule)
        self.assertIn("official Starting Grid now lists all 22 entrants", schedule)
        self.assertIn("provisional grid agrees row by row", schedule)
        self.assertIn("FIA Document 50, final classification p. 2", schedule)
        self.assertIn("FIA Document 51, provisional Starting Grid p. 2", schedule)
        self.assertNotIn("Starting Grid page still says", schedule)
        self.assertNotIn("No replacement start time", schedule)
        self.assertIn(content_brazil.F1_STARTING_GRID, schedule)
        self.assertIn(content_brazil.THE_RACE_PROVISIONAL_GRID, schedule)

    def test_brazil_double_yellow_document_is_interpreted_in_briefings(self):
        pages = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )
        for slug in ("overview", "notes"):
            body = pages[slug]["body"]
            normalized = " ".join(body.split())
            for name in ("Franco Colapinto", "Alexander Albon", "Luke Browning",
                         "Rafael Câmara", "Dino Beganovic"):
                self.assertIn(name, normalized)
            self.assertIn(
                "not a race penalty or a revised FP1 classification", normalized
            )
            self.assertIn(content_brazil.FIA_FP1_DOUBLE_YELLOW_URL, normalized)

    def test_brazil_qualifying_grid_and_strategy_are_distinguished(self):
        pages = content_brazil.build_pages(
            dict(self.contexts["brazil"], status="live"), self.env
        )
        schedule = " ".join(pages["schedule"]["body"].split())
        self.assertIn("Lando Norris took pole in 1:27.470", schedule)
        self.assertIn("earlier post-penalty order was provisional", schedule)
        self.assertIn("Do not substitute starting positions for qualifying results", schedule)
        self.assertNotIn("Qualifying and Starting Grid pages both returned", schedule)

        notes = " ".join(pages["notes"]["body"].split())
        self.assertIn("eight deleted Qualifying lap-time entries", notes)
        self.assertIn("Stroll's 1:42.680 lap", notes)
        self.assertIn(content_brazil.FIA_QUALIFYING_DELETIONS_URL, notes)
        self.assertIn(content_brazil.FIA_STROLL_DOUBLE_YELLOW_URL, notes)

        tyres = " ".join(pages["tyres"]["body"].split())
        self.assertIn("Post-qualifying race-strategy assessment", tyres)
        self.assertIn("two stints on Soft and one on Medium", tyres)
        self.assertIn("about three seconds quicker", tyres)
        self.assertIn("around ten seconds slower", tyres)
        self.assertNotIn("Long-run degradation data: awaiting a verified update.", tyres)
        self.assertIn("no graining and similar abrasion", tyres)
        self.assertIn("No driver-by-driver practice long-run table is transcribed here.", tyres)
        self.assertIn("Pirelli report itself gives no lap windows", tyres)
        self.assertIn("Soft → Medium → Soft", tyres)
        self.assertIn("23–29; 50–56", tyres)
        self.assertIn("16–22; 44–50", tyres)
        self.assertIn("28–34", tyres)
        self.assertIn(content_brazil.CCM_BRAZIL_STRATEGY, tyres)
        self.assertIn(content_brazil.BRAZIL_STRATEGY_ASSET, tyres)
        self.assertTrue(
            (Path(build.ROOT) / "assets_src" / content_brazil.BRAZIL_STRATEGY_ASSET).is_file()
        )
        self.assertIn("60% when published", tyres)
        self.assertNotIn("00:29 UTC", tyres)
        self.assertNotIn("00:16 UTC", tyres)
        self.assertNotIn("pre-qualifying assessment", tyres)
        self.assertIn(content_brazil.PIRELLI_FP2_STRATEGY, tyres)
        self.assertIn(content_brazil.PIRELLI_POST_QUALI_STRATEGY, tyres)
        self.assertIn("lists new sets by compound only", tyres)
        self.assertIn("no driver-by-driver used figures are transcribed", tyres)
        self.assertNotIn("used-slick counts are zero", tyres)
        self.assertNotIn("not a strategy-window", tyres)

    def test_brazil_published_technical_sources_replace_generic_pending_copy(self):
        ctx = dict(self.contexts["brazil"], status="live")
        pages = content_brazil.build_pages(ctx, self.env)
        tyres = pages["tyres"]["body"]
        self.assertIn("brazil_pirelli_tyres_2026.webp", tyres)
        self.assertIn("brazil-tyre-limits", tyres)
        self.assertNotIn("Pirelli's compound allocation:", tyres)
        self.assertIn("tyre-preview-img", tyres)
        self.assertIn("brazil-energy-limits", pages["powerunit"]["body"])
        self.assertNotIn("once it is issued", pages["powerunit"]["body"])
        self.assertIn("Two Straight Mode zones, one Overtake activation", pages["circuit"]["body"])
        upgrades = pages["upgrades"]["body"]
        upgrades_text = " ".join(upgrades.split())
        self.assertIn("14:00 and 14:29 UTC listing checks", upgrades_text)
        self.assertIn("15:32 CET", upgrades_text)
        self.assertIn("FIA Document 12", upgrades_text)
        self.assertIn("lists four performance-motivated items", upgrades_text)
        self.assertIn("other ten teams each submitted an explicit nil return", upgrades_text)
        self.assertIn("Performance - Flow Conditioning", upgrades_text)
        self.assertIn("Performance - Local Load", upgrades_text)
        self.assertNotIn("If the filing appears", upgrades_text)
        for team, page, items in content_brazil.UPGRADE_SUBMISSIONS:
            self.assertIn(f'href="#upgrade-submission-{page}" data-document-reader', upgrades)
            self.assertIn(f'<details id="upgrade-submission-{page}">', upgrades)
            for number in ([page, page + 1] if items else [page]):
                asset = f"{content_brazil.FIA_UPGRADES_ASSET}-p{number}.png"
                self.assertIn(asset, upgrades)
                self.assertTrue((Path(__file__).parent / "assets_src" / asset).is_file())
                self.assertIn(content_brazil.FIA_UPGRADES_URL + f"#page={number}", upgrades)
        self.assertEqual(upgrades.count('<details id="upgrade-submission-'), 11)
        self.assertNotIn("12:46 UTC", pages["upgrades"]["body"])
        self.assertNotIn("Review at 06:05 UTC", pages["upgrades"]["body"])
        powerunit = pages["powerunit"]["body"]
        usage = re.search(
            r'<table class="data compact" id="brazil-pu-usage">(.*?)</table>',
            powerunit,
            re.S,
        )
        self.assertIsNotNone(usage)
        self.assertEqual(len(re.findall(r"<tr>", usage.group(1))), 23)
        self.assertIn("<td>63</td><td>George Russell</td><td>5</td><td>5</td><td>5</td>"
                      "<td>4</td><td>4</td><td>4</td><td>5</td>", usage.group(1))
        self.assertIn("pu_elements_used_per_driver_up_to_now.pdf#page=2", powerunit)
        for slug in ("tyres", "powerunit", "circuit"):
            body = pages[slug]["body"]
            for asset in re.findall(r'src="\.\./assets/([^"]+)"', body):
                self.assertTrue((Path(build.ROOT) / "assets_src" / asset).is_file(), asset)
            media = f1lib.render_fia_media(ctx, slug, body)
            for asset in re.findall(r'src="\.\./assets/(fia-[^"]+)"', body):
                self.assertNotIn(asset, media)

    def test_mexico_published_pirelli_preview_replaces_pending_compound_copy(self):
        body = content_generic.build_pages(
            self.contexts["mexico"], self.env
        )["tyres"]["body"]
        self.assertIn("C3 Hard / C4 Medium / C5 Soft", body)
        self.assertIn("mexico_pirelli_tyres_2026.webp", body)
        self.assertIn(
            "what-tyres-will-the-teams-and-drivers-have-for-the-2026-mexico-city-grand-prix",
            body,
        )
        self.assertIn("Full-resolution original", body)
        self.assertNotIn("Pirelli's compound allocation:", body)
        self.assertTrue(
            (Path(build.ROOT) / "assets_src" / "mexico_pirelli_tyres_2026.webp").is_file()
        )

    def test_past_generic_tyre_page_does_not_keep_friday_pending_placeholder(self):
        future_ctx = dict(self.contexts["mexico"], status="future")
        future = content_generic.build_pages(future_ctx, self.env)["tyres"]["body"]
        self.assertIn("Long-run degradation data: awaiting a verified update.", future)
        past = content_generic.build_pages(
            dict(self.contexts["mexico"], status="past"), self.env
        )["tyres"]["body"]
        self.assertNotIn("Long-run degradation data: awaiting a verified update.", past)
        self.assertIn("No source-reviewed stint-by-stint degradation transcription", past)
        self.assertIn("not stint data", past)

    def test_all_seventeen_surfaces_are_authored_or_engine_provided(self):
        engine_pages = {"results", "news", "h2h", "reliability", "penalties"}
        for slug, pages in (("italy", self.italy()), ("spain", self.spain()),
                            ("bahrain", self.bahrain())):
            nav = {row[0] for row in self.contexts[slug]["nav"]}
            self.assertEqual(len(nav), 17)
            self.assertFalse(nav - set(pages) - engine_pages)
            self.assertTrue(all(page["body"].strip() for page in pages.values()))

    def test_standings_subtitle_tracks_event_phase(self):
        future_ctx = dict(self.contexts["bahrain"], status="future", results=[])
        future = content_generic.build_pages(future_ctx, self.env)
        completed_ctx = dict(
            future_ctx, status="past", results=[{"label": "Race"}]
        )
        completed = content_generic.build_pages(completed_ctx, self.env)
        live_ctx = dict(future_ctx, status="live")
        live = content_generic.build_pages(live_ctx, self.env)
        self.assertIn("ahead of this round", future["standings"]["sub"])
        self.assertIn(
            "before this Grand Prix's Race classification",
            live["standings"]["sub"],
        )
        self.assertIn("after the completed Grand Prix", completed["standings"]["sub"])

    def test_sepang_pirelli_preview_is_full_and_source_linked(self):
        body = self.bahrain()["tyres"]["body"]
        self.assertIn("../assets/bahrain_pirelli_tyres_2026.webp", body)
        self.assertIn("4vcrMxYY9DWg7PwyiNMrEV", body)
        self.assertIn("Official Pirelli event-preview graphic", body)
        self.assertTrue(
            (Path(build.ROOT) / "assets_src" / "bahrain_pirelli_tyres_2026.webp").is_file()
        )

    def test_singapore_uses_verified_event_specific_coverage(self):
        self.assertIs(build.BESPOKE["singapore"], content_singapore.build_pages)
        pages = self.singapore()
        tyres = pages["tyres"]["body"]
        self.assertIn("../assets/singapore_pirelli_tyres_2026.webp", tyres)
        self.assertIn("4rG7uAn2d6vveGmRlkE5RM", tyres)
        self.assertIn("C3 / C4 / C5", tyres)
        self.assertTrue(
            (Path(build.ROOT) / "assets_src" / "singapore_pirelli_tyres_2026.webp").is_file()
        )

        self.assertIn("Heat Hazard", pages["overview"]["body"])
        self.assertIn("Heat Hazard", pages["schedule"]["body"])
        self.assertIn("Heat Hazard", pages["notes"]["body"])
        circuit = pages["circuit"]["body"]
        self.assertIn("five Straight Mode zones", circuit)
        self.assertIn("30 m after Turn 17", circuit)
        self.assertIn("A5", circuit)

        upgrades = pages["upgrades"]["body"]
        for team in ("McLaren", "Mercedes", "Red Bull"):
            self.assertIn(team, upgrades)
        self.assertIn("No updates submitted", upgrades)
        self.assertNotIn("will be populated", upgrades)

        overview = pages["overview"]["body"]
        self.assertIn("George Russell", overview)
        self.assertIn("1:32.274", overview)

    def test_singapore_figures_fit_screen_and_support_zoom(self):
        pages = self.singapore()
        for name in ("tyres", "upgrades", "circuit", "powerunit"):
            figures = re.findall(r"<figure.*?</figure>", pages[name]["body"], re.S)
            self.assertTrue(figures, name)
            for figure in figures:
                if "fia-singapore-" not in figure and "singapore_pirelli_" not in figure:
                    continue
                self.assertIn('class="circuit-fig"', figure)
                self.assertIn('class="circuit-img tyre-preview-img"', figure)
                self.assertIn('onclick="zoomImg(this)"', figure)
                self.assertIn('role="button" tabindex="0"', figure)
                self.assertIn("event.key==='Enter'", figure)
                self.assertIn("event.key===' '", figure)
                self.assertIn("Click to zoom / full screen.", figure)

    def test_sepang_carries_colapinto_sanction_with_original_fia_reader(self):
        pages = self.bahrain()
        article = content_bahrain.F1_PENALTY_ARTICLE
        pdf = content_bahrain.FIA_DOC_66
        for page in ("overview", "notes", "penalties"):
            self.assertIn("five-place drop", pages[page]["body"])
            self.assertIn(article, pages[page]["body"])
            self.assertIn(pdf, pages[page]["body"])
        penalty = pages["penalties"]["body"]
        row = next(
            match.group(1)
            for match in re.finditer(r"<tr>(.*?)</tr>", penalty, re.S)
            if ">Azerbaijan Doc 66</a>" in match.group(1)
        )
        self.assertIn("10-second time penalty converted to five grid places", row)
        self.assertIn("Turn 1 collision with team-mate Pierre Gasly", row)
        self.assertNotIn("Overtaking under yellow flags", row)
        self.assertIn('<details class="penalty-document"', row)
        self.assertIn("data-document-reader", row)
        self.assertIn("fia-azerbaijan-b7d2f0775263-9d5a9ffc644dfc50-p1.png", row)
        self.assertIn("fia-azerbaijan-b7d2f0775263-9d5a9ffc644dfc50-p2.png", row)
        self.assertIn("Qualifying and the official Bahrain starting grid are still",
                      pages["penalties"]["body"])

    def test_sepang_team_watch_replaces_placeholder_with_dated_official_form(self):
        page = self.bahrain()["teams"]
        body = page["body"]
        self.assertIn("Baku to Sepang: team-by-team watch", body)
        self.assertIn(content_bahrain.F1_AZERBAIJAN_RESULT, body)
        self.assertIn("one-race form, not season totals", body)
        self.assertNotIn("Team-by-team weekend storylines: awaiting", body)
        for team in (
            "Mercedes", "Red Bull Racing", "Ferrari", "McLaren", "Racing Bulls",
            "Haas F1 Team", "Williams", "Audi", "BWT Alpine F1 Team", "Cadillac",
            "Aston Martin Aramco F1 Team",
        ):
            self.assertIn(f"<th scope=\"row\">{team}</th>", body)
        self.assertIn("Colapinto DNF; Gasly DNF", body)
        self.assertIn("confirmed five-place grid drop", body)

    def test_cross_event_penalty_does_not_hide_same_number_local_document(self):
        ctx = self.contexts["bahrain"]
        local = dict(
            doc="Doc 66", no="1", driver="Local driver", team="Local team",
            session="Race", fact="Local matter", outcome="Local ruling",
            kind="warning", source_url="https://www.fia.com/system/files/local.pdf",
        )
        carryover = dict(
            doc="Azerbaijan Doc 66", source_event="azerbaijan", no="43",
            driver="Franco Colapinto", session="Race", fact="Carry-over",
            outcome="Five grid places", kind="penalty",
            source_url=content_bahrain.FIA_DOC_66,
        )
        with patch.object(f1lib, "_load_auto", return_value=[local]):
            body = f1lib.render_penalties(ctx, [carryover])
        self.assertIn("Azerbaijan Doc 66", body)
        self.assertIn("Local driver", body)
        self.assertIn("Local ruling", body)

    def test_completed_italy_leads_with_sourced_race_chronology(self):
        pages = self.italy()
        self.assertIn("Completed 6 September", pages["overview"]["kicker"])
        for slug in ("overview", "notes", "teams"):
            body = pages[slug]["body"]
            self.assertIn("6 September: Antonelli wins from P19", body)
            self.assertIn(content_italy.RACE_REPORT_URL, body)
            self.assertLess(body.index("Qualifying and grid"), body.index("Opening laps"))
            self.assertLess(body.index("Opening laps"), body.index("Strategy split"))
            self.assertLess(body.index("Strategy split"), body.index("Finish:"))
        self.assertIn("Pre-race briefing archive", pages["overview"]["body"])
        self.assertIn("Antonelli wins at Monza from P19", pages["news"]["body"])
        self.assertNotIn("Session-by-session commentary notes: awaiting", pages["notes"]["body"])

    def test_italy_practice_data_and_actual_strategy_replace_stale_placeholder(self):
        body = self.italy()["tyres"]["body"]
        self.assertIn('href="results.html">FP2 clean-lap long runs', body)
        self.assertIn("not a fitted degradation curve", body)
        self.assertIn("fresh mediums under the later VSC", body)
        self.assertNotIn("Long-run degradation data: awaiting", body)
        self.assertNotIn("every driver must use both compounds", body)
        self.assertNotIn("top-10 runners who start on their Q2 time", body)
        self.assertIn("no requirement for top-ten qualifiers", body)
        self.assertNotIn("Tyre sets available for the race (official)", body)
        self.assertFalse(hasattr(content_italy, "TYRES_AVAILABLE_FOR_RACE"))

    def test_italian_home_win_history_is_not_frozen_before_race(self):
        pages = self.italy()
        for slug in ("overview", "facts", "moments"):
            self.assertNotIn("No Italian driver has won", pages[slug]["body"])
            self.assertNotIn("No Italian has won", pages[slug]["body"])
        self.assertIn("2026 — Antonelli wins", pages["moments"]["body"])
        self.assertIn("2021–2025", pages["facts"]["body"])
        self.assertIn("Current-grid track-history", pages["facts"]["body"])

    def test_automatic_comparisons_and_pit_data_are_preserved(self):
        with patch.object(content_italy, "auto_h2h", return_value="EVENT_H2H"), \
             patch.object(content_italy, "render_reliability", return_value="PIT_DATA") as pits:
            pages = self.italy()
        self.assertIn("EVENT_H2H", pages["h2h"]["body"])
        self.assertNotIn("No audited season-long", pages["h2h"]["body"])
        self.assertEqual(pages["reliability"]["body"], "PIT_DATA")
        self.assertIn("suspected car damage", pits.call_args.kwargs["intro_html"])
        self.assertIn("not establish medical clearance", pits.call_args.kwargs["intro_html"])

    def test_madrid_confirmed_replacements_are_not_pending(self):
        pages = self.spain()
        for slug in ("overview", "notes", "rookies", "teams"):
            self.assertIn("Liam Lawson", pages[slug]["body"])
            self.assertIn("Yuki Tsunoda", pages[slug]["body"])
            self.assertIn(content_spain.LINEUP_URL, pages[slug]["body"])
        self.assertNotIn("Reserve or replacement driver changes: awaiting",
                         pages["rookies"]["body"])
        self.assertIn("Rookie FP1 line-ups", pages["rookies"]["body"])
        self.assertNotIn("Team-by-team weekend storylines: awaiting", pages["teams"]["body"])

    def test_madrid_history_and_unknowns_are_explicit(self):
        pages = self.spain()
        for slug in ("facts", "moments"):
            self.assertIn("not applicable before its debut", pages["facts"]["body"])
            self.assertIn("different-track", pages["facts"]["body"])
        self.assertNotIn("Past winners, polesitters and weekend-specific trivia: awaiting",
                         pages["facts"]["body"])
        self.assertIn("Antonelli won the Madring's inaugural Grand Prix", pages["moments"]["body"])
        self.assertIn("Measured long-run degradation and stint strategy: unavailable in this build",
                      pages["tyres"]["body"])
        self.assertIn("no Madrid Heat Hazard", pages["schedule"]["body"])
        self.assertIn("Hadjar", pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", pages["schedule"]["body"])

    def test_madrid_permutations_are_dated_and_do_not_reuse_old_scoring(self):
        body = self.spain()["standings"]["body"]
        self.assertIn("Madrid's effect on the title fight", body)
        self.assertIn("widened his lead, it did not narrow it", body)
        self.assertIn("Russell concedes the title fight", body)
        self.assertNotIn("10 September snapshot", body)
        self.assertIn(self.contexts["spain"]["standings"]["drivers"], body)

    def test_sepang_compounds_and_2026_overtaking_modes_are_current(self):
        pages = content_generic.build_pages(self.contexts["bahrain"], self.env)
        tyres = pages["tyres"]["body"]
        circuit = pages["circuit"]["body"]
        powerunit = pages["powerunit"]["body"]
        notes = pages["notes"]["body"]

        self.assertIn("C2 Hard / C3 Medium / C4 Soft", tyres)
        self.assertIn(
            "https://press.pirelli.com/tyre-compound-selections-for-baku-sepang-and-singapore/",
            tyres,
        )
        self.assertIn("not a driver-by-driver remaining-set inventory", tyres)
        self.assertNotIn("Pirelli's compound allocation: awaiting", tyres)
        self.assertIn("Sepang's asphalt is abrasive", tyres)
        self.assertIn("rates tyre stress and abrasion 4/5", tyres)
        self.assertIn("Turns 6–12 section was resurfaced in 2023", tyres)
        self.assertIn("additional levelling and cleaning took place", tyres)
        self.assertIn("overall surface characteristics remain similar to 2017", tyres)
        self.assertNotIn("has not been resurfaced since", tyres)
        self.assertIn("lap-time differential between one- and two-stop strategies", tyres)
        self.assertNotIn("Historically one of the toughest tyre circuits", tyres)
        self.assertIn("Straight Mode zones", circuit)
        self.assertIn("4", circuit)
        self.assertIn("start/finish straight", circuit)
        self.assertIn("Turns 3–4, 8–9 and 14–15", circuit)
        self.assertIn(
            "https://www.formula1.com/en/latest/article/"
            "circuit-guide-everything-you-need-to-know-about-the-sepang-international-circuit."
            "2KTLvyxBXmwVftSJxmYeZ2",
            circuit,
        )
        self.assertIn("Straight Mode zones", notes)
        self.assertIn("Overtake activation", notes)
        self.assertIn("Circuit Map v4", circuit)
        self.assertIn("absolute Overtake line distances TBC", circuit)
        self.assertIn("Overtake activation zones", circuit)
        self.assertNotIn("Not confirmed", circuit)
        self.assertNotIn("DRS", circuit)
        self.assertNotIn("with DRS", pages["overview"]["body"])
        self.assertIn("Straight Mode", powerunit)
        self.assertIn("<strong>Overtake</strong>", powerunit)
        self.assertEqual(pages["powerunit"]["title"], "Power Unit & Overtake")
        self.assertNotIn("override", powerunit.casefold())

    def test_bahrain_published_fia_maps_are_transcribed(self):
        pages = self.bahrain()
        powerunit = pages["powerunit"]["body"]
        circuit = pages["circuit"]["body"]
        tyres = pages["tyres"]["body"]
        notes = pages["notes"]["body"]

        for value in (
            "8.5 MJ", "9.0 MJ", "7.5 MJ", "3365 m", "100 kW/s",
            "T4–T7 (1550–2500 m)", "T9–T14 (3100–4100 m)",
            "5110 m (TBC)", "5160 m (TBC)", "loop L18", "loop L19",
        ):
            self.assertIn(value, powerunit)
        self.assertIn(
            "../assets/fia-bahrain-776bb5f3f154-50419bb38d97434c-p2.png",
            powerunit,
        )
        self.assertIn(content_bahrain.FIA_PU_URL + "#page=2", powerunit)
        self.assertNotIn(
            "The FIA power-unit and energy-map document for this event: awaiting",
            powerunit,
        )

        self.assertIn("FIA Circuit Map v4", circuit)
        self.assertIn("65 m after T15", circuit)
        self.assertIn("85 m after T15", circuit)
        self.assertIn("45 m before the exit of T15", circuit)
        self.assertIn("Overtake activation zones", circuit)
        self.assertIn(content_bahrain.FIA_CIRCUIT_MAP_URL + "#page=2", circuit)

        for value in (
            "25.0 psi", "≥25.5 psi", "−3.25°", "0.124",
            "0.122", "2 hours", "Mandatory race tyres:</strong> C2 and C3",
        ):
            self.assertIn(value, tyres)
        self.assertIn(content_bahrain.FIA_TYRE_PREVIEW_URL + "#page=2", tyres)
        self.assertIn("3365 m at 100 kW/s", notes)
        self.assertIn("both TBC", notes)
        self.assertIn("during and after qualifying", " ".join(notes.split()))
        self.assertIn("invalidates that lap time", notes)
        self.assertIn(
            "may also invalidate the immediately following lap time",
            notes,
        )
        self.assertIn("less than 90 seconds remaining", notes)
        self.assertIn(content_bahrain.FIA_RD_NOTES_URL + "#page=7", notes)

    def test_sepang_preview_is_responsive_and_preserves_original(self):
        body = self.bahrain()["tyres"]["body"]
        self.assertIn('class="circuit-img tyre-preview-img"', body)
        self.assertIn('class="circuit-fig"', body)
        self.assertIn('role="button" tabindex="0"', body)
        self.assertIn("event.key==='Enter'", body)
        self.assertIn("Full-resolution original", body)
        self.assertNotIn('class="tyre-fig"', body)
        self.assertIn("22.5 seconds pit-stop loss", body)

    def test_sepang_heat_grid_reports_and_history_are_source_qualified(self):
        pages = self.bahrain()
        for slug in ("overview", "schedule", "notes"):
            self.assertIn("Heat Hazard declared", pages[slug]["body"])
            self.assertIn(content_bahrain.HEAT_URL, pages[slug]["body"])
        for slug in ("overview", "penalties", "powerunit", "notes"):
            self.assertIn("not yet event rulings", pages[slug]["body"])
            self.assertIn("Isack Hadjar", pages[slug]["body"])
        self.assertIn("06:00–07:00 Tallinn", pages["upgrades"]["body"])
        self.assertIn("distinct from the Car Presentation Submissions", pages["upgrades"]["body"])
        self.assertIn("second race and", pages["moments"]["body"])
        self.assertNotIn("Brawn GP's first race", pages["moments"]["body"])
        self.assertIn("complied", pages["powerunit"]["body"])

    def test_sepang_all_upgrade_rows_and_inline_sources_are_populated(self):
        submissions = content_bahrain.UPGRADE_SUBMISSIONS
        self.assertEqual(len(submissions), 11)
        self.assertEqual(sum(len(items) for _, _, items in submissions), 14)
        self.assertEqual(sum(bool(items) for _, _, items in submissions), 7)
        self.assertEqual([name for name, _, items in submissions if not items],
                         ["Williams", "Aston Martin", "Audi", "Cadillac"])
        self.assertEqual(len(next(items for team, _, items in submissions if team == "Mercedes")), 7)
        pages = self.bahrain()
        body = pages["upgrades"]["body"]
        self.assertNotIn("FIA car presentation submissions for this round: awaiting", body)
        self.assertNotIn("not yet a filed component", body)
        for team, page, items in submissions:
            self.assertIn(f'href="#upgrade-submission-{page}" data-document-reader', body)
            self.assertIn(f'<details id="upgrade-submission-{page}">', body)
            for number in ([page, page + 1] if items else [page]):
                asset = f"{content_bahrain.UPGRADES_ASSET}-p{number}.png"
                self.assertIn(asset, body)
                self.assertTrue((Path(__file__).parent / "assets_src" / asset).is_file())
                self.assertIn(content_bahrain.UPGRADES_URL + f"#page={number}", body)
        self.assertEqual(body.count('<details id="upgrade-submission-'), 11)
        for slug in ("overview", "teams", "notes"):
            self.assertIn("FIA Document 12", pages[slug]["body"])
        media = f1lib.render_fia_media(self.contexts["bahrain"], "upgrades", body)
        self.assertNotIn(content_bahrain.UPGRADES_ASSET, media)

    def test_sepang_pu_inventory_has_all_named_drivers_and_dated_scope(self):
        body = self.bahrain()["powerunit"]["body"]
        table = body.split('id="sepang-pu-inventory">', 1)[1].split("</table>", 1)[0]
        rows = re.findall(r"<tr>(.*?)</tr>", table.split("<tbody>", 1)[1], re.S)
        self.assertEqual(len(rows), 22)
        self.assertTrue(all(len(re.findall(r"<td>", row)) == 9 for row in rows))
        self.assertIn("<td>Fernando Alonso</td><td>5</td><td>5</td><td>3</td><td>5</td><td>7</td><td>6</td><td>9</td>", table)
        self.assertIn("not remaining allocation or final post-Sepang totals", body)
        self.assertIn("Friday 08:30 snapshot", body)
        self.assertIn("pu_elements_used_per_driver_up_to_now.pdf#page=2", body)

    def test_event_specific_fia_cautions_and_values_survive(self):
        italy, spain = self.italy(), self.spain()
        self.assertIn("5.0 MJ", italy["powerunit"]["body"])
        self.assertIn("Pre-running snapshot, not final post-Monza totals", italy["powerunit"]["body"])
        self.assertIn("Document 33", italy["powerunit"]["body"])
        self.assertIn("1:42.0 between the Safety Car lines", italy["circuit"]["body"])
        self.assertIn("during and after qualifying", italy["circuit"]["body"])
        self.assertIn(content_italy.FIA_SC_TIME_URL, italy["circuit"]["body"])
        for slug in ("overview", "facts", "notes", "circuit", "powerunit"):
            self.assertIn("5.414 km", spain[slug]["body"])
            self.assertIn("5.416 km", spain[slug]["body"])
        self.assertIn("7.5 MJ", spain["powerunit"]["body"])
        self.assertIn("L24 at 5160 m", spain["powerunit"]["body"])
        self.assertIn("L25 at 5230 m", spain["powerunit"]["body"])
        self.assertIn("Document 25", spain["powerunit"]["body"])
        self.assertIn("Team-by-team car presentation submissions", spain["upgrades"]["body"])


class AzerbaijanParityTests(unittest.TestCase):
    def setUp(self):
        self.ctx = next(ctx for ctx in build.season_gps() if ctx["dir"] == "azerbaijan")
        self.ctx.update(status="live", results=[], extra={}, weather={}, weather_ok=False)
        self.env = {"schedule_rows": lambda: "SCHEDULE_ROWS",
                    "weather_cards": lambda: "WEATHER_CARDS", "weather_ok": False}
        self.pages = content_azerbaijan.build_pages(self.ctx, self.env)

    def test_directory_url_has_an_overview_redirect(self):
        ctx = dict(self.ctx)
        ctx["nav"] = [row for row in ctx["nav"] if row[0] == "overview"]
        ctx["pages"] = lambda *_: {"overview": self.pages["overview"]}
        files = mock_open()
        lib = content_azerbaijan.f1lib
        with patch.object(lib, "prepare"), patch.object(lib.os.path, "exists", return_value=False), \
             patch.object(lib.os.path, "isdir", return_value=False), \
             patch.object(lib.os, "makedirs"), patch.object(lib, "shell", return_value="OVERVIEW"), \
             patch.object(lib, "render_index", return_value="SEASON_INDEX"), \
             patch("builtins.open", files):
            lib.build_all([ctx])
        files.assert_any_call(lib.os.path.join(lib.OUT, "azerbaijan", "index.html"), "w")
        writes = "".join(call.args[0] for call in files().write.call_args_list)
        self.assertIn('content="0; url=overview.html"', writes)
        self.assertIn('rel="canonical" href="overview.html"', writes)

    def test_seventeen_surfaces_preserve_automatic_feeds(self):
        automatic = {"results", "news", "h2h"}
        self.assertEqual({n[0] for n in self.ctx["nav"]}, set(self.pages) | automatic)
        with patch.object(content_azerbaijan.f1lib, "auto_reliability",
                          return_value="LIVE_PIT_TABLE"):
            pages = content_azerbaijan.build_pages(self.ctx, self.env)
        self.assertIn("LIVE_PIT_TABLE", pages["reliability"]["body"])

    def test_automatic_news_subtitle_stays_phase_accurate(self):
        pending = f1lib.news_page_subtitle(self.ctx)
        complete = f1lib.news_page_subtitle(
            dict(self.ctx, results=[{"label": "Race"}])
        )
        self.assertIn("as each session is completed", pending)
        self.assertIn("the Race is complete", complete)
        self.assertNotIn("rerun during the weekend", complete)

    def test_visually_reviewed_prescriptions_correct_old_errors(self):
        body = self.pages["tyres"]["body"]
        self.assertIn("C3 and C4", body)
        self.assertIn("not C5", body)
        self.assertIn("70&deg;C for slicks\nand intermediates", body)
        self.assertIn("40&deg;C for wets", body)
        self.assertIn("19.5-second", body)
        self.assertIn("not on Pirelli's", body)
        self.assertNotIn("after Friday practice", body)
        self.assertNotIn("mandatory race tyres alongside C5", body)
        self.assertIn(content_azerbaijan.PREVIEW_IMAGE, body)
        self.assertIn(content_azerbaijan.FIA_TYRES_ASSET, body)

    def test_race_day_tyres_replace_stale_inventory_and_illustrative_windows(self):
        body = self.pages["tyres"]["body"]
        for text in ("Laps 26–32", "Laps 16–22", "Laps 21–27",
                     content_azerbaijan.STRATEGY_URL, content_azerbaijan.STRATEGY_IMAGE,
                     "not on Pirelli's", "not a per-driver fitted",
                     "only drivers without a new Medium", "Sainz has no new Soft"):
            self.assertIn(text, body)
        for text in ("No verified post-qualifying race-set chart", "Laps 24–31",
                     "Laps 17–24", "Laps 18–26", "only if Thursday long runs"):
            self.assertNotIn(text, body)
        for slug in ("overview", "notes"):
            self.assertIn("26 September race-day tyre update", self.pages[slug]["body"])
            self.assertIn("Medium–Soft laps 26–32", self.pages[slug]["body"])

    def test_baku_inventory_matches_reviewed_image_and_all_22_entrants(self):
        lib = content_azerbaijan.f1lib
        root = Path(__file__).parent
        saved = json.loads((root / "data/azerbaijan/race_tyres_verified.json").read_text())
        snapshot = {key: saved[key] for key in ("year", "gp", "race_date")}
        snapshot["chart"] = {"sha256": saved["source_sha256"]}
        verified = lib.reviewed_race_tyres(self.ctx, snapshot)
        self.assertEqual(verified["state"], "verified")
        asset = f"race-tyres-2026-azerbaijan-{verified['source_sha256'][:16]}.webp"
        self.assertEqual(verified["source_sha256"], hashlib.sha256(
            (root / "assets_src" / asset).read_bytes()).hexdigest())
        self.assertEqual(verified["compounds"], ["C3", "C4", "C5"])
        self.assertEqual(set(verified["drivers"]), {
            "PIA", "NOR", "RUS", "ANT", "VER", "HAD", "LEC", "HAM", "ALB",
            "SAI", "LIN", "LAW", "STR", "ALO", "OCO", "BEA", "HUL", "BOR",
            "GAS", "COL", "PER", "BOT",
        })
        for code, counts in verified["drivers"].items():
            with self.subTest(driver=code):
                self.assertEqual(counts[4:], [1, 0])
                self.assertEqual(counts[2:4], [0, 1] if code in ("RUS", "ANT") else [1, 0])
        self.assertEqual(verified["drivers"]["ANT"][:2], [4, 1])
        self.assertEqual(verified["drivers"]["SAI"][:2], [0, 4])
        self.assertEqual(verified["drivers"]["ALB"][:2], [1, 4])
        rendered = lib.render_tyre_availability(
            self.ctx, official=verified["drivers"], compounds=verified["compounds"],
            source_url=content_azerbaijan.STRATEGY_URL)
        table_body = re.search(r"<tbody>(.*?)</tbody>", rendered, re.S).group(1)
        self.assertEqual(table_body.count("<tr>"), 22)

    def test_mexico_inventory_review_matches_chart_and_race_entrants(self):
        root = Path(__file__).parent
        snapshot = json.loads((root / "data/mexico/race_tyres.json").read_text())
        verified = f1lib.reviewed_race_tyres({"dir": "mexico"}, snapshot)
        self.assertEqual(verified["state"], "verified")
        image = root / "assets_src" / snapshot["chart"]["asset"]
        self.assertEqual(verified["source_sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
        race = json.loads((root / "data/mexico/session_results.json").read_text())
        race_rows = next(s["rows"] for s in race["sessions"] if s["label"] == "Race")
        self.assertEqual(set(verified["drivers"]), {row[2].split()[-1] for row in race_rows})
        self.assertEqual(verified["drivers"]["STR"][:2], [3, 2])
        self.assertEqual(verified["drivers"]["ALO"][:2], [4, 1])

    def test_complete_energy_sheet_and_qualifying_only_exceptions(self):
        body = self.pages["powerunit"]["body"]
        for value in ("3,796 m", "50 kW/s", "4,177 m", "4,270 m", "(TBC)",
                      "Outlaps other than in the race", "Base–Overtake",
                      "1,500–2,870 m", "[4,050–5,300 m]", "[5,600–6,000 m]",
                      "qualifying only", "1.0 s", "exceed their season allocation"):
            self.assertIn(value, body)
        self.assertNotIn("Sunday", body)
        self.assertNotIn("Manual Override", body)

    def test_circuit_map_notes_are_interpreted_not_just_linked(self):
        body = self.pages["circuit"]["body"]
        for value in ("45 m after T19", "45 m after T20", "110 m after T2",
                      "160 m after T2", "90 m after T16", "20 m before T17",
                      "2.033 / 2.025 / 1.945", "less than 100 seconds",
                      "during and after qualifying", "before T16", "80 km/h"):
            self.assertIn(value, body)
        self.assertNotIn("DRS-assisted", body)
        self.assertNotIn("statistical certainty", body)

    def test_all_teams_upgrades_and_rookie_context(self):
        body = self.pages["teams"]["body"]
        for team in ("Mercedes", "Ferrari", "McLaren", "Red Bull", "Racing Bulls",
                     "Alpine", "Haas", "Audi", "Williams", "Aston Martin", "Cadillac"):
            self.assertIn(team, body)
        self.assertNotIn("Team-by-team weekend storylines: awaiting", body)
        self.assertIn("10:00–11:00 Tallinn", self.pages["upgrades"]["body"])
        self.assertIn("Car Presentation Submissions", self.pages["upgrades"]["body"])
        self.assertIn("Mercedes, Ferrari,\nAston Martin, Haas and Alpine submitted no updates",
                      self.pages["upgrades"]["body"])
        self.assertIn("FIA Document 11 lists 14 Audi component entries", body)
        self.assertNotIn("no verified event upgrade declaration yet", body)
        self.assertIn("(14 listed components)", self.pages["upgrades"]["body"])
        self.assertIn(content_azerbaijan.AUDI_UPGRADE_URL,
                      self.pages["upgrades"]["body"])
        self.assertIn("Arvid Lindblad", self.pages["rookies"]["body"])
        self.assertIn("painful", body)

    def test_schedule_and_notes_follow_saturday_race(self):
        self.assertIn("SCHEDULE_ROWS", self.pages["schedule"]["body"])
        self.assertIn("WEATHER_CARDS", self.pages["schedule"]["body"])
        for slug in ("overview", "notes"):
            self.assertIn("15:00 Baku / 14:00 Tallinn", self.pages[slug]["body"])
            self.assertIn(self.ctx["standings"]["summary"], self.pages[slug]["body"])
            self.assertIn("post-qualifying update", self.pages[slug]["body"])
            self.assertNotIn("qualifying follows later Friday", self.pages[slug]["body"])
        self.assertIn("Russell took pole in 1:42.526", self.pages["notes"]["body"])
        self.assertIn("official starting grid is now available", self.pages["overview"]["body"])
        self.assertNotIn("Session-by-session commentary notes: awaiting",
                         self.pages["notes"]["body"])
        self.assertIn(
            "The Race classification remains pending until the official result is available",
            self.pages["notes"]["body"],
        )
        self.assertNotIn("pending until Saturday", self.pages["notes"]["body"])
        post_race_ctx = dict(self.ctx)
        post_race_ctx["results"] = [{
            "label": "Race",
            "headers": [],
            "rows": [],
        }]
        post_race_notes = content_azerbaijan.build_pages(
            post_race_ctx, self.env
        )["notes"]["body"]
        self.assertIn("the official Race classification is published", post_race_notes)
        self.assertNotIn("remains pending until the official result", post_race_notes)
        self.assertIn("every other rival", self.pages["standings"]["body"])
        self.assertIn("no fastest-lap bonus", self.pages["standings"]["body"])
        self.assertNotIn("A curated moments list", self.pages["moments"]["body"])

    def test_post_race_brief_replaces_pre_race_and_qualifying_material(self):
        results_path = Path(__file__).parent / "data/azerbaijan/session_results.json"
        result_record = json.loads(results_path.read_text(encoding="utf-8"))
        race = next(block for block in result_record["sessions"] if block["label"] == "Race")
        ctx = dict(self.ctx, results=[race])
        pages = content_azerbaijan.build_pages(ctx, self.env)
        self.assertIn("after the completed Grand Prix", pages["standings"]["sub"])
        for slug in ("overview", "notes"):
            body = pages[slug]["body"]
            self.assertIn("Race classification: Russell wins in Baku", body)
            self.assertIn("1:38:02.143", body)
            self.assertNotIn("25 September post-qualifying update", body)
            self.assertNotIn("Russell took pole in 1:42.526", body)
            self.assertNotIn("Championship permutations", body)
        reliability = pages["reliability"]["body"]
        self.assertIn("Post-race result status", reliability)
        self.assertNotIn("The Grand Prix has not run yet", reliability)
        teams = pages["teams"]["body"]
        self.assertIn("Post-race team update", teams)
        self.assertIn("Race-day team results — official classification", teams)
        self.assertIn("George Russell", teams)
        self.assertIn("records 6 entrants as not classified", teams)
        self.assertNotIn("Baku tests whether", teams)

    def test_post_race_pirelli_strategy_is_added_only_after_classification(self):
        self.assertNotIn("Pirelli's account", self.pages["tyres"]["body"])
        record = json.loads(
            (Path(__file__).parent / "data/azerbaijan/session_results.json")
            .read_text(encoding="utf-8")
        )
        race = next(block for block in record["sessions"] if block["label"] == "Race")
        pages = content_azerbaijan.build_pages(
            dict(self.ctx, results=[race]), self.env
        )
        body = " ".join(pages["tyres"]["body"].split())
        for fact in (
            "Russell and Verstappen started on C4 Medium",
            "Hadjar started on C5 Soft",
            "49% of laps were on C4",
            "51% on C5",
            "does not provide a per-driver stint or pit-lap ledger",
            content_azerbaijan.PIRELLI_RACE_URL,
        ):
            self.assertIn(fact, body)

    def test_post_qualifying_updates_replace_expired_weekend_placeholders(self):
        self.assertNotIn("Pre-FP1 watch", self.pages["teams"]["body"])
        self.assertIn("Post-qualifying team context", self.pages["teams"]["body"])
        self.assertIn("Sainz 14th", self.pages["teams"]["body"])
        self.assertIn("FP1 line-up checked", self.pages["rookies"]["body"])
        self.assertNotIn("Rookie FP1 line-ups for this round: awaiting",
                         self.pages["rookies"]["body"])
        self.assertNotIn("24 September pre-FP1 source check",
                         self.pages["tyres"]["body"])
        self.assertNotIn("after Thursday practice",
                         self.pages["tyres"]["body"])
        self.assertIn("Post-qualifying tyre evidence", self.pages["tyres"]["body"])
        self.assertIn("Document 48", self.pages["penalties"]["body"])
        self.assertIn("Document 49", self.pages["penalties"]["body"])
        penalty_body = " ".join(self.pages["penalties"]["body"].split())
        self.assertIn("Sainz 14th, Perez 20th, Alonso 21st and Stroll 22nd",
                      penalty_body)
        for doc, url in (
            ("Doc 48", content_azerbaijan.FIA_ROOT
             + "infringement_-_car_11_-_impeding_car_81.pdf"),
            ("Doc 49", content_azerbaijan.FIA_ROOT
             + "infringement_-_car_55_-_failure_to_slow_for_yellow_flags_0.pdf"),
        ):
            row = next(
                match.group(1)
                for match in re.finditer(r"<tr>(.*?)</tr>",
                                         self.pages["penalties"]["body"], re.S)
                if f">{doc}</a>" in match.group(1)
            )
            self.assertIn('<details class="penalty-document"', row)
            self.assertIn(url, row)
            self.assertIn("data-document-reader", row)

    def test_race_day_fia_updates_are_sourced_and_distinguished(self):
        powerunit = self.pages["powerunit"]["body"]
        upgrades = self.pages["upgrades"]["body"]
        notes = self.pages["notes"]["body"]
        penalties = self.pages["penalties"]["body"]
        self.assertIn("Document 55 (26 September)", powerunit)
        self.assertIn("four of four permitted", powerunit)
        self.assertIn("five of six", powerunit)
        self.assertIn("new_pu_elements_for_this_competition_1.pdf#page=2", powerunit)
        self.assertIn("Parc Fermé component replacements (Document 57)", upgrades)
        self.assertIn("Every listed replacement was approved", upgrades)
        self.assertIn("parts_and_parameters_been_replaced_and_or_changed_during_parc_ferme.pdf",
                      upgrades)
        self.assertIn("not, by itself, evidence of a defect or reliability failure", upgrades)
        self.assertIn("Documents 55 and 57", notes)
        for entry in (
            "McLaren, Car 81", "Mercedes, Cars 63 and 12", "Red Bull Racing, Cars 03 and 06",
            "Ferrari, Car 16", "Atlassian Williams, Car 23", "Racing Bulls, Cars 41 and 30",
            "Aston Martin Aramco Honda, Car 18", "Audi, Car 27", "Alpine, Car 43",
            "Cadillac, Cars 11 and 77", "rotac actuator set", "clutch-shaft torque sensor",
            "ICE sump bumper protection plate", "front ride-height laser lens",
        ):
            self.assertIn(entry, upgrades)
        penalties = self.pages["penalties"]["body"]
        self.assertIn("The Race decisions are now published", penalties)
        self.assertIn("five grid places at the next race in which he participates",
                      " ".join(penalties.split()))
        self.assertIn("late-race Documents 65–67 are listed above", penalties)
        self.assertIn("latest successful recheck, 18:53 UTC", penalties)
        self.assertIn("Documents 68–70 also resolve the three", penalties)
        self.assertIn("Bortoleto received a 10-second penalty", penalties)
        self.assertNotIn("50 PDFs after Qualifying", penalties)
        for document, url, outcome in (
            ("Doc 65", "decision_-_car_41_-_collision_with_car_30_in_turn_1.pdf",
             "No further action"),
            ("Doc 66", "infringement_-_car_43_-_collision_with_car_10_in_turn_1.pdf",
             "next race in which the driver participates"),
            ("Doc 67", "decision_-_car_77_-_turn_15_incident.pdf",
             "No further action"),
        ):
            row = next(
                match.group(1)
                for match in re.finditer(r"<tr>(.*?)</tr>", penalties, re.S)
                if f">{document}</a>" in match.group(1)
            )
            self.assertIn(url, row)
            self.assertIn(outcome, row)
            self.assertIn('<details class="penalty-document"', row)
            self.assertIn("data-document-reader", row)
        for document, url in (
            ("Doc 60", "summons_-_car_5_-_overtaking_under_yellow_flags_.pdf"),
            ("Doc 61", "summons_-_car_55_-_alleged_failure_to_follow_race_directors_instructions_-_practice_start.pdf"),
            ("Doc 62", "summons_-_car_6_-_alleged_failure_to_follow_race_directors_instructions_-_practice_start.pdf"),
        ):
            row = next(
                match.group(1)
                for match in re.finditer(r"<tr>(.*?)</tr>", penalties, re.S)
                if f">{document}</a>" in match.group(1)
            )
            self.assertIn(url, row)
            self.assertIn("Resolved by Document", row)
        for document, url, ruling in (
            ("Doc 68", "car_5_-_overtaking_under_yellow_flags.pdf",
             "10 second time penalty"),
            ("Doc 69", "car_6_-_failing_to_follow_race_directors_instructions_-_practice_start.pdf",
             "Driver: Warning"),
            ("Doc 70", "car_55_-_failing_to_follow_race_directors_instructions_-_practice_start.pdf",
             "Driver: Warning"),
        ):
            row = next(
                match.group(1)
                for match in re.finditer(r"<tr>(.*?)</tr>", penalties, re.S)
                if f">{document}</a>" in match.group(1)
            )
            self.assertIn(url, row)
            self.assertIn(ruling, row)
            self.assertIn('<details class="penalty-document"', row)
            self.assertIn("data-document-reader", row)


if __name__ == "__main__":
    unittest.main()
