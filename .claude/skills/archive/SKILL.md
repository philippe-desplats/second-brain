---
name: archive
description: Archive an inactive project, client, partner, or internal project from sources/ into archives/. Confirms inactivity, physically moves the folder (git mv preserves history), updates the incoming references (other projects that point to the archived one), regenerates the Dataview indexes, and runs Basic Memory reindex. Policy: physical move WITHOUT a redundant status. Use when a project is marked `status: done` or `status: cancelled` for 6+ months, or on an explicit decision to archive.
argument-hint: "<slug-or-path> [-t client|partner|internal|personal] [-f force] [-a auto] [--dry-run]"
model: opus
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

<objective>
Move an inactive project from `sources/{type}/{slug}/` into `archives/{type}/{slug}/`, without breaking references. Policy: physical move without a redundant status. The Dataview indexes will filter automatically (queries like `FROM "sources/clients"` ignore the archives).

Out of scope: archiving `.claude/`, `basic-memory/`, `atlas/`, `knowledge/` (non-project zones). Out of scope: archiving an isolated note (use an `archive/` subfolder within the project for obsolete internal artifacts).
</objective>

<quick_start>

```bash
/archive legacy-migration                      # archive sources/internal/legacy-migration/
/archive globex -t client                      # force the type, archive sources/clients/globex/
/archive hooli/partner-portal -t partner       # archive a specific project of a partner
/archive legacy-migration --dry-run            # simulate, show what would happen
/archive legacy-migration -a                   # auto, skip confirmations
/archive legacy-migration -f                   # force, ignore the 6-month inactivity check
```

</quick_start>

<flags>

| Flag | Long | Description |
|------|------|-------------|
| `-t` | `--type` | Entity type: `client|partner|internal|personal`. Auto-deduced if absent |
| `-f` | `--force` | Skip the "inactive for 6 months" check, archive directly |
| `-a` | `--auto` | Skip user confirmations |
| `--dry-run` | no value | Show what would be done without executing |

</flags>

<workflow>
1. **Init** -> Parse args, resolve the source path, deduce the type
2. **Confirm** -> Present the state (last activity, incoming refs), ask for validation
3. **Move** -> git mv into archives/, update the parent CLAUDE.md if applicable
4. **Reindex** -> Regenerate the Dataview indexes, run Basic Memory reindex
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Parse args, resolve `{source_path}`, `{target_path}`, `{type}` |
| 01 | `steps/step-01-confirm.md` | Audit last activity, incoming references, user confirmation |
| 02 | `steps/step-02-move.md` | git mv, update the parent CLAUDE.md, update references |
| 03 | `steps/step-03-reindex.md` | generate_indexes.py + bm reindex + fix_double_frontmatter |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{slug}` | string | step-00 |
| `{type}` | enum (`client\|partner\|internal\|personal`) | step-00 |
| `{source_path}` | string | step-00 (sources/{type}/{slug}/ or sources/{type}/{slug}/{project}/) |
| `{target_path}` | string | step-00 (archives/{type}/{slug}/) |
| `{is_project_scope}` | boolean | step-00 (true if slug = "X/Y", we archive only project Y) |
| `{last_activity_date}` | date | step-01 |
| `{months_inactive}` | number | step-01 |
| `{incoming_refs}` | list | step-01 (other files that point to the path) |
| `{dry_run}` | boolean | step-00 |
| `{auto_mode}` | boolean | step-00 |
| `{force_mode}` | boolean | step-00 |

</state_variables>

<execution_rules>
- **Always git mv** (not cp+rm), to preserve history
- **Always --dry-run first** if the user is unsure (borderline case)
- **6 months of inactivity** = default check, override with `-f`
- **Incoming refs**: if > 5 other notes point to this path, alert explicitly
- **Parent CLAUDE.md**: if archiving a client project (not the whole client), update its CLAUDE.md to mention the archiving
- **No auto update of wiki-links**: Obsidian wiki-links update automatically on rename. In CLI, older textual paths (non-wikilinks) may keep pointing to `sources/...` historically; git history lets you retrieve them
- **`bm reindex`** mandatory after writing (if Basic Memory is installed)
- **Refuse if target already exists**: `archives/{type}/{slug}/` already exists -> ask the user (merge, overwrite, abandon)
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`
</entry_point>
