# inbox/

A buffer for captures that are not yet classified. When you grab something quickly and do not know where it belongs, drop it here, then file it into `sources/`, `knowledge/`, or `atlas/` within a week.

## Conventions

- **7-day rule.** Nothing stays in `inbox/` longer than 7 days. An item still here after a week gets classified or deleted, never left to rot.
- **Naming.** `YYYY-MM-DD-description.md`, so the capture date is always visible and items sort chronologically.
- **Classify with the three questions.** Raw artifact -> `sources/`. Distilled reusable knowledge -> `knowledge/`. Index, map, or entity -> `atlas/`.
- The `/curate` skill flags stale inbox items during its review pass.
- This is a staging area, not a filing zone. Do not build structure or subfolders here.

## Web clippings land here

`templates/obsidian-web-clipper.json` is a ready-made template for the [Obsidian Web Clipper](https://obsidian.md/clipper) browser extension. Import it once (extension settings, Templates, drag the file in) and every page you clip arrives here as `YYYY-MM-DD-clipping-slug.md`, already carrying `type: clipping` and its `source_url`, conforming to `basic-memory/schemas/clipping.md`.

From there they follow the same 7-day rule as everything else: `/capture -i` files them into the project they belong to, under a `clippings/` subfolder. A clip with no project goes to a watch project, for example `sources/internal/watch/clippings/`, never to a zone root.

No Obsidian? Paste the URL into `/capture` and it does the same job, one page at a time.
