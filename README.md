# Prio marketing site

Static, localized marketing site for [Prio](https://prio.tl-dr.ch).

## Build and test

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s scripts/tests
python3 scripts/build_site.py --output _site
python3 scripts/preview_site.py --port 4173
```

`content/locales.json` is the canonical marketing-copy source. Every locale must
keep the same schema as `en-US`; the build validates coverage before rendering.
Pushing `main` runs the tests, builds `_site`, and deploys it with GitHub Pages.
The preview command stages a complete build before replacing `_site` and sends
no-cache headers so local browsers never mix markup and styles from different
revisions.

## App screenshots

The gallery shows real Android screens from the Prio repository's store
screenshot capture (`store-listing/screenshots/`). After a new capture, refresh
the committed responsive WebP files and rebuild:

```bash
python3 scripts/import_screenshots.py --source ../prio/store-listing/screenshots
```

The importer requires 1080x1920 sources and writes 540, 720, and 1080 px WebP
variants to `assets/screens/`. CI does not run it, so commit the regenerated
files. The hero matrix stays HTML/CSS, localized per locale under
`heroSurface`, so the largest above-the-fold element never waits on an image.
Gallery captions and alt text live in `gallery.items`, ordered like
`GALLERY_SCREENS` in `scripts/build_site.py`.

## Search indexing

The build emits static HTML for every locale, reciprocal `hreflang` links,
self-referencing canonicals, localized metadata, `Organization`, `WebSite`, and
`SoftwareApplication` structured data, a web app manifest with maskable icons,
an `apple-touch-icon`, favicons, a branded `404.html`, `robots.txt`, and
`sitemap.xml`. Brand icons are generated from `logo.svg` at build time, so the
mark stays in sync across the favicon, home-screen, and PWA sizes. Locale links
remain normal anchors so visitors and crawlers can reach every translation
without JavaScript.

After the first production deploy or a domain change:

1. Verify the `prio.tl-dr.ch` domain property in Google Search Console.
2. Submit `https://prio.tl-dr.ch/sitemap.xml`.
3. Inspect the root URL and at least one localized URL, then request indexing
   after a material launch update.
4. Monitor Page indexing and Core Web Vitals; fix reported crawl, canonical,
   mobile-usability, or structured-data errors.
5. Update `LAST_MODIFIED` in `scripts/build_site.py` only for significant
   content changes so sitemap freshness remains trustworthy.

These signals make the site crawlable and eligible for search features; no
implementation can guarantee indexing position or ranking.
