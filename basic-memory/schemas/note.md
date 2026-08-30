---
title: Note
type: schema
entity: note
version: 1
schema:
  context?(array): string, "project context"
  summary?(array): string, "summary of an exchange"
  checkpoint?(array): string, "status point"
  reminder?(array): string, "memory aid"
  task?(array): string, "task to do"
  client?: ClientContext, "client involved if relevant"
  partner?: PartnerContext, "partner involved if relevant"
  about?: Topic, "topic or project involved"
settings:
  validation: warn
  frontmatter:
    date: string, "note date in YYYY-MM-DD format"
    title: string, "short, descriptive title"
    note_type?(enum):
    - summary
    - context
    - cheatsheet
    - reading
    - journal
    - history
    - checkpoint
    - reminder
    - todo
    - other
    subtype?(enum):
    - moc
    - index
    - pattern
    - playbook
    - guide
    - runbook
    - decision
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
    topics?(array): string, "topic slugs this note belongs to, read by the MOC Bases views"
    about?: Topic, "topic or project involved"
    written_by?(enum):
    - owner
    - agent
---

# Schema, Note

Catch-all for short captures, summaries, histories, reading notes, memory aids, and project context. Free structure, short format (often 10 to 40 lines).

Usable in every workspace zone. The `note_type` field is optional but strongly recommended to avoid a sprawling catch-all that gets drowned at scale.

## Typical location

`sources/{zone}/{entity}/{project}/YYYY-MM-DD-note-slug.md`, with an optional `notes/` subfolder.

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

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
- `journal`, dated daily entry, quick captures of the day
- `history`, summarized history of exchanges
- `checkpoint`, status point of a project
- `reminder`, reminder of an action to take
- `todo`, operational checklist
- `other`, case not covered

## Daily journal

A journal entry is a `note` with `note_type: journal`, one file per day, filed in its own project folder:

`sources/personal/journal/YYYY-MM-DD-note-journal.md`, or `sources/internal/journal/` when the `personal` zone was pruned at setup.

Obsidian users get this for free: the Daily notes core plugin is preconfigured in `.obsidian/daily-notes.json` to write at that path, with that filename, from `templates/journal-template.md`. The folder ships with the workspace and must keep existing, since Obsidian does not create a missing daily-notes folder; it refuses with `Folder "..." not found`. Everyone else creates the file by hand or through `/capture`.

The `category` field is deliberately absent from the journal template. It is optional, and an absent field beats a wrong one when the journal may live under either zone.

An empty journal entry is valid. The point of the journal is a place to put a thought in five seconds, not a form to fill.

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
type: note
schema_version: 1
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

## Relations
- client [[Northwind]]
- about [[Northwind website]]
```
