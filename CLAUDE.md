# CLAUDE.md

This file provides guidance to Claude Code when working in this workspace.

## Workspace profile

The machine-readable source of truth is `.sb-config.json` (written by `/sb-init`, consumed by skills and scripts). The block below mirrors it for agent context; `/sb-init` keeps both in sync and `/sb-doctor` checks the sync.

<!-- This block is filled by /sb-init. Do not edit the markers. -->
<!-- sb-init:profile -->
- **Owner**: NOT CONFIGURED
- **Organization**: NOT CONFIGURED
- **Profile**: NOT CONFIGURED (agency | freelance | solopreneur | personal)
- **Working language**: NOT CONFIGURED
- **Basic Memory project**: NOT CONFIGURED
<!-- /sb-init:profile -->

**If the profile above says NOT CONFIGURED, stop and tell the user to run `/sb-init` first.** The workspace is not ready for real work until initialization completes.

## What is this workspace

This is **NOT a code project**. It is a second brain: a general-purpose workspace for capturing, organizing, and retrieving everything about the owner's work and projects. Typical activities: filing emails and meeting notes, writing deliverables, research, brainstorming, strategic analysis, and maintaining distilled knowledge.

**ALWAYS** read `sources/internal/CONTEXT.md` when you need business context (identity, offer, strategy, metrics).

**Entity context** lives in `sources/{zone}/{entity}/CLAUDE.md` and is auto-loaded by Claude Code when working inside that entity's directory. It contains the entity profile and communication preferences.

## Context lookup

Before answering any question about an entity, a project, or past work:

1. **Query Basic Memory first** (if the MCP server is connected): `search_notes` for semantic discovery, `build_context` on a `memory://` URI to follow relations, `recent_activity` for what changed recently.
2. **Then read the files** for authoritative content: the entity's `CLAUDE.md`, then the relevant project folder, then `sources/internal/CONTEXT.md` for business context.
3. If no local data exists, say so explicitly and ask whether to create a context file.

**NEVER** invent context. When the user mentions a name or asks "what did we do for X", always search local files before responding.

## File organization: three zones

| Zone | Purpose |
|---|---|
| `sources/` | Raw artifacts, the raw material (emails, meeting notes, deliverables, research, entity contexts) |
| `knowledge/` | Distilled reusable knowledge, independent of any entity (patterns, playbooks, guides, runbooks, decisions). See `.claude/rules/knowledge.md` |
| `atlas/` | Maps, indexes, referenceable entities (people, services, topics, MOCs, home.md). See `.claude/rules/atlas.md` |

Plus two utility zones: `archives/` (inactive projects, mirror of `sources/`) and `inbox/` (7-day buffer for unclassified artifacts).

### Three questions to file any new note

1. Is it a raw artifact (email, meeting notes, deliverable, raw research)? → `sources/`
2. Is it distilled reusable knowledge (pattern, playbook, guide, runbook, decision)? → `knowledge/`
3. Is it an index, a map, or a referenceable entity (person, service, topic, MOC)? → `atlas/`

If none fits: `inbox/` (classify within 7 days) or `archives/` (if inactive).

### Detailed paths

| Path | What goes there |
|---|---|
| `sources/clients/{client}/` | Client work: `CLAUDE.md` (context + preferences) + project subdirectories |
| `sources/partners/{partner}/` | Partnership work (bilateral relationships, resellers, co-delivery): same structure as clients |
| `sources/internal/{project}/` | Internal work (pricing, strategy, infrastructure, methodology) |
| `sources/personal/{project}/` | Personal projects (learning, side ideas) |
| `knowledge/ops/` | Operational playbooks and procedures |
| `knowledge/tech/` | Technical patterns, architectures, runbooks |
| `knowledge/business/` | Strategy, pricing, commercial methodology |
| `atlas/people/` | People files (`type: person`) |
| `atlas/services/` | Your services or offers (`type: service`) |
| `atlas/topics/` | Transverse topics (`type: topic`) |
| `atlas/maps/` | MOCs (`subtype: moc`) + generated indexes (`subtype: index`) |
| `atlas/home.md` | Workspace entry point hub |

Unused zones may have been pruned by `/sb-init` depending on the profile; trust the directories that exist.

### Save conventions

**Nothing at an entity root.** Every file MUST live inside a project folder:

- `sources/clients/{client}/{project}/...` ✅
- `sources/clients/{client}/file.md` ❌ FORBIDDEN (except `CLAUDE.md`)

When a skill produces a deliverable, follow `.claude/skills/references/save-conventions.md` for path resolution, subfolder mapping, and naming.

Subfolder conventions: `emails/` for correspondence, `meetings/` for meeting notes, `transcripts/` for transcripts, `deliverables/` for final deliverables; everything else (research, brainstorm, note, strategy) at the project root. Do NOT pre-create empty subdirectories.

### File naming

`YYYY-MM-DD-{type}-slug.md` with types: `research`, `brainstorm`, `writing`, `meeting`, `strategy`, `note`.

Emails: `YYYY-MM-DD-{seq}-{direction}-slug.md` where `seq` is the sequential number for the day (`01`, `02`, ...) and `direction` is `out` (sent), `in` (received), or `reply`. See `.claude/rules/emails.md` and `templates/email-template.md`.

## Basic Memory: schemas and rules

Every markdown file in the workspace conforms to one of the canonical types defined in `basic-memory/schemas/`. The central manifest and decision matrix is `.claude/rules/frontmatter.md`.

- **Canonical schemas**: `basic-memory/schemas/*.md`
- **Maintenance scripts**: `basic-memory/scripts/*.py` (index generation, orphan detection, frontmatter repair, entity linking)
- **Indexing**: if Basic Memory is wired as an MCP server, files resync at session start; run `bm reindex` manually anytime

## Skill routing

Before invoking any skill, consult `.claude/skill-registry.md` to select the best match for the user's request.

## Workspace maintenance

The second brain is maintained, not built once. Four skills form the curation cycle, orchestrated by the `librarian` agent, always with human validation:

| Skill | Role | Trigger |
|---|---|---|
| `/curate` | Scan and propose distill / archive / moc actions | Weekly (`-w 7`) or monthly (`-w 30`) review |
| `/distill` | Promote a recurring pattern from `sources/` to `knowledge/` | Third repetition of a topic |
| `/moc-new` | Create a Map of Content in `atlas/maps/` | Dense topic, 10+ notes |
| `/archive` | Move a dead project to `archives/` via `git mv` | `status: done` or `cancelled` for 6+ months |

## Communication rules

- Write generated content (notes, emails, deliverables) in the **working language** declared in the profile block above.
- Structural files (schemas, rules, skills) stay in English.
- Never mention AI assistance in client-facing content.
- Follow `.claude/rules/communication.md` for tone and formatting of outward-facing documents.
