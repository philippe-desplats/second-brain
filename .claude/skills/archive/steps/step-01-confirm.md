---
name: step-01-confirm
description: Audit last activity, incoming refs, confirm the archive
prev_step: steps/step-00-init.md
next_step: steps/step-02-move.md
---

# Step 1, Confirm Archive

## MANDATORY EXECUTION RULES:

- 🛑 NEVER archive if the last activity is < 6 months (except `{force_mode}` = true)
- ✅ ALWAYS list the incoming references before moving
- ✅ ALWAYS ask for explicit user confirmation (except in `{auto_mode}`)

## EXECUTION SEQUENCE:

### 1. Measure the last activity

```bash
# Last modified file in the source path
find {source_path} -type f -name "*.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -1
```

Compute `{last_activity_date}` and `{months_inactive}` (months between today and `{last_activity_date}`).

### 2. Check the 6-month threshold

**If `{months_inactive}` < 6 AND `{force_mode}` = false**:

Present to the user:

```
⚠ Recent activity detected on {source_path}
- Last modification: {last_activity_date} ({months_inactive} months)
- Recommended archive threshold: 6 months minimum

Are you sure you want to archive?
```

AskUserQuestion:
- Yes, archive anyway (equivalent to `-f`)
- No, abandon

### 3. List the incoming references

Look for all files that point to `{source_path}`:

```bash
# Textual paths
grep -rln "{source_path-without-trailing-slash}" --include="*.md" sources/ atlas/ knowledge/ 2>/dev/null

# Wiki-links to modeled entities (if we archive a whole entity)
grep -rln "\[\[{Entity Name}\]\]" --include="*.md" sources/ atlas/ knowledge/ 2>/dev/null
```

Build `{incoming_refs}` as a list of paths.

### 4. Alert if refs > 5

**If `len({incoming_refs})` > 5**:

```
⚠ {N} other notes point to {source_path}
- {path 1}
- {path 2}
- ...

These references will keep pointing to `sources/{type}/{slug}/` after archiving. Obsidian will re-point the wiki-links if renamed through Obsidian. In CLI, the textual paths will stay historical.

Do you still validate?
```

AskUserQuestion (except in `{auto_mode}`).

### 5. Check the frontmatter status

If the entity has a `CLAUDE.md` with `status:` in the frontmatter:

- If `status: active`, alert: "The project is still marked active. Sure?"
- If `status: done` or `status: cancelled` for a long time, OK.

### 6. Final summary before move

```
Planned archive:
- Source: {source_path}
- Target: {target_path}
- Last activity: {last_activity_date} ({months_inactive} months)
- Frontmatter status: {status}
- Incoming refs: {N}
- Mode: {actual | dry-run}
```

Final confirmation via AskUserQuestion (except in `{auto_mode}`).

---

## SUCCESS METRICS:

✅ `{last_activity_date}` and `{months_inactive}` computed
✅ `{incoming_refs}` populated
✅ User validated the final archive

## FAILURE MODES:

❌ Skipping the 6-month check without `-f`
❌ Skipping user confirmation except in `-a`

---

## NEXT STEP:

Load `./step-02-move.md`
