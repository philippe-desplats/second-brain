---
name: step-02-draft
description: Draft the proposal, self-audit, review loop, and save
prev_step: steps/step-01-context.md
next_step: null
---

# Step 2: Draft, Review, Save

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER use em dashes, en dashes, semicolon chains, or emoji
- 🛑 NEVER invent a price, a day rate, or a figure not in `{offer_context}`
- ✅ ALWAYS load `.claude/skills/references/writing-rules.md` and obey it
- ✅ ALWAYS write in `{language}`, in the calibrated register
- ✅ ALWAYS get approval before saving
- 📋 YOU ARE the owner writing a proposal, not a template generator

## YOUR TASK:

Write a complete proposal the entity could act on, self-audit it, refine it with the user, then save it as a draft.

---

## EXECUTION SEQUENCE:

### 1. Draft the proposal

Follow this structure. Every section earns its place, no filler.

```markdown
# Proposal, {project title}

For: {entity_name}
From: {owner identity from the profile block}
Date: {YYYY-MM-DD}

## 1. Context

{A short recap of the situation and why this proposal exists. Grounded in {entity_context}, specific to this entity, not a generic intro.}

## 2. Understanding of the need

{Reformulate the need in your own words to show you grasp the stakes. Three to five sentences, concrete.}

## 3. Proposed approach

{The method to address the need. Key steps, tools, and choices. Explain why this approach, not only what. Pragmatic and credible.}

## 4. Scope and deliverables

| Deliverable | Description |
|-------------|-------------|
| {item} | {what it is} |

## 5. Timeline

| Phase | Estimated duration | Deliverables |
|-------|--------------------|--------------|
| {phase} | {duration} | {deliverables} |

## 6. Investment

{Pricing from {offer_context}. Be specific: a day count times the day rate, or a fixed package with terms. Show amounts excluding tax and state the payment terms.}

| Item | Estimate |
|------|----------|
| {item} | {amount} |
| Total | {amount} |

## 7. Next steps

{What happens if the entity accepts: a call, a signature, a kickoff.}
```

**Pricing discipline:**

- Use only figures present in `{offer_context}`. Be concrete, "5 days at the standard day rate" beats a vague bracket.
- If `{offer_context}` has no pricing, replace the investment table with a clearly marked placeholder and a note:

```markdown
## 6. Investment

> PLACEHOLDER, no pricing is configured in the workspace.
> Fill `sources/internal/CONTEXT.md` with the offer and day rate, then regenerate this section.

| Item | Estimate |
|------|----------|
| {deliverable} | {to price} |
| Total | {to price} |
```

Never guess a number to fill the gap.

### 2. Self-audit

```
[ ] Written in {language}, proper diacritics if applicable
[ ] No em dashes, no en dashes, no semicolon chains, no emoji
[ ] Every price traces to {offer_context}, or the placeholder is used
[ ] Each section adds value, no filler
[ ] Deliverables are specific, not generic
[ ] Timeline durations are realistic
[ ] Next steps are actionable
[ ] Direct and credible, not corporate filler
[ ] The entity would understand exactly what they are buying
```

### 3. Review

Show the full proposal, then AskUserQuestion:

```yaml
questions:
  - header: "Proposal"
    question: "What do you think?"
    options:
      - label: "Good"
        description: "Save it"
      - label: "Edit a section"
        description: "I want to adjust one part"
      - label: "Redo"
        description: "Wrong direction, start over"
    multiSelect: false
```

- **Good:** save.
- **Edit a section:** ask which and what, apply it, re-run the self-audit, re-present.
- **Redo:** ask the direction, regenerate, re-present.

### 4. Save

Follow `.claude/skills/references/save-conventions.md`. A proposal being drafted is a `writing` (status draft), saved at the project root, not in `deliverables/`. It moves to `deliverables/` as a `deliverable` only once finalized and signed.

1. Entity base: `sources/{entity_zone}/{entity_slug}`.
2. Resolve the project: list `{entity_base}/*/`. One project, use it. Several, infer from the need or ask. None, ask for a project name (for a sales scope, `proposal` is a sensible default) and create the folder.
3. Filename at the project root: `YYYY-MM-DD-writing-proposal-{slug}.md`, slug in kebab-case.
4. Frontmatter, per the writing schema (`basic-memory/schemas/writing.md`) and the save conventions:

```yaml
---
title: Proposal, {project title}
type: writing
schema_version: 1
writing_type: proposal
date: {YYYY-MM-DD}
category: {client | partner}
client: {Canonical name, if client scope}
partner: {Canonical name, if partner scope}
status: draft
destination: Email
---
```

Use `client:` or `partner:` to match `{entity_zone}`, not both.

5. Body: the proposal, then:

```markdown
## Observations
- [claim] {a promise the proposal makes}
- [proof] {a supporting argument or reference}
- [cta] {the next step asked of the entity}

## Relations
- for [[{Entity canonical name}]]
```

6. Confirm the saved path. If `{save_silent}` is true, save to the inferred path without a confirming question.

---

## SUCCESS METRICS:

- ✅ Proposal follows the structure, no filler
- ✅ Pricing traces to the workspace, or the placeholder is used
- ✅ No banned characters or patterns
- ✅ User approved before saving
- ✅ Saved as a valid writing file with Observations and Relations

## FAILURE MODES:

- ❌ Inventing a price to avoid the placeholder
- ❌ Generic deliverables or filler sections
- ❌ Saving before approval
- ❌ Missing `type: writing` or `writing_type: proposal`

## WORKFLOW COMPLETE:

After the save is confirmed, the skill is done. If a quote or contract is the natural next step, offer to draft it.
