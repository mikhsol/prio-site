#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

import markdown
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "content" / "locales.json"
TEMPLATE_PATH = ROOT / "content" / "landing.html"
LEGAL_TEMPLATE_PATH = ROOT / "content" / "legal-page.html"
NOT_FOUND_TEMPLATE_PATH = ROOT / "content" / "not-found.html"
DEFAULT_OUTPUT = ROOT / "_site"

SITE_URL = "https://prio.tl-dr.ch"
SITE_NAME = "Prio"
PLAY_URL = "https://play.google.com/store/apps/details?id=com.prio.app"
LAST_MODIFIED = "2026-09-14"

EXPECTED_LOCALES = (
    "en-US",
    "de-DE",
    "es-ES",
    "fr-FR",
    "it-IT",
    "ja-JP",
    "ko-KR",
    "nl-NL",
    "pt-BR",
    "ru-RU",
    "zh-Hans",
)

EXPECTED_PATHS = {
    "en-US": "",
    "de-DE": "de",
    "es-ES": "es",
    "fr-FR": "fr",
    "it-IT": "it",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "nl-NL": "nl",
    "pt-BR": "pt-br",
    "ru-RU": "ru",
    "zh-Hans": "zh-hans",
}

BADGE_FILES = {
    "en-US": "en.png",
    "de-DE": "de.png",
    "es-ES": "es.png",
    "fr-FR": "fr.png",
    "it-IT": "it.png",
    "ja-JP": "ja.png",
    "ko-KR": "ko.png",
    "nl-NL": "nl.png",
    "pt-BR": "pt-br.png",
    "ru-RU": "ru.png",
    "zh-Hans": "zh-cn.png",
}

SOCIAL_CARD_FILES = BADGE_FILES

ICON_BACKGROUND = "#0D9488"
ICON_FOREGROUND = "#FFFFFF"
ICON_MASTER_SIZE = 2048
RASTER_ICONS = {
    "favicon-32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
}
MANIFEST_THEME_COLOR = "#0f766e"
MANIFEST_BACKGROUND_COLOR = "#fbfcf7"

EXPECTED_ARRAY_LENGTHS = {
    "hero.trust": 4,
    "benefits.items": 3,
    "how.items": 3,
    "gallery.captions": 4,
    "privacy.points": 3,
    "updates.items": 4,
    "features.items": 6,
    "faq.items": 4,
}

COPY_FILES = (
    "CNAME",
    ".nojekyll",
    "logo.svg",
    "social-card.png",
    "style.css",
    "site.js",
)

LEGAL_PAGES = {
    "privacy-policy": {
        "title": "Privacy Policy",
        "description": "How Prio processes local data and optional network features.",
        "meta": "Effective July 10, 2026 · Last updated September 14, 2026",
    },
    "terms-of-service": {
        "title": "Terms of Service",
        "description": "Terms for using the Prio task and planning app.",
        "meta": "Effective July 10, 2026 · Last updated September 14, 2026",
    },
    "delete-data": {
        "title": "Delete Your Data",
        "description": "How to delete local Prio data and copies held by optional services.",
        "meta": "Current deletion guidance for Android and iOS",
    },
}


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _shape(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_shape(item) for item in value]
    return type(value).__name__


def _nested(data: dict[str, Any], dotted_path: str) -> Any:
    value: Any = data
    for component in dotted_path.split("."):
        value = value[component]
    return value


