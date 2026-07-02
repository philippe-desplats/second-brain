---
title: Strategy
type: schema
entity: strategy
schema_version: 1
schema:
  date: string, "document date in YYYY-MM-DD format"
  title: string, "title of the plan or strategy"
  category?(enum):
  - internal
  - client
  - partner
  - personal
  client?: ClientContext, "client involved if client scope"
  partner?: PartnerContext, "partner involved if partnership scope"
  effort?: string, "effort estimate, e.g. 3 days, 2 weeks"
  status?(enum):
  - draft
  - active
  - executed
  - archived
  scope?: string, "scope covered"
  implements?: Research, "research or study the strategy implements"
settings:
  validation: warn
---

# Schema, Strategy

Action plan, roadmap, architecture, positioning, communication angle, financial projection, learning plan. Forward-looking, committing document, structured by phases or steps.

Usable for the 4 categories, client (project plan), partnership (shared roadmap), internal (product roadmap), personal (learning plan, career plan).

## Typical location

- `sources/clients/{client}/{project}/YYYY-MM-DD-strategy-slug.md`
- `sources/partners/{partner}/{project}/YYYY-MM-DD-strategy-slug.md`
- `sources/internal/{project}/YYYY-MM-DD-strategy-slug.md`
- `sources/personal/{project}/YYYY-MM-DD-strategy-slug.md`

## Reference examples

- `sources/clients/globex/infra-migration/2026-02-12-strategy-migration-action-plan.md` (client)
- `sources/internal/internal-wiki/architecture/2026-03-15-strategy-unified-architecture.md` (internal)
- `sources/internal/email-signature/2026-04-14-strategy-signature-angles.md` (internal)
- Typical personal example, `sources/personal/learn-rust/2026-05-01-strategy-rust-learning-plan-3-months.md`

## Expected observations

- `[goal]` objective to reach
- `[milestone]` roadmap milestone
- `[decision]` structuring decision
- `[risk]` identified risk
- `[kpi]` success indicator

## Typed relations in the frontmatter

- `client` or `partner`, beneficiary if scope identified
- `implements`, research or study the strategy implements

## Additional relations in markdown

- `for [[Client | Partner | Internal]]`, beneficiary as a text link
- `produces [[Deliverable]]`, expected deliverables

## Minimal example

```yaml
---
date: 2026-02-12
title: Action plan, Swarmpit to Dokploy migration
category: client
client: Globex
effort: 3 days
status: active
scope: Containerized infrastructure migration
implements: Swarmpit to Dokploy brainstorm
---

# Action plan, Swarmpit to Dokploy migration

## Observations
- [goal] Migration with no service interruption
- [milestone] Dokploy installed on staging, 2026-02-15
- [milestone] Production cutover, 2026-02-22
- [risk] Loss of historical logs during the switchover
- [kpi] Zero downtime, rollback within 10 min if needed

## Relations
- for [[Globex]]
- produces [[Globex migration report]]
```
