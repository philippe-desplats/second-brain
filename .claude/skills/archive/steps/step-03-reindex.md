---
name: step-03-reindex
description: Regenerate Dataview indexes, Basic Memory reindex, final validation
prev_step: steps/step-02-move.md
next_step: null
---

# Step 3, Reindex and Validate

## MANDATORY EXECUTION RULES:

- ✅ ALWAYS regenerate the Dataview indexes (they filter out the archives automatically)
- ✅ ALWAYS run `bm reindex` so Basic Memory forgets the old path and indexes the new one (if Basic Memory is installed)
- ✅ ALWAYS run `fix_double_frontmatter.py` after reindex (known Basic Memory bug)

## EXECUTION SEQUENCE:

### 1. Regenerate the Dataview indexes (if the maintenance scripts are present)

```bash
python3 basic-memory/scripts/generate_indexes.py
```

The static indexes (`atlas/maps/*-static.md`) regenerate. The archived entity disappears automatically from:

- `clients-active-static.md` (if a client, the frontmatter is no longer under `sources/clients/`)
- `partners-active-static.md` (if a partner)
- `projects-active-static.md` (if we archived an entity or a project brief)

### 2. Basic Memory reindex (if Basic Memory is installed)

```bash
command -v bm >/dev/null 2>&1 && bm reindex
```

(Or use `bm reset --reindex` if `bm reindex` fails because of moved files, as observed during migration.)

### 3. Fix double frontmatter (post-reindex)

```bash
python3 basic-memory/scripts/fix_double_frontmatter.py
python3 basic-memory/scripts/check_double_frontmatter.py
```

### 4. Check that no incoming ref is broken

Re-scan for paths that still point to `sources/{type-folder}/{slug}/` (the old path).

```bash
grep -rln "sources/{type-folder}/{slug}/" --include="*.md" sources/ atlas/ knowledge/ 2>/dev/null | head -10
```

If there are results:
- These are textual paths in historical minutes/emails, OK to leave for traceability
- But if it is an active README, flag it to the user

### 5. Check that the new path is indeed in archives/

```bash
ls -la {target_path}
test -d {target_path} && echo "OK" || echo "FAIL"
```

### 6. Final confirmation

```
Archive complete:

✓ {source_path} -> {target_path}
✓ Parent CLAUDE.md updated
✓ Dataview indexes regenerated
✓ Basic Memory reindex clean
✓ {N} remaining incoming refs (historical traceability, OK)

You can now commit:

git add -A
git commit -m "chore(archive): archive {slug} ({months_inactive}mo inactive)"

If you want to reactivate the archived one later:

git mv {target_path} {source_path}
bm reindex
```

### 7. Next-step suggestion

If several projects are eligible for archiving, suggest continuing:

```
Want to archive other dormant projects?
Candidates detected by activity > 6 months:
- {candidate 1} ({N months})
- {candidate 2} ({N months})

Run `/archive {candidate}` for the next one.
```

(This suggestion assumes an automatic audit command for dormant projects, to implement in a future iteration.)

---

## SUCCESS METRICS:

✅ Dataview indexes regenerated
✅ Basic Memory reindex clean
✅ 0 double frontmatter
✅ New path validated
✅ User confirmation

## FAILURE MODES:

❌ Basic Memory reindex fails -> run `bm reset --reindex`
❌ Static indexes still contain the archived one -> check the paths in the script
❌ Forgetting the final commit (the user does it, not the skill)

---

## END

Archive complete. No next step. Suggest next actions and exit.
