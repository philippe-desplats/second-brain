---
name: step-04-personalize
description: Write charter and context files, fill the profile block, prune zones, adjust schemas
prev_step: steps/step-03-identity.md
next_step: steps/step-05-memory.md
---

# Step 4: Personalize the workspace

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER execute before the step-03 recap was approved. If the owner is away and the approval question times out, do NOT proceed: save the collected answers to `.sb-init-answers.json` at the workspace root, say so in one line, and end the session there. A later `/sb-init` run detects that file and resumes at the recap.
- 🛑 NEVER touch anything under `sources/` other than `sources/internal/`
- ✅ ALWAYS show the exact list of writes/removals before executing
- ✅ ALWAYS keep edits surgical: replace markers and enum lines, do not rewrite whole files
- 📋 YOU ARE AN EXECUTOR now; this is the step that writes

## EXECUTION SEQUENCE:

Announce the action list, get one confirmation, then execute all of it.

### 1. Write the config and fill the CLAUDE.md profile block

**First, `.sb-config.json`** (machine-readable source of truth): set `initialized: true`, `owner`, `organization`, `profile`, `zones` (the final list), `working_language`, and `working_language_secondary` (null if none). Leave `basic_memory_project` and `curation_ritual` for steps 5 and 6. Delete `.sb-init-answers.json` if it exists (the run is completing). Keep `schema` and `boilerplate_version` untouched. Update `demo_content` to `"removed"` if the demo is deleted in section 4.

**Then mirror it** into the root `CLAUDE.md`, replacing the content between `<!-- sb-init:profile -->` and `<!-- /sb-init:profile -->`:

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

## Relations
- about [[{org_name}, company context]]
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

## Relations
- see_also [[Second brain charter]]
```

Written in the working language.

### 4. Demo content (before any pruning)

The boilerplate ships with a fictional client (Globex) so the system can be seen working. Read `references/demo-manifest.md` (this skill's references folder); if the listed paths still exist, ask:

- **Keep for now (Recommended for first-timers)**: explore it, then remove later by deleting the paths listed in the manifest.
- **Remove now**: delete every path in the manifest (files and the `sources/clients/globex/` folder), keep the zone directories.

If the manifest is missing or all paths are already gone, skip silently. If the owner drops the `clients` zone in step 5 but keeps the demo, warn that the demo lives in `sources/clients/` and must be kept or removed as a whole.

### 5. Prune zones

For each zone NOT in `{zones}`:

- **Safety gate first**: list the zone's contents. If it contains anything other than `.gitkeep` and the demo paths already handled in 4, DO NOT delete; show the contents and ask the owner to move or archive them first (this matters in `-r` reconfigure runs on a lived-in workspace).
- If empty: remove `sources/{zone}/` and `archives/{zone}/` with `git rm -r` (NOT plain `rm`: interactive `rm -i` shell aliases silently break the chain and leave a half-done prune), and remove the zone's row from CLAUDE.md's path table (already done in 1).
- If `partners` was dropped, clean every functional reference:
  - `git rm basic-memory/schemas/partner-context.md`
  - `basic-memory/schemas/client-context.md`: remove the partner-relation fields (`managed_by`, `owned_by`, `referred_by`, `co_delivered_with`), their relations-vocabulary bullets, the symmetric-pairs section, and the "client that is a partner's product" section
  - `basic-memory/schemas/person.md`: remove the `partner_at` field
  - Every operational schema (`note`, `meeting`, `email`, `research`, `brainstorm`, `strategy`, `writing`, `transcript`, `deliverable`, `project-brief`): remove the `- partner` value from the `category` enum, remove `partner?: PartnerContext` fields, and fix examples using `category: partner` or a `partner:` field
  - `basic-memory/schemas/README.md`: update the strict-schema count and list, remove the partner-context table row and any partner-context example block
  - `.claude/rules/entities.md`: rewrite as clients-only (title, decision section, project naming, symmetric pairs, maintenance notes)
  - `.claude/rules/frontmatter.md`: remove the partner-context rows, the `partner:` wikilink resolution line, and the symmetric-pairs section; reword partner-based examples
- **Leave the maintenance scripts untouched** (`check_symmetric_relations.py`, `retype_files.py`, `auto_link_entities.py`, `add_observations_from_frontmatter.py`, `generate_indexes.py`): they are zone-agnostic, do nothing when no partner-context note exists, and keep working if the owner re-adds the zone later with a simple `mkdir`. The same goes for generic prose mentions of partners in `communication.md`, `knowledge.md`, `emails.md`, and the skills: leave them.

### 6. Adjust schema enums

- In every schema that declares `category`, keep only the values matching `{zones}` (internal maps to `internal`, personal to `personal`).
- In `basic-memory/schemas/service.md`, replace the `service_type` enum with `{service_types}` (kebab-case). Skip for the personal profile (and delete `service.md` plus `atlas/services/` if the owner has no commercial activity).

### 7. Verify

- `grep -c "NOT CONFIGURED" CLAUDE.md` must return 0.
- `python3 -c "import json; json.load(open('.sb-config.json'))"` must succeed, and `initialized` must be `true`.
- The pruned directories must be gone; the kept ones intact.
- **If `partners` was dropped, verify the full cleanup with global greps** (a partial prune is worse than none):
  - `test ! -f basic-memory/schemas/partner-context.md`
  - `grep -rin "PartnerContext|partner-context" basic-memory/schemas/ .claude/rules/ CLAUDE.md` returns nothing
  - `grep -rin "partner" basic-memory/schemas/ .claude/rules/entities.md .claude/rules/frontmatter.md` returns nothing (or only lines you deliberately kept and can justify)
  Maintenance scripts are expected to still mention partner-context; that is by design. If any check fails, finish the cleanup NOW before moving on.
- Re-read the two written files once to confirm frontmatter is valid YAML.

Report what was written and removed, in two short lists.

## NEXT STEP:

Load `steps/step-05-memory.md`.
