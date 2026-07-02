---
name: step-03-execute
description: Delegate to the validated skills (/distill, /archive, /moc-new), track executions
prev_step: steps/step-02-report.md
next_step: null
---

# Step 3, Execute Validated Actions

## MANDATORY EXECUTION RULES:

- 🛑 NEVER reimplement inline what the delegated skills already do
- ✅ ALWAYS invoke via the Skill tool, not via Bash
- ✅ ALWAYS execute actions sequentially (not in parallel, they may touch the same graph)
- ✅ ALWAYS produce an execution log even if the user skips the review log

## EXECUTION SEQUENCE:

### 1. Execution order

Execute in this order, which minimizes conflicts:

1. **Archive first**: moves entities, frees refs, changes the structure
2. **Distill next**: creates new files in knowledge/ (reads the sources, so ideally after archiving)
3. **MOC last**: aggregates what now exists (integrates the archive + distill changes)

### 2. Execute each action

For each action in `{validated_actions}` (in the order above):

#### Archive

```
Skill("archive", "{path-or-args}")
```

Follow the output. If the skill triggers an AskUserQuestion (second-level confirmation), let the user answer. On exit, capture:
- `{published_path}` (the new location in archives/)
- Status: success or abort

#### Distill

```
Skill("distill", "{topic} --kind {kind}")
```

Follow the output. Capture:
- `{published_path}` of the knowledge/ file
- Status

#### MOC

```
Skill("moc-new", "{topic}")
```

Follow the output. Capture:
- `{published_path}` of the MOC
- Status

### 3. Handle partial errors

**If an action fails or is aborted**:

- Log the error
- Continue with the following actions (do not abandon everything)
- Mark this action as `{status}: failed` in `{executed_actions}`

**If an action has a conflict** (e.g. a MOC is created that points to an entity that `/archive` just moved):

- The delegated skill normally handles it (internal validation)
- If the user aborts inside the skill, mark it skipped and continue

### 4. Final index regeneration (if the maintenance scripts are present)

**Once, at the end**:

```bash
python3 basic-memory/scripts/generate_indexes.py
```

Each delegated skill already runs it at its own end, but a final consolidated pass helps ensure everything is coherent post-batch.

### 5. Final Basic Memory reindex (if Basic Memory is installed)

```bash
command -v bm >/dev/null 2>&1 && bm reindex
python3 basic-memory/scripts/fix_double_frontmatter.py
python3 basic-memory/scripts/check_double_frontmatter.py
```

(Same as step 4, the skills each do it already, but a final pass ensures global coherence.)

### 6. Write the review log (if validated in step-02)

**If the user accepted the log**:

Write `atlas/reviews/{YYYY-MM-DD}-review.md` with:

- Frontmatter validated in step-02
- Validated and executed actions (with success/failed status)
- Skipped actions with their reason
- An empty "Learnings" section (to fill in manually)

### 7. Final synthesis

```
╔══════════════════════════════════════════════════════════╗
║         CURATION REVIEW COMPLETE, {YYYY-MM-DD}          ║
╚══════════════════════════════════════════════════════════╝

✅ Actions executed: {N success}
   - /distill: {N1 done} / {N1 validated}
   - /archive: {N2 done} / {N2 validated}
   - /moc-new: {N3 done} / {N3 validated}

⚠️  Failures: {N failed}
   {list with reason}

📝 Review log: {path or "not created"}

Indexes regenerated. Basic Memory reindex clean.

Next steps:
- Check the local graph of the new MOCs in Obsidian
- Fill in the "Learnings" section of the log if created
- Re-run `/curate` in {window_days} days (or the next {weekly|monthly} review)

If some actions failed, run the matching skill manually to understand the blocker.
```

### 8. Frequency suggestion

Depending on the results:

- **0 candidates detected**: "Clean workspace, space the reviews out to every 2 weeks."
- **1-3 actions**: "Current cadence is fine, keep it weekly."
- **4-10 actions**: "Plenty to do, maybe switch to a bi-weekly review to avoid buildup."
- **10+ actions**: "Heavy buildup, plan a dedicated slot for the next review."

---

## SUCCESS METRICS:

✅ All `{validated_actions}` were attempted
✅ Indexes regenerated at the end of the batch
✅ Final Basic Memory reindex clean
✅ Review log created if requested
✅ Synthesis presented to the user

## FAILURE MODES:

❌ Reimplementing inline (a direct git mv instead of calling /archive)
❌ Running actions in parallel (graph conflicts)
❌ Skipping the final index regeneration
❌ Abandoning everything on a single failed action

---

## END

This is the last step. Review complete. Suggest next actions and exit.
