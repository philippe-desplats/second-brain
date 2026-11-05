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

Corrupted files break parsing and indexing. Fix: preview the merge with `python3 basic-memory/scripts/fix_double_frontmatter.py` (dry-run by default), then `python3 basic-memory/scripts/fix_double_frontmatter.py --apply`. A file flagged as outside the corpus is repaired by hand.

### 2. Orphan notes (🟡)

```bash
python3 basic-memory/scripts/check_orphans.py
```

Notes with no incoming or outgoing wiki-link are invisible to graph navigation. Fix: add `## Relations` blocks, or run `python3 basic-memory/scripts/auto_link_entities.py --dry-run` to preview automatic linking.

### 3. Symmetric relations (🟡, only if `sources/partners/` exists)

```bash
python3 basic-memory/scripts/check_symmetric_relations.py --check
```

Broken pairs (managed_by without manages, etc.) corrupt the entity graph. Fix: apply the script's suggestions manually in the listed CLAUDE.md files.

### 4. Filing conventions (🔴)

- Files at an entity root (forbidden except CLAUDE.md/CONTEXT.md): `find sources/*/*/ -maxdepth 1 -type f ! -name 'CLAUDE.md' ! -name 'CONTEXT.md' ! -name 'README.md' ! -name '.gitkeep'`
- Names not matching `YYYY-MM-DD-{type}-slug.md` in project folders (report count, list in verbose). Legacy files predating the convention are INFO, not CRITICAL.

Fix: `git mv` to the conventional path/name; `/capture` files things correctly going forward.

### 5. Frontmatter typing (🟡)

- Markdown files under `sources/`, `knowledge/`, `atlas/` with no `type:` in frontmatter, or a `type:` not present in `basic-memory/schemas/` (grep-based scan, exclude READMEs and .gitkeep).

Fix: `python3 basic-memory/scripts/retype_files.py --dry-run` then `--apply`, or edit manually.

### 5bis. Workspace self-consistency (🔴)

```bash
python3 basic-memory/scripts/check_consistency.py
```

Three classes, all of them silent failures rather than errors:

- a skill template that emits frontmatter the schemas reject, so a note written from it belongs to no type and disappears from every index and every view
- a Bases view reading a property no schema declares, so the column stays empty or the filter never matches, while the view still renders and looks fine
- a wiki-link resolving to nothing

Exit code 1 means findings. Nothing here is auto-fixable: each one is a decision about which side is wrong, the template or the schema.

### 6. Index freshness (🟡)

- For each `atlas/maps/*-static.md`: read the `generated:` frontmatter date. Older than 7 days → stale.
- If `atlas/maps/` contains no `*-static.md` at all, report it as a finding rather than passing silently. An empty glob means the indexes have never been generated, not that they are fresh.
- The `atlas/maps/*.base` files are queries, not snapshots. They never go stale and are not checked here.

Fix: `python3 basic-memory/scripts/generate_indexes.py`.

### 7. Inbox age (🟡)

- Items in `inbox/` older than 7 days (file mtime), excluding README and .gitkeep.

Fix: `/capture -i`.

### 8. Workspace config (🟡)

- `.sb-config.json` exists and parses (`python3 -c "import json; json.load(open('.sb-config.json'))"`).
- `initialized` is `true` (if false, the workspace never ran `/sb-init`: that is the fix).
- Its values match the CLAUDE.md profile block (owner, profile, working language, Basic Memory project); a divergence means one was edited by hand.

Fix: re-run `/sb-init -r` to resync both, or align the drifted field manually.

### 9. Basic Memory sync (🔵, only if `bm` is installed)

```bash
command -v bm >/dev/null 2>&1 && bm status --project {basic_memory_project from .sb-config.json}
```

Unindexed files mean search misses them. Fix: `bm reindex --project {basic_memory_project}`.

### 10. Graph orphan cross-check (🔵, only if `bm` is installed)

```bash
command -v bm >/dev/null 2>&1 && bm orphans --project {basic_memory_project from .sb-config.json} --json | python3 -c "import json,sys; d=json.load(sys.stdin); z=('sources/','knowledge/','atlas/'); print(d.get('error','') if isinstance(d,dict) else '\n'.join(e['file_path'] for e in d if e['file_path'].startswith(z) and not e['file_path'].endswith('-static.md')))"
```

Reads the indexed graph where check 2 reads the raw files, so only the filtered paths are comparable. Raw `bm orphans` covers every indexed entity of the project, `LICENSE`, the Python scripts, `docs/`, `archives/`, images, none of which check 2 scans; the filter keeps the three zones it does scan, minus the `-static.md` indexes it also ignores. Anything the filter drops is out of scope, never a finding. Report a finding only for a filtered path absent from check 2's list: the index is stale, or a relation the raw scan resolved failed to parse. Fix: `bm reindex --project {basic_memory_project}` for that divergence, `## Relations` blocks for a genuinely unlinked note, same fix as check 2. If the workspace is not a registered Basic Memory project, the command prints its error instead of a path list: report SKIPPED with that reason.

### 11. Schema validation (🟡, only if `bm` is installed)

```bash
command -v bm >/dev/null 2>&1 && for t in $(ls basic-memory/schemas/*.md | xargs -n1 basename | sed 's/\.md$//' | grep -v README); do bm schema validate "$t" --strict --project {basic_memory_project from .sb-config.json}; done
```

The type argument is not optional in practice: omitting it does not validate everything as the help text claims, it reports `No notes found of type 'unknown'` (observed on 0.21.1 and 0.22.1). Hence the loop over the schema names. A type with no note yet answers `No notes found of type '{t}'`, which is normal on a young workspace, not a finding.

Validates every note carrying a `type:` that matches a schema, against both that schema's frontmatter contract and its body contract. Fix: add the missing observation or relation to the note body, or correct the frontmatter field; `bm schema diff {type}` shows where a whole type has drifted from its schema. `--strict` exits with code 1 on validation errors, so this check also runs unattended in a pipeline. If `bm` is absent, the workspace is not a registered Basic Memory project, or nothing is indexed yet, report SKIPPED with that reason.

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
