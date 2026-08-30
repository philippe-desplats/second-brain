---
title: Clipping
type: schema
entity: clipping
version: 1
schema:
  quote?(array): string, "passage worth keeping verbatim"
  takeaway?(array): string, "what this changes for us, in our own words"
  question?(array): string, "question the source raises"
  about?: Topic, "subject the clipping documents"
  cited_in?(array): Deliverable, "deliverable that reuses the source"
  client?: ClientContext, "client involved if the clipping was captured for one"
  partner?: PartnerContext, "partner involved if the clipping was captured for one"
settings:
  validation: warn
  frontmatter:
    date: string, "capture date in YYYY-MM-DD format"
    title: string, "title of the captured page"
    source_url: string, "canonical URL of the captured page"
    author?: string, "author of the source"
    published?: string, "publication date of the source, YYYY-MM-DD when known"
    site?: string, "site or publisher name"
    status?(enum):
    - unread
    - read
    - archived
    category?(enum):
    - internal
    - client
    - partner
    - personal
    tags?(array): string, "free-form keywords"
    client?: ClientContext, "client involved if the clipping was captured for one"
    partner?: PartnerContext, "partner involved if the clipping was captured for one"
    about?: Topic, "subject the clipping documents"
---

# Schema, Clipping

An external page captured into the workspace: an article, a documentation page, a thread, a post. Content someone else wrote, kept because it will be needed again.

Fed by the Obsidian Web Clipper through `templates/obsidian-web-clipper.json`, or by `/capture` when a URL is pasted. Usable in every workspace zone.

## Typical location

`sources/{zone}/{entity}/{project}/clippings/YYYY-MM-DD-clipping-slug.md`

A clipping tied to no project is still not filed at a zone root: put it in a watch project, for example `sources/internal/watch/clippings/`. Captures land in `inbox/` first and get filed from there, within the 7-day rule.

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

## Reference example

`sources/clients/globex/website-redesign/clippings/2026-06-24-clipping-progressive-disclosure-in-b2b-search.md`

## Difference from other types

- `research` is what you produce: sourced, structured, argued. `clipping` is what you captured: someone else's page, kept close to verbatim.
- A `note` with `note_type: reading` is your reading note about a source. A `clipping` is the source. The two coexist: the clipping holds the material, the note holds your thinking.
- Once several clippings on one subject start saying the same thing, that is the signal to `/distill` them into `knowledge/`.

## Dates, and which is which

`date` is the capture date, consistent with every other type in this workspace where `date` is when the artifact entered the workspace or happened. The source's own publication date lives in `published`, and is often unknown, which is why it is optional.

## Expected observations

- `[quote]` passage worth keeping verbatim, with quotation marks
- `[takeaway]` what this changes for us, in our own words, not the author's
- `[question]` question the source raises

A clipping with no `[takeaway]` is a bookmark. That is a legitimate state on the day of capture, and a bad state three months later.

## Status values

- `unread`, captured but not yet read. This is the value both capture paths write, the Web Clipper template and `/capture`, because neither reads the page
- `read`, read, and the observations reflect it
- `archived`, kept for the record, no longer live

## Typed relations in the frontmatter

- `about`, subject the clipping documents
- `client` or `partner`, entity involved if the clipping was captured for one

## Additional relations in markdown

- `cited_in [[Deliverable]]`, deliverable that reuses the source

## On storing someone else's content

A clipping is a personal working copy, kept for retrieval. Keep the `source_url` on every clipping so the origin is always one click away, credit the author in `author`, and never move captured text into a client deliverable without attribution.

## Minimal example

```yaml
---
date: 2026-06-24
title: Progressive disclosure in B2B search interfaces
type: clipping
schema_version: 1
source_url: https://example.com/articles/progressive-disclosure-b2b-search
author: Robin Vasquez
published: 2026-05-30
site: Example Journal
status: read
category: client
client: Globex
tags: [search, ux]
about: Catalog Search
---

# Progressive disclosure in B2B search interfaces

## Observations

- [quote] "Trade buyers do not browse, they verify: they arrive knowing the part number and leave if the first screen cannot confirm it."
- [takeaway] Our catalog search should treat the part number as the primary path and faceted browsing as the fallback, which is the opposite of the current build order
- [question] Does this hold when the buyer knows the machine but not the part

## Relations

- client [[Globex]]
- about [[Catalog Search]]
```
