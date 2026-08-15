---
title: Email
type: schema
entity: email
version: 1
schema:
  decision?(array): string, "decision shared in the email"
  action?(array): string, "action started or requested"
  commitment?(array): string, "commitment made, a deadline, a deliverable, a reply"
  question?(array): string, "question asked or received"
  to?(array): Person, "recipient, on an outgoing email or a reply"
  from?: Person, "sender, on an incoming email"
  for?: Entity, "context beneficiary entity"
  about?: ProjectBrief, "project involved"
  replies_to?: Email, "previous email in the thread"
settings:
  validation: warn
  frontmatter:
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
    about?: ProjectBrief, "project involved"
    replies_to?: Email, "previous email in the thread"
---

# Schema, Email

Represents an incoming email, an outgoing email, or a reply. Canonical source, `.claude/rules/emails.md`. Two improvements over the historical convention, `to` and `cc` become YAML arrays (robust filtering), and the `category` field is added to record which workspace zone the email belongs to.

## Typical location

Usable in every workspace zone.

`sources/{zone}/{entity}/{project}/emails/YYYY-MM-DD-{seq}-{direction}-slug.md`

Live example in this repository, `sources/clients/globex/website-redesign/emails/2026-06-15-01-in-kickoff-questions.md`.

`{zone}` is a zone under `sources/` and `{entity}` a client or partner folder; entity-less zones such as `internal` and `personal` hold their projects directly under the zone.

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
- `for [[Entity]]` context beneficiary

## Important YAML notes

- If the `subject` contains `:`, `#`, `&`, `*`, `[`, `]`, put it in quotes
- The `time` field must be in quotes to avoid YAML interpreting it as a number

## Example

```yaml
---
type: email
schema_version: 1
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
