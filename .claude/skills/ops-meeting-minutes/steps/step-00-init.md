---
name: step-00-init
description: Parse flags, capture the raw content, set the register
next_step: steps/step-01-extract.md
---

# Step 0: Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER extract or format anything in this step
- ✅ ALWAYS secure the raw content before proceeding
- 📋 YOU ARE an initializer, not an analyst
- 🚫 FORBIDDEN to load step 1 before raw content is available

## DEFAULTS:

```yaml
register: "client-facing"   # -i switches to "internal"
entity_slug: ""             # -e <slug> sets it directly
save_silent: false          # -s enables silent save
```

## EXECUTION SEQUENCE:

### 1. Parse flags and input

```
-e <slug>   -> {entity_slug} = <slug>
-i          -> {register} = "internal"
-s          -> {save_silent} = true

Remainder   -> pasted notes, a @file reference, or a description
```

### 2. Resolve the raw content

- **Pasted notes or recap:** store the remainder as `{raw_content}`.
- **File reference (`@path`):** read the file (transcript, notes, or text) and store its content as `{raw_content}`.
- **Nothing usable:** ask the user to paste the notes or point to a transcript file.

Do not reject short input. A fifteen minute meeting can yield brief minutes.

### 3. Light context sniff

Scan `{raw_content}` for a date, company or entity names, and project hints. Note them for step 1. Do not ask questions yet.

### 4. Show the setup and continue

```
Register: {client-facing / internal}
Source: {pasted notes / transcript file / recap}
Detected date: {date or "to determine"}
```

Proceed to step 1.

---

## SUCCESS METRICS:

- ✅ `{raw_content}` is populated
- ✅ Register set from `-i`
- ✅ Any obvious context noted for step 1

## FAILURE MODES:

- ❌ Extracting or formatting here
- ❌ Empty `{raw_content}` with no prompt to the user
- ❌ Asking questions the content already answers

## NEXT STEP:

Load `./step-01-extract.md`
