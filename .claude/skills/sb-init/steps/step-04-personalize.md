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

**First, `.sb-config.json`** (machine-readable source of truth): set `initialized: true`, `owner`, `organization`, `profile`, `working_language`, and `working_language_secondary` (null if none). Leave `basic_memory_project` and `curation_ritual` for steps 5 and 6, and **leave `zones` untouched for now**: section 5 writes it once the prune has actually happened. Writing the intended list here would be a lie if the safety gate in section 5 refuses to delete a non-empty zone, and every skill resolves the zone list from that array, so the owner's data would become invisible to the whole workspace. Delete `.sb-init-answers.json` if it exists (the run is completing). Keep `schema` and `boilerplate_version` untouched. Update `demo_content` to `"removed"` if the demo is deleted in section 4.

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

Write it in the working language: this file belongs to the owner, not to the structure. (The charter and `CONTEXT.md` are the two zone-level files of `sources/internal/`, which is a zone root and not an entity root; everything else written there goes in a project folder.)

### 3. Write the business context

Create `sources/internal/CONTEXT.md`:

```markdown
---
title: {org_name}, company context
type: note
status: active
date: {today}
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

Written in the working language. Keep the `date` key exactly as above: `basic-memory/schemas/note.md` requires `date` and `title`, and does not declare `last_updated`, so do not substitute one for the other.

### 4. Demo content (before any pruning)

The boilerplate ships with a fictional client (Globex) and the partner who referred them (Proseware), so the system can be seen working, symmetric relations included. Read `references/demo-manifest.md` (this skill's references folder); if the listed paths still exist, ask:

- **Keep for now (Recommended for first-timers)**: explore it, then remove later by deleting the paths listed in the manifest.
- **Remove now**: delete every path in the manifest (files and the `sources/clients/globex/` folder), keep the zone directories.

If the manifest is missing or all paths are already gone, skip silently. If `clients` is not in `{zones}` (the zone list was chosen in step 02 and gets pruned in section 5 below) but the owner keeps the demo, warn that the demo lives in `sources/clients/` and must be kept or removed as a whole.

### 5. Prune zones

For each zone NOT in `{zones}`:

- **Safety gate first**: list the zone's contents. If it contains anything other than `.gitkeep`, the shipped-empty `personal/journal/` folder (which holds nothing but its own `.gitkeep`), and the demo paths already handled in 4, DO NOT delete; show the contents and ask the owner to move or archive them first (this matters in `-r` reconfigure runs on a lived-in workspace). A journal folder that holds real entries is owner data and blocks the prune like anything else.
- If empty: remove `sources/{zone}/` and `archives/{zone}/` with `git rm -r` (NOT plain `rm`: interactive `rm -i` shell aliases silently break the chain and leave a half-done prune), and remove the zone's row from CLAUDE.md's path table (already done in 1).
- **If the pruned zone is `personal`, move the journal instead of deleting it.** Run `git mv sources/personal/journal sources/internal/journal` BEFORE removing the zone, then set `folder` to `sources/internal/journal` in `.obsidian/daily-notes.json` and update the two paths named in the `## Daily journal` section of `basic-memory/schemas/note.md`. The folder has to exist on disk: Obsidian does not create a missing daily-notes folder, it fails with `Folder "..." not found`, so a repointed config over a missing directory breaks the button just as surely as no config at all.

**If `partners` was dropped**, clean every functional reference by running 5a, then 5b, then looping on 5c. The bullets in 5a and 5b are a starting point, NOT the complete list: **the grep in 5c is the authority**. A prune that stops at the bullets leaves dead schema references behind, and a partial prune is worse than none.

**Deletion hygiene, applies to every bullet of 5a and 5b.** Delete the enclosing structure, not just the line. When the removed item was the last one of a section, a list, a table, or a fenced code block, the heading, the fence, and the sentence that introduces them go in the same edit (a `## Reference example` whose only example is a partner path, a `## Relations` block whose every line is a partner relation, a code fence left empty). And rewrite, in that same pass, whatever counts or names what was just removed: a heading such as "D1, split `context` into 2 schemas", a sentence such as "both strict validation" or "the 4 roots", any enumeration of the four zones. None of these leftovers carries the word "partner", so the grep in 5c can never report them; this rule is the only thing that catches them.

**Replace a worked example, never repaint it.** When an example is built on the pruned zone (a partner persona, a partner path, a partner category), swap the whole example for one drawn from a kept zone. Changing `category: partner` to `category: client` while keeping the partner's name, participants and vocabulary produces an example that parses and teaches nothing true, and no grep will ever flag it.

#### 5a. Schemas

