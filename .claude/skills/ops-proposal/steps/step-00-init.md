---
name: step-00-init
description: Parse the entity and need, derive the slug, check local context
next_step: steps/step-01-context.md
---

# Step 0: Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write any proposal content in this step
- ✅ ALWAYS secure an entity name and a need before proceeding
- 📋 YOU ARE an initializer, not a writer
- 🚫 FORBIDDEN to load step 1 before both are set

## DEFAULTS:

```yaml
save_silent: false   # -s enables silent save
```

## EXECUTION SEQUENCE:

### 1. Parse flags and arguments

```
-s          -> {save_silent} = true

Remainder   -> {entity_name} and {need}
```

Split the remainder on the first " - ". The first part is `{entity_name}`, the second is `{need}`. If there is no dash, infer both from the sentence.

### 2. Fill missing arguments

- **No entity:** ask for the client or prospect name.
- **No need:** ask for a one-line description of what they need.

Use AskUserQuestion or a plain prompt.

### 3. Derive the slug and check local context

- `{entity_slug}`: kebab-case of `{entity_name}`, accents stripped, spaces to dashes.
- Check for an existing entity folder: `sources/clients/{entity_slug}/`, then `sources/partners/{entity_slug}/`. Set `{entity_zone}` to the match. If neither exists, treat it as a new prospect and default `{entity_zone}` to `clients`.

### 4. Note profile availability

Read the root `CLAUDE.md` profile block. If the owner is `NOT CONFIGURED`, stop and tell the user to run `/sb-init`: a proposal needs an owner and an offer.

### 5. Summary and transition

```
Entity: {entity_name} ({entity_zone})
Need: {need}
Local context: {folder path found or "new prospect"}
```

Proceed to step 1.

---

## SUCCESS METRICS:

- ✅ `{entity_name}` and `{need}` set
- ✅ `{entity_slug}` derived, `{entity_zone}` resolved
- ✅ Owner profile confirmed present

## FAILURE MODES:

- ❌ Writing proposal content
- ❌ Proceeding without a need
- ❌ Ignoring an unconfigured owner profile

## NEXT STEP:

Load `./step-01-context.md`
