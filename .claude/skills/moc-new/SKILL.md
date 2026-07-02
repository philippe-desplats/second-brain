---
name: moc-new
description: Create a new MOC (Map of Content) in atlas/maps/ to aggregate the notes linked to a topic. Scans sources/, knowledge/, atlas/topics/ to find the relevant notes (frontmatter topics:, wiki-links, keywords), pre-fills the atlas-moc-template.md with those notes, offers a review to the user, and saves into atlas/maps/MOC-{slug}.md with subtype: moc. Aligned with LYT/MOC best practices (Nick Milo). Use when a topic has become dense enough (10+ notes) to deserve a navigation entry point.
argument-hint: "<topic> [-t MOC|index] [-m N] [-d depth] [-a auto]"
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
Create a navigable MOC in `atlas/maps/` for a dense topic. The MOC acts as an Obsidian hub: it aggregates wiki-links to the relevant notes, organized by type/context, and lets a human or an agent grasp a subject at a glance.

Aligned with the layered design (atlas/maps/ holds MOCs + indexes) and the practice of building a handful of manual MOCs for the densest topics.

Out of scope: generating dynamic Dataview indexes (use `generate_indexes.py` for that). Out of scope: creating entity notes (use the conventions in `atlas/people/`, `atlas/services/`, `atlas/topics/`).
</objective>

<quick_start>

```bash
/moc-new accessibility-audits                   # MOC on the accessibility-audits topic
/moc-new ai-agents                              # MOC on AI agents
/moc-new workspace-methodology                  # MOC on the workspace methodology
/moc-new automation-patterns -t MOC             # force the MOC type
/moc-new active-clients -t index -d 1           # flat index, depth=1 (just the CLAUDE.md files)
/moc-new accessibility-audits -m 15             # require 15 notes minimum (default: 10)
/moc-new -a accessibility-audits                # auto, no confirmations
```

</quick_start>

<flags>

| Flag | Long | Description |
|------|------|-------------|
| `-t` | `--type` | Map type: `MOC` (manual, contextual) or `index` (flat, listing). Default: MOC |
| `-m` | `--min` | Minimum note threshold to justify a MOC (default: 10) |
| `-d` | `--depth` | Scan depth (1 = only files at the root, 2 = includes first-level subfolders, 99 = fully recursive). Default: 99 |
| `-a` | `--auto` | Skip confirmations |

</flags>

<workflow>
1. **Init** -> Parse topic, flags, validate that `atlas/maps/MOC-{slug}.md` does not already exist
2. **Scan** -> Find the linked notes (frontmatter, wiki-links, slugs), group by context
3. **Draft** -> Pre-fill the atlas-moc-template with sections per context
4. **Publish** -> User validation, save into atlas/maps/, optionally regenerate the indexes
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Parse args, check for no duplicate |
| 01 | `steps/step-01-scan.md` | Scan the notes linked to the topic, group by client/context |
| 02 | `steps/step-02-draft.md` | Pre-fill the MOC template with structured wiki-links |
| 03 | `steps/step-03-publish.md` | Validate, save into atlas/maps/, create back-links (optional) |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{topic}` | string | step-00 |
| `{slug}` | string | step-00 (kebab-case of the topic) |
| `{map_type}` | enum (`MOC\|index`) | step-00 |
| `{min_notes}` | number | step-00 (default 10) |
| `{depth}` | number | step-00 (default 99) |
| `{auto_mode}` | boolean | step-00 |
| `{target_path}` | string | step-00 (atlas/maps/MOC-{slug}.md) |
| `{notes_found}` | list | step-01 (grouped by context) |
| `{draft_content}` | string | step-02 |
| `{published_path}` | string | step-03 |

</state_variables>

<references>

| Reference | Used by |
|-----------|---------|
| `templates/atlas-moc-template.md` | step-02 (canonical template) |
| `.claude/rules/atlas.md` | step-00, step-02 (conventions) |
| `references/moc-patterns.md` | step-02 (examples by topic type) |

</references>

<execution_rules>
- **Minimum threshold**: at least `{min_notes}` notes found (default 10), otherwise refuse/defer
- **No duplicate**: if `atlas/maps/MOC-{slug}.md` already exists, propose an update instead of creating
- **Strict frontmatter**: `type: note` + `subtype: moc` (or `subtype: index` if `-t index`)
- **Wiki-links**: every referenced note must be a valid wiki-link `[[Exact Title]]`
- **Group by context**: by client/partner, or by type, or by sub-theme depending on density
- **No raw listing**: a structured MOC aggregates AND comments, not just a dump of links
- **Local graph utility**: mentally test that the MOC opens a readable local graph in Obsidian
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`
</entry_point>
