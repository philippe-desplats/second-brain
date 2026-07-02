---
name: step-00-init
description: Parse args, validate no duplicate
next_step: steps/step-01-scan.md
---

# Step 0, Initialize MOC creation

## MANDATORY EXECUTION RULES:

- 🛑 NEVER create a duplicate; if `atlas/maps/MOC-{slug}.md` exists, propose an update
- ✅ ALWAYS validate the kebab-case slug
- 📋 YOU ARE a parser, not a writer

## EXECUTION SEQUENCE:

### 1. Parse arguments

- **First positional argument**: `{topic}` (in human form or kebab-case)
- **Flag `-t`**: `MOC` or `index` -> `{map_type}` (default MOC)
- **Flag `-m`**: integer -> `{min_notes}` (default 10)
- **Flag `-d`**: integer -> `{depth}` (default 99 = recursive)
- **Flag `-a`**: boolean -> `{auto_mode}`

If `{topic}` is empty, ask via AskUserQuestion:

```yaml
questions:
  - header: "Topic"
    question: "Which topic do you want to create a MOC for? (e.g. accessibility-audits, ai-agents, automation-patterns)"
    allowFreeText: true
```

### 2. Generate the slug

```
{slug} = kebab-case({topic})
```

Examples:
- "Accessibility Audits" -> `accessibility-audits`
- "AI Agents" -> `ai-agents`
- "Automation Patterns" -> `automation-patterns`

### 3. Resolve the target path

Depending on `{map_type}`:

```
if MOC:   {target_path} = atlas/maps/MOC-{slug}.md
if index: {target_path} = atlas/maps/{slug}-index.md
```

### 4. Check for no duplicate

```bash
test -f {target_path} && echo "EXISTS" || echo "NEW"
```

**If it exists**:

Present to the user via AskUserQuestion:

```yaml
questions:
  - header: "Existing MOC"
    question: "A MOC on {topic} already exists at {target_path}. What to do?"
    options:
      - label: "Update, enrich"
        description: "Re-scan and merge the newly found notes with the existing MOC"
      - label: "Overwrite, replace"
        description: "Redo from scratch, overwrites the existing content"
      - label: "Abandon"
        description: "Do not touch the existing MOC"
    multiSelect: false
```

Depending on the answer:
- Update -> `{mode}` = update, continue
- Overwrite -> `{mode}` = overwrite, continue
- Abandon -> exit

### 5. Present the plan

```
Planned MOC:
- Topic: {topic}
- Slug: {slug}
- Type: {map_type}
- Target: {target_path}
- Minimum threshold: {min_notes} notes
- Scan depth: {depth}
- Mode: {new | update | overwrite}
```

Confirm via AskUserQuestion (except in `{auto_mode}`).

---

## SUCCESS METRICS:

✅ `{topic}` and `{slug}` resolved
✅ `{target_path}` non-conflicting (or explicit resolution)
✅ Plan validated by the user

## FAILURE MODES:

❌ Duplicate not handled
❌ Invalid slug (special characters, spaces)

---

## NEXT STEP:

Load `./step-01-scan.md`
