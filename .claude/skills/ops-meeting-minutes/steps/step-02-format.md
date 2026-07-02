---
name: step-02-format
description: Format the minutes, review, and save with the meeting frontmatter
prev_step: steps/step-01-extract.md
next_step: null
---

# Step 2: Format, Review, Save

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER use em dashes, en dashes, semicolon chains, or emoji
- 🛑 NEVER put internal commentary in client-facing minutes
- ✅ ALWAYS load `.claude/skills/references/writing-rules.md` and obey it
- ✅ ALWAYS get approval before saving
- 📋 YOU ARE a minute-taker producing a document, factual and clean

## YOUR TASK:

Format the validated extraction into minutes in `{language}`, in the register set by `{register}`, then save under the entity's project.

---

## EXECUTION SEQUENCE:

### 1. Title the meeting

A short descriptive title from the topics: a regular check-in, a kickoff, a workshop on a theme. Keep it plain.

### 2. Build the frontmatter

Per the meeting schema (`basic-memory/schemas/meeting.md`) and `.claude/skills/references/save-conventions.md`:

```yaml
---
title: {meeting title}
type: meeting
schema_version: 1
date: {YYYY-MM-DD}
participants:
  - {Full Name}
  - {Full Name}
time: "{HH:MM if known}"
duration: "{duration if known}"
source: {recording URL if any}
format: report
status: done
category: {client | partner | internal | personal}
tags:
  - {free keyword}
client: {Canonical client name, if client scope}
partner: {Canonical partner name, if partner scope}
---
```

Keep `time` in quotes. Use `client:` or `partner:` depending on the zone, not both.

### 3. Write the body

```markdown
# Minutes, {meeting title}

Date: {DD month YYYY, in {language}}
Participants: {names, with role or company}
Subject: {one-line topic}

## Discussion points

### {Topic 1}

{Two to five factual sentences. What was discussed, what positions were expressed, what was shown. No interpretation.}

### {Topic 2}

{...}

## Decisions

1. {Decision, readable on its own}

## Action items

| Owner | Action | Deadline |
|-------|--------|----------|
| {Name} | {Specific action} | {Date or "to define"} |

## Open questions

- {Unresolved item}

## Observations

- [decision] {decision}
- [action] {owner} does {action} by {date}
- [question] {open question}

## Relations

- with [[{Participant}]]
- about [[{Entity canonical name}]]
```

**Register rules:**

- **Client-facing** (`{register}` = "client-facing"): no internal notes, no cost or margin talk, no "we should" asides. Only what the client should read.
- **Internal** (`{register}` = "internal"): the same structure plus a final section, clearly fenced:

```markdown
## Internal notes (not for the client)

{Frank observations, risks, things to prepare, opinions. Explicitly off the record.}
```

**Formatting:**

- Omit a section entirely when it is empty, except decisions and actions when data exists.
- Every action row needs an owner. Use [to assign] if unknown.
- Date the header in `{language}` (for French, lowercase month names).
- The `## Observations` block uses the schema tags `[decision]`, `[action]`, `[risk]`, `[milestone]`, `[question]`.

### 4. Self-audit

```
[ ] No em dashes, no en dashes, no semicolon chains, no emoji
[ ] Written in {language}
[ ] Client-facing carries no internal commentary
[ ] Every action row has an owner
[ ] Decisions are decisions, not suggestions
[ ] Topics are factual, not editorial
[ ] Length fits the meeting
```

### 5. Review

Show the full minutes, then AskUserQuestion:

```yaml
questions:
  - header: "Minutes"
    question: "Do these work?"
    options:
      - label: "Good"
        description: "Save them"
      - label: "Edit"
        description: "I will tell you what to change"
      - label: "Redo"
        description: "Wrong approach, start the formatting over"
    multiSelect: false
```

- **Good:** save.
- **Edit:** apply only the requested change, re-run the self-audit, re-present.
- **Redo:** ask what is wrong, reformat. After two full rewrites, revisit the extraction in step 1.

### 6. Save

Follow `.claude/skills/references/save-conventions.md`:

1. Entity base: `sources/{entity_zone}/{entity_slug}`.
2. Project: use the one resolved in step 1, or list `{entity_base}/*/` and infer or ask. Create the folder if none exists.
3. Subfolder: `meetings/`. Create it if missing.
4. Filename: `YYYY-MM-DD-meeting-{slug}.md`, slug in kebab-case from the title.
5. Save with the frontmatter and body above.
6. Confirm the path. If `{save_silent}` is true, save to the inferred path without a confirming question.

---

## SUCCESS METRICS:

- ✅ Minutes follow the structure and the register
- ✅ No banned characters or patterns
- ✅ User approved before saving
- ✅ Saved as a valid meeting file with Relations

## FAILURE MODES:

- ❌ Internal commentary in client-facing minutes
- ❌ An action row without an owner
- ❌ Saving before approval
- ❌ Missing `type: meeting` or a wrong path

## WORKFLOW COMPLETE:

After the save is confirmed, the skill is done.
