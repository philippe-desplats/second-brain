---
name: step-00-init
description: Parse flags, validate scope, normalize windows
next_step: steps/step-01-scan.md
---

# Step 0, Initialize Curation Review

## MANDATORY EXECUTION RULES:

- 🛑 NEVER run in auto mode without explicitly warning the user
- ✅ ALWAYS validate that the delegated skills exist (`/distill`, `/archive`, `/moc-new`)
- 📋 YOU ARE a flag parser, not a scanner

## EXECUTION SEQUENCE:

### 1. Parse arguments

- **Flag `-s`**: `full | clients | partners | internal | knowledge | topics` -> `{scope}` (default `full`)
- **Flag `-w`**: integer -> `{window_days}` (default 30, used to qualify "recent")
- **Flag `-min`**: integer -> `{min_inactive_months}` (default 6, threshold for archive)
- **Flag `-only`**: `distill,archive,moc` (combination) -> `{only_filter}` (default all 3)
- **Flag `-a`**: boolean -> `{auto_mode}`
- **Flag `-r`**: boolean -> `{report_mode}` (report-only: scan and write the report to `atlas/reviews/`, no questions, no delegation; designed for scheduled headless runs)

`-r` and `-a` are mutually exclusive; if both are set, abort with an explanation (`-r` never executes actions, `-a` executes them all).

### 2. Validate the delegated skills

```bash
test -f .claude/skills/distill/SKILL.md && echo "DISTILL OK" || echo "DISTILL MISSING"
test -f .claude/skills/archive/SKILL.md && echo "ARCHIVE OK" || echo "ARCHIVE MISSING"
test -f .claude/skills/moc-new/SKILL.md && echo "MOC-NEW OK" || echo "MOC-NEW MISSING"
```

If a skill is missing AND it is part of `{only_filter}`, alert the user and exit. Otherwise remove the affected type from `{only_filter}` and continue with a warning.

### 3. Auto-mode warning

**If `{auto_mode}` = true**:

Warn one last time via AskUserQuestion:

```yaml
questions:
  - header: "Auto mode"
    question: "Auto mode will trigger ALL skills (`/distill`, `/archive`, `/moc-new`) on ALL detected candidates, without individual validation. Confirm?"
    options:
      - label: "Cancel, I want the interactive review"
        description: "Switch back to per-candidate validation"
      - label: "Confirm, I know what I am doing"
        description: "Continue in auto mode, everything will be processed"
    multiSelect: false
```

If "Cancel", set `{auto_mode}` = false.

### 3bis. Report mode

**If `{report_mode}` = true**: skip the auto-mode warning and the plan confirmation entirely (there is nothing to confirm, the run is read-only plus one report file). Proceed straight to step-01.

### 4. Present the plan

```
Planned curation review:
- Scope: {scope}
- Time window: {window_days} days (sense of "recent")
- Dormant threshold: {min_inactive_months} months
- Action filters: {only_filter}
- Mode: {interactive | auto}

Upcoming detection:
- Recurring patterns not yet distilled (toward `/distill`)
- Dormant entities (toward `/archive`)
- Dense topics without a MOC (toward `/moc-new`)
```

Confirm via AskUserQuestion (except in `{auto_mode}`).

---

## SUCCESS METRICS:

✅ Flags parsed and defaults applied
✅ Delegated skills verified as available
✅ Plan validated by the user

## FAILURE MODES:

❌ Auto mode without an explicit warning
❌ Missing delegated skill not detected

---

## NEXT STEP:

Load `./step-01-scan.md`
