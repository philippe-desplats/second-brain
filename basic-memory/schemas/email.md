---
title: Email
type: schema
entity: email
schema_version: 1
schema:
  date: string, "email date in YYYY-MM-DD format"
  time: string, "time of sending or receipt in HH:MM format, in quotes"
  seq: integer, "chronological number within the day, starts at 1"
  direction(enum):
  - out
  - in
  - reply
  status(enum):
  - draft
  - sent
  - cancelled
  from: string, "sender full name"
  to(array): string, "list of primary recipients"
  subject: string, "email subject"
  category?(enum):
  - client
  - partner
  - internal
  - personal
  cc?(array): string, "list of people in copy"
  thread?: string, "conversation thread identifier in kebab-case"
  about?: Project, "project involved"
  replies_to?: Email, "previous email in the thread"
settings:
  validation: warn
---

# Schema, Email

Represents an incoming email, an outgoing email, or a reply. Canonical source, `.claude/rules/emails.md`. Two improvements over the historical convention, `to` and `cc` become YAML arrays (robust filtering), and the `category` field is added to distinguish clients, partners, internal, and personal.

## Typical location

Usable for all 4 categories.

- `sources/clients/{client}/{project}/emails/YYYY-MM-DD-{seq}-{direction}-slug.md`
- `sources/partners/{partner}/{project}/emails/YYYY-MM-DD-{seq}-{direction}-slug.md`
- `sources/internal/{project}/emails/YYYY-MM-DD-{seq}-{direction}-slug.md`
- `sources/personal/{project}/emails/YYYY-MM-DD-{seq}-{direction}-slug.md`

## Naming convention

`YYYY-MM-DD-{seq}-{direction}-slug.md`

- `seq`, `01`, `02`, `03`... restarts each new day, counts all emails (out, in, reply), including cancelled ones that keep their number
- `direction`, `out` sending, `in` receipt, `reply` reply
- `slug`, kebab-case, short and descriptive

## Status values

- `draft`, email being drafted, not sent
- `sent`, email sent or received (for incoming ones)
- `cancelled`, abandoned email, keep the file for traceability

## Expected observations

- `[decision]` decision shared in the email
- `[action]` action started or requested
- `[commitment]` commitment made (deadline, deliverable, reply)
- `[question]` question asked or received

## Typed relations in the frontmatter

- `about`, project involved
- `replies_to`, previous email in the thread

## Additional relations in markdown

- `to [[Person]]` or `from [[Person]]` depending on direction, link to the person entity
- `for [[Client | Partner | Internal]]` context beneficiary

## Important YAML notes

- If the `subject` contains `:`, `#`, `&`, `*`, `[`, `]`, put it in quotes
- The `time` field must be in quotes to avoid YAML interpreting it as a number

## Example

```yaml
---
date: 2026-04-08
time: "09:15"
seq: 1
direction: out
status: sent
from: Jane Doe
to:
  - Sam Rivera
  - Chris Bell
cc:
  - Robin Lee
subject: "Re: Technical details for the RFP, item 11"
thread: umbrella-rfp-item11
category: client
about: Umbrella tender 2026
replies_to: 2026-04-07-03-in-technical-question
---

Hello Sam,

[Email body]

Best regards,
Jane

## Relations
- to [[Sam Rivera]]
- from [[Jane Doe]]
- for [[Umbrella]]
```
