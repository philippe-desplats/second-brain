---
title: Writing
type: schema
entity: writing
version: 1
schema:
  claim?(array): string, "statement or promise made"
  proof?(array): string, "supporting proof or argument"
  cta?(array): string, "call to action"
  for?: Entity, "beneficiary entity"
  client?: ClientContext, "client involved if client scope"
  partner?: PartnerContext, "partner involved if partnership scope"
  based_on?: Research, "research that feeds this writing"
settings:
  validation: warn
  frontmatter:
    aliases?(array): string, "the note's own title, written by add_title_aliases.py so Obsidian can resolve it"
    date: string, "writing date in YYYY-MM-DD format"
    title: string, "title of the written content"
    writing_type(enum):
    - quote
    - contract
    - newsletter
    - post
    - outline
    - proposal
    - article
    - pitch-deck
    - email-signature
    - bio
    - landing-copy
    - video-script
    - specification
    - terms-of-sale
    - legal-notice
    - privacy-policy
    - letter
    - other
    category?(enum):
    - internal
    - client
    - partner
    - personal
    client?: ClientContext, "client involved if client scope"
    partner?: PartnerContext, "partner involved if partnership scope"
    status?(enum):
    - draft
    - review
    - final
    - sent
    - archived
    destination?: string, "target channel, e.g. LinkedIn, billing tool, Email, print, website"
    based_on?: Research, "research that feeds this writing"
---

# Schema, Writing

Written content meant to be distributed or copied into another tool (billing tool, LinkedIn, email, website). A broad type covering many writing formats, disciplined by the `writing_type` field.

Usable in every workspace zone. If a dominant `writing_type` emerges, consider promoting it to a dedicated schema later.

## Typical location

`sources/{zone}/{entity}/{project}/YYYY-MM-DD-writing-slug.md`, with an optional `content/` subfolder.

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

## Reference examples

- `sources/clients/vandelay/seo/2026-02-18-writing-quote-content.md` (quote)
- `sources/clients/northwind/website/content/2026-03-06-writing-content-outline.md` (outline)
- `sources/partners/dimwave/support/deliverables/2026-04-06-writing-newsletter-dimwave.md` (newsletter)
- `sources/internal/email-signature/2026-04-14-writing-signature-jane.md` (signature, internal)

## Difference with deliverable

A `writing` is the raw content being drafted. A `deliverable` is the finalized and delivered version. The transition happens when `writing.status` moves to `final` (then the file can be moved or duplicated into a `deliverable`).

## Expected observations

- `[claim]` statement or promise made
- `[proof]` supporting proof or argument
- `[cta]` call to action

## Typed relations in the frontmatter

- `client` or `partner`, beneficiary if scope identified
- `based_on`, source research

## Additional relations in markdown

- `for [[Entity]]`, beneficiary as a text link

## Minimal example

```yaml
---
date: 2026-02-18
title: Vandelay SEO quote content
type: writing
schema_version: 1
writing_type: quote
category: client
client: Vandelay
status: final
destination: billing tool
based_on: Vandelay SEO audit 2026-02
---

# Vandelay quote content, SEO

## Observations
- [claim] Improved local SEO within 3 months
- [proof] Preliminary audit documents 42 usable keywords
- [cta] Quote approval for a March 2026 start

## Relations
- for [[Vandelay]]
```
