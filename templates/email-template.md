# Template, Email

> This template defines the standard structure for email files in the workspace.

## Naming convention

```
YYYY-MM-DD-{seq}-{direction}-{slug}.md
```

| Field | Description | Values |
|-------|-------------|--------|
| `seq` | Sequential number within the day | `01`, `02`, `03`... |
| `direction` | Direction of the email | `out` (sent), `in` (received), `reply` (response) |
| `slug` | Short kebab-case description | e.g. `commercial-proposal` |

### Examples

```
2026-07-02-01-out-commercial-proposal.md
2026-07-02-02-reply-quote-validation.md
2026-07-02-03-out-content-follow-up.md
2026-07-02-04-in-client-photo-feedback.md
```

## Required frontmatter

```yaml
---
date: 2026-07-02
time: "14:30"
seq: 1
direction: out
status: sent
from: Jane Doe
to: Alex Martin
cc: Sam Rivera
subject: Weekly portal sync notes, 07/02
thread: weekly-portal
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `date` | yes | ISO date (YYYY-MM-DD) |
| `time` | yes | Time of sending or drafting (HH:MM, in quotes) |
| `seq` | yes | Sequential number within the day (integer) |
| `direction` | yes | `out`, `in`, or `reply` |
| `status` | yes | `draft`, `sent`, or `cancelled` |
| `from` | yes | Sender (full name) |
| `to` | yes | Recipient(s) (separated by ` ; `) |
| `cc` | no | Copy (separated by ` ; `) |
| `subject` | yes | Email subject |
| `thread` | no | Thread identifier (kebab-case, to group exchanges) |

## Email body

```markdown
# {{email subject}}

---

{{email body}}

{{signature if applicable}}
```

## Notes

- The `status` field tracks the state of each email:
  - `draft`, being written, not yet sent
  - `sent`, sent to the recipient
  - `cancelled`, abandoned (the file is kept for traceability)
- The `thread` field is optional but recommended when several emails belong to the same exchange
- For received emails (`direction: in`), the file serves as a trace, not a draft
- Adapt the content to the entity's preferences (see the entity `CLAUDE.md`)
