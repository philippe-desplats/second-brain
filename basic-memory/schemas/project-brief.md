---
title: Project Brief
type: schema
entity: project-brief
schema_version: 1
schema:
  title: string, "project title"
  category?(enum):
  - internal
  - client
  - partner
  - personal
  client?: ClientContext, "client involved if category=client"
  partner?: PartnerContext, "partner involved if category=partner"
  created?: string, "creation date in YYYY-MM-DD format"
  status?(enum):
  - active
  - done
  - paused
  - rejected
  - archived
  owner?: Person, "main owner"
  depends_on?: ProjectBrief, "project this project depends on"
settings:
  validation: strict
---

# Schema, Project Brief

A `README.md` or `CLAUDE.md` file at the root of a project. Describes the objective, the context, the planned activities, the folder structure and the decisions. This schema covers both cases:

- **`README.md`**, human entry point, documentation-oriented
- **Project `CLAUDE.md`** (e.g. `sources/internal/kubernetes-cluster/CLAUDE.md`), agent instructions loaded automatically

When a project has both, the `CLAUDE.md` takes priority for agent instructions, the `README.md` for human documentation.

## Location

- `sources/internal/{project}/README.md` or `CLAUDE.md`
- `sources/clients/{client}/{project}/README.md` or `CLAUDE.md`
- `sources/partners/{partner}/{project}/README.md` or `CLAUDE.md`
- `sources/personal/{project}/README.md` or `CLAUDE.md`

## Recommended markdown sections

- `## Objective`, 1 to 3 lines
- `## Context`, 2 to 3 sentences
- `## Planned activities`, list or checklist
- `## Structure`, tree and conventions
- `## Decisions and notes`, chronological log

## Variants by project nature

- **Long-term strategic project** (internal-wiki), architecture, diagrams, deliverables
- **Community project** (community), metrics, onboarding, contacts
- **Lightweight operational project** (automation-workflows), minimal structure
- **Rejected project post mortem** (sunset-experiment), `status: rejected` + `[rejection-reason]` observation

## Expected observations

- `[goal]` objective to reach
- `[milestone]` milestone reached or planned
- `[decision]` scope or architecture decision
- `[rejection-reason]` rejection reason if `status: rejected`

## Typed relations in the frontmatter

- `client` or `partner`, parent entity
- `depends_on`, other project this one depends on

## Additional relations in markdown

- `parent [[Client | Partner | Internal]]`, parent entity as a text link
- `produces [[Deliverable]]`, deliverables produced

## Reference examples

- `sources/internal/internal-wiki/README.md` (long-term strategic)
- `sources/internal/community/README.md` (community)
- `sources/internal/automation-workflows/README.md` (lightweight operational)
- `sources/internal/sunset-experiment/README.md` (rejected post mortem)
- `sources/internal/kubernetes-cluster/CLAUDE.md` (project with an instruction CLAUDE.md)

## Minimal example

```yaml
---
title: Basic Memory, technology evaluation
category: internal
created: 2026-04-15
status: active
owner: Jane Doe
---

# Basic Memory, technology evaluation

## Objective
Understand Basic Memory and evaluate its value for the workspace.

## Observations
- [goal] Deliver a research report and a POC plan
- [milestone] Phase 1 schema design, 2026-04-15

## Relations
- parent [[Acme]]
- produces [[Basic Memory exploration report]]
```
