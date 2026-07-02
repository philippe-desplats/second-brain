# Entity Context Rules (clients and partners)

An **entity** is a client or a partner: a third party you maintain a working relationship with, filed under `sources/clients/{X}/` or `sources/partners/{X}/`. Each entity owns a `CLAUDE.md` context file and a set of project subdirectories. This file covers the conventions shared by both, and the distinction between the two.

## Canonical schemas

- Client `CLAUDE.md` structure and frontmatter: `basic-memory/schemas/client-context.md` (strict validation).
- Partner `CLAUDE.md` structure and frontmatter: `basic-memory/schemas/partner-context.md` (strict validation).

## Client vs partner, how to decide

A **client** is a third party you deliver paid work to. A **partner** is a third party you maintain a **bilateral relationship** with, distinct from a one-off engagement. Partner types:

- **Commercial partners**, resellers, affiliates, co-sellers
- **Technical partners**, white label, cross-delivery
- **Strategic partners**, expert networks, co-shareholding
- **White-label partners**, who resell your work to their own clients

A partner can have client facets (a one-off paid relationship), but the main relationship stays bilateral. Use the `client_facets` and `vendor_facets` fields in the partner schema to capture mixed cases.

Hybrid cases (a partner who is also a client):

- **Main relationship = partnership** (recurring white label, co-shareholding) -> `sources/partners/{partner}/`
- **Main relationship = service you deliver** (a one-off website) -> `sources/clients/{client}/`
- If a partner also has a project treated as a client engagement, the project stays in `sources/clients/{project}/` with `managed_by` and `owned_by` pointing to the partner, and the partner mirrors with `manages` and `owns`.

## Context loading

When working inside an entity folder (`sources/clients/{X}/` or `sources/partners/{X}/`):

1. `CLAUDE.md` is the primary file, loaded automatically by Claude Code
2. Read the communication preferences in the frontmatter **before** any entity-facing output
3. Never invent context, ask the user when information is missing

## Nothing at the entity root

**No file at the root of an entity folder**, everything goes in a project subfolder. The only exception is `CLAUDE.md`.

- `sources/clients/{client}/{project}/...` correct
- `sources/clients/{client}/file.md` forbidden (except `CLAUDE.md`)

## Project naming

Use descriptive kebab-case names for subprojects.

**Clients**, name by the nature of the work:

- `website`, `landing-page`, web projects
- `seo-audit`, `seo`, SEO projects
- `consulting`, strategic consulting or catch-all
- `maintenance`, ongoing maintenance or development
- `contract`, contractual formalization
- `proposal`, sales

**Partners**, name by the nature of the relationship (do not prefix with `partner-`, the parent `sources/partners/` already implies it):

- `follow-up`, recurring follow-up and catch-all
- `white-label`, reselling under a third-party brand
- `reseller`, reselling the partner's product
- `affiliation`, cross or one-way affiliation
- `{product-theme}`, if the partnership is organized around a product

Specific projects inside a relationship: `reseller-contract`, `affiliation-contract`, `lead-sourcing`, `co-dev-{product}`, `{specific-campaign}`.

## Mandatory symmetric pairs

A relation declared on one side must be mirrored on the other, see `.claude/rules/frontmatter.md`.

| Client side | Partner side |
|---|---|
| `managed_by` | `manages` |
| `owned_by` | `owns` |
| `referred_by` | `brings_lead` |
| `co_delivered_with` | `co_delivered_with` |

Check via `python3 basic-memory/scripts/check_symmetric_relations.py --check`.

## Context maintenance

When entity information changes significantly:

1. Update the relevant section in `CLAUDE.md`
2. Update `last_updated` in the frontmatter
3. For partners, if the contractual nature changes (for example prospect -> reseller), update the `partnership_type` field (not `type`, which stays `partner-context` for BM indexing)
4. If frontmatter fields changed, rerun `python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply`

## Forbidden rules

- Do not mention AI assistance in entity-facing content (see `.claude/rules/communication.md`)
- Do not use `client:` in partner frontmatter, use `partner:` (see the `partner-context` schema)