def _assert_non_empty(value: Any, path: str) -> None:
    if isinstance(value, str):
        if not value.strip():
            raise ValueError(f"{path} must not be empty")
        if "{{" in value or "}}" in value:
            raise ValueError(f"{path} contains an unresolved placeholder")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_non_empty(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_non_empty(item, f"{path}[{index}]")


def load_locales() -> dict[str, dict[str, Any]]:
    raw = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("content/locales.json must contain a JSON object")
    locales = raw.get("locales", raw)
    if not isinstance(locales, dict):
        raise ValueError("content/locales.json must contain locale objects")
    validate_locales(locales)
    return locales


def validate_locales(locales: dict[str, dict[str, Any]]) -> None:
    if tuple(locales) != EXPECTED_LOCALES:
        raise ValueError(
            f"Locale order/coverage mismatch: expected {EXPECTED_LOCALES}, "
            f"found {tuple(locales)}"
        )

    reference_shape = _shape(locales["en-US"])
    seen_paths: set[str] = set()
    for locale, data in locales.items():
        if _shape(data) != reference_shape:
            raise ValueError(f"{locale} does not match the en-US localization schema")
        if data["path"] != EXPECTED_PATHS[locale]:
            raise ValueError(
                f"{locale} path must be {EXPECTED_PATHS[locale]!r}, "
                f"found {data['path']!r}"
            )
        if data["path"] in seen_paths:
            raise ValueError(f"Duplicate locale path: {data['path']!r}")
        seen_paths.add(data["path"])
        for dotted_path, expected_length in EXPECTED_ARRAY_LENGTHS.items():
            actual = _nested(data, dotted_path)
            if len(actual) != expected_length:
                raise ValueError(
                    f"{locale}.{dotted_path} must contain {expected_length} items"
                )
        if len(data["seo"]["title"]) > 65:
            raise ValueError(f"{locale}.seo.title must be at most 65 characters")
        if len(data["seo"]["description"]) > 160:
            raise ValueError(
                f"{locale}.seo.description must be at most 160 characters"
            )
        for key, value in data.items():
            if key != "path":
                _assert_non_empty(value, f"{locale}.{key}")


def _text(value: str) -> str:
    return html.escape(value, quote=False)


def _attribute(value: str) -> str:
    return html.escape(value, quote=True)


def _page_url(locale_data: dict[str, Any]) -> str:
    path = locale_data["path"]
    return f"{SITE_URL}/{path}/" if path else f"{SITE_URL}/"


def _page_href(locale_data: dict[str, Any]) -> str:
    path = locale_data["path"]
    return f"/{path}/" if path else "/"


def _render_language_options(
    current_locale: str,
    locales: dict[str, dict[str, Any]],
) -> str:
    options = []
    for locale, data in locales.items():
        selected = " selected" if locale == current_locale else ""
        options.append(
            "            "
            f'<option value="{_attribute(_page_href(data))}" '
            f'lang="{_attribute(locale)}"{selected}>'
            f"{_text(data['languageName'])}</option>"
        )
    return "\n".join(options)


def _render_language_links(
    current_locale: str,
    locales: dict[str, dict[str, Any]],
) -> str:
    links = []
    for locale, data in locales.items():
        current = ' aria-current="page"' if locale == current_locale else ""
        links.append(
            "      "
            f'<a class="locale-link" href="{_attribute(_page_href(data))}" '
            f'lang="{_attribute(locale)}" hreflang="{_attribute(locale)}"'
            f"{current}>{_text(data['languageName'])}</a>"
        )
    return "\n".join(links)


def _render_hreflang(locales: dict[str, dict[str, Any]]) -> str:
    links = [
        f'  <link rel="alternate" hreflang="{_attribute(locale)}" '
        f'href="{_attribute(_page_url(data))}">'
        for locale, data in locales.items()
    ]
    links.append(
        f'  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/">'
    )
    return "\n".join(links)


def _render_og_alternates(
    current_locale: str,
    locales: dict[str, dict[str, Any]],
) -> str:
    return "\n".join(
        f'  <meta property="og:locale:alternate" '
        f'content="{_attribute(data["ogLocale"])}">'
        for locale, data in locales.items()
        if locale != current_locale
    )


def _render_structured_data(
    locale: str,
    data: dict[str, Any],
) -> str:
    organization_id = f"{SITE_URL}/#organization"
    organization = {
        "@type": "Organization",
        "@id": organization_id,
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "logo": {
            "@type": "ImageObject",
            "url": f"{SITE_URL}/icon-512.png",
            "width": 512,
            "height": 512,
        },
    }
    website = {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "inLanguage": locale,
        "publisher": {"@id": organization_id},
    }
    software = {
        "@type": "SoftwareApplication",
        "@id": f"{SITE_URL}/#software",
        "name": SITE_NAME,
        "operatingSystem": "Android 10 or later",
        "applicationCategory": "ProductivityApplication",
        "description": data["seo"]["description"],
        "url": _page_url(data),
        "downloadUrl": PLAY_URL,
        "inLanguage": locale,
        "isAccessibleForFree": True,
        "publisher": {"@id": organization_id},
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "url": PLAY_URL,
        },
        "featureList": data["features"]["items"],
    }
    graph = {
        "@context": "https://schema.org",
        "@graph": [organization, website, software],
    }
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace(
        "</",
        "<\\/",
    )


ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "arrow-down": '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    "globe": (
        '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/>'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10'
        ' 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z"/>'
    ),
    "shield-check": (
        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01'
        'C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72'
        'a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1Z"/>'
        '<path d="m9 12 2 2 4-4"/>'
    ),
    "cloud-off": (
        '<path d="m2 2 20 20"/>'
        '<path d="M5.78 5.78A7 7 0 0 0 9 19h8.5a4.5 4.5 0 0 0 1.3-.19"/>'
        '<path d="M21.53 16.5A4.5 4.5 0 0 0 17.5 10h-1.79A7 7 0 0 0 10 5.07"/>'
    ),
    "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "cpu": (
        '<rect x="4" y="4" width="16" height="16" rx="2"/>'
        '<rect x="9" y="9" width="6" height="6"/>'
        '<path d="M9 2v2"/><path d="M15 2v2"/><path d="M9 20v2"/>'
        '<path d="M15 20v2"/><path d="M2 9h2"/><path d="M2 15h2"/>'
        '<path d="M20 9h2"/><path d="M20 15h2"/>'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "zap": (
        '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46'
        'l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2'
        'a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>'
    ),
    "flag": (
        '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>'
        '<path d="M4 22v-7"/>'
    ),
    "mic": (
        '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>'
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/>'
    ),
    "lock": (
        '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    ),
    "sparkles": (
        '<path d="M9.94 14.06A2 2 0 0 0 8.5 12.62l-5.13-1.32a.5.5 0 0 1 0-.96'
        'L8.5 9.02a2 2 0 0 0 1.44-1.44l1.32-5.13a.5.5 0 0 1 .96 0l1.32 5.13'
        'A2 2 0 0 0 14.98 9l5.13 1.32a.5.5 0 0 1 0 .98L14.98 12.6a2 2 0 0 0-1.44 1.44'
        'l-1.32 5.13a.5.5 0 0 1-.96 0z"/>'
    ),
    "calendar": (
        '<path d="M8 2v4"/><path d="M16 2v4"/>'
        '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>'
    ),
    "bell": (
        '<path d="M10.27 21a2 2 0 0 0 3.46 0"/>'
        '<path d="M3.26 15.33A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.67'
        'C19.41 13.96 18 12.5 18 8A6 6 0 0 0 6 8c0 4.5-1.41 5.96-2.74 7.33"/>'
    ),
    "sun": (
        '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/>'
        '<path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
        '<path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/>'
        '<path d="m19.07 4.93-1.41 1.41"/>'
    ),
}


