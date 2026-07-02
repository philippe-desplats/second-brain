---
title: Basic Memory Picoschema schema index
type: index
---

# Picoschema Schemas, Basic Memory

This folder contains the **15 Picoschema schemas** that describe the canonical note types of the workspace. Each schema formalizes a pattern the second brain relies on, so the AI agent and the maintenance scripts share one vocabulary.

This README doubles as the design manifest: the type catalog, the strict/warn philosophy, the design decisions, the relation vocabulary, and the mandatory symmetric pairs.

## Principle, mixed warn and strict

- **6 schemas in `validation: strict`** (stable context and entity types), client-context, partner-context, person, service, topic, project-brief. These types have settled shapes, so records must validate.
- **9 schemas in `validation: warn`** (operational types), meeting, transcript, email, research, brainstorm, strategy, writing, note, deliverable. Warnings are reported without blocking.

Moving additional operational types to strict is optional and conditioned on the stabilization of your writing practices. This follows the "structure grows with you" philosophy: let patterns emerge and flag inconsistencies without blocking, then tighten to strict once a type has settled.

## The 15 schemas

### 9 operational schemas (covering the 4 categories, internal/client/partner/personal)

| Schema | Role |
|---|---|
| [meeting.md](meeting.md) | Meeting, workshop or call report |
| [transcript.md](transcript.md) | Raw transcript from a recording |
| [email.md](email.md) | Incoming, outgoing or reply email |
| [research.md](research.md) | Research document, audit, benchmark, monitoring |
| [brainstorm.md](brainstorm.md) | Ideation session, solo or collective |
| [strategy.md](strategy.md) | Action plan, roadmap, architecture |
| [writing.md](writing.md) | Written content (quote, contract, newsletter, post, bio, etc.) |
| [note.md](note.md) | Short capture, summary, memo |
| [deliverable.md](deliverable.md) | Finalized deliverable, commercial or internal |

### 2 context schemas (category-specific)

| Schema | Role |
|---|---|
| [client-context.md](client-context.md) | Client `CLAUDE.md`, communication preferences and relations |
| [partner-context.md](partner-context.md) | Partner `CLAUDE.md`, partnership nature and relations |

### 1 project schema (covering the 4 categories)

| Schema | Role |
|---|---|
| [project-brief.md](project-brief.md) | Project `README.md` or `CLAUDE.md` |

### 3 cross-cutting entity schemas

| Schema | Role |
|---|---|
| [person.md](person.md) | Individual person, contact, interlocutor |
| [topic.md](topic.md) | Recurring subject (technology, concept, domain) |
| [service.md](service.md) | An offer or service from your organization |

## Coverage of the 4 workspace categories

The operational schemas and `project-brief` apply to the 4 roots:

- `sources/clients/` (commercial relationships)
- `sources/partners/` (bilateral relationships)
- `sources/internal/` (internal projects)
- `sources/personal/` (personal projects)

The `client-context` and `partner-context` schemas are specific to their category. The 3 cross-cutting schemas (`person`, `topic`, `service`) live at the workspace root in `atlas/people/`, `atlas/topics/`, `atlas/services/` respectively.

## Design decisions

### D1, split `context` into 2 schemas

Content requirements diverge structurally between clients (`Communication preferences`) and partners (structuring elements, `partnership_type`, `active_tracks`, `contract`, `business_referral`). Two distinct schemas rather than one polymorphic type.

### D2, `writing` kept with an extended enum

An ambiguous type historically, disciplined by an extended `writing_type(enum)` (quote, contract, newsletter, post, outline, proposal, article, pitch-deck, email-signature, bio, landing-copy, video-script, specification, terms-of-sale, legal-notice, privacy-policy, journal, letter, other).

### D3, `basic-memory/` location

The `basic-memory/` folder at the workspace root groups everything operational for Basic Memory. It is a visible folder (not a dotfolder) because Basic Memory ignores dotfolders during indexing.

Internal structure:

- `schemas/`, the 15 canonical Picoschema schemas plus this index
- `scripts/`, the Python maintenance scripts (frontmatter fixes, symmetric relation checks, index generation, retyping, etc.)

### D4, validation warn by default

Philosophy "structure grows with you", let patterns emerge and flag inconsistencies without blocking. The 6 stable context and entity types (client-context, partner-context, person, service, topic, project-brief) run strict, the 9 operational types stay in warn.

### D5, numeric fields for amounts

`deliverable.amount_pre_tax` and `amount_with_tax` are typed as `number`, not strings. This allows automatic summing, revenue analytics, and filtering by threshold. Keep `amount_label` (string) for non-standard cases (subscriptions, pay-as-you-go) where a single number does not make sense.

### D6, typed relations in the Picoschema block

Critical relations (`managed_by`, `owns`, `client`, `partner`, etc.) are declared in the `schema:` block with Entity typing, not only in markdown prose. This enables validation and inference.

