---
name: step-03-publish
description: User validation, save, create back-links to the sources
prev_step: steps/step-02-draft.md
next_step: null
---

# Step 3, Publish to knowledge/

## MANDATORY EXECUTION RULES:

- 🛑 NEVER save without user validation (except `{auto_mode}` = true)
- ✅ ALWAYS create the `used_in` back-links in the distilled sources
- ✅ ALWAYS run `bm reindex` after writing to index the new note (if Basic Memory is installed)

## EXECUTION SEQUENCE:

### 1. Present the draft to the user

Except if `{auto_mode}` = true, present the full draft (frontmatter + body) and ask via AskUserQuestion:

```yaml
questions:
  - header: "Distillation"
    question: "Does the draft work for you?"
    options:
      - label: "Looks good, save it"
        description: "Write the file and create the back-links"
      - label: "Edit"
        description: "I want to adjust a section first"
      - label: "Redo"
        description: "The draft does not work, start over"
    multiSelect: false
```

**If "Edit"**: ask which section, adjust, re-present, re-validate.
**If "Redo"**: return to step-02 with different instructions (max 2 attempts).
**If "Looks good"**: proceed to save.

### 2. Write the file

```bash
# Verify target dir exists
mkdir -p knowledge/{target}/
```

Write `{draft_content}` into `{draft_path}` via the Write tool.

### 3. Create the back-links in the sources

For EVERY source in `{sources_found}`:

1. Read the source file
2. Check that it has a `## Relations` section
   - If yes, add a `- used_in [[{Distilled title}]]` line at the end
   - If no, create the `## Relations` section at the end of the body and add the line
3. Save

This lets you navigate from the source to the distilled pattern in the Obsidian graph.

**Example**:

```markdown
## Relations

- about [[Globex]]
- managed_by [[Jane Doe]]
- used_in [[Playbook, Accessibility Audit]]   <- added by distill
```

### 4. Regenerate the Dataview indexes (if the maintenance scripts are present)

```bash
python3 basic-memory/scripts/generate_indexes.py
```

The new pattern will appear in `atlas/maps/decisions-recent-static.md` if it is a `subtype: decision`.

### 5. Basic Memory reindex (if Basic Memory is installed)

```bash
command -v bm >/dev/null 2>&1 && bm reindex
```

(Or ask the user to run it manually if `bm reindex` takes too long in practice.)

Also run `python3 basic-memory/scripts/fix_double_frontmatter.py` after reindex.

### 6. Confirmation

```
Distilled: {draft_path}

Cited sources:
- {Source 1 path}
- {Source 2 path}
- {Source 3 path}

{N} `used_in` back-links added in the sources.
Indexes regenerated. Basic Memory reindex done.

Suggested next steps:
- Check in Obsidian that the pattern's local graph shows the sources
- Add more anti-patterns or variants over time
- If a 4th source appears, update via `/distill {topic}` (update mode)
```

### 7. Optional, create a MOC if there is volume

If after this distillation more than 3 patterns exist in `knowledge/{target}/` around the same `{main topic}`, suggest creating a MOC:

```
{main topic} now has {N} entries in knowledge/{target}/.
Want to create a MOC to aggregate them? Run `/moc-new {main topic}`.
```

Store the final path in `{published_path}`.

---

## SUCCESS METRICS:

✅ File written in `knowledge/{target}/`
✅ `used_in` back-links created in all sources
✅ Indexes regenerated
✅ Basic Memory reindex clean

## FAILURE MODES:

❌ Saving without validation (except auto)
❌ Forgetting the back-links (breaks the graph)
❌ Skipping Basic Memory reindex (the note will not be indexed)

---

## END

This is the last step. After publication, suggest next actions and exit.