def _icon(name: str) -> str:
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


def _render_cards(
    items: list[dict[str, str]],
    class_name: str,
    icons: tuple[str, ...] | None = None,
) -> str:
    rows = []
    for index, item in enumerate(items, start=1):
        icon_html = (
            f'<span class="{class_name}__icon" aria-hidden="true">'
            f"{_icon(icons[index - 1])}</span>"
            if icons
            else ""
        )
        rows.append(
            f'          <article class="{class_name}">'
            f"{icon_html}"
            f'<span class="{class_name}__number">0{index}</span>'
            f"<h3>{_text(item['title'])}</h3>"
            f"<p>{_text(item['body'])}</p></article>"
        )
    return "\n".join(rows)


_MATRIX_CELLS = (
    ("do", "2", "Do First", "Urgent · important"),
    ("schedule", "4", "Schedule", "Important · plan it"),
    ("delegate", "2", "Delegate", "Urgent · hand off"),
    ("later", "2", "Maybe Later", "Low priority"),
)
_MATRIX_HTML = "".join(
    f'<div class="matrix__cell matrix__cell--{key}">'
    f'<span class="matrix__count">{count}</span>'
    f'<span class="matrix__name">{name}</span>'
    f'<span class="matrix__hint">{hint}</span></div>'
    for key, count, name, hint in _MATRIX_CELLS
)

