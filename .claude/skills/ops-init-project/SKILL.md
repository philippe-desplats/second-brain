---
name: ops-init-project
description: Initialize a new work session by understanding what you want to do, preparing the workspace, and loading the right context. Works for internal projects, client work, partner work, and personal projects.
argument-hint: <description of what you want to work on>
---

<objective>
Understand the user's intent from their prompt, prepare the workspace (folders, context), and ensure the agent has everything needed to be immediately productive. This skill bridges the gap between "I want to work on X" and actually having the right setup to start.
</objective>

<parameters>
**Input**: A natural language description of what the user wants to work on.

**Examples**:
```
/ops-init-project brainstorm new pricing strategy for the hosting offer
/ops-init-project prepare quarterly review meeting with Globex
/ops-init-project research competitor landscape for managed hosting
/ops-init-project help Globex rethink their digital strategy
/ops-init-project explore AI tools for personal productivity
```

No flags: the skill infers everything from the prompt and asks when unsure.
</parameters>

<state_variables>
- `{user_prompt}` - Raw input from the user
- `{project_name}` - Slug for the project (e.g. `hosting-pricing`, `acme-digital-strategy`)
- `{project_category}` - `internal` | `clients` | `partners` | `personal`
- `{entity_name}` - Client or partner name if applicable (for `clients` or `partners`)
- `{activities}` - List of expected activities (research, brainstorm, writing, meetings, strategy)
- `{context_files}` - Relevant context files to load
- `{missing_context}` - Context that should exist but does not
</state_variables>

<entry_point>
Load `steps/step-01-understand.md`
</entry_point>

<step_files>
| Step | File | Purpose |
|---|---|---|
| 1 | `steps/step-01-understand.md` | Analyze prompt, determine project type and needs |
| 2 | `steps/step-02-setup.md` | Create workspace, load context, confirm readiness |
</step_files>
