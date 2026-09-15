from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts import build_site


def _legal_text(source: str) -> str:
    return " ".join(re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL).split())


class SiteBuildTests(unittest.TestCase):
    def test_legal_copy_does_not_count_commented_disclosures(self) -> None:
        source = "<!-- same app installation or device -->\n<p>Visible policy</p>"
        self.assertNotIn("same app installation or device", _legal_text(source))
        self.assertIn("Visible policy", _legal_text(source))

    def test_locales_have_complete_matching_schema(self) -> None:
        locales = build_site.load_locales()
        self.assertEqual(tuple(locales), build_site.EXPECTED_LOCALES)

    def test_build_renders_every_locale_and_required_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)
            locales = build_site.load_locales()

            for locale, data in locales.items():
                page = (
                    output / "index.html"
                    if not data["path"]
                    else output / data["path"] / "index.html"
                )
                self.assertTrue(page.is_file(), locale)
                source = page.read_text(encoding="utf-8")
                self.assertIn(f'<html lang="{locale}">', source)
                self.assertIn(build_site.PLAY_URL, source)
                self.assertIn('rel="canonical"', source)
                self.assertIn(
                    'class="gallery-grid" role="region"',
                    source,
                )
                self.assertIn(
                    f"/assets/social/{build_site.SOCIAL_CARD_FILES[locale]}",
                    source,
                )
                self.assertNotRegex(source, r"\{\{[A-Z_]+\}\}")
                for alternate in build_site.EXPECTED_LOCALES:
                    self.assertIn(f'hreflang="{alternate}"', source)
                self.assertEqual(
                    source.count('class="locale-link"'),
                    len(build_site.EXPECTED_LOCALES),
                    locale,
                )
                self.assertIn(
                    f'data-open-label="{data["common"]["menu"]}"',
                    source,
                )
                self.assertIn(
                    f'data-close-label="{data["common"]["closeMenu"]}"',
                    source,
                )
                self.assertIn('class="mobile-menu"', source)
                self.assertIn('aria-current="page"', source)

            for filename in build_site.COPY_FILES:
                self.assertTrue((output / filename).is_file(), filename)
            for filename in build_site.SOCIAL_CARD_FILES.values():
                self.assertTrue(
                    (output / "assets" / "social" / filename).is_file(),
                    filename,
                )
            for slug in build_site.LEGAL_PAGES:
                legal_page = output / f"{slug}.html"
                self.assertTrue(legal_page.is_file(), slug)
                legal_source = legal_page.read_text(encoding="utf-8")
                self.assertEqual(legal_source.count("<h1>"), 1, slug)
            self.assertTrue((output / "sitemap.xml").is_file())
            self.assertTrue((output / "robots.txt").is_file())
            sitemap = (output / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn(
                "https://prio.tl-dr.ch/privacy-policy.html",
                sitemap,
            )
            self.assertNotIn("<changefreq>", sitemap)
            self.assertNotIn("<priority>", sitemap)
            self.assertIn(
                f"<lastmod>{build_site.LAST_MODIFIED}</lastmod>",
                sitemap,
            )

    def test_rendered_pages_use_current_product_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)
            source = (output / "index.html").read_text(encoding="utf-8")

            self.assertIn('"price":"0"', source)
            self.assertIn("all current features are free", source.lower())
            self.assertNotIn("$6.99", source)
            self.assertNotIn("$99.99", source)
            self.assertNotIn("5 AI classifications", source)
            self.assertNotIn("join the waitlist", source.lower())
            self.assertNotIn("crypto", source.lower())
            self.assertNotIn("without sending a single byte", source.lower())
            self.assertNotIn("fonts.googleapis.com", source)
            self.assertNotIn("no permissions required", source.lower())
            self.assertNotIn("Eliminate", source)
            self.assertIn("Do First", source)
            self.assertIn("Maybe Later", source)
            self.assertIn("microphone access", source)

            terms = (output / "terms-of-service.html").read_text(encoding="utf-8")
            privacy = (output / "privacy-policy.html").read_text(encoding="utf-8")
            self.assertNotIn("$6.99", terms)
            self.assertIn("All currently shipped Prio features", terms)
            self.assertIn("each off by default and independent", privacy)
            self.assertIn("drive.appdata", privacy)
            self.assertIn("AI health diagnostics", privacy)
            self.assertNotIn("Settings &gt; Diagnostics", privacy)
            self.assertIn(
                'class="table-wrap" role="region"',
                privacy,
            )
            privacy_text = _legal_text(privacy)
            terms_text = _legal_text(terms)
            deletion_text = _legal_text(
                (output / "delete-data.html").read_text(encoding="utf-8")
            )
            self.assertIn("same app installation or device", privacy_text)
            self.assertIn("Google authorization", privacy_text)
            self.assertNotIn("Prio requests Google Sign-In", privacy_text)
            self.assertIn(
                "Crash reporting withdrawal completes after restarting Prio",
                privacy_text,
            )
            self.assertIn("unsent reports", deletion_text)
            self.assertIn("restarting Prio", deletion_text)
            for legal_text in (privacy_text, terms_text):
                self.assertIn("available iCloud account", legal_text)
                self.assertNotIn(
                    "does not declare the required iCloud capability",
                    legal_text,
                )
                self.assertNotIn(
                    "signed target lacks the required capability",
                    legal_text,
                )

    def test_seo_copy_fits_search_result_limits(self) -> None:
        for locale, data in build_site.load_locales().items():
            self.assertLessEqual(len(data["seo"]["title"]), 65, locale)
            self.assertLessEqual(len(data["seo"]["description"]), 160, locale)

    def test_rendered_android_diagnostic_export_disclosure_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)
            privacy = _legal_text(
                (output / "privacy-policy.html").read_text(encoding="utf-8")
            )
            deletion = _legal_text(
                (output / "delete-data.html").read_text(encoding="utf-8")
            )

            for disclosure in (
                "For Android only",
                "Crashlytics reports and Firebase session data",
                "restricted Google BigQuery dataset in the EU",
                "raw stack traces and installation/session identifiers",
                "not anonymous aggregates",
                "does not enable Analytics, streaming, or iOS exports",
                "tables, views, and partitions automatically expire after 60 days",
                "unlinking the export does not erase existing copies",
                "Google may retain recovery copies",
            ):
                with self.subTest(disclosure=disclosure):
                    self.assertIn(disclosure, privacy)

            for disclosure in (
                "Android Crashlytics BigQuery copy",
                "does not erase existing copies",
                "automatically expire after 60 days",
                "Google may retain recovery copies",
                "deletion request about this private copy, contact Prio",
            ):
                with self.subTest(deletion_disclosure=disclosure):
                    self.assertIn(disclosure, deletion)

    def test_non_english_footer_copy_is_localized(self) -> None:
        for locale, data in build_site.load_locales().items():
            if locale == "en-US":
                continue
            self.assertNotIn(
                "All rights reserved",
                data["footer"]["rights"],
                locale,
            )

    def test_gallery_captions_match_current_screenshots(self) -> None:
        captions = build_site.load_locales()["en-US"]["gallery"]["captions"]
        self.assertEqual(
            captions,
            [
                "Quick Capture with a priority suggestion",
                "Morning briefing",
                "Goal progress",
                "Task details",
            ],
        )

    def test_screenshots_render_as_chrome_free_app_plates(self) -> None:
        locales = build_site.load_locales()
        template = build_site.TEMPLATE_PATH.read_text(encoding="utf-8")
        source = build_site.render_page(
            "en-US",
            locales["en-US"],
            locales,
            template,
        )
        styles = (build_site.ROOT / "style.css").read_text(encoding="utf-8")

        self.assertIn('class="app-surface app-surface--hero"', source)
        self.assertIn('class="matrix"', source)
        for cell in ("do", "schedule", "delegate", "later"):
            self.assertIn(f"matrix__cell--{cell}", source)
        for label in ("Do First", "Schedule", "Delegate", "Maybe Later"):
            self.assertIn(label, source)
        for variant in ("capture", "briefing", "goals", "task"):
            self.assertIn(f"app-surface--{variant}", source)

        self.assertNotIn("/screenshots/", source)
        self.assertNotIn("app-plate", source)
        self.assertNotIn("phone-frame", source)
        self.assertNotIn("phone-speaker", source)
        self.assertNotIn("gallery-card__phone", source)
        self.assertNotIn("quadrant-card", source)
        self.assertNotIn("hero-proof", source)

        self.assertIn(".app-surface", styles)
        self.assertIn(".matrix__cell--do", styles)
        self.assertNotIn("object-fit: cover", styles)
        self.assertRegex(
            styles,
            r"\.gallery-grid\s*\{[^}]*"
            r"grid-template-columns:\s*repeat\(2,",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)
            self.assertFalse((output / "screenshots").exists())
            rendered = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn('class="app-surface app-surface--hero"', rendered)

    def test_structured_data_describes_brand_entities(self) -> None:
        locales = build_site.load_locales()
        template = build_site.TEMPLATE_PATH.read_text(encoding="utf-8")
        for locale, data in locales.items():
            rendered = build_site.render_page(locale, data, locales, template)
            match = re.search(
                r'<script type="application/ld\+json">(.*?)</script>',
                rendered,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(match, locale)
            payload = json.loads(match.group(1))
            self.assertEqual(payload["@context"], "https://schema.org")
            self.assertEqual(
                [node["@type"] for node in payload["@graph"]],
                ["Organization", "WebSite", "SoftwareApplication"],
                locale,
            )
            nodes = {node["@type"]: node for node in payload["@graph"]}
            organization_id = nodes["Organization"]["@id"]
            self.assertEqual(
                nodes["Organization"]["logo"]["url"],
                "https://prio.tl-dr.ch/icon-512.png",
            )
            self.assertEqual(
                nodes["WebSite"]["publisher"]["@id"],
                organization_id,
            )
            self.assertEqual(
                nodes["SoftwareApplication"]["publisher"]["@id"],
                organization_id,
            )
            self.assertEqual(
                nodes["SoftwareApplication"]["offers"]["price"],
                "0",
            )
            self.assertNotIn("FAQPage", match.group(1))

    def test_build_emits_pwa_icons_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)

            for filename, dimension in build_site.RASTER_ICONS.items():
                path = output / filename
                self.assertTrue(path.is_file(), filename)
                with Image.open(path) as icon:
                    self.assertEqual(icon.size, (dimension, dimension), filename)
            self.assertTrue((output / "favicon.ico").is_file())

            manifest_path = output / "site.webmanifest"
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["start_url"], "/")
            self.assertEqual(manifest["display"], "standalone")
            self.assertTrue(manifest["description"].strip())
            icon_sizes = {icon["sizes"] for icon in manifest["icons"]}
            self.assertIn("192x192", icon_sizes)
            self.assertIn("512x512", icon_sizes)

            index = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn('rel="manifest"', index)
            self.assertIn('rel="apple-touch-icon"', index)
            self.assertIn('href="/favicon-32.png"', index)

    def test_build_emits_branded_not_found_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "_site"
            build_site.build(output)
            page = output / "404.html"
            self.assertTrue(page.is_file())
            source = page.read_text(encoding="utf-8")
            self.assertIn('name="robots"', source)
            self.assertIn("noindex", source)
            self.assertIn(build_site.PLAY_URL, source)
            self.assertIn('href="/"', source)
            self.assertNotRegex(source, r"\{\{[A-Z_]+\}\}")


if __name__ == "__main__":
    unittest.main()