HERO_SURFACE_HTML = (
    '            <div class="app-surface app-surface--hero" aria-hidden="true">\n'
    '              <div class="app-surface__bar">\n'
    "                <div>\n"
    '                  <p class="app-surface__eyebrow">Saturday · Feb 21</p>\n'
    '                  <p class="app-surface__heading">Good morning</p>\n'
    "                </div>\n"
    '                <span class="app-surface__pill">2 urgent</span>\n'
    "              </div>\n"
    f'              <div class="matrix">{_MATRIX_HTML}</div>\n'
    '              <div class="focus-row">\n'
    '                <span class="focus-row__index">1</span>\n'
    '                <div class="focus-row__text">\n'
    '                  <p class="focus-row__task">Fix critical auth bug in production</p>\n'
    '                  <p class="focus-row__meta">Do First · due 1:26 PM</p>\n'
    "                </div>\n"
    f'                <span class="focus-row__check">{_icon("check")}</span>\n'
    "              </div>\n"
    "            </div>"
)

_CAPTURE_SURFACE = (
    '            <div class="app-surface app-surface--capture" aria-hidden="true">\n'
    '              <div class="capture-field">\n'
    f'                <span class="capture-field__mic">{_icon("mic")}</span>\n'
    '                <span class="capture-field__text">Prepare Q1 board deck</span>\n'
    f'                <span class="capture-field__lock">{_icon("lock")}</span>\n'
    "              </div>\n"
    '              <div class="capture-ai">\n'
    f'                <span class="capture-ai__spark">{_icon("sparkles")}</span>\n'
    "                <div>\n"
    '                  <p class="capture-ai__label">Suggested priority</p>\n'
    '                  <p class="capture-ai__value">Schedule · important, not urgent</p>\n'
    "                </div>\n"
    "              </div>\n"
    '              <div class="capture-meta">\n'
    f'                <span class="capture-meta__item">{_icon("calendar")} Fri, 9:00 AM</span>\n'
    f'                <span class="capture-meta__item">{_icon("bell")} Reminder</span>\n'
    "              </div>\n"
    '              <span class="surface-btn">Create task</span>\n'
    "            </div>"
)

_BRIEFING_SURFACE = (
    '            <div class="app-surface app-surface--briefing" aria-hidden="true">\n'
    '              <div class="briefing-card">\n'
    f'                <p class="briefing-card__eyebrow">{_icon("sun")} Your morning briefing</p>\n'
    '                <p class="briefing-card__stat">2 urgent tasks · 0 meetings</p>\n'
    '                <p class="briefing-card__note">Top task: “Prepare Q1 review presentation”</p>\n'
    "              </div>\n"
    '              <p class="surface-label">Do First</p>\n'
    '              <div class="mini-task"><span class="mini-task__dot mini-task__dot--do">1</span>'
    "Prepare Q1 review presentation</div>\n"
    '              <div class="mini-task"><span class="mini-task__dot mini-task__dot--do">2</span>'
    "Fix critical auth bug</div>\n"
    "            </div>"
)

_GOALS_SURFACE = (
    '            <div class="app-surface app-surface--goals" aria-hidden="true">\n'
    '              <div class="goals-head">\n'
    '                <div class="goals-ring" style="--value:45%"><span>45%</span></div>\n'
    '                <div class="goals-head__stats">\n'
    "                  <span><strong>3</strong> active</span>\n"
    "                  <span><strong>2</strong> on track</span>\n"
    "                  <span><strong>1</strong> at risk</span>\n"
    "                </div>\n"
    "              </div>\n"
    '              <div class="goal-line">\n'
    '                <div class="goal-line__top"><span class="tag">Career</span>'
    '<span class="goal-line__pct">45%</span></div>\n'
    '                <p class="goal-line__name">Get promoted to Staff Engineer</p>\n'
    '                <div class="bar"><span style="width:45%"></span></div>\n'
    "              </div>\n"
    '              <div class="goal-line">\n'
    '                <div class="goal-line__top"><span class="tag">Health</span>'
    '<span class="goal-line__pct">30%</span></div>\n'
    '                <p class="goal-line__name">Run a half marathon</p>\n'
    '                <div class="bar"><span style="width:30%"></span></div>\n'
    "              </div>\n"
    "            </div>"
)

