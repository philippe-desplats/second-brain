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
| `atlas/` | Maps, indexes, entities (people, services, topics, MOCs, Bases index views, this hub) |
| `archives/` | Inactive or finished projects/clients/missions (mirror of sources) |
| `inbox/` | Buffer zone for artifacts not yet classified (7 days maximum) |
| `basic-memory/` | Basic Memory infrastructure (schemas, scripts, implementation) |
| `templates/` | Note templates |

## Generated indexes (Bases + static)

Bases views refresh automatically when opened in Obsidian. Bases is a core plugin, so nothing to install. The `*-static.md` versions are readable outside Obsidian (any editor, agents) and are produced by `basic-memory/scripts/generate_indexes.py`.

- [[clients-active.base|clients-active]], clients with status: active
- [[partners-active.base|partners-active]], partners with status: active
- [[projects-active.base|projects-active]], project briefs with status: active
- [[recent-emails.base|recent-emails]], the most recent emails
- `decisions-recent`, decisions observed in the last 90 days

`decisions-recent` is static only, and the `-static.md` files are generated rather than committed, so they appear after the first run of `basic-memory/scripts/generate_indexes.py`. It reads `- [decision]` observations from note bodies, which Bases filters cannot reach.

## Referenceable entities

- `atlas/people/`, people files (contacts, decision-makers, prospects)
- `atlas/services/`, your offerings (technical, consulting, hosting, etc.)
- `atlas/topics/`, cross-cutting subjects (ai-agents, accessibility, seo, kubernetes, etc.)

## Maps of Content (MOC)

Manual thematic maps, for dense subjects that deserve an entry page.

```base
filters:
  and:
    - file.inFolder("atlas/maps")
    - note.subtype == "moc"
views:
  - type: list
    name: Maps of Content
    order:
      - file.name
    sort:
      - property: file.name
        direction: ASC
```

## Distilled knowledge by domain

```base
filters:
  and:
    - file.inFolder("knowledge")
    - note.subtype != null
properties:
  note.title:
    displayName: Note
  note.subtype:
    displayName: Kind
  note.status:
    displayName: Status
  file.folder:
    displayName: Domain
views:
  - type: table
    name: Distilled knowledge
    order:
      - title
      - subtype
      - status
      - file.folder
    sort:
      - property: file.folder
        direction: ASC
      - property: file.name
        direction: ASC
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

- contains [[clients-active.base]]
- contains [[partners-active.base]]
- contains [[projects-active.base]]
- contains [[recent-emails.base]]
