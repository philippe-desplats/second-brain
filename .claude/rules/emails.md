# Email Conventions

## Canonical schema

The frontmatter fields and enum values are defined in `basic-memory/schemas/email.md` (warn validation).

## Naming convention

```
YYYY-MM-DD-{seq}-{direction}-{slug}.md
```

- `seq`, chronological number within the day, starts at `01`, increments for every email (out, in, reply, cancelled). Restarts at `01` each new day.
- `direction`, `out` (sending), `in` (received), `reply` (response).
- `slug`, kebab-case, short, descriptive.

Example, `2026-07-02-01-out-project-kickoff.md`.

## Before creating a new email

1. Scan the target `emails/` folder to find the current day's sequence
2. Take the next number
3. Follow the `email` schema for the frontmatter (required fields, enums)
4. Check the communication preferences in the client or partner `CLAUDE.md`

## Status and traceability

- `draft`, email being written, not sent
- `sent`, email sent or received
- `cancelled`, email abandoned, **keep the file for traceability, never delete it**

## Legacy files

Files predating this naming convention should not be renamed. Automatic retyping will type them as `email` regardless of their filename.

## Quality control

See `.claude/rules/communication.md` for the rules on tone, format, and taboos (no AI mentions, no em dashes).