_TASK_SURFACE = (
    '            <div class="app-surface app-surface--task" aria-hidden="true">\n'
    '              <div class="task-title">Prepare Q1 review presentation</div>\n'
    '              <p class="surface-label">Notes</p>\n'
    '              <div class="task-notes">Include team metrics, project outcomes, '
    "and individual contributions. Needs it by Friday.</div>\n"
    '              <div class="task-priority">\n'
    '                <span class="task-priority__flag">!</span>\n'
    "                <div>\n"
    '                  <p class="task-priority__label">Priority</p>\n'
    '                  <p class="task-priority__value">Do First</p>\n'
    "                </div>\n"
    "              </div>\n"
    f'              <span class="surface-btn surface-btn--full">{_icon("check")} Complete</span>\n'
    "            </div>"
)

GALLERY_SURFACES = (
    _CAPTURE_SURFACE,
    _BRIEFING_SURFACE,
    _GOALS_SURFACE,
    _TASK_SURFACE,
)


def _render_gallery(captions: list[str]) -> str:
    return "\n".join(
        '          <figure class="gallery-card">\n'
        f"{surface}\n"
        f"            <figcaption>{_text(caption)}</figcaption>\n"
        "          </figure>"
        for surface, caption in zip(GALLERY_SURFACES, captions)
    )