- `git rm basic-memory/schemas/partner-context.md`
- **Every schema declares its fields twice**, once in the top-level `schema:` block (the body contract) and once in `settings.frontmatter:`. A partner field almost always appears in both, so clean both blocks in every file below. A single leftover breaks the check in section 7.
- `basic-memory/schemas/client-context.md`: remove the partner-relation fields (`managed_by`, `owned_by`, `referred_by`, `co_delivered_with`) from both blocks. Its `## Typed relations in the frontmatter` section holds exactly those four bullets and nothing else, so delete the whole section, heading included; do not leave an orphan heading. Also remove the `## Special case, client that is a partner's product` section, reword the `competes_with` bullet ("former partner turned competitor") in `## Additional relations in markdown`, and clean the worked example at the bottom, which still carries `managed_by: Alex Martin` and `owned_by: Alex Martin` in its frontmatter plus the matching lines under `## Relations`. This schema is strict, so a leftover in its own example is a documented validation error.
- `basic-memory/schemas/person.md`: remove the `partner_at` field from both blocks, its bullet in the typed-relations section, and the `sources/partners/{partner}/people/` alternative location
- `basic-memory/schemas/service.md`: remove the `resold_by` relation from the `schema:` block, its bullet in the relations section, and the "services resold by partners" sentence in "Why this schema"
- Every operational schema (`note`, `meeting`, `research`, `brainstorm`, `strategy`, `writing`, `transcript`, `clipping`, `session`, `deliverable`, `project-brief`): remove the `- partner` value from the `category` enum, remove the `partner?: PartnerContext` field from both blocks, and fix examples using `category: partner` or a `partner:` field
- `basic-memory/schemas/email.md`: it carries no partner field, only the `- partner` value in its `category` enum. Remove that value, then clean the shared categories below like every other operational schema
- **Shared categories the bullets above miss.** They live in most operational schemas, are invisible if you only grep for `PartnerContext`, and account for the bulk of a botched prune:
  - the `sources/partners/{partner}/...` line in the "Typical location" section, plus any `sources/partners/...` path in the reference examples
  - typed-relation bullets written "`client` or `partner`, entity met" (also: involved, parent, recipient, beneficiary): drop the partner half
  - body relations written `for [[Client | Partner | Internal]]`, `parent [[Client | Partner | Internal]]`, `with [[Client | Partner]]`
  - field descriptions such as `for?: Entity, "beneficiary, the client, partner, or internal scope"`, in both blocks
  - prose such as "Usable for all 4 categories, client, partnership, internal, personal" and "covering the 4 categories, internal/client/partner/personal": recount and relist the categories

#### 5b. Counts, rules, templates, navigation

- **Schema counts**, dropping `partner-context` takes the total down by one and the strict count down by one. Read the current numbers before editing rather than trusting the ones written here, and update the three files that carry them:
  - `basic-memory/schemas/README.md`: the single sentence stating how many schemas exist ("There are N schemas today", the only place that number is written), plus the strict and warn type lists under "Principle, mixed warn and strict". In the same file, remove the partner-context table row, the `sources/partners/` line, and the symmetric-pairs example built on a partner path
  - `.claude/rules/frontmatter.md`: the count in the intro, in the fundamental rule, in the "The N canonical types" heading, in the references section, and "Context schemas (2, strict validation)" which becomes 1. Also remove the partner-context table row, the partner row of the decision matrix, the `partner:` wikilink resolution line, the collision example built on a partner, and the symmetric-pairs section
  - `AGENTS.md`: the schema count, and the skill count if a skill was removed in the same pass
- `.claude/rules/entities.md`: rewrite as clients-only (title, decision section, project naming, symmetric pairs, maintenance notes)
- `.claude/rules/atlas.md`: remove the `atlas/maps/partners-active.base` index line and the `type:partner-context` color group; reword the people line ("individual partners") and the wiki-link line ("Clients or partners involved")
- `templates/entity-CLAUDE-template.md`: **step 6 hands this template to the owner to create their first entity context**, so a leftover here makes the first real file they write invalid and points it at a schema that no longer exists. Its partner content is structural, not a commented variant of the client lines. Remove: the whole `## Expected frontmatter, partner` section (heading, prose, YAML block, and the closing sentence listing the partner typed relations); in the header blockquote, the "clients and partners" scope, the `sources/partners/{partner}/CLAUDE.md` copy target, and the `partner-context.md` reference with its "both strict validation"; the sentence "The four typed relations (`managed_by`, `owned_by`, `referred_by`, `co_delivered_with`) are frontmatter fields too"; `partnership_type` and the "does not offer the same set on both sides" clause in the enum-token note; the partner half of the "Following sections" sentence and its `Partnership nature` bullet. Then two rewrites: `## Expected frontmatter, client` drops its ", client" qualifier, being the only frontmatter block left, and `## "Relations" section (recommended)` empties out (its client block is exactly those four partner relations, its partner block is their mirror), so delete the section or reduce it to the relations `client-context.md` still declares
- `templates/atlas-moc-template.md`: the "Clients or partners involved" heading and the `[[{{Partner}}]]` placeholder
- `atlas/home.md`: **the entry hub of the whole workspace**. It carries two links to the partner index, `[[partners-active.base|partners-active]]` in the index list and `[[partners-active.base]]` in the `contains` relations, plus the partner mention in the zone table. A dead link here is the first thing the owner sees
- `atlas/maps/README.md`: the partner mention in the dual-index prose
- `atlas/maps/partners-active.base`: **delete the file itself**. It is a live Bases view filtering `note.type == "partner-context"`, so in a pruned workspace it renders as a permanently empty table on a zone that no longer exists
- `sources/README.md`: the `sources/partners/{partner}/` table row
- `GETTING-STARTED.md`: "For each client or partner you touched this week"
- `CLAUDE.md`: confirm the `sources/partners/{partner}/` path-table row is gone (section 1 removes it) and that no partner mention survives elsewhere in the file
- **Leave the maintenance scripts untouched** (`check_symmetric_relations.py`, `retype_files.py`, `auto_link_entities.py`, `add_observations_from_frontmatter.py`, `generate_indexes.py`): they are zone-agnostic, do nothing when no partner-context note exists, and keep working if the owner re-adds the zone later with a simple `mkdir`. The same goes for generic prose mentions of partners in `communication.md`, `knowledge.md`, and `emails.md`: leave them.
- `.obsidian/graph.json`: remove the color group whose query targets the pruned zone's context type, so the graph configuration stops describing a type that no longer exists.
- **Leave the skills untouched too**, and for a stronger reason than prose: the places that act on a zone resolve the list at runtime from the `zones` array in `.sb-config.json` (or from the zone directories present on disk), so they already degrade to the zones the owner kept. That covers the weekly-pulse scan coverage, the `ops-init-project` category question and its entity-context creation, and the `capture` classification. Hand-pruning them would only break the workspace the day the owner re-adds the zone.

