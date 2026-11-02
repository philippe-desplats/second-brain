---
title: Session
type: schema
entity: session
version: 1
schema:
  done?(array): string, "work actually completed during the session"
  next?(array): string, "next step, ideally the very first thing to pick up"
  blocker?(array): string, "what is blocking, and what would unblock it"
  decision?(array): string, "decision taken during the session"
  open-question?(array): string, "question raised and left unanswered"
  about?: ProjectBrief, "project worked on"
  continues?: Session, "previous session on the same thread"
  client?: ClientContext, "client involved if client-scoped"
  partner?: PartnerContext, "partner involved if partnership-scoped"
settings:
  validation: warn
  frontmatter:
    aliases?(array): string, "the note's own title, written by add_title_aliases.py so Obsidian can resolve it"
    date: string, "session date in YYYY-MM-DD format"
    title: string, "what the session was about, in one line"
    status?(enum):
    - open
    - closed
    category?(enum):
    - internal
    - client
    - partner
    - personal
    duration?: string, "indicative duration, e.g. 2h, 45min"
    tags?(array): string, "free-form keywords"
    client?: ClientContext, "client involved if client-scoped"
    partner?: PartnerContext, "partner involved if partnership-scoped"
    about?: ProjectBrief, "project worked on"
    continues?: Session, "previous session on the same thread"
    written_by?(enum):
    - owner
    - agent
---

# Schema, Session

End-of-session memory. Records what a working session actually produced, what is left, and what would block the next one, so the following session starts from a point of resumption instead of a search.

Written by `/close-session` at the end of a session, or by hand. Usable in every workspace zone.

## Typical location

`sources/{zone}/{entity}/{project}/sessions/YYYY-MM-DD-session-slug.md`

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

## Reference example

`sources/clients/globex/website-redesign/sessions/2026-06-23-session-content-inventory.md`

## Why this is its own type

Basic Memory filters by the `type:` field, through `note_types` in `search_notes`. A session filed as a `note` with `note_type: session` would therefore be unreachable by the one query that justifies writing it: "give me the last point of resumption on this project". The same reasoning separates `transcript` from `meeting`.

## Difference from other types

- A `meeting` records what several people said to each other. A `session` records what one person, or one person and their agent, actually got done.
- A `note` with `note_type: checkpoint` is a status point on a project, written when it is useful. A `session` is written at the end of a session, every time, and always carries a `[next]`.
- A `project-brief` holds the durable objective. A `session` holds the perishable state.

## Expected observations

- `[done]` work actually completed, not work attempted
- `[next]` next step, ideally the very first thing to pick up
- `[blocker]` what is blocking, and what would unblock it
- `[decision]` decision taken during the session
- `[open-question]` question raised and left unanswered

## Typed relations in the frontmatter

- `about`, project worked on
- `continues`, previous session on the same thread
- `client` or `partner`, entity involved if relevant

## Status values

- `open`, the thread is alive, `[next]` items remain
- `closed`, the thread is finished, nothing is waiting

`open` is the useful default: it makes every unfinished thread listable in one query.

## Resuming from a session

Retrieval, in order of preference:

1. Basic Memory, `search_notes` with `note_types=["session"]` and the project name, then `build_context` on the returned `memory://` URI to follow `continues` backwards through the thread
2. Without Basic Memory, list `sources/{zone}/{entity}/{project}/sessions/` and read the most recent file

## Minimal example

```yaml
---
date: 2026-06-23
title: Content inventory before the redesign
type: session
schema_version: 1
status: open
category: client
duration: "2h"
client: Globex
tags: [content, discovery]
about: Globex Website Redesign
---

# Session, content inventory before the redesign

Went through the existing site page by page to size the content work. The inventory is complete, the arbitration on what gets dropped is not.

## Observations
- [done] Full inventory of the 128 existing pages, exported to the project root
- [done] 31 pages identified as dead, no traffic over 12 months
- [next] Get the client arbitration on the 31 dead pages before touching the tree
- [blocker] No analytics access on the blog subdomain, asked Jane on 06-23
- [decision] The legacy blog stays out of scope for v1
- [open-question] Do the 2019 press releases have any legal retention obligation

## Relations
- client [[Globex]]
- about [[Globex Website Redesign]]
```
