---
name: step-00-init
description: Parse flags, acquire the content or build the inbox queue
next_step: steps/step-01-classify.md
---

# Step 0: Init

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER start classifying here; acquisition only
- 🛑 NEVER modify or reformat the acquired content
- ✅ ALWAYS parse all flags before touching any file
- 📋 YOU ARE AN INTAKE CLERK, not a classifier
- 🚫 FORBIDDEN to load step-01 without content in hand (or a non-empty inbox queue)

## EXECUTION SEQUENCE:

### 1. Parse flags

```
Defaults: {mode} = single, {entity_override} = none, {type_override} = none
-i            → {mode} = inbox
-e <slug>     → {entity_override} = <slug>
-t <type>     → {type_override} = <type>, must be a canonical schema type; abort with the valid list otherwise
Remainder     → content, or @path reference
```

### 2. Acquire content

**Single mode, by priority:**

1. Remainder is an `@path` → Read the file verbatim into `{raw_content}`, set `{source_path}`.
2. Remainder is inline text → that is `{raw_content}`.
3. Nothing provided → ask the user to paste the content (plain question, no tool), wait.

**Inbox mode (`-i`):**

```bash
ls -1t inbox/ | grep -v README | grep -v .gitkeep
```

Build `{queue}` sorted oldest first. Show a compact table: item, age in days, size. Items older than 7 days flagged. If the queue is empty, report "inbox is clean" and stop here.

Take the first item: Read it into `{raw_content}`, set `{source_path}`.

### 3. Sanity notes

- Binary files (pdf, docx, xlsx) in single or inbox mode: capture files them WITHOUT reading content into frontmatter guesses; classification will rely on filename and user input, and the file is moved (not wrapped in markdown).
- Content over ~500 lines: fine, capture never rewrites it anyway.

## NEXT STEP:

Load `steps/step-01-classify.md`.

<critical>
Init acquires; it never interprets. Classification starts in step-01.
</critical>