#### 5c. Loop until the grep is silent

Enumeration always misses something, so finish on the grep, not on the checklist. Run, from the workspace root:

`grep -rEin "partner" basic-memory/ .claude/agents/ .claude/rules/ .claude/skill-registry.md templates/ atlas/ sources/ archives/README.md AGENTS.md CLAUDE.md GETTING-STARTED.md .obsidian/`

Clean what it reports, run it again, repeat until the only surviving lines are the generic prose deliberately kept above (`communication.md`, `knowledge.md`, `emails.md`) and you can justify each one out loud. Do NOT move to section 6 while a schema, rule, template, or atlas file is still in the output.

The path list deliberately excludes `.claude/skills/`. Those files keep their zone vocabulary on purpose: they resolve the live list from `.sb-config.json` at runtime, and pruning them by hand would break the workspace the day the owner re-adds the zone.

#### 5d. Record what actually happened

Only now, with the tree in its final shape, write `zones` into `.sb-config.json`: the list of directories that actually exist under `sources/`, not the list the owner asked for. If the safety gate refused to remove a zone, that zone stays in the array and the owner is told, in one line, that it was kept because it holds data.

### 6. Adjust schema enums

- In every schema that declares `category`, keep only the values matching `{zones}` (internal maps to `internal`, personal to `personal`).
- In `basic-memory/schemas/service.md`, replace the `service_type` enum with `{service_types}` (kebab-case), and **always keep the value `other`, last in the enum**. This schema is strict, so without that escape hatch the first offer outside the declared categories becomes a validation error with no way to file it. Skip for the personal profile (and delete `service.md` plus `atlas/services/` if the owner has no commercial activity).

### 7. Verify

- `grep -c "NOT CONFIGURED" CLAUDE.md` must return 0.
- `python3 -c "import json; json.load(open('.sb-config.json'))"` must succeed, and `initialized` must be `true`.
- The pruned directories must be gone; the kept ones intact.
- **`zones` in `.sb-config.json` must equal the directories actually present under `sources/`.** Every skill resolves the zone list from that array, so a divergence in either direction is a real defect: a zone listed but absent makes a skill try to write into nothing, a zone present but unlisted makes the owner's data invisible to the whole workspace. Compare the two lists explicitly, do not assume section 5 succeeded.
- **If `partners` was dropped, verify the full cleanup with global greps** (a partial prune is worse than none). Run them from the workspace root, and keep the `-E`: without it the `|` is a literal character in a basic regular expression, the pattern matches nothing whatever the state of the tree, and the check becomes a permanent false pass.
  - `test ! -f basic-memory/schemas/partner-context.md`
  - `grep -rEin "PartnerContext|partner-context" basic-memory/ .claude/agents/ .claude/rules/ .claude/skill-registry.md templates/ atlas/ sources/ archives/README.md AGENTS.md CLAUDE.md GETTING-STARTED.md .obsidian/` must return nothing, no exception: a dangling `PartnerContext` type or a link to a deleted schema is always a defect.
  - `grep -rEin "partner" basic-memory/ .claude/agents/ .claude/rules/ .claude/skill-registry.md templates/ atlas/ sources/ archives/README.md AGENTS.md CLAUDE.md GETTING-STARTED.md .obsidian/` must return nothing, or only the generic prose in `communication.md`, `knowledge.md`, and `emails.md` that section 5 deliberately keeps. Anything else is unfinished work, not an accepted exception.
  Maintenance scripts sit outside these paths and are expected to still mention partner-context; that is by design. If any check fails, finish the cleanup NOW before moving on.
- Re-read the two written files once to confirm frontmatter is valid YAML, and that `sources/internal/CONTEXT.md` carries `date` (required by the `note` schema).

Report what was written and removed, in two short lists.

## NEXT STEP:

Load `steps/step-05-memory.md`.
