---
name: distill
description: Distill a recurring pattern from sources/ into knowledge/. Scans the notes to find N similar occurrences (by topic, tag, or keyword), generates a pattern, playbook, guide, runbook, or decision in knowledge/{ops,tech,business}/ with the canonical Basic Memory frontmatter, and creates back-links to the distilled sources. Core of the layered second-brain philosophy: it turns recurring artifacts into reusable knowledge. Use when a subject, technique, or process recurs at least 3 times in the workspace and deserves to be codified.
argument-hint: "<topic|--auto> [-t ops|tech|business] [-k pattern|playbook|guide|runbook|decision] [-m N] [-a auto]"
model: opus
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - Skill
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

<objective>
Distill repeated knowledge in `sources/` into reusable notes in `knowledge/`. Aim for the **3rd repetition**, the pattern documented in `.claude/rules/knowledge.md`. Without this workflow, `knowledge/` stays empty forever and the second brain never performs its distillation role.

Out of scope: creating content outside the workspace, scraping external sources, or inventing unsourced content.
</objective>

<quick_start>

```bash
/distill accessibility-audit                     # distill the accessibility-audit pattern
/distill accessibility-audit -t ops -k playbook  # force the domain and the subtype
/distill --auto                                  # scan all of sources/, propose distillation candidates
/distill api-retry-pattern -t tech               # distill a technical retry pattern
/distill pricing-website -t business -k guide
/distill accessibility-audit -m 5                # require at least 5 occurrences (default: 3)
/distill -a accessibility-audit                  # auto, no intermediate confirmations
```

</quick_start>

<flags>

| Flag | Long | Description |
|------|------|-------------|
| `-t` | `--target` | Target subfolder in knowledge/, values: `ops`, `tech`, `business`. Auto-deduced if absent |
| `-k` | `--kind` | Deliverable subtype, values: `pattern`, `playbook`, `guide`, `runbook`, `decision`. Auto-deduced if absent |
| `-m` | `--min` | Minimum occurrence threshold to distill (default: 3) |
| `-a` | `--auto` | Skip confirmations, generate and save directly |
| `--auto` (mode) | no value | Scan all of sources/ to propose distillation candidates (discovery mode) |

</flags>

<workflow>
1. **Init** -> Parse topic, flags, deduce target/kind if not provided
2. **Scan** -> Find the occurrences (frontmatter topics:, wiki-links, keywords), group by client/project
3. **Draft** -> Pre-fill the knowledge template with the extracted patterns, cite the sources
4. **Publish** -> User validation, save into knowledge/{target}/, create the back-links
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Parse args, deduce target/kind, validate threshold |
| 01 | `steps/step-01-scan.md` | Scan sources/ for occurrences, group, score |
| 02 | `steps/step-02-draft.md` | Pre-fill the template with Basic Memory frontmatter + distilled body |
| 03 | `steps/step-03-publish.md` | Validate, save, create back-links to sources |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{topic}` | string | step-00 |
| `{mode}` | enum (`topic\|auto`) | step-00 |
| `{target}` | enum (`ops\|tech\|business`) | step-00 (or step-01 auto-deduce) |
| `{kind}` | enum (`pattern\|playbook\|guide\|runbook\|decision`) | step-00 (or step-01 auto-deduce) |
| `{min_occurrences}` | number | step-00 (default 3) |
| `{auto_mode}` | boolean | step-00 |
| `{sources_found}` | list | step-01 (paths + excerpts) |
| `{occurrence_count}` | number | step-01 |
| `{draft_path}` | string | step-02 |
| `{draft_content}` | string | step-02 |
| `{published_path}` | string | step-03 |

</state_variables>

<references>

| Reference | Used by |
|-----------|---------|
| `references/knowledge-template.md` | step-02 (subtype-specific template) |
| `.claude/rules/knowledge.md` | step-00, step-02 (conventions) |
| `basic-memory/schemas/note.md` | step-02 (frontmatter validation) |

</references>

<execution_rules>
- **Always scan before proposing**: no pattern without at least 3 real sources (or the `-m` threshold)
- **Cite every source** in the produced pattern via `distilled_from [[Source]]` wiki-links
- **Anonymize client content**: no registration numbers, no internal emails, no confidential details
- **Strict frontmatter**: `type: note` + `subtype:` (no dedicated BM schemas)
- **Naming convention**: `knowledge/{target}/{short-subtype}-{slug}.md`
- **Validate before writing**: always show the draft to the user (except `-a auto`)
- **If fewer than N occurrences**: refuse to distill, suggest trying again later
- **If already distilled**: if a file knowledge/{target}/{subtype}-{slug}.md exists, offer to update rather than duplicate
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`
</entry_point>