def render_page(
    locale: str,
    data: dict[str, Any],
    locales: dict[str, dict[str, Any]],
    template: str,
) -> str:
    gallery = _render_gallery(data["gallery"]["captions"])
    privacy_points = "\n".join(
        "          <article class=\"privacy-point\">"
        f'<span aria-hidden="true">0{index}</span>'
        f"<div><h3>{_text(item['title'])}</h3>"
        f"<p>{_text(item['body'])}</p></div></article>"
        for index, item in enumerate(data["privacy"]["points"], start=1)
    )
    faq_items = "\n".join(
        "          <details>"
        f"<summary>{_text(item['question'])}</summary>"
        f"<p>{_text(item['answer'])}</p></details>"
        for item in data["faq"]["items"]
    )
    trust_strip = "\n".join(
        f'        <div class="trust-strip__item">'
        f'<span class="trust-strip__icon" aria-hidden="true">{_icon(icon)}</span>'
        f"<strong>{_text(item)}</strong></div>"
        for icon, item in zip(
            ("shield-check", "cloud-off", "ban", "cpu"),
            data["hero"]["trust"],
        )
    )
    how_items = "\n".join(
        "          <li class=\"step-card\">"
        f'<span class="step-card__number">{index}</span>'
        f"<div><h3>{_text(item['title'])}</h3>"
        f"<p>{_text(item['body'])}</p></div></li>"
        for index, item in enumerate(data["how"]["items"], start=1)
    )
    updates = "\n".join(
        f'          <li><span aria-hidden="true">{_icon("check")}</span>'
        f"{_text(item)}</li>"
        for item in data["updates"]["items"]
    )
    features = "\n".join(
        f'          <li><span aria-hidden="true">{_icon("check")}</span>'
        f"{_text(item)}</li>"
        for item in data["features"]["items"]
    )

    common = data["common"]
    replacements = {
        "LANG": locale,
        "TITLE": data["seo"]["title"],
        "META_DESCRIPTION": data["seo"]["description"],
        "CANONICAL_URL": _page_url(data),
        "OG_LOCALE": data["ogLocale"],
        "SOCIAL_IMAGE_ALT": data["hero"]["title"],
        "SOCIAL_CARD_FILE": SOCIAL_CARD_FILES[locale],
        "OG_ALTERNATES": _render_og_alternates(locale, locales),
        "HREFLANG_LINKS": _render_hreflang(locales),
        "STRUCTURED_DATA": _render_structured_data(locale, data),
        "SKIP_LINK": common["skipLink"],
        "NAV_ARIA": common["navigation"],
        "HOME_URL": _page_href(data),
        "NAV_BENEFITS": data["nav"]["benefits"],
        "NAV_HOW": data["nav"]["how"],
        "NAV_PRIVACY": data["nav"]["privacy"],
        "NAV_UPDATES": data["nav"]["updates"],
        "NAV_INSTALL": data["nav"]["install"],
        "LANGUAGE_LABEL": common["language"],
        "LANGUAGE_OPTIONS": _render_language_options(locale, locales),
        "LANGUAGE_LINKS": _render_language_links(locale, locales),
        "MENU_LABEL": common["menu"],
        "CLOSE_MENU_LABEL": common["closeMenu"],
        "HERO_SURFACE": HERO_SURFACE_HTML,
        "PLAY_URL": PLAY_URL,
        "PLAY_ARIA": common["playAria"],
        "BADGE_FILE": BADGE_FILES[locale],
        "HERO_EYEBROW": data["hero"]["eyebrow"],
        "HERO_TITLE": data["hero"]["title"],
        "HERO_BODY": data["hero"]["body"],
        "HERO_SECONDARY_CTA": data["hero"]["secondaryCta"],
        "HERO_PROOF_LABEL": data["hero"]["proofLabel"],
        "TRUST_ARIA": data["benefits"]["eyebrow"],
        "TRUST_STRIP": trust_strip,
        "BENEFITS_EYEBROW": data["benefits"]["eyebrow"],
        "BENEFITS_TITLE": data["benefits"]["title"],
        "BENEFITS_BODY": data["benefits"]["body"],
        "BENEFIT_ITEMS": _render_cards(
            data["benefits"]["items"],
            "outcome-card",
            ("target", "zap", "flag"),
        ),
        "HOW_EYEBROW": data["how"]["eyebrow"],
        "HOW_TITLE": data["how"]["title"],
        "HOW_ITEMS": how_items,
        "GALLERY_EYEBROW": data["gallery"]["eyebrow"],
        "GALLERY_TITLE": data["gallery"]["title"],
        "GALLERY_BODY": data["gallery"]["body"],
        "GALLERY_ITEMS": gallery,
        "PRIVACY_EYEBROW": data["privacy"]["eyebrow"],
        "PRIVACY_TITLE": data["privacy"]["title"],
        "PRIVACY_BODY": data["privacy"]["body"],
        "PRIVACY_DETAIL": data["privacy"]["detail"],
        "PRIVACY_POINTS": privacy_points,
        "UPDATES_EYEBROW": data["updates"]["eyebrow"],
        "UPDATES_TITLE": data["updates"]["title"],
        "UPDATES_BODY": data["updates"]["body"],
        "UPDATE_ITEMS": updates,
        "FEATURES_EYEBROW": data["features"]["eyebrow"],
        "FEATURES_TITLE": data["features"]["title"],
        "FEATURE_ITEMS": features,
        "FREE_EYEBROW": data["free"]["eyebrow"],
        "FREE_TITLE": data["free"]["title"],
        "FREE_BODY": data["free"]["body"],
        "FREE_CTA": data["free"]["cta"],
        "FAQ_EYEBROW": data["faq"]["eyebrow"],
        "FAQ_TITLE": data["faq"]["title"],
        "FAQ_ITEMS": faq_items,
        "FINAL_TITLE": data["final"]["title"],
        "FINAL_BODY": data["final"]["body"],
        "FINAL_CTA": data["final"]["cta"],
        "FOOTER_TAGLINE": data["footer"]["tagline"],
        "FOOTER_PRIVACY": data["footer"]["privacy"],
        "FOOTER_TERMS": data["footer"]["terms"],
        "FOOTER_DELETE": data["footer"]["deleteData"],
        "FOOTER_CONTACT": data["footer"]["contact"],
        "FOOTER_RIGHTS": data["footer"]["rights"],
        "FOOTER_PLAY_TRADEMARK": data["footer"]["playTrademark"],
    }

    rendered = template
    raw_fragments = {
        "OG_ALTERNATES",
        "HREFLANG_LINKS",
        "STRUCTURED_DATA",
        "LANGUAGE_OPTIONS",
        "LANGUAGE_LINKS",
        "HERO_SURFACE",
        "TRUST_STRIP",
        "BENEFIT_ITEMS",
        "HOW_ITEMS",
        "GALLERY_ITEMS",
        "PRIVACY_POINTS",
        "UPDATE_ITEMS",
        "FEATURE_ITEMS",
        "FAQ_ITEMS",
    }
    for key, value in replacements.items():
        replacement = value if key in raw_fragments else _attribute(str(value))
        rendered = rendered.replace(f"{{{{{key}}}}}", replacement)

    unresolved = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", rendered)))
    if unresolved:
        raise ValueError(
            f"{locale} rendered with unresolved placeholders: {unresolved}"
        )
    return rendered


