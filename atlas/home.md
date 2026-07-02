---
title: Atlas, workspace entry point
type: note
subtype: moc
schema_version: 1
date: YYYY-MM-DD
status: active
---

# Atlas, workspace entry point

_Main hub of the second brain. Single entry point to navigate the workspace._

## Understanding the structure

The workspace is organized in layered zones. Each note lives in exactly one zone according to its nature.

| Zone | What you find there |
|---|---|
| `sources/` | Raw artifacts, the raw material (emails, transcripts, meeting notes, deliverables, client/partner/project context) |
| `knowledge/` | Distilled knowledge reusable outside a client context (patterns, playbooks, guides, runbooks, cross-cutting decisions) |
| `atlas/` | Maps, indexes, entities (people, services, topics, MOCs, Dataview indexes, this hub) |
| `archives/` | Inactive or finished projects/clients/missions (mirror of sources) |
| `inbox/` | Buffer zone for artifacts not yet classified (7 days maximum) |
| `basic-memory/` | Basic Memory infrastructure (schemas, scripts, implementation) |
| `templates/` | Note templates |

## Generated indexes (Dataview + static)

Dataview indexes refresh automatically when opened in Obsidian. The `*-static.md` versions are readable outside Obsidian (any editor, agents). All are produced by `basic-memory/scripts/generate_indexes.py`.

- [[clients-active]], clients with status: active
- [[partners-active]], partners with status: active
- [[projects-active]], project briefs with status: active
- [[recent-emails]], emails from the last 14 days
- [[decisions-recent]], decisions observed in the last 90 days

## Referenceable entities

- `atlas/people/`, people files (contacts, decision-makers, prospects)
- `atlas/services/`, your offerings (technical, consulting, hosting, etc.)
- `atlas/topics/`, cross-cutting subjects (ai-agents, accessibility, seo, kubernetes, etc.)

## Maps of Content (MOC)

Manual thematic maps, for dense subjects that deserve an entry page.

```dataview
LIST FROM "atlas/maps"
WHERE subtype = "moc"
SORT file.name
```

## Distilled knowledge by domain

```dataview
TABLE subtype, status
FROM "knowledge"
SORT file.path ASC
```

- `knowledge/ops/`, operational processes (client onboarding, billing workflow, audit procedures)
- `knowledge/tech/`, technical patterns (deployment, infrastructure, APIs, automation)
- `knowledge/business/`, strategy, pricing, commercial methodology

## Filing conventions

Three questions to file any new note:

1. Is it a raw artifact (email, transcript, deliverable)? -> `sources/`
2. Is it distilled reusable knowledge? -> `knowledge/`
3. Is it an index, a map, or an entity? -> `atlas/`

If none fits, `inbox/` to classify within the week.

Full details in the root `CLAUDE.md` and `.claude/rules/`.

## Relations

- contains [[clients-active]]
- contains [[partners-active]]
- contains [[projects-active]]
