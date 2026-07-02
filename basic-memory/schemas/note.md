---
title: Note
type: schema
entity: note
schema_version: 1
schema:
  date: string, "note date in YYYY-MM-DD format"
  title: string, "short, descriptive title"
  note_type?(enum):
  - summary
  - context
  - cheatsheet
  - reading
  - history
  - checkpoint
  - reminder
  - todo
  - other
  category?(enum):
  - internal
  - client
  - partner
  - personal
  client?: ClientContext, "client involved if relevant"
  partner?: PartnerContext, "partner involved if relevant"
  status?(enum):
  - draft
  - active
  - archived
  tags?(array): string, "free-form keywords"
  about?: Topic, "topic or project involved"
settings:
  validation: warn
---

# Schema, Note

Catch-all for short captures, summaries, histories, reading notes, memory aids, and project context. Free structure, short format (often 10 to 40 lines).

Usable for all 4 categories. The `note_type` field is optional but strongly recommended to avoid a sprawling catch-all that gets drowned at scale.

## Typical location

- `sources/clients/{client}/{project}/YYYY-MM-DD-note-slug.md`
- `sources/partners/{partner}/{project}/YYYY-MM-DD-note-slug.md`
- `sources/internal/{project}/YYYY-MM-DD-note-slug.md`
- `sources/personal/{project}/YYYY-MM-DD-note-slug.md`
- A `notes/` subfolder is possible in each case

## Reference examples

- `sources/clients/taylor-brooks/seo-audit/2026-02-18-note-seo-audit.md` (client)
- `sources/clients/penword/reviews/notes/2026-04-02-note-quote-details.md` (client, subfolder)
- `sources/internal/community/2026-03-14-note-product-watch-newsletter.md` (internal)

## Difference from other types

Use `note` when no other type fits. If the content grows (more than 50 lines) or becomes structured, promote it to `research`, `brainstorm`, or `strategy` and archive the note.

## note_type values

- `summary`, summary of an exchange or information
- `context`, brief project context
- `cheatsheet`, personal reminder or quick reference
- `reading`, reading note on an article, book, or doc
- `history`, summarized history of exchanges
- `checkpoint`, status point of a project
- `reminder`, reminder of an action to take
- `todo`, operational checklist
- `other`, case not covered

## Expected observations

Free categories depending on the context. A few useful examples:

- `[context]` project context
- `[summary]` summary of an exchange
- `[checkpoint]` status point
- `[reminder]` memory aid
- `[task]` task to do

## Typed relations in the frontmatter

- `about`, topic or project involved
- `client` or `partner`, entity involved if relevant

## Minimal example

```yaml
---
date: 2026-04-13
title: Northwind v1 client feedback summary
note_type: summary
category: client
client: Northwind
status: active
tags: [summary, website]
about: Northwind website
---

# Summary of v1 client feedback

## Observations
- [summary] 3 pieces of feedback on the v1 site, all positive on the design
- [context] Awaiting iteration on the mobile side
- [reminder] Follow up with Casey in late April on the v2 schedule
```
