---
name: step-02-profile
description: Select the workspace profile and the entity zones to keep
prev_step: steps/step-01-why.md
next_step: steps/step-03-identity.md
---

# Step 2: Profile and zones

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER delete or create directories here; decisions only, execution happens in step-04
- ✅ ALWAYS explain what each zone is for before asking
- ✅ ALWAYS default to FEWER zones; an unused zone is clutter, and adding one later is a `mkdir`
- 📋 YOU ARE A CONFIGURATOR, not an interviewer

## BACKGROUND

The workspace ships with four entity zones under `sources/` (mirrored in `archives/`):

| Zone | For | Typical profile |
|---|---|---|
| `sources/clients/` | People or companies you deliver work to | Agency, freelance |
| `sources/partners/` | Bilateral relationships: resellers, white-label, co-delivery, referrers | Agency |
| `sources/internal/` | Your own organization: strategy, pricing, infrastructure, methodology | Everyone |
| `sources/personal/` | Personal projects, learning, side ideas | Everyone |

`internal/` is always kept: it hosts `CONTEXT.md` (the business context) and the workspace charter.

## EXECUTION SEQUENCE:

### 1. Ask for the profile

Use AskUserQuestion:

> "Which profile is closest to how you work?"

| Option | Description | Default zones |
|---|---|---|
| **Agency** | You run a team serving multiple clients, possibly with partners or resellers | clients, partners, internal, personal |
| **Freelance** | You deliver work to clients on your own | clients, internal, personal |
| **Solopreneur** | You build and sell your own products or services, few or no client folders | internal, personal (clients optional) |
| **Personal** | Knowledge, learning, and life projects; no commercial activity | internal, personal |

Store `{profile}`.

### 2. Confirm the zone list

Present the default zones for the chosen profile and ask whether to adjust. In quick mode, take the defaults without asking. Rules:

- `internal` and `personal` cannot be removed.
- If the owner hesitates about `partners`, drop it: it is the most specialized concept (its schema models resellers, white-label, business referral) and easy to add later.
- Store the final list in `{zones}`.

### 3. Explain the consequence once

One sentence, no lecture: removed zones disappear from `sources/`, `archives/`, the schemas' `category` enum, and the CLAUDE.md path table; nothing else changes.

## NEXT STEP:

Load `steps/step-03-identity.md`.
