---
name: step-02-setup
description: Create workspace structure with folder architecture, load context, and confirm readiness
prev_step: steps/step-01-understand.md
---

# Step 2: Setup the Workspace

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER create folders or files that won't be used
- ✅ ALWAYS create the README.md project brief for persistent context
- ✅ ALWAYS load relevant context files before declaring readiness
- 📋 YOU ARE A WORKSPACE PREPARER, not the one doing the actual work
- 💬 FOCUS on preparing everything so the NEXT conversation turn can be productive
- 🚫 FORBIDDEN to start the actual project work in this step

## EXECUTION PROTOCOLS:

- 🎯 Create folder architecture based on step-01 analysis
- 💾 Load all relevant context into the conversation
- 📖 Present a clear brief so the user can start working immediately after
- 🚫 FORBIDDEN to skip loading context files

## CONTEXT BOUNDARIES:

- All variables from step-01 are available: `{project_name}`, `{project_category}`, `{entity_name}`, `{activities}`, `{context_files}`, `{missing_context}`
- `sources/internal/CONTEXT.md` was already read in step-01
- Don't start doing the actual project work

## YOUR TASK:

Prepare the workspace by creating the project folder architecture, generating a README.md brief, loading relevant context, and presenting a ready-to-go summary.

---

## EXECUTION SEQUENCE:

### 1. Create Project Folder Architecture

Create the project folder and its internal structure based on category.

**If `{project_category}` = clients:**
```
sources/clients/{entity_name}/{project_name}/
├── README.md              # Project brief (created in step 3)
├── deliverables/          # Final deliverables for the client
└── references/            # Docs received from client, specs, screenshots
```

**If `{project_category}` = partners:**
```
sources/partners/{entity_name}/{project_name}/
├── README.md              # Project brief (created in step 3)
├── deliverables/          # Final deliverables (if applicable)
└── references/            # Docs from partner, specs, screenshots
```

**If `{project_category}` = internal:**
```
sources/internal/{project_name}/
├── README.md              # Project brief (created in step 3)
└── references/            # External docs, benchmarks, competitor data
```

**If `{project_category}` = personal:**
```
sources/personal/{project_name}/
├── README.md              # Project brief (created in step 3)
```
No subfolders for personal projects, keep it minimal.

**CRITICAL: Only create subfolders that match the project's needs.** If the project clearly won't need `references/` (e.g. a quick brainstorm), skip it.

### 2. Handle Client or Partner Context

**If `{project_category}` = clients AND `{entity_name}` context file doesn't exist:**

Ask the user for key client context, then create `sources/clients/{entity_name}/CLAUDE.md` with the canonical `client-context` schema (strict validation, see `basic-memory/schemas/client-context.md`):

```markdown
---
client: {Client Name}
status: active
last_updated: {YYYY-MM-DD}
industry: {if known}
tone: {professional | friendly | technical | direct | formal | commercial | educational}
addressing: {informal | formal | variable}
primary_channel: {email | slack | teams | whatsapp | video | direct}
language: {fr | en | other}
---

# {Client Name}, Context

> This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.

## Communication preferences
- **Tone**: {tone}
- **Addressing**: {addressing}
- **Channel**: {primary_channel}

## Company
- **Name**: {name}
- **Industry**: {industry}
- **Size**: {if known}

## Key contacts
- [contact] {Name}, {Role}

## Working relationship
- **Services**: {what the organization does for them}
- **Since**: {if known}
- [preference] {any relevant context from the user}
```

**If `{project_category}` = partners AND `{entity_name}` context file doesn't exist:**

Ask the user for key partner context, then create `sources/partners/{entity_name}/CLAUDE.md` with the canonical `partner-context` schema (strict validation, see `basic-memory/schemas/partner-context.md`):

```markdown
---
partner: {Partner Name}
type: partner-context
status: active
partnership_type: {commercial | technical | strategic | white-label | mixed}
last_updated: {YYYY-MM-DD}
active_tracks:
  - {e.g. reselling the internal offer}
  - {e.g. joint technical delivery}
contract: {affiliation | reseller | white-label | co-ownership | informal}
language: {fr | en | other}
---

# {Partner Name}, Context

> This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.

## Communication preferences
- **Tone**: {tone}
- **Addressing**: {informal | formal | variable}

## Partnership nature
- **Type**: {partnership_type}
- **Since**: {if known}
- [active-track] {track 1}
- [active-track] {track 2}
- [contact] {Name}, {Role}
```

Important for `partner-context` validation (strict): the allowed `partnership_type` values are **`commercial | technical | strategic | white-label | mixed`**. The values `reseller`, `co-ownership`, `affiliation` go in the optional `contract:` field (a separate enum), not in `partnership_type:`.

Use AskUserQuestion to gather minimum viable context:

```yaml
questions:
  - header: "Client"
    question: "A few facts about this client so I can help effectively?"
    options:
      - label: "I'll give you the context"
        description: "I will describe the client and the project"
      - label: "Not needed"
        description: "You have enough, let's move on"
      - label: "Search connected tools"
        description: "Look up this client in your connected knowledge base or project management tool"
    multiSelect: false
```

