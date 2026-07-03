---
name: sb-doctor
description: Workspace health check for the second brain. Runs the maintenance scripts (orphan notes, double frontmatter, symmetric relations), verifies naming and filing conventions, checks index freshness and inbox age, and produces a severity-ranked health report with the exact command to fix each finding. Read-only, never fixes anything itself. Triggers on "sb-doctor", "check the workspace", "health check", "is my second brain healthy".
argument-hint: "[-v]"
---

<objective>
A monthly (or whenever-in-doubt) hygiene pass over the whole workspace. It detects rot early: orphan notes nobody will ever find again, convention drift that breaks predictable addressability, stale indexes that lie to agents. It reports and prescribes; the fixes stay in the owner's hands.
</objective>

<quick_start>

```
/sb-doctor        # full health report
/sb-doctor -v     # verbose: list every affected file instead of counts
```

</quick_start>

<execution_rules>
- **Read-only.** Never write, move, or fix anything; every finding comes with the command or skill that fixes it
- Run every check even if an early one fails; the report must be complete
- A check that cannot run (missing script, missing tool) is reported as SKIPPED with the reason, never silently dropped
- Findings are ranked: 🔴 CRITICAL (breaks retrieval or integrity), 🟡 WARN (drift, will hurt later), 🔵 INFO (hygiene)
</execution_rules>

<checks>

Run each check from the workspace root and collect results.

### 1. Double frontmatter (🔴)

```bash
python3 basic-memory/scripts/check_double_frontmatter.py
```

Corrupted files break parsing and indexing. Fix: `python3 basic-memory/scripts/fix_double_frontmatter.py --apply`.

### 2. Orphan notes (🟡)

```bash
python3 basic-memory/scripts/check_orphans.py
```

Notes with no incoming or outgoing wiki-link are invisible to graph navigation. Fix: add `## Relations` blocks, or run `python3 basic-memory/scripts/auto_link_entities.py --dry-run` to preview automatic linking.

### 3. Symmetric relations (🟡, only if `sources/partners/` exists)

```bash
python3 basic-memory/scripts/check_symmetric_relations.py
```

Broken pairs (managed_by without manages, etc.) corrupt the entity graph. Fix: apply the script's suggestions manually in the listed CLAUDE.md files.

### 4. Filing conventions (🔴)

- Files at an entity root (forbidden except CLAUDE.md/CONTEXT.md): `find sources/*/*/ -maxdepth 1 -type f ! -name 'CLAUDE.md' ! -name 'CONTEXT.md' ! -name 'README.md' ! -name '.gitkeep'`
- Names not matching `YYYY-MM-DD-{type}-slug.md` in project folders (report count, list in verbose). Legacy files predating the convention are INFO, not CRITICAL.

Fix: `git mv` to the conventional path/name; `/capture` files things correctly going forward.

### 5. Frontmatter typing (🟡)

- Markdown files under `sources/`, `knowledge/`, `atlas/` with no `type:` in frontmatter, or a `type:` not present in `basic-memory/schemas/` (grep-based scan, exclude READMEs and .gitkeep).

Fix: `python3 basic-memory/scripts/retype_files.py --dry-run` then `--apply`, or edit manually.

### 6. Index freshness (🟡)

- For each `atlas/maps/*-static.md`: read the `generated:` frontmatter date. Older than 7 days → stale.

Fix: `python3 basic-memory/scripts/generate_indexes.py`.

### 7. Inbox age (🟡)

- Items in `inbox/` older than 7 days (file mtime), excluding README and .gitkeep.

Fix: `/capture -i`.

### 8. Basic Memory sync (🔵, only if `bm` is installed)

```bash
command -v bm >/dev/null 2>&1 && bm status --project {project from CLAUDE.md profile block}
```

Unindexed files mean search misses them. Fix: `bm reindex --project {project}`.

</checks>

<report>

Assemble a single report, worst first:

```
# Workspace health: {🔴 n critical / 🟡 n warnings / 🔵 n info}

| # | Severity | Check | Findings | Fix |
|---|---|---|---|---|
{one row per non-clean check, findings as count (or file list if -v)}

✓ Clean: {comma-separated list of checks that passed}
⏭ Skipped: {check: reason, if any}

Suggested order: {the 1-3 fixes that matter most, as ready-to-run commands}
```

Write it in the owner's working language (see the CLAUDE.md profile block). No generic reassurance; if everything is clean, say exactly that in one line.
</report>
