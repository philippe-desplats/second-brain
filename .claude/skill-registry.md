# Skill Registry

Central router for the workspace skills. Consult this table before invoking any skill, to match the right skill to the actual request.

## Quick routing

| If the owner wants to... | Skill |
|---|---|
| Initialize or reconfigure this workspace | `/sb-init` |
| File inbound content (email, transcript, notes) or process the inbox | `/capture` (`-i` for inbox) |
| Check the workspace health (orphans, conventions, frontmatter) | `/sb-doctor` |
| Run the weekly or monthly workspace review | `/curate` |
| Promote a recurring pattern into reusable knowledge | `/distill` |
| Create a Map of Content for a dense topic | `/moc-new` |
| Archive a dead project | `/archive` |
| Summarize raw content (transcript, notes, article) | `/ops-resume` |
| Write a professional email (new or reply) | `/ops-email` |
| Turn notes or a transcript into meeting minutes | `/ops-meeting-minutes` |
| Draft a commercial proposal | `/ops-proposal` |
| Start a new project or work session with proper structure | `/ops-init-project` |
| Get a dashboard of the week's activity | `/ops-weekly-pulse` |
| Analyze reference or competitor websites | `/ops-benchmark-web` |
| Create or analyze spreadsheets (Excel, CSV) | `/ops-xlsx` |

## Maintenance cycle

`/curate` is the orchestrator: it scans and proposes; `/distill`, `/moc-new`, and `/archive` execute, each with human validation. The `librarian` agent (`.claude/agents/librarian.md`) can drive the whole cycle. Recommended ritual: `/curate -w 7` once a week.

## Full registry

| Skill | Triggers | Input | Output | Dependencies |
|---|---|---|---|---|
| `sb-init` | first run, "initialize", "set up my second brain", `-q` quick, `-r` reconfigure | interview answers | charter, CONTEXT.md, profile block, pruned zones, optional Basic Memory wiring | none (Basic Memory optional) |
| `capture` | "capture this", "file this email", "process my inbox", `-i` `-e {entity}` `-t {type}` | pasted content, @file, or inbox queue | artifact filed at the conventional path, schema frontmatter, verbatim body | none |
| `sb-doctor` | "check the workspace", "health check", monthly hygiene | none (scans the workspace) | health report: orphans, double frontmatter, broken conventions, stale indexes, aged inbox | Python 3 |
| `curate` | weekly/monthly review, `-w {days}` | window of recent activity | report of distill/archive/moc candidates, delegation on approval | Basic Memory optional |
| `distill` | 3rd repetition of a topic, "distill X" | topic or slug, `-t {ops\|tech\|business}` `-k {kind}` | note in `knowledge/` with provenance line and back-links | Basic Memory optional |
| `moc-new` | dense topic (10+ notes), "create a map for X" | topic slug | MOC in `atlas/maps/` (Dataview + curated list) | Obsidian Dataview for live view |
| `archive` | project done/cancelled 6+ months, `--dry-run` | project slug | `git mv` to `archives/`, reference fixes, reindex | git; Basic Memory optional |
| `ops-resume` | "summarize this", transcript or article pasted | raw content | structured summary saved via save-conventions | none |
| `ops-email` | "write an email to X", "reply to this", `-e {entity}` `-s` | purpose or pasted thread | draft calibrated on prior emails and entity preferences, saved with email frontmatter (draft, then sent) | none |
| `ops-meeting-minutes` | "make minutes from this", notes or `@transcript`, `-e {entity}` `-i` internal | raw notes, transcript, or recap | client-facing or internal minutes in `meetings/` with meeting frontmatter | none |
| `ops-proposal` | "proposal for X", `{entity} - {need}` | entity + scope interview | structured proposal (understanding, approach, deliverables, timeline, investment) with writing frontmatter; never invents pricing | none |
| `ops-init-project` | "new project for X", session bootstrap | intent description | project folder + README/context files from schemas | none |
| `ops-weekly-pulse` | "what happened this week" | scan of the 4 zones | weekly dashboard in `sources/internal/weekly-pulse/` | none |
| `ops-benchmark-web` | "analyze these sites", `-p {entity}` | URLs, optional entity context | benchmark report (design/UX/stack patterns) | web access |
| `ops-xlsx` | any spreadsheet creation/analysis | file or data | .xlsx/.csv deliverable | Python 3 |

## Conventions every skill follows

- Deliverables are saved according to `.claude/skills/references/save-conventions.md` (never at an entity root, always `YYYY-MM-DD-{type}-slug.md`).
- Generated content uses the owner's working language (see the profile block in `CLAUDE.md`); skill structure stays in English.
- Frontmatter conforms to `basic-memory/schemas/`; the decision matrix is `.claude/rules/frontmatter.md`.
- Outward-facing content follows `.claude/rules/communication.md` (no emoji, no em dashes, never mention AI assistance).

## Extending

Add new skills under `.claude/skills/{name}/` with a `SKILL.md` entry point, then register them here. Keep one row per skill and update the quick-routing table only for the frequent cases.
