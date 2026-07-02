---
name: step-02-move
description: git mv into archives/, update the parent CLAUDE.md
prev_step: steps/step-01-confirm.md
next_step: steps/step-03-reindex.md
---

# Step 2, Move to archives/

## MANDATORY EXECUTION RULES:

- 🛑 NEVER `cp + rm`, always `git mv` to preserve history
- ✅ ALWAYS create the parent folder in archives/ if absent
- ✅ ALWAYS update the parent CLAUDE.md if archiving a project (not the whole entity)

## EXECUTION SEQUENCE:

### 1. Skip if dry-run

**If `{dry_run}` = true**:

Present what would happen without executing:

```
[DRY-RUN] Would have executed:
- git mv {source_path} {target_path}
- (other listed updates)
```

Do not write, do not call step-03. Finish.

### 2. Create the parent folder in archives/

```bash
mkdir -p $(dirname {target_path})
```

For example, if `{target_path}` = `archives/clients/globex/`, create `archives/clients/` if absent.

### 3. Execute the git mv

```bash
git mv {source_path} {target_path}
```

**If git mv fails**:
- The source folder is not tracked (untracked) -> use `mv` (without git)
- Check the result with `ls`

### 4. Update the parent CLAUDE.md (if project scope)

**If `{is_project_scope}` = true** (we archive only a project, not the whole entity):

Read `{parent_claude_md}` = `sources/{type-folder}/{slug}/CLAUDE.md`

Add a mention at the bottom of the body:

```markdown
## Archived projects

- {project_name} archived on {YYYY-MM-DD}, moved to `archives/{type-folder}/{slug}/{project_name}/`
```

(Create the `## Archived projects` section if it does not exist.)

Update `last_updated` in the frontmatter to today's date.

### 5. Update the entity CLAUDE.md (if whole-entity scope)

**If `{is_project_scope}` = false**:

The entity's `CLAUDE.md` was moved into archives/ with it. No need to modify.

But add a final note in the archived `CLAUDE.md`:

```markdown
## Archived

Archived on {YYYY-MM-DD}. Previous path, `sources/{type-folder}/{slug}/`.
Reason, `{months_inactive} months without activity` or the explicit reason if provided.
```

Update `status: archived` in the frontmatter of the archived CLAUDE.md (an exception to the "no redundant status" rule, because here we document the factual fact of archiving for traceability).

### 6. Optional, update textual paths in incoming refs

**Not automatic**, because wiki-links are handled by Obsidian on rename, and textual paths in historical minutes must stay (traceability).

**But**: if an incoming ref is the README of an active project that lists the related sources, manually suggest to the user to update that README. List the affected refs.

### 7. Confirmation

```
Archived:
- {source_path} -> {target_path}
- {N} file(s) moved
- Parent CLAUDE.md updated (if project scope)

Remaining incoming refs: {N} (not auto-updated, to review)
```

---

## SUCCESS METRICS:

✅ git mv succeeded
✅ Parent or entity CLAUDE.md updated
✅ No file lost along the way
✅ Git history preserved

## FAILURE MODES:

❌ Using cp+rm instead of git mv (loses history)
❌ Forgetting to update the parent CLAUDE.md
❌ Silently refusing if the target exists (should be blocked in step-00)

---

## NEXT STEP:

Load `./step-03-reindex.md`
