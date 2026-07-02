---
name: step-02-report
description: Present the grouped report and allow per-candidate validation via AskUserQuestion
prev_step: steps/step-01-scan.md
next_step: steps/step-03-execute.md
---

# Step 2, Report and Validate

## MANDATORY EXECUTION RULES:

- 🛑 NEVER auto-validate a candidate (except `{auto_mode}` = true)
- ✅ ALWAYS present the score and the reason for each candidate
- ✅ ALWAYS allow an explicit "skip" (pass this candidate)

## EXECUTION SEQUENCE:

### 1. Present the global report

```
╔══════════════════════════════════════════════════════════╗
║              CURATION REVIEW, {YYYY-MM-DD}              ║
╚══════════════════════════════════════════════════════════╝

📚 DISTILL ({N1} candidates)
┌──────────────────────────────────────────────────────────
│ {score}/10  {topic}
│ {source_count} occurrences, suggested kind: {kind}
│ -> {suggested_command}
└──────────────────────────────────────────────────────────

🗄  ARCHIVE ({N2} candidates)
┌──────────────────────────────────────────────────────────
│ {months_inactive} months  {path}
│ {incoming_refs} incoming refs
│ -> {suggested_command}
└──────────────────────────────────────────────────────────

🗺  MOC ({N3} candidates)
┌──────────────────────────────────────────────────────────
│ {note_count} notes  {topic} (new)
│ -> {suggested_command}
│
│ {new_notes_since} new  {topic} (update)
│ -> {suggested_command}
└──────────────────────────────────────────────────────────

Total: {N1 + N2 + N3} suggested actions
```

### 2. Auto mode, direct execution

**If `{auto_mode}` = true**:

All actions are automatically added to `{validated_actions}`. Move to step-03 without asking.

### 3. Interactive mode, per-candidate validation

**For each candidate** in the order `candidates_distill` -> `candidates_archive` -> `candidates_moc`:

Present via AskUserQuestion:

```yaml
questions:
  - header: "{TYPE} suggestion ({i}/{total})"
    question: "{topic or path}, score {score}. {reason} What to do?"
    options:
      - label: "Run now"
        description: "Delegate to `{suggested_command}` in step-03"
      - label: "Skip"
        description: "Ignore for this review, keep as is"
      - label: "Skip and note"
        description: "Skip but add to the review log with a reason"
      - label: "Edit the command"
        description: "Adjust the slug, kind, scope before running"
    multiSelect: false
```

**If "Run"**: add to `{validated_actions}` with `{suggested_command}` as is.
**If "Skip"**: note in `{skipped_actions}` (not in the log).
**If "Skip and note"**: ask for the reason, add to the review log.
**If "Edit"**: open a free-text question to adjust, validate the new command, add to `{validated_actions}`.

### 4. Batch mode (volume > 10 candidates)

If total candidates > 10, offer a batch shortcut before individual validation:

```yaml
questions:
  - header: "High volume"
    question: "{N} candidates detected. How do you want to proceed?"
    options:
      - label: "All top {N_top} (score >= {threshold})"
        description: "Batch-run the most obvious actions, skip the rest"
      - label: "Individual validation"
        description: "Review each candidate one by one (may be long)"
      - label: "Only distill"
        description: "Filter to {N1} distill candidates and validate individually"
      - label: "Only archive"
        description: "Filter to {N2} archive candidates and validate individually"
    multiSelect: false
```

If "top N" is selected: automatically add the top N to `{validated_actions}`, skip the rest with a note.

### 5. Final confirmation

Present the list of validated actions:

```
Actions to execute ({N validated}):

DISTILL:
- /distill accessibility-audit --kind playbook
- /distill api-retry-pattern --kind pattern

ARCHIVE:
- /archive sources/clients/globex/

MOC:
- /moc-new ai-agents

Skipped: {N skipped}

OK to run in step-03?
```

Via AskUserQuestion (except in `{auto_mode}`):

```yaml
options:
  - label: "Confirm and run"
    description: "Execute the {N} actions sequentially"
  - label: "Edit the list"
    description: "Remove or adjust some actions"
  - label: "Cancel everything"
    description: "Exit without executing anything, just the review log"
```

### 6. Prepare the review log (optional)

If the user wants traceability, offer to create a log:

```
atlas/reviews/{YYYY-MM-DD}-review.md
```

Content:

```markdown
---
title: Curation Review, {YYYY-MM-DD}
type: note
subtype: note
schema_version: 1
date: {YYYY-MM-DD}
status: archived
---

# Curation Review, {YYYY-MM-DD}

## Context
{Weekly|Monthly} review via `/curate`. Scope: {scope}. Thresholds: {min_inactive_months}mo / 3+ occurrences / 10+ notes.

## Validated actions
- Distill: {N validated} ({list})
- Archive: {N validated} ({list})
- MOC: {N validated} ({list})

## Skipped actions
- {topic|path}, reason: {reason if provided}

## Learnings
{Free text, add manually after the review}

## Relations
- about [[Workspace Methodology]]
```

Validate via AskUserQuestion. If yes, create in step-03. If no, do not create.

---

## SUCCESS METRICS:

✅ All candidates reviewed (except an explicit top N batch)
✅ `{validated_actions}` contains at least one action OR a recorded decision to skip everything
✅ Review log prepared (created in step-03 if requested)

## FAILURE MODES:

❌ Auto-validating without user confirmation (except auto_mode)
❌ Forcing a skipped action
❌ Skipping the global final validation

---

## NEXT STEP:

Load `./step-03-execute.md`
