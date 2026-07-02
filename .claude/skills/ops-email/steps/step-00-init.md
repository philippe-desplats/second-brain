---
name: step-00-init
description: Parse flags, set the email mode, prepare state
next_step: steps/step-01-context.md
---

# Step 0: Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write any email text in this step
- ✅ ALWAYS parse flags before anything else
- 📋 YOU ARE an initializer, not a writer
- 🚫 FORBIDDEN to load step 1 before mode and input are set

## DEFAULTS:

```yaml
mode: "new"          # -r switches to "reply"
entity_slug: ""      # -e <slug> sets it directly
save_silent: false   # -s enables silent save
```

## EXECUTION SEQUENCE:

### 1. Parse flags and input

```
-r            -> {mode} = "reply"
-e <slug>     -> {entity_slug} = <slug>
-s            -> {save_silent} = true

Remainder     -> brief (new) or pasted thread (reply)
```

### 2. Resolve the input by mode

- **Reply mode** (`{mode}` = "reply"): the remainder is the email being answered. Store it as `{thread}`. If no thread text is present, ask the user to paste it.
- **New mode**: the remainder is the brief of what to write. If empty, ask the user what the email should say and to whom.

### 3. Note profile availability

Read the root `CLAUDE.md` profile block. If the owner is `NOT CONFIGURED`, stop and tell the user to run `/sb-init` first: the email cannot be signed without an owner identity.

### 4. Transition

Proceed to step 1. No confirmation needed here.

---

## SUCCESS METRICS:

- ✅ `{mode}` set to "new" or "reply"
- ✅ Input captured as `{thread}` or as a brief
- ✅ Owner identity confirmed present

## FAILURE MODES:

- ❌ Drafting email text here
- ❌ Reply mode with no thread and no prompt to paste it
- ❌ Proceeding with an unconfigured owner profile

## NEXT STEP:

Load `./step-01-context.md`
