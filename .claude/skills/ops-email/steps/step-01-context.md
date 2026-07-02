---
name: step-01-context
description: Resolve the entity, load preferences, gather recipient, purpose, key points
prev_step: steps/step-00-init.md
next_step: steps/step-02-calibrate.md
---

# Step 1: Context

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER draft email text in this step, context only
- ✅ ALWAYS load the entity preferences before any entity-facing decision
- 📋 YOU ARE a context gatherer, not a writer
- 🚫 FORBIDDEN to invent a recipient relationship, ask when unknown

## YOUR TASK:

Determine who the email is for, load that entity's communication preferences, and assemble the purpose and key points.

---

## EXECUTION SEQUENCE:

### 1. Resolve the entity

**If `{entity_slug}` was set by `-e`:** use it. Otherwise detect it:

- **Reply mode:** read `{thread}` for the sender name, their register (formal or informal), the questions raised, and any deadline. Match the sender name to an entity folder.
- **New mode:** parse the brief for a recipient or company name.

Then locate the entity folder, trying in order:

1. `sources/clients/{slug}/` -> `{entity_zone}` = `clients`
2. `sources/partners/{slug}/` -> `{entity_zone}` = `partners`
3. `sources/internal/` for internal recipients -> `{entity_zone}` = `internal`
4. `sources/personal/` for personal correspondence -> `{entity_zone}` = `personal`

If no entity can be resolved, ask the user: which client, partner, or is this internal or personal.

### 2. Load preferences

Read the entity `CLAUDE.md` frontmatter and store `{entity_prefs}`:

- `tone` (professional, friendly, technical, direct, formal, commercial, pedagogical)
- `addressing` (formal, informal, variable)
- `primary_channel`, `email_format`
- `language`
- `constraints` (list, honor each one)

Resolve `{language}`: use the entity `language:` if present, otherwise the working language from the root `CLAUDE.md` profile block.

For internal or personal recipients with no entity `CLAUDE.md`, read `sources/internal/CONTEXT.md` for defaults when it exists. If it does not exist yet, fall back to the profile block and a neutral professional register, and note that `sources/internal/CONTEXT.md` is not set up.

### 3. Assemble purpose and key points

- **Reply mode:** list what must be answered from `{thread}`, plus anything the brief adds.
- **New mode:** derive `{purpose}` and `{key_points}` from the brief.

### 4. Fill only real gaps

Ask at most one or two questions, and only for what you cannot infer. Common gaps: the recipient name, the addressing register when the entity sets `variable` and the thread gives no signal, a vague ask that needs a concrete target.

Use AskUserQuestion for a register choice, a plain prompt for open information. In reply mode, match the sender's register automatically and do not ask.

### 5. Compile and continue

Summarize internally: recipient, relationship, resolved language and addressing, purpose, key points, call to action. Show a one-line summary, then proceed.

---

## SUCCESS METRICS:

- ✅ Entity resolved with zone and preferences loaded
- ✅ Language and addressing resolved, not left open
- ✅ At least one key point and a clear purpose
- ✅ Thread fully read in reply mode

## FAILURE MODES:

- ❌ Writing email text
- ❌ Guessing tone instead of reading the entity `CLAUDE.md`
- ❌ Asking more than two questions when the context was sufficient

## NEXT STEP:

Load `./step-02-calibrate.md`
