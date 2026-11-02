---
title: Meeting
type: schema
entity: meeting
version: 1
schema:
  decision?(array): string, "decision made during the meeting"
  action?(array): string, "action to take, ideally with owner and deadline"
  risk?(array): string, "risk or point of attention identified"
  milestone?(array): string, "milestone or key event"
  question?(array): string, "question raised without an immediate answer"
  with?(array): Entity, "participants or entities met"
  produces?(array): Deliverable, "resulting deliverable"
  client?: ClientContext, "client involved if client-scoped"
  partner?: PartnerContext, "partner involved if partnership-scoped"
  about?: ProjectBrief, "project involved"
  follows?: Meeting, "previous report in the same series"
settings:
  validation: warn
  frontmatter:
    aliases?(array): string, "the note's own title, written by add_title_aliases.py so Obsidian can resolve it"
    date: string, "meeting date in YYYY-MM-DD format"
    title: string, "meeting title"
    participants(array): string, "list of participants with full name"
    time?: string, "start time in HH:MM format, mandatory quotes"
    duration?: string, "indicative duration, e.g. 1h, 45min"
    source?: string, "recording URL if any"
    format?(enum):
    - report
    - transcript
    - hybrid
    status?(enum):
    - scheduled
    - done
    - cancelled
    category?(enum):
    - client
    - partner
    - internal
    - personal
    tags?(array): string, "free-form keywords"
    client?: ClientContext, "client involved if client-scoped"
    partner?: PartnerContext, "partner involved if partnership-scoped"
    about?: ProjectBrief, "project involved"
    follows?: Meeting, "previous report in the same series"
---

# Schema, Meeting

Report of a meeting, workshop, call, video conference, or in-person encounter. Captures decisions, actions, and points of attention. The `format` field distinguishes a structured report, a raw transcript, or a hybrid (report plus transcript embedded at the bottom).

Usable in every workspace zone, internal team workshops included.

## Typical location

`sources/{zone}/{entity}/{project}/meetings/YYYY-MM-DD-meeting-slug.md`

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

## Reference example

`sources/clients/globex/website-redesign/meetings/2026-06-22-meeting-kickoff.md`

## Expected observations

- `[decision]` decision made during the meeting
- `[action]` action to take, ideally with owner and deadline
- `[risk]` risk or point of attention identified
- `[milestone]` milestone or key event
- `[question]` question raised without an immediate answer

## Typed relations in the frontmatter

- `client` or `partner`, entity met
- `about`, project involved
- `follows`, previous report in the series

## Additional relations in markdown

- `with [[Person]]` or `with [[Entity]]`, participants or entities met
- `produces [[Deliverable]]`, resulting deliverable

## YAML notes

- `time` always in quotes, `"08:30"` not `08:30`

## Minimal example

```yaml
---
date: 2026-04-15
title: Automation workshop report
type: meeting
schema_version: 1
participants:
  - Jane Doe
  - Morgan Reed
time: "08:30"
duration: "1h"
source: https://example.com/rec/xyz
format: hybrid
status: done
category: partner
tags: [automation, n8n]
partner: Morgan Reed
about: Automation with Morgan Reed
---

# Report, Automation workshop

## Observations
- [decision] Validation of the tripartite framework
- [action] Jane delivers the N8N POC by 2026-04-22

## Relations
- with [[Morgan Reed]]
- produces [[N8N POC Morgan Reed]]
```