### D7, entity schemas that cover blind spots

Four schemas exist to fill gaps that would otherwise leave the graph incomplete:

- `person` (physical people existed only as orphan wikilinks)
- `topic` (recurring subjects, avoids empty nodes in the graph)
- `service` (organization offers, needed to model `resells [[Service]]`)
- `transcript` (raw transcripts, distinct from structured reports)

### D8, wikilink convention

Wikilinks use the identity field value (`client`, `partner`, `name`) as is. For people with an identical name, use `[[First Last (Company)]]`.

### D9, schema_version on every schema

Each schema includes `schema_version: 1` in its frontmatter. This enables controlled migration when schemas evolve.

## Relation vocabulary

### Common relations

| Relation | Meaning | Usage |
|---|---|---|
| `about [[X]]` | concerns X | Attachment to a subject, topic, project |
| `for [[X]]` | intended for X | Beneficiary of a deliverable or a strategy |
| `with [[X]]` | with X | Joint interaction (meeting) |

### Lineage relations

| Relation | Meaning |
|---|---|
| `based_on [[X]]` | builds on X (writing based on research) |
| `implements [[X]]` | implements X (strategy executes research, deliverable executes strategy) |
| `produces [[X]]` | produces X |
| `feeds [[X]]` | feeds X (brainstorm feeds strategy) |
| `cited_in [[X]]` | cited in X |
| `replies_to [[X]]` | replies to X (email) |
| `follows [[X]]` | follows X (meeting in a series) |
| `succeeds [[X]]` | succeeds X (deliverable in a sequence) |
| `evolved_from [[X]]` | evolution of an entity (prospect to client) |

### Context relations

| Relation | Meaning |
|---|---|
| `parent [[X]]` | hierarchical parent |
| `depends_on [[X]]` | depends on X |
| `to [[X]]`, `from [[X]]` | recipient, sender (email) |

### Person to entity relations

| Relation | Meaning |
|---|---|
| `works_at [[Client]]` | works at |
| `partner_at [[Partner]]` | carries a partnership |
| `contact_for [[Project]]` | primary contact for a project |
| `manages [[Person]]` | supervises a person |
| `reports_to [[Person]]` | is supervised by |

### Service relations

| Relation | Meaning |
|---|---|
| `sold_to [[Client]]` | service sold to a client |
| `resold_by [[Partner]]` | service resold by a partner |
| `replaces [[Old service]]` | replaces an offer |
| `bundles [[Other service]]` | combined offer |

### Client to partner relations (mandatory symmetric pairs)

| Client side | Partner side | Meaning |
|---|---|---|
| `managed_by` | `manages` | Operational management |
| `owned_by` | `owns` | Commercial ownership |
| `referred_by` | `brings_lead` | Lead sourcing |
| `co_delivered_with` | `co_delivered_with` | Mixed delivery, symmetric |

### Advanced business relations

| Relation | Meaning |
|---|---|
| `resells [[Service]]` | resells a service |
| `affiliated_with [[Partner]]` | cross affiliation |
| `competes_with [[Other entity]]` | direct competitor |
| `subcontracts_to [[Person or Partner]]` | subcontracts to |
| `industry_peer_of [[Other client]]` | sector peer |

## Mandatory symmetric pairs

Basic Memory treats relations as opaque strings. A relation declared on only one side creates a silent asymmetry in the graph. Golden rule, always declare the mirror:

- `managed_by` ↔ `manages`
- `owned_by` ↔ `owns`
- `referred_by` ↔ `brings_lead`
- `co_delivered_with` ↔ `co_delivered_with` (self-symmetric, same name)
- `works_at` ↔ `employs` (future, if Person to Client is modeled)

The `check_symmetric_relations.py` script in `../scripts/` verifies these pairs automatically.

## Concrete case, a partner-owned product

Suppose a small brand (`Bloom`) is a product of a white-label partner (`Alex Martin`). It is at once a client (you deliver a website) and a property of the partner. The two context files declare mirror relations:

### `sources/clients/bloom/CLAUDE.md` declares

```yaml
---
client: Bloom (Alex Martin)
status: active
last_updated: 2026-04-08
legal_form: "sole proprietorship"
managed_by: Alex Martin
owned_by: Alex Martin
---
```

### `sources/partners/alex-martin/CLAUDE.md` declares the mirror

```yaml
---
partner: Alex Martin
type: partner-context
status: active
partnership_type: white-label
manages:
  - Bloom (Alex Martin)
owns:
  - Bloom (Alex Martin)
brings_lead:
  - Taylor Brooks
  - Jordan Kim
---
```

### Impact

Basic Memory builds the graph automatically. `bm tool build-context memory://sources/clients/bloom --depth 2` traverses Bloom to Alex Martin to Taylor Brooks in one query. Cross queries become possible: "all clients brought by a partner", "which partner manages which clients".
