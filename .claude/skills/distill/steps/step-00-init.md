---
name: step-00-init
description: Parse args, deduce target/kind, validate threshold
next_step: steps/step-01-scan.md
---

# Step 0, Initialize Distillation

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER distill without having found at least `{min_occurrences}` real occurrences (default 3)
- ✅ ALWAYS read `.claude/rules/knowledge.md` for the conventions
- ✅ ALWAYS validate that `knowledge/{target}/` exists before going further
- 📋 YOU ARE an intent parser, not a writer. The writing happens in step-02
- 🚫 FORBIDDEN to load step-01 without having resolved `{topic}`, `{target}`, `{kind}`

## EXECUTION PROTOCOLS:

- 🎯 Parse the flags from the arguments
- 💾 Store the state in the state variables
- 🚫 FORBIDDEN to invent a topic; ask the user if absent and not in `--auto` mode

## CONTEXT BOUNDARIES:

- `{user_prompt}` holds the raw arguments
- Read `.claude/rules/knowledge.md` for the valid enums

---

## EXECUTION SEQUENCE:

### 1. Parse arguments

From `{user_prompt}`:

- **First positional argument**:
  - If `--auto`, set `{mode}` = `auto`
  - Otherwise, set `{mode}` = `topic`, `{topic}` = value
- **Flag `-t`**: value in `{ops, tech, business}` -> `{target}`
- **Flag `-k`**: value in `{pattern, playbook, guide, runbook, decision}` -> `{kind}`
- **Flag `-m`**: integer -> `{min_occurrences}` (default 3)
- **Flag `-a`**: boolean -> `{auto_mode}` (different from `--auto` discovery mode)

### 2. Auto-deduction if flags are missing

**If `{target}` is missing**, deduce from the topic:

| Topic contains | Target |
|---|---|
| `audit`, `accessibility`, `seo`, `onboarding`, `billing`, `pricing-process`, `weekly-review` | `ops` |
| `n8n`, `kubernetes`, `nextjs`, `pulumi`, `docker`, `deploy`, `api` | `tech` |
| `pricing-{service}`, `proposal`, `sales-methodology`, `strategy`, `positioning` | `business` |
| (nothing matches) | ask the owner (see `AGENTS.md`, Asking the owner) |

**If `{kind}` is missing**, deduce from the topic:

| Signals | Kind |
|---|---|
| `audit-`, `playbook-`, `process-`, `onboarding-` | `playbook` |
| `pattern-`, `n8n-`, `kubernetes-`, pure technique | `pattern` |
| `guide-`, long doc, methodology | `guide` |
| `runbook-`, `incident-`, recurring intervention | `runbook` |
| `decision-`, `adr-`, architecture choice | `decision` |
| (nothing matches) | ask the owner (see `AGENTS.md`, Asking the owner) |

### 3. Validation

- Check that `knowledge/{target}/` physically exists. Otherwise, fail with a clear message (offer to create the folder after validation).
- Check that `{min_occurrences}` >= 2 (otherwise default to 3).
- If `{mode}` = `topic` and `{topic}` is empty, ask the owner (see `AGENTS.md`, Asking the owner).

### 4. Present the plan to the user

**Except if `{auto_mode}` = true**, present:

```
Planned distillation:
- Topic: {topic} (or "auto-scan" if auto mode)
- Target: knowledge/{target}/
- Subtype: {kind}
- Minimum threshold: {min_occurrences} occurrences
```

Ask the owner for confirmation:

```yaml
questions:
  - header: "Distillation"
    question: "Run the scan with this configuration?"
    options:
      - label: "Yes, scan"
        description: "Proceed to step-01-scan"
      - label: "Adjust"
        description: "I want to change a parameter first"
    multiSelect: false
```

If `{auto_mode}` = true, skip the confirmation and go straight to step-01.

---

## SUCCESS METRICS:

✅ `{topic}` or `{mode}: auto` resolved
✅ `{target}` validated (existing knowledge/ subfolder)
✅ `{kind}` validated (strict enum)
✅ `{min_occurrences}` numeric
✅ User confirmed (except in `--auto`)

## FAILURE MODES:

❌ Empty topic in topic mode
❌ `{target}` or `{kind}` invalid outside the enum
❌ Skipping validation

---

## NEXT STEP:

Load `./step-01-scan.md`

<critical>
This step only parses and validates. The scan and the draft happen later. No content production in this step.
</critical>
