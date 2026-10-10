#!/usr/bin/env python3
"""Convert committed Prio Play Store screenshots into responsive gallery WebPs.

The source is the app repository's ``store-listing/screenshots`` directory,
captured on the Android emulator by ``android/scripts/generate_store_screenshots.sh``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_site import (  # noqa: E402
    GALLERY_SCREENS,
    ROOT,
    SCREEN_SIZE,
    SCREEN_WIDTHS,
    SCREENS_DIR,
)

DEFAULT_SOURCE = ROOT.parent / "prio" / "store-listing" / "screenshots"
WEBP_QUALITY = 82

SOURCE_FILES = {
    "quick-capture": "02_quick_capture.png",
    "morning-briefing": "03_morning_briefing.png",
    "goal-health": "04_goals_progress.png",
    "calendar": "07_calendar_view.png",
    "privacy-controls": "05_settings_privacy.png",
    "today-dark": "08_dark_mode.png",
}


def import_screenshots(source: Path, output: Path = SCREENS_DIR) -> list[Path]:
    if set(SOURCE_FILES) != set(GALLERY_SCREENS):
        raise ValueError("SOURCE_FILES must map every gallery screen exactly once")
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in GALLERY_SCREENS:
        path = source / SOURCE_FILES[name]
        if not path.is_file():
            raise FileNotFoundError(f"Screenshot source is missing: {path}")
        with Image.open(path) as image:
            if image.size != SCREEN_SIZE:
                raise ValueError(
                    f"{path} must be {SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}, "
                    f"found {image.size[0]}x{image.size[1]}"
                )
            rgb = image.convert("RGB")
            for width in SCREEN_WIDTHS:
                height = round(width * SCREEN_SIZE[1] / SCREEN_SIZE[0])
                resized = (
                    rgb
                    if width == SCREEN_SIZE[0]
                    else rgb.resize((width, height), Image.Resampling.LANCZOS)
                )
                target = output / f"{name}-{width}.webp"
                resized.save(target, format="WEBP", quality=WEBP_QUALITY, method=6)
                written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Screenshot directory (default: {DEFAULT_SOURCE})",
    )
    args = parser.parse_args()
    written = import_screenshots(args.source.resolve())
    total = sum(path.stat().st_size for path in written)
    print(f"Wrote {len(written)} WebP files ({total / 1024:.0f} KiB) to {SCREENS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
