---
title: Brainstorm
type: schema
entity: brainstorm
schema_version: 1
schema:
  date: string, "session date in YYYY-MM-DD format"
  title: string, "brainstorm subject"
  category?(enum):
  - internal
  - client
  - partner
  - personal
  mode?(enum):
  - solo
  - collective
  process?: string, "process used, e.g. 4 phases, divergence-convergence"
  participants?(array): string, "participants if collective session"
  client?: ClientContext, "client involved if the brainstorm is scoped to a client"
  partner?: PartnerContext, "partner involved if the brainstorm is scoped to a partnership"
  status?(enum):
  - draft
  - converged
  - archived
  about?: Topic, "brainstorm subject"
  feeds?: Strategy, "strategy fed by this brainstorm"
settings:
  validation: warn
---

# Schema, Brainstorm

Ideation session, creative exploration, or challenge of a problem. Not a conclusive document, rather an open space that can later produce research, a strategy, or a project.

Usable for all 4 categories. The `mode` field distinguishes solo sessions (individual reflection) from collective sessions (with `participants` filled in).

## Typical location

- `sources/clients/{client}/{project}/YYYY-MM-DD-brainstorm-slug.md`
- `sources/partners/{partner}/{project}/YYYY-MM-DD-brainstorm-slug.md`
- `sources/internal/{project}/YYYY-MM-DD-brainstorm-slug.md`
- `sources/personal/{project}/YYYY-MM-DD-brainstorm-slug.md`

## Reference examples

- `sources/internal/workspace-methodology/2026-02-12-brainstorm-structure.md` (internal, solo)
- `sources/clients/globex/infra-migration/2026-02-12-brainstorm-swarmpit-to-dokploy.md` (client)
- `sources/personal/keyboard-locker/2026-03-08-brainstorm-keyboard-locker.md` (personal, solo)

## Expected observations

- `[idea]` raw idea, even if not fully formed
- `[question]` question explored
- `[pro]` argument for an option
- `[con]` argument against an option
- `[decision]` decision emerging at the end of the session

## Typed relations in the frontmatter

- `about`, brainstorm subject
- `client` or `partner`, entity involved if a scope is identified
- `feeds`, strategy or project fed afterwards

## Additional relations in markdown

- `for [[Client | Partner | Internal]]`, beneficiary if a scope is identified

## Minimal example

```yaml
---
date: 2026-02-12
title: Brainstorm, Swarmpit to Dokploy migration
category: client
mode: solo
process: 4 phases, exploration + challenge + synthesis + crystallization
client: Globex
status: converged
about: Globex infrastructure
---

# Brainstorm, Swarmpit to Dokploy migration

## Observations
- [idea] Dokploy handles multi-tenant natively
- [pro] Documented REST API, simple CI integration
- [con] Smaller community, risk of discontinuation
- [decision] Migration approved, roadmap to be produced

## Relations
- for [[Globex]]
- feeds [[Dokploy migration action plan]]
```