def _write_sitemap(
    output: Path,
    locales: dict[str, dict[str, Any]],
) -> None:
    localized_urls = [
        "  <url>\n"
        f"    <loc>{html.escape(_page_url(data))}</loc>\n"
        f"    <lastmod>{LAST_MODIFIED}</lastmod>\n"
        "  </url>"
        for data in locales.values()
    ]
    legal_urls = [
        "  <url>\n"
        f"    <loc>{SITE_URL}/{slug}.html</loc>\n"
        f"    <lastmod>{LAST_MODIFIED}</lastmod>\n"
        "  </url>"
        for slug in LEGAL_PAGES
    ]
    urls = "\n".join((*localized_urls, *legal_urls))
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    (output / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (output / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


def _render_legal_pages(output: Path) -> None:
    template = LEGAL_TEMPLATE_PATH.read_text(encoding="utf-8")
    for slug, metadata in LEGAL_PAGES.items():
        markdown_source = ROOT / "content" / f"{slug}.md"
        markdown_body = re.sub(
            r"\A# .+\n+",
            "",
            markdown_source.read_text(encoding="utf-8"),
            count=1,
        )
        rendered_markdown = markdown.markdown(
            markdown_body,
            extensions=("tables", "sane_lists"),
            output_format="html5",
        )
        table_label = _attribute(f"{metadata['title']} data table")
        rendered_markdown = rendered_markdown.replace(
            "<table>",
            f'<div class="table-wrap" role="region" '
            f'aria-label="{table_label}" tabindex="0"><table>',
        ).replace("</table>", "</table></div>")
        page = template
        replacements = {
            "TITLE": metadata["title"],
            "DESCRIPTION": metadata["description"],
            "SLUG": slug,
            "META": metadata["meta"],
            "CONTENT": rendered_markdown,
        }
        for key, value in replacements.items():
            replacement = value if key == "CONTENT" else _attribute(value)
            page = page.replace(f"{{{{{key}}}}}", replacement)
        output.joinpath(f"{slug}.html").write_text(page, encoding="utf-8")


def _cubic_bezier_points(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 24,
) -> list[tuple[float, float]]:
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        mt = 1 - t
        a = mt * mt * mt
        b = 3 * mt * mt * t
        c = 3 * mt * t * t
        d = t * t * t
        points.append(
            (
                a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
            )
        )
    return points


def _logo_contours() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Return the outer glyph and inner counter of the Prio "P" from logo.svg."""

    outer: list[tuple[float, float]] = [
        (36, 28),
        (36, 80),
        (46, 80),
        (46, 60),
        (56, 60),
    ]
    outer += _cubic_bezier_points((56, 60), (67, 60), (76, 51.5), (76, 44))
    outer += _cubic_bezier_points((76, 44), (76, 36.5), (67, 28), (56, 28))
    outer.append((36, 28))

    inner: list[tuple[float, float]] = [(46, 37), (55, 37)]
    inner += _cubic_bezier_points((55, 37), (61.5, 37), (67, 40.5), (67, 44))
    inner += _cubic_bezier_points((67, 44), (67, 47.5), (61.5, 51), (55, 51))
    inner += [(46, 51), (46, 37)]
    return outer, inner


def _render_master_icon() -> Image.Image:
    scale = ICON_MASTER_SIZE / 108
    image = Image.new("RGB", (ICON_MASTER_SIZE, ICON_MASTER_SIZE), ICON_BACKGROUND)
    draw = ImageDraw.Draw(image)
    outer, inner = _logo_contours()
    draw.polygon([(x * scale, y * scale) for x, y in outer], fill=ICON_FOREGROUND)
    draw.polygon([(x * scale, y * scale) for x, y in inner], fill=ICON_BACKGROUND)
    return image


def _write_brand_icons(output: Path) -> None:
    master = _render_master_icon()
    for filename, dimension in RASTER_ICONS.items():
        master.resize(
            (dimension, dimension),
            Image.Resampling.LANCZOS,
        ).save(output / filename, format="PNG", optimize=True)
    master.resize((256, 256), Image.Resampling.LANCZOS).save(
        output / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )


def _write_web_manifest(output: Path, description: str) -> None:
    manifest = {
        "name": SITE_NAME,
        "short_name": SITE_NAME,
        "description": description,
        "lang": "en-US",
        "dir": "ltr",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": MANIFEST_BACKGROUND_COLOR,
        "theme_color": MANIFEST_THEME_COLOR,
        "icons": [
            {
                "src": "/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }
    (output / "site.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _render_not_found(output: Path, en_data: dict[str, Any]) -> None:
    template = NOT_FOUND_TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "PLAY_URL": PLAY_URL,
        "PLAY_ARIA": en_data["common"]["playAria"],
        "BADGE_FILE": BADGE_FILES["en-US"],
    }
    page = template
    for key, value in replacements.items():
        page = page.replace(f"{{{{{key}}}}}", _attribute(str(value)))
    unresolved = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", page)))
    if unresolved:
        raise ValueError(f"404 page rendered with unresolved placeholders: {unresolved}")
    (output / "404.html").write_text(page, encoding="utf-8")


def _build_output(output: Path) -> None:
    locales = load_locales()
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    output.mkdir(parents=True)

    for filename in COPY_FILES:
        source = ROOT / filename
        if not source.is_file():
            raise FileNotFoundError(f"Required site asset is missing: {source}")
        shutil.copy2(source, output / filename)

    badge_source = ROOT / "assets" / "google-play"
    badge_output = output / "assets" / "google-play"
    badge_output.mkdir(parents=True)
    for filename in BADGE_FILES.values():
        source = badge_source / filename
        if not source.is_file():
            raise FileNotFoundError(f"Google Play badge is missing: {source}")
        shutil.copy2(source, badge_output / filename)

    social_source = ROOT / "assets" / "social"
    social_output = output / "assets" / "social"
    social_output.mkdir(parents=True)
    for filename in SOCIAL_CARD_FILES.values():
        source = social_source / filename
        if not source.is_file():
            raise FileNotFoundError(f"Localized social card is missing: {source}")
        shutil.copy2(source, social_output / filename)

    _write_brand_icons(output)
    _write_web_manifest(output, locales["en-US"]["seo"]["description"])

    for locale, data in locales.items():
        target = output if not data["path"] else output / data["path"]
        target.mkdir(parents=True, exist_ok=True)
        target.joinpath("index.html").write_text(
            render_page(locale, data, locales, template),
            encoding="utf-8",
        )

    _render_legal_pages(output)
    _render_not_found(output, locales["en-US"])
    _write_sitemap(output, locales)


def build(output: Path = DEFAULT_OUTPUT) -> None:
    output = output.resolve()
    staging = output.with_name(f".{output.name}.next")
    previous = output.with_name(f".{output.name}.previous")

    for transient in (staging, previous):
        if transient.exists():
            shutil.rmtree(transient)

    try:
        _build_output(staging)
        if output.exists():
            output.rename(previous)
        staging.rename(output)
    except Exception:
        if not output.exists() and previous.exists():
            previous.rename(output)
        raise
    else:
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the localized Prio site")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory (default: _site)",
    )
    args = parser.parse_args()
    build(args.output.resolve())
    print(f"Built {len(EXPECTED_LOCALES)} localized pages in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