**If "Search connected tools":** If a knowledge base or project management tool integration is available, search it with the client name, fetch the most relevant results, and extract key context. If no integration is connected, skip this option.

**If client context file already exists:** Read it and load it into conversation context.

### 3. Generate README.md Project Brief

Create `README.md` at the project root. This file serves as **persistent project context** that any skill or future session can read to understand the project immediately.

**Mandatory frontmatter** for Basic Memory indexing (canonical schema `basic-memory/schemas/project-brief.md`, strict validation):

```markdown
---
title: {Project Name, human-readable}
category: {internal | client | partner | personal}
client: {Canonical client name}    # only if category=client
partner: {Canonical partner name}  # only if category=partner
created: {YYYY-MM-DD}
status: active
owner: {Owner Name}
---

# {Project Name, human-readable}

**Category**: {Internal | Client, {entity_name} | Partner, {entity_name} | Personal}
**Created**: {YYYY-MM-DD}
**Status**: Active

## Objective

{One paragraph describing what the project aims to achieve, based on the user's original prompt and step-01 analysis}

## Context

{2-3 sentences of relevant context: why this project exists, what triggered it, any constraints}

## Planned activities

{Bulleted list of expected activities from step-01: research, brainstorm, writing, meeting, strategy, etc.}

## Structure

{Brief explanation of the folder structure and file naming convention}

- Working files at the root: `YYYY-MM-DD-{type}-slug.md`
{- `deliverables/`: Final deliverables for the client (only if client project)}
{- `references/`: External docs and references (only if the folder was created)}

## Decisions and notes

{Empty section, will be filled as the project progresses}

## Relations

- parent [[{Entity or Acme for internal}]]
```

**CRITICAL:** Write the README in the owner's working language (see `sources/internal/CONTEXT.md`; default English). Keep it concise, factual, no fluff. Map the folder category to the frontmatter enum: `clients` -> `client`, `partners` -> `partner`, `internal` -> `internal`, `personal` -> `personal`.

### 4. Load All Relevant Context

Read and internalize all relevant context files:

- `sources/internal/CONTEXT.md` (already loaded from step-01)
- `sources/clients/{entity_name}/CLAUDE.md` or `sources/partners/{entity_name}/CLAUDE.md` (if client or partner project)
- Any existing files in the project folder (if resuming a project)
- Any existing related files in `sources/clients/`, `sources/partners/`, `sources/internal/`, or `sources/personal/` (search by project name or topic)

### 5. Search for Additional Context

**If relevant, search for extra context:**

- **Connected tools**: If a knowledge base or project management tool integration is available, search for pages or records related to the project topic. Present key findings.
- **Existing projects**: Check if related work was done before in `sources/clients/`, `sources/partners/`, `sources/internal/`, or `sources/personal/`.

Only do this if it adds clear value, don't search just to search.

### 6. Present the Project Brief

Present a complete brief to the user:

```markdown
---

## Project: {project_name}

**Category**: {Internal | Client, {entity_name} | Partner, {entity_name} | Personal}
**Objective**: {one-sentence summary of what the user wants to achieve}

### Workspace created
```
{show the actual tree of folders/files created}
```

### Context loaded
- {list each context file loaded with a one-line summary of what it contains}

### Additional context found
- {list relevant records found in connected tools, if any, with brief description}

### Planned activities
{numbered list of what the user wants to do, in order}

### Ready to start
{One sentence confirming everything is ready, and inviting the user to give the first instruction}

---
```

### 7. Transition to Work

The skill is complete. The user can now start working with full context loaded. Their next message will be a work instruction, not a skill step.

**Do NOT use AskUserQuestion here.** Simply present the brief and wait for the user's first real instruction.

---

## SUCCESS METRICS:

✅ Project folder architecture created with appropriate subfolders
✅ README.md created with project brief and structure documentation
✅ Client or partner context file created or loaded (if applicable)
✅ All relevant context files read and internalized
✅ Connected tools searched for additional context (if relevant)
✅ Clear project brief presented to user with workspace tree
✅ User is ready to give their first work instruction

## FAILURE MODES:

❌ Creating empty folders that won't be used
❌ Not creating README.md
❌ Not loading context files before declaring readiness
❌ Starting to do the actual project work
❌ Presenting a brief without having loaded the context
❌ Creating subfolders for personal projects (keep minimal)
❌ **CRITICAL**: Skipping client or partner context creation when it's needed

---

## SETUP PROTOCOLS:

- Create folder architecture appropriate to the project category
- Always generate README.md, it's the project's persistent memory
- Prefer loading existing context over creating new
- Search connected tools only when it adds clear value
- The brief must be actionable, the user should know exactly what to do next
- Show the actual tree created, not a generic template
- After the brief, the skill is DONE, no more steps

<critical>
Remember: After presenting the brief, STOP. The user's next message is their first real work instruction, not part of this skill. The README.md is the most important deliverable of this step, it ensures project context survives across sessions.
</critical>
