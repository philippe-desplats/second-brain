---
title: Writing
type: schema
entity: writing
schema_version: 1
schema:
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
  - journal
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
settings:
  validation: warn
---

# Schema, Writing

Written content meant to be distributed or copied into another tool (billing tool, LinkedIn, email, website). A broad type covering many writing formats, disciplined by the `writing_type` field.

Usable for the 4 categories. If a dominant `writing_type` emerges, consider promoting it to a dedicated schema later.

## Typical location

- `sources/clients/{client}/{project}/YYYY-MM-DD-writing-slug.md`
- `sources/partners/{partner}/{project}/YYYY-MM-DD-writing-slug.md`
- `sources/internal/{project}/YYYY-MM-DD-writing-slug.md`
- `sources/personal/{project}/YYYY-MM-DD-writing-slug.md`
- A `content/` subfolder is possible in each case

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

- `for [[Client | Partner | Internal]]`, beneficiary as a text link

## Minimal example

```yaml
---
date: 2026-02-18
title: Vandelay SEO quote content
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
