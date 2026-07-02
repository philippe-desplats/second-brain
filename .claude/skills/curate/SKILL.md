---
name: curate
description: Weekly or monthly workspace review. Automatically detects candidates for `/distill` (recurring patterns not yet distilled), `/archive` (dormant entities), and `/moc-new` (dense topics without a MOC). Presents a report grouped by action and lets the user trigger each skill through interactive validation. Aligned with the periodic curation ritual ("what did I learn this week that deserves distillation, archiving, or mapping?"). NEVER writes files directly; it is a suggestion orchestrator, not an autonomous executor. Use for a weekly review (end of week), a monthly review (first of the month), or after an intense writing period.
argument-hint: "[-s scope] [-w window] [-min N] [-only distill|archive|moc] [-a auto]"
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
  - Skill
---

<objective>
Periodically scan the workspace to identify curation opportunities: distilling recurring patterns into `knowledge/`, archiving dormant entities into `archives/`, and creating MOCs for dense, unmapped topics. Present a grouped report to the user and trigger the matching skills (`/distill`, `/archive`, `/moc-new`) based on their validation.

Aligned with the LYT/PARA philosophy: "a second brain is maintained, not built once and forgotten." The goal is to prevent workspace entropy while keeping the human in the loop for every action.

Out of scope: writing or moving files directly; that is the job of the delegated skills. Out of scope: archiving or distilling without user validation.
</objective>

<quick_start>

```bash
/curate                                          # full review, full workspace scope
/curate -s clients                               # scope only clients (archive candidates mostly)
/curate -s knowledge                             # scope distillation (recurring patterns)
/curate -w 7                                     # 7-day window (weekly review)
/curate -w 30                                    # 30-day window (monthly review)
/curate -only distill                            # only distill candidates
/curate -only archive -min 12                    # archive candidates inactive > 12 months
/curate -a                                       # auto mode, execute without confirmation (discouraged)
```

</quick_start>

<flags>

| Flag | Long | Description |
|------|------|-------------|
| `-s` | `--scope` | Scan scope: `full` (default), `clients`, `partners`, `internal`, `knowledge`, `topics` |
| `-w` | `--window` | Time window in days to detect "recent" (default: 30) |
| `-min` | `--min-inactive` | Months of inactivity to qualify a dormant entity (default: 6) |
| `-only` | `--only` | Filter suggestion type: `distill`, `archive`, `moc`, or a comma-separated combination |
| `-a` | `--auto` | Skip confirmations, execute all suggestions (discouraged outside tests) |

</flags>

<workflow>
1. **Init** -> Parse flags, validate scope and windows
2. **Scan** -> Detect the 3 candidate types with numeric criteria
3. **Report** -> Present a report grouped by action and allow per-candidate validation
4. **Execute** -> For each validated candidate, delegate to the matching skill (`/distill`, `/archive`, `/moc-new`)
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Parse args, validate scope |
| 01 | `steps/step-01-scan.md` | Detect distill/archive/moc candidates with criteria |
| 02 | `steps/step-02-report.md` | Present the grouped report, AskUserQuestion per candidate |
| 03 | `steps/step-03-execute.md` | Delegate to validated skills, track executions |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{scope}` | enum | step-00 |
| `{window_days}` | number | step-00 |
| `{min_inactive_months}` | number | step-00 |
| `{only_filter}` | list | step-00 |
| `{auto_mode}` | boolean | step-00 |
| `{candidates_distill}` | list of dicts | step-01 |
| `{candidates_archive}` | list of dicts | step-01 |
| `{candidates_moc}` | list of dicts | step-01 |
| `{validated_actions}` | list | step-02 |
| `{executed_actions}` | list | step-03 |

</state_variables>

<references>

| Reference | Used by |
|-----------|---------|
| `.claude/skills/distill/SKILL.md` | step-03 (delegation) |
| `.claude/skills/archive/SKILL.md` | step-03 (delegation) |
| `.claude/skills/moc-new/SKILL.md` | step-03 (delegation) |
| `.claude/rules/knowledge.md` | step-01 (the "3rd repetition" criterion) |
| `.claude/rules/atlas.md` | step-01 (MOC vs index) |

</references>

<execution_rules>
- **Numeric detection, not instinct**: every candidate must produce a score and the reason behind the score (count, dates, etc.)
- **No direct writes**: this skill orchestrates, it never writes into the workspace (except optional logs)
- **Per-candidate validation**: unless `{auto_mode}`, each candidate goes through an individual AskUserQuestion (or grouped if the volume is high)
- **Clean delegation**: call the `/distill`, `/archive`, `/moc-new` skills via the Skill tool, never reimplement them inline
- **Idempotence**: running `/curate` twice in a row must give the same result if nothing changed
- **Review log**: optionally create a note `atlas/reviews/{YYYY-MM-DD}-review.md` for traceability (validated in step-03)
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`
</entry_point>
