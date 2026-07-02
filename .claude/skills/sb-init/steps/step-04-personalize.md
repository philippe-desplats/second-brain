---
name: step-04-personalize
description: Write charter and context files, fill the profile block, prune zones, adjust schemas
prev_step: steps/step-03-identity.md
next_step: steps/step-05-memory.md
---

# Step 4: Personalize the workspace

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER execute before the step-03 recap was approved
- 🛑 NEVER touch anything under `sources/` other than `sources/internal/`
- ✅ ALWAYS show the exact list of writes/removals before executing
- ✅ ALWAYS keep edits surgical: replace markers and enum lines, do not rewrite whole files
- 📋 YOU ARE AN EXECUTOR now; this is the step that writes

## EXECUTION SEQUENCE:

Announce the action list, get one confirmation, then execute all of it.

### 1. Fill the CLAUDE.md profile block

Replace the content between `<!-- sb-init:profile -->` and `<!-- /sb-init:profile -->` in the root `CLAUDE.md`:

```markdown
- **Owner**: {owner_name} ({email})
- **Organization**: {org_name}
- **Profile**: {profile}
- **Working language**: {working_language}
- **Basic Memory project**: pending (set in step 5)
```

Remove the "If the profile above says NOT CONFIGURED" warning paragraph. If zones were pruned, also remove the corresponding rows from the "Detailed paths" table.

### 2. Write the workspace charter (skip in quick mode)

Create `sources/internal/second-brain-charter.md` from `{charter}`:

```markdown
---
title: Second brain charter
type: strategy
status: active
date: {today}
---

# Second brain charter

*Written during /sb-init on {today}. Re-read this when the system starts to drift.*

## Why this exists
{trigger, in the owner's words}

## What it replaces
{status quo}

## Success in 90 days
{success_90d, testable}

## The wedge flow
{wedge_flow}: this flow must work perfectly before anything else matters.

## Retrieval pain to kill
{retrieval_pain}

## Observations
- [trigger] {one-line trigger}
- [wedge] {wedge flow}
- [success-criterion] {success_90d}
```

Write it in the working language: this file belongs to the owner, not to the structure.

### 3. Write the business context

Create `sources/internal/CONTEXT.md`:

```markdown
---
title: {org_name}, company context
type: note
status: active
last_updated: {today}
---

# {org_name}, context

## Identity
{owner_name}, {org_name}, {website}. {One-line positioning from the interview.}

## Offer
{service_types as a list, one line each; leave placeholders for pricing the owner can fill later}

## Communication defaults
- Tone: {comm_defaults.tone}
- Addressing: {comm_defaults.addressing}
- Signature: {comm_defaults.signature}

## Strategy notes
*To be filled as strategy notes accumulate. The /distill skill will point here.*
```

Written in the working language.

### 4. Prune zones

For each zone NOT in `{zones}`: remove `sources/{zone}/` and `archives/{zone}/` (they contain only `.gitkeep`), remove the zone's row from CLAUDE.md's path table (already done in 1), and if `partners` was dropped: delete `basic-memory/schemas/partner-context.md`, remove the partner-relation fields (`managed_by`, `owned_by`, `referred_by`, `co_delivered_with`) from `basic-memory/schemas/client-context.md`, and remove the partner references from `.claude/rules/entities.md` and `.claude/rules/frontmatter.md` (the symmetric-pairs section).

### 5. Adjust schema enums

- In every schema that declares `category`, keep only the values matching `{zones}` (internal maps to `internal`, personal to `personal`).
- In `basic-memory/schemas/service.md`, replace the `service_type` enum with `{service_types}` (kebab-case). Skip for the personal profile (and delete `service.md` plus `atlas/services/` if the owner has no commercial activity).

### 6. Verify

- `grep -c "NOT CONFIGURED" CLAUDE.md` must return 0.
- The pruned directories must be gone; the kept ones intact.
- Re-read the two written files once to confirm frontmatter is valid YAML.

Report what was written and removed, in two short lists.

## NEXT STEP:

Load `steps/step-05-memory.md`.
