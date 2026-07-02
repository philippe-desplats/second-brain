---
name: step-03-draft
description: Draft the email, self-audit, present, iterate, and save
prev_step: steps/step-02-calibrate.md
next_step: null
---

# Step 3: Draft, Refine, Save

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER use em dashes, en dashes, semicolon chains, or emoji
- 🛑 NEVER put markdown styling inside the email body
- ✅ ALWAYS load `.claude/skills/references/writing-rules.md` and obey it
- ✅ ALWAYS write in `{language}` and match the entity `addressing`
- ✅ ALWAYS save after approval, following the email convention
- 📋 YOU ARE the owner writing this email, not an assistant generating one

## YOUR TASK:

Write one polished draft in the calibrated register, self-audit it, let the user refine it, then save it.

---

## EXECUTION SEQUENCE:

### 1. Load the writing rules

Read `.claude/skills/references/writing-rules.md`. Keep the bans and the self-audit in mind as you write.

### 2. Choose a shape

Pick the smallest structure that does the job:

| Situation | Shape |
|-----------|-------|
| Quick confirmation | Greeting, one to three sentences, sign-off |
| Standard reply | Greeting, acknowledge, answer, concrete ask, sign-off |
| Detailed reply | Greeting, acknowledge, structured paragraphs, next action, sign-off |
| New request | Greeting, one line of context, the ask, details, concrete next step, sign-off |
| Sending a document | Greeting, "here is ..." line, one precision, sign-off |
| Follow-up | Greeting, reference, factual reminder, concrete ask, sign-off |

### 3. Write the draft

- Greet with the recipient's name. Never a bare greeting with no name.
- Match `{voice_sample}`: sentence length, warmth, greeting and sign-off habits.
- One idea per paragraph, two to four sentences. Vary the length.
- Active voice, concrete verbs. Specific asks ("tell me if Tuesday works"), never "do not hesitate to".
- Use a list only for three or more concrete items. A comma closes intermediate items, a period closes the last.
- In reply mode, answer every point raised in `{thread}`. Do not re-quote the whole original. Match the sender's register.
- Sign with the owner identity from the root `CLAUDE.md` profile block.

### 4. Self-audit

Run the self-audit from the writing rules before showing anything:

```
[ ] No em dashes, no en dashes
[ ] No semicolon chains
[ ] No emoji
[ ] No markdown styling in the body
[ ] No corporate cliches, no AI tells
[ ] Language and addressing match the entity
[ ] Every entity constraint honored
[ ] Greeting names the recipient, first line is on point
[ ] Concrete ask present
[ ] Length fits the purpose
[ ] All key points covered
[ ] Reads like a person wrote it
```

Fix any failure before presenting.

### 5. Present

Show the email cleanly:

```
Subject: {subject line, for a new email}

{full body}
```

For a reply, omit the subject unless it should change.

### 6. Refine

Ask with AskUserQuestion:

```yaml
questions:
  - header: "Email"
    question: "Does this work?"
    options:
      - label: "Good to send"
        description: "Ready, I will copy it"
      - label: "Small edits"
        description: "I will tell you what to change"
      - label: "Wrong tone"
        description: "Too formal or too casual"
      - label: "Start over"
        description: "Not what I meant"
    multiSelect: false
```

- **Good to send:** go to save.
- **Small edits:** apply only what was asked, re-run the self-audit, re-present the full email.
- **Wrong tone:** shift one level and re-present.
- **Start over:** ask what to change, return to the draft with the new direction.

Change only what the user asked. Re-present the whole email, not fragments. After three rounds, offer to restart with a different approach.

### 7. Save

Save after approval, following `.claude/skills/references/save-conventions.md` and `.claude/rules/emails.md`.

1. Entity base: `sources/{entity_zone}/{entity_slug}`.
2. Resolve the project: list `{entity_base}/*/`. One project, use it. Several, infer from subject or recipient, ask if ambiguous. None, ask for a project name and create the folder.
3. Subfolder: `emails/`. Create it if missing.
4. Direction: `reply` if `{mode}` is "reply", otherwise `out`.
5. Sequence: scan the `emails/` folder for today's date and take the next `seq` (`01`, `02`, ...). Every email of the day counts.
6. Filename: `YYYY-MM-DD-{seq}-{direction}-{slug}.md`, slug in kebab-case.
7. Frontmatter, per the email schema (`basic-memory/schemas/email.md`):

```yaml
---
type: email
date: YYYY-MM-DD
time: "HH:MM"
seq: 1
direction: out
status: draft
from: {owner full name}
to:
  - {recipient full name}
subject: {subject}
category: {client | partner | internal | personal}
thread: {thread-slug if any}
---
```

`type: email` is mandatory for indexing. `to` and `cc` are YAML arrays. Put `time` and any `subject` containing `:` in quotes. Save with `status: draft`. When the user confirms the email was sent, update `status` to `sent`.

8. Body: the email text, then a `## Relations` section:

```
## Relations
- to [[{Recipient full name}]]
- from [[{Owner full name}]]
- for [[{Entity canonical name}]]
```

9. Confirm the saved path. If `{save_silent}` is true, save to the inferred path without a confirming question. Otherwise state the path you chose and save.

---

## SUCCESS METRICS:

- ✅ Draft passes the full self-audit
- ✅ Register matches the calibration
- ✅ User approved before saving
- ✅ File saved with valid email frontmatter and Relations

## FAILURE MODES:

- ❌ Any banned character or pattern in the draft
- ❌ Saving before approval
- ❌ Missing `type: email` or non-array `to`
- ❌ Over-revising beyond what the user asked

## WORKFLOW COMPLETE:

After the save is confirmed, the skill is done.
