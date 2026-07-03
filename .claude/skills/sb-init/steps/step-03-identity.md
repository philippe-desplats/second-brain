---
name: step-03-identity
description: Collect owner identity, working language, and communication defaults
prev_step: steps/step-02-profile.md
next_step: steps/step-04-personalize.md
---

# Step 3: Identity and communication

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write files here; collect and confirm only
- 🛑 NEVER infer identity from the machine (git config, hostname) without confirming it with the owner
- ✅ ALWAYS ask for real facts; a wrong identity poisons every generated email and deliverable
- 📋 YOU ARE A REGISTRAR, not a biographer

## EXECUTION SEQUENCE:

### 1. Owner and organization

Ask (pre-fill suggestions from `git config user.name` / `user.email` if available, but confirm):

- Full name (as it should appear in signatures and documents)
- Organization name (for solo profiles, may be the same as the owner's name; that is fine)
- Primary email address for outgoing correspondence
- Website or main public link (optional)

Store `{owner_name}`, `{org_name}`, and the contact details.

### 2. Working language

> "Which language do you work in? All notes, emails, and deliverables I generate will use it. The workspace structure itself stays in English."

Store `{working_language}`. If the owner works in two languages (for example local clients + international), store the primary in `{working_language}` and the secondary in `{working_language_secondary}`; both land in `.sb-config.json`.

### 3. Communication defaults

These become the fallback when an entity has no specific preferences in its own `CLAUDE.md`:

- Default tone for outward writing: professional-warm, professional-neutral, or casual
- Default addressing for languages that distinguish it (tu/vous, du/Sie): informal, formal, or per-entity
- Email signature: name only, name + organization, or a custom block (ask them to paste it)

Store `{comm_defaults}`.

### 4. Offer categories (skip for the personal profile)

> "How would you categorize what you sell or deliver? A few words each, for example: consulting, development, hosting, training."

These become the `service_type` enum in `basic-memory/schemas/service.md` and seed `atlas/services/`. Two to eight categories. Store `{service_types}`. In quick mode, keep the generic defaults from the schema.

### 5. Recap checkpoint

Show everything collected so far ({charter} summary if present, {profile}, {zones}, identity, language, communication defaults, service types) in one compact table and confirm. This is the last stop before writing to disk.

**If the owner does not respond** (away from keyboard, timed-out question): write all collected answers to `.sb-init-answers.json` at the workspace root, announce it in one line, and STOP. Never proceed to step-04 on an unanswered gate.

## NEXT STEP:

Load `steps/step-04-personalize.md`.
