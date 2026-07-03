---
name: step-00-welcome
description: Detect workspace state, parse flags, explain the journey
next_step: steps/step-01-why.md
---

# Step 0: Welcome

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER start the interview here
- 🛑 NEVER write any file in this step
- ✅ ALWAYS check the initialization state before anything else
- 📋 YOU ARE A GATEKEEPER AND A HOST, not an interviewer
- 🚫 FORBIDDEN to load step-01 until the state check is complete

## EXECUTION SEQUENCE:

### 1. Parse flags

```
Defaults: {quick_mode} = false, {reconfigure} = false
-q or --quick        → {quick_mode} = true
-r or --reconfigure  → {reconfigure} = true
```

### 2. Check initialization state

**Interrupted run?** If `.sb-init-answers.json` exists at the workspace root, a previous run was interrupted at the recap gate. Offer to resume: reload the saved answers, show the recap again (step-03 section 5), and continue from there on approval. If the owner prefers a fresh start, delete the file and proceed normally.

Read the root `CLAUDE.md` and inspect the `<!-- sb-init:profile -->` block:

- **If every field says NOT CONFIGURED** → fresh workspace, proceed normally.
- **If fields are filled and `{reconfigure}` = false** → STOP. Tell the owner the workspace is already initialized, show the current profile block, and explain that `/sb-init -r` re-runs the configuration (existing notes are never touched, only configuration files are rewritten).
- **If fields are filled and `{reconfigure}` = true** → proceed, and carry the existing values as defaults through every step.

### 3. Sanity checks

Run quick checks and note results for later steps (do not block on failures, just record them):

```bash
git rev-parse --is-inside-work-tree   # git present?
which bm                              # Basic Memory CLI present?
ls .mcp.json 2>/dev/null              # MCP config already created?
```

### 4. Welcome and journey overview

Present a short welcome (adapt to the language the owner used, if any):

```
👋 Welcome to your second brain.

Here is what happens next (about 15 minutes):

1. WHY: a few sharp questions about what you actually need (skipped in quick mode)
2. PROFILE: how your work is structured (agency, freelance, solo, personal)
3. IDENTITY: who you are, how you communicate, which language you work in
4. PERSONALIZE: I write your charter and context files, and trim what you will not use
5. MEMORY: optional, wire up semantic search over all your notes
6. LAUNCH: file your first note and set your maintenance ritual

Nothing is written to disk before you approve a recap in step 4.
Ready?
```

Wait for acknowledgment, then proceed.

## NEXT STEP:

If `{quick_mode}` = true → load `steps/step-02-profile.md` directly.
Otherwise → load `steps/step-01-why.md`.
