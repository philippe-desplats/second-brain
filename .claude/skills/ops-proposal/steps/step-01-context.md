---
name: step-01-context
description: Load entity and offer context, calibrate register, interview for scope, validate
prev_step: steps/step-00-init.md
next_step: steps/step-02-draft.md
---

# Step 1: Context and Scope

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER invent context, an offer, or a price
- ✅ ALWAYS read the internal context file for the offer and pricing
- ✅ ALWAYS read the entity `CLAUDE.md` when it exists
- 📋 YOU ARE a context analyst, not a writer
- 🚫 FORBIDDEN to write proposal content here

## YOUR TASK:

Assemble everything the proposal needs: the owner's offer, the entity's history, the scope of the need, and the register to write in.

---

## EXECUTION SEQUENCE:

### 1. Load the offer context

Read `sources/internal/CONTEXT.md` and extract into `{offer_context}`:

- the service catalog (what the owner offers),
- the positioning and differentiators,
- the pricing model (day rate, packages, terms).

**If `sources/internal/CONTEXT.md` does not exist or has no pricing:** note it. Leave `{offer_context}.pricing` empty and carry on. The investment section in step 2 will use a marked placeholder and prompt the owner to fill this file.

### 2. Load the entity context

Read the entity `CLAUDE.md` at `sources/{entity_zone}/{entity_slug}/CLAUDE.md` when it exists. Extract relationship history, past projects, technical stack, contacts, and the communication preferences. Store as `{entity_context}`. Resolve `{language}` from the entity `language:`, falling back to the working language in the root profile block.

**If no entity context exists** (new prospect): ask the user for the essentials in one prompt, company, sector, size, main contact, and the context of the request. Store the answer as `{entity_context}`.

### 3. Calibrate the register

Establish `{voice_sample}` from the best available source, in order:

- **(a)** Search `sources/{entity_zone}/{entity_slug}/**/` for an earlier proposal (`writing_type: proposal`) or, failing that, an earlier outgoing email. Read one or two and capture the register, not the sentences.
- **(b)** If none exist, ask the user to paste one or two short samples of their own writing. Optional, the user can skip.
- **(c)** If neither, build the register from the entity `tone` and `addressing` with a neutral default: credible, direct, concrete, no corporate warmth.

### 4. Interview for scope

Compare `{need}` against `{offer_context}`. Ask only for what is missing, in a single grouped set of questions. The scope fields:

- **Objectives:** what outcome the entity wants.
- **Deliverables:** the concrete things produced.
- **Timeline:** a target window or constraints.
- **Budget range:** any figure or bracket the entity mentioned. Do not push, record what is known and leave the rest to the placeholder.

Use AskUserQuestion for the gaps. Store answers in `{scope}`.

### 5. Validate

Present a synthesis:

```
## Offer
- Relevant services: {matched services}
- Pricing basis: {pricing or "not configured, placeholder will be used"}

## Entity
- {entity_context summary}
- History: {prior work or "new prospect"}

## Scope
- Objectives: {objectives}
- Deliverables: {deliverables}
- Timeline: {timeline or "to define"}
- Budget: {budget or "to define"}
```

Then AskUserQuestion:

```yaml
questions:
  - header: "Context"
    question: "Is the context complete?"
    options:
      - label: "Good, draft it"
        description: "Move to the proposal"
      - label: "Missing information"
        description: "I will add or correct something"
    multiSelect: false
```

If information is missing, collect it, update the state, re-present.

---

## SUCCESS METRICS:

- ✅ `{offer_context}` loaded, or its absence noted
- ✅ `{entity_context}` loaded or collected
- ✅ `{voice_sample}` established
- ✅ `{scope}` filled or gaps explicitly marked
- ✅ User validated the synthesis

## FAILURE MODES:

- ❌ Inventing a service, a price, or entity history
- ❌ Skipping the internal context file
- ❌ Writing proposal content
- ❌ Asking scattered questions instead of one grouped set

## NEXT STEP:

Load `./step-02-draft.md`
