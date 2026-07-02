---
name: ops-proposal
description: Draft a structured commercial proposal for a client or prospect. Loads the entity context and the owner's offer from the internal context file, interviews for missing scope, and writes a proposal covering understanding, approach, deliverables, timeline, and investment. Never invents pricing, leaves marked placeholders when no pricing exists. Saves with the writing schema frontmatter.
argument-hint: "[-s] <entity> - <one-line description of the need>"
---

<objective>
Generate a clear, tailored commercial proposal a prospect or client can read and act on. It draws the offer, positioning, and pricing from the workspace, never from invention, and it fills scope gaps by interviewing the owner. The proposal is written in the entity's language, in the owner's register, and saved as a draft under the entity's project.
</objective>

<parameters>
**Positional input:**
- `entity`: the client or prospect name.
- `need`: a one-line description of what they need.

Split on the first " - " (space dash space), or infer both from natural language.

**Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `-s` | Save silently after approval, using the inferred path. | confirm path |

**Examples:**
```
/ops-proposal Globex - website redesign on a modern stack
/ops-proposal Initech - infrastructure audit and recommendations
/ops-proposal -s New prospect - managed hosting and support
```
</parameters>

<state_variables>
**Persist throughout all steps:**

| Variable | Type | Description |
|----------|------|-------------|
| `{entity_name}` | string | Client or prospect display name |
| `{entity_slug}` | string | Kebab-case slug for paths |
| `{entity_zone}` | string | `clients` or `partners` |
| `{entity_context}` | string | Loaded entity context and history |
| `{language}` | string | Resolved output language |
| `{offer_context}` | object | Services, positioning, pricing from the internal context file |
| `{need}` | string | The need, clarified |
| `{scope}` | object | Objectives, deliverables, timeline, budget range |
| `{voice_sample}` | string | Register reference from calibration |
| `{proposal}` | string | The drafted proposal |
| `{save_silent}` | boolean | From `-s` |
</state_variables>

<writing_style>
Load `.claude/skills/references/writing-rules.md` and obey it. Write in `{language}`. Professional but not corporate, technically credible, concrete. No em dashes, no en dashes, no semicolon chains, no emoji. Never invent a price or a day rate. When no pricing exists in the workspace, use a clearly marked placeholder and tell the owner to fill `sources/internal/CONTEXT.md`.
</writing_style>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Description |
|------|------|-------------|
| 0 | `steps/step-00-init.md` | Parse the entity and need, derive the slug, check local context |
| 1 | `steps/step-01-context.md` | Load entity and offer context, calibrate register, interview for scope, validate |
| 2 | `steps/step-02-draft.md` | Draft the proposal, self-audit, review loop, save |
</step_files>
