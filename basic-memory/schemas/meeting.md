---
title: Meeting
type: schema
entity: meeting
schema_version: 1
schema:
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
  about?: Project, "project involved"
  follows?: Meeting, "previous report in the same series"
settings:
  validation: warn
---

# Schema, Meeting

Report of a meeting, workshop, call, video conference, or in-person encounter. Captures decisions, actions, and points of attention. The `format` field distinguishes a structured report, a raw transcript, or a hybrid (report plus transcript embedded at the bottom).

Usable for all 4 categories, client, partnership, internal (team workshops), personal.

## Typical location

- `sources/clients/{client}/{project}/meetings/YYYY-MM-DD-meeting-slug.md`
- `sources/partners/{partner}/{project}/meetings/YYYY-MM-DD-meeting-slug.md`
- `sources/internal/{project}/meetings/YYYY-MM-DD-meeting-slug.md`
- `sources/personal/{project}/meetings/YYYY-MM-DD-meeting-slug.md`

## Reference example

`sources/partners/morgan-reed/automation/meetings/2026-04-15-meeting-automation-partnership.md`

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

- `with [[Person]]` or `with [[Client | Partner]]`, participants or entities met
- `produces [[Deliverable]]`, resulting deliverable

## YAML notes

- `time` always in quotes, `"08:30"` not `08:30`

## Minimal example

```yaml
---
date: 2026-04-15
title: Automation workshop report
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
