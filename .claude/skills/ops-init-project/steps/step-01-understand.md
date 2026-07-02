---
name: step-01-understand
description: Analyze the user's prompt to determine what they want to do, for whom, and what's needed
next_step: steps/step-02-setup.md
---

# Step 1: Understand the Request

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER assume the project category, infer from prompt, confirm if ambiguous
- ✅ ALWAYS read `sources/internal/CONTEXT.md` to ground your understanding in the organization's reality
- 📋 YOU ARE AN ANALYST understanding intent, not an executor starting work
- 💬 FOCUS on understanding what the user needs, not on doing it yet
- 🚫 FORBIDDEN to create files or start work in this step

## EXECUTION PROTOCOLS:

- 🎯 Analyze the prompt before asking anything
- 📖 Complete understanding fully before moving to setup
- 🚫 FORBIDDEN to load step-02 until project scope is confirmed

## CONTEXT BOUNDARIES:

- `{user_prompt}` is available from SKILL.md
- Read `sources/internal/CONTEXT.md` for business context
- Check `sources/clients/` and `sources/partners/` for existing entity context
- Don't assume knowledge about what will happen in step-02

## YOUR TASK:

Analyze the user's prompt to determine the project category, scope, expected activities, and destination folder.

---

## EXECUTION SEQUENCE:

### 1. Read Business Context

Read `sources/internal/CONTEXT.md` to understand the organization's current situation, services, clients, and strategy. This grounds every project in reality.

### 2. Analyze the Prompt

From `{user_prompt}`, determine:

**Project category** - Who is this for?
- `internal` - Internal work (pricing, strategy, infra, processes, operations), in `sources/internal/`
- `clients` - Work for a specific client, in `sources/clients/`
- `partners` - Work for a partner (reseller, white-label, co-ownership), in `sources/partners/`
- `personal` - Personal projects (learning, side ideas, experiments), in `sources/personal/`

Keywords:
- **internal**: pricing, internal strategy, offer, internal process, productivity, infra, operations
- **clients**: client name, "for [company]", "with [company]", external company reference
- **partners**: partner, white-label, reseller, affiliation, co-ownership, partnership, "with [partner]" (bilateral relationship)
- **personal**: "personal", "for me", personal learning, side project, experiment

Disambiguation: a partner is a **bilateral relationship** (resell, white-label, co-ownership) where the organization and the entity work together. A client is a **paying customer** receiving a service. Some entities are both (partner first, with secondary client facets); check `sources/partners/` first when in doubt.

**Expected activities** - What types of work will this involve?
- `research` - market analysis, competitor study, tech investigation
- `brainstorm` - ideation, concept exploration, opportunity mapping
- `writing` - copywriting, proposals, emails, content creation
- `meeting` - meeting prep, agendas, pre-reads
- `strategy` - business planning, financial analysis, roadmaps
- `note` - general notes, quick captures

**Project name** - Generate a slug: `kebab-case`, descriptive, short
- internal: `hosting-pricing`, `q2-diversification-plan`
- clients: `digital-strategy`, `q1-audit`
- partners: `white-label`, `onboarding`, `co-dev-{product}`
- personal: `ai-learning`, `side-project-x`

**Entity name** (only if category = `clients` or `partners`)
- Extract the name from the prompt
- Generate a slug: `kebab-case`, lowercase

### 3. Check Existing Context

**If client project:**
- Check if `sources/clients/{entity-name}/CLAUDE.md` exists
- If yes, note it for loading in step-02
- If no, flag as missing context to create

**If partner project:**
- Check if `sources/partners/{entity-name}/CLAUDE.md` exists
- If yes, note it for loading in step-02
- If no, flag as missing context to create

**If internal project:**
- `sources/internal/CONTEXT.md` is the primary context
- Check if related files already exist in `sources/internal/`

**If personal project:**
- No specific context required
- Check if related files already exist in `sources/personal/`

### 4. Confirm Understanding

Present a brief summary to the user:

```
**Project**: {project_name}
**Category**: {internal | clients | partners | personal} {entity_name if applicable}
**Destination**:
  - If clients: sources/clients/{entity_name}/{project_name}/
  - If partners: sources/partners/{entity_name}/{project_name}/
  - If internal: sources/internal/{project_name}/
  - If personal: sources/personal/{project_name}/
**Planned activities**: {list of activities}
**Available context**: {list of context files found}
**Missing context**: {what's missing, if anything}
```

Then use AskUserQuestion to confirm:

```yaml
questions:
  - header: "Confirm"
    question: "Is this understanding of the project correct?"
    options:
      - label: "Yes, continue (Recommended)"
        description: "The understanding is right, prepare the workspace"
      - label: "Not quite"
        description: "I want to adjust some points"
    multiSelect: false
```

**If "Not quite":** Ask what needs to change, update understanding, re-confirm.

---

## SUCCESS METRICS:

✅ Business context read from `sources/internal/CONTEXT.md`
✅ Project category correctly identified (internal, clients, partners, or personal)
✅ Activities list determined from prompt analysis
✅ Existing context files checked
✅ Missing context identified
✅ User confirmed understanding

## FAILURE MODES:

❌ Guessing project category without analyzing prompt
❌ Not reading business context before analyzing
❌ Starting to do the actual work instead of just understanding
❌ Skipping the confirmation step
❌ **CRITICAL**: Not using AskUserQuestion for confirmation

---

## NEXT STEP:

After user confirms understanding, load `./step-02-setup.md`

<critical>
Remember: This step is ONLY about understanding, don't create files, don't start work!
</critical>
