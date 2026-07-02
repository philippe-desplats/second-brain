---
name: step-03-publish
description: User validation, save into atlas/maps/, create optional back-links
prev_step: steps/step-02-draft.md
next_step: null
---

# Step 3, Publish MOC

## MANDATORY EXECUTION RULES:

- 🛑 NEVER save without user validation (except `{auto_mode}` = true)
- ✅ ALWAYS run `bm reindex` after writing to index the new MOC (if Basic Memory is installed)
- ✅ ALWAYS offer (but do not force) the `referenced_in [[MOC X]]` back-links

## EXECUTION SEQUENCE:

### 1. Present the draft to the user

Except if `{auto_mode}` = true, present the full draft (frontmatter + body) and ask via AskUserQuestion:

```yaml
questions:
  - header: "MOC draft"
    question: "Does the MOC work for you?"
    options:
      - label: "Looks good, save it"
        description: "Write the file into atlas/maps/ and regenerate the indexes"
      - label: "Edit a section"
        description: "I want to adjust before saving"
      - label: "Change the structure"
        description: "Go back to step-02 with a different structuring mode"
      - label: "Abandon"
        description: "Cancel, save nothing"
    multiSelect: false
```

**If "Edit"**: ask which section, adjust, re-present, re-validate.
**If "Change the structure"**: return to step-02 with a different `{structure_mode}` (max 2 tries).
**If "Abandon"**: exit without writing anything.
**If "Looks good"**: proceed to save.

### 2. Update vs new mode

**If `{mode}` = update** (existing MOC):

Read the existing one. Merge:

- Add the newly scanned notes into the existing sections
- Keep the manual annotations (comments the user wrote)
- Do not overwrite the "Overview" if the user rewrote it
- Update `last_updated` in the frontmatter to today's date

**If `{mode}` = new**: direct write.

**If `{mode}` = overwrite**: warn one last time via AskUserQuestion before overwriting.

### 3. Write the file

```bash
mkdir -p atlas/maps/
```

Write `{draft_content}` into `{target_path}` via the Write tool.

### 4. Back-links (optional)

Ask via AskUserQuestion (except in `{auto_mode}`):

```yaml
questions:
  - header: "Back-links"
    question: "Add `referenced_in [[MOC, {Topic}]]` to the Relations of the cited notes? (Lets you navigate from any note to its MOC in Obsidian)"
    options:
      - label: "Yes, add to all"
        description: "Patch the {N} scanned notes with a `referenced_in` line in their Relations section"
      - label: "No, skip"
        description: "The MOC is a hub, but the notes stay unchanged"
      - label: "Selective"
        description: "Choose which ones to patch (only the main notes, not the emails)"
    multiSelect: false
```

**If "Yes" or "Selective"**:

For EACH targeted note:

1. Read the file
2. Check that it has a `## Relations` section
   - If yes, add `- referenced_in [[MOC, {Topic}]]` at the end
   - If no, create the `## Relations` section at the end of the body with the line
3. Save

Obsidian benefit: from any note in the `{topic}` ecosystem, you get back to the MOC in one click.

### 5. Regenerate the Dataview indexes (if the maintenance scripts are present)

```bash
python3 basic-memory/scripts/generate_indexes.py
```

The MOC does not change the usual static indexes, but if an index `atlas/maps/mocs-static.md` (list of MOCs) exists, it will be updated.

### 6. Basic Memory reindex (if Basic Memory is installed)

```bash
command -v bm >/dev/null 2>&1 && bm reindex
```

Then:

```bash
python3 basic-memory/scripts/fix_double_frontmatter.py
python3 basic-memory/scripts/check_double_frontmatter.py
```

### 7. Final validation in Obsidian (suggested)

```
MOC published: {target_path}

✓ Strict frontmatter (type: note + subtype: {moc|index})
✓ {N} notes referenced with annotation
✓ {N} `referenced_in` back-links added (if enabled)
✓ Dataview indexes regenerated
✓ Basic Memory reindex clean

Next steps:
- Open the MOC in Obsidian
- Check that the local graph (depth 1) shows all cited notes
- If an area of the graph is isolated, manually add the missing wiki-link
- Over time, add the new notes via `/moc-new {topic}` (update mode)
```

### 8. Next-step suggestion

Depending on the context, suggest:

```
{Topic} is now mapped.

If you want to distill a recurring pattern seen during the scan:
- `/distill {topic}` (will create knowledge/{target}/{kind}-{slug}.md)

If other dense topics deserve a MOC, detected candidates:
- {other topic 1} ({N notes})
- {other topic 2} ({N notes})

Run `/moc-new {topic}` for the next one.
```

(Candidate detection is best-effort, based on the most represented topics in `sources/` that are not yet mapped.)

Store the final path in `{published_path}`.

---

## SUCCESS METRICS:

✅ File written in `atlas/maps/MOC-{slug}.md` (or `{slug}-index.md`)
✅ User validation OK
✅ Indexes regenerated
✅ Basic Memory reindex clean
✅ (Optional) `referenced_in` back-links created

## FAILURE MODES:

❌ Saving without validation (except auto)
❌ Incomplete frontmatter or missing subtype
❌ Broken wiki-links (titles nonexistent in the workspace)
❌ Skipping Basic Memory reindex (the MOC will not be indexed)

---

## END

This is the last step. After publication, suggest next actions and exit.
