---
title: Basic Memory Picoschema schema index
type: note
schema_version: 1
subtype: index
date: 2026-08-15
status: active
---

# Picoschema Schemas, Basic Memory

This folder contains the **canonical Picoschema schemas** that describe the note types of the workspace. Each schema formalizes a pattern the second brain relies on, so the AI agent and the maintenance scripts share one vocabulary.

**There are 15 schemas today.** This sentence is the only place that number is written down, so it is the one line to update when a schema is added or removed.

This README doubles as the design manifest: the type catalog, the strict/warn philosophy, the design decisions, the relation vocabulary, and the mandatory symmetric pairs.

## Principle, mixed warn and strict

- **`validation: strict`** (stable context and entity types), client-context, partner-context, person, service, topic, project-brief. These types have settled shapes, so records must validate.
- **`validation: warn`** (operational types), meeting, transcript, email, research, brainstorm, strategy, writing, note, deliverable. Warnings are reported without blocking.

Moving additional operational types to strict is optional and conditioned on the stabilization of your writing practices. This follows the "structure grows with you" philosophy: let patterns emerge and flag inconsistencies without blocking, then tighten to strict once a type has settled.

## Principle, two contracts per schema

Every schema declares two contracts, one per block, and each is read for a different purpose.

- **`settings.frontmatter:`**, the frontmatter contract. Read it to know which YAML fields a note carries, with their required and optional markers.
- **`schema:`**, the body contract. Read it to know which observations (`- [category] value`) and which `## Relations` entries the body should carry.

Entity-typed fields such as `about` appear in both, written in the frontmatter and mirrored in the body relations. See D10 for the mechanics and for the mapping between Picoschema syntax and body syntax.

## The canonical schemas

### Operational schemas (usable in every workspace zone)

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

### Context schemas (zone-specific)

| Schema | Role |
|---|---|
| [client-context.md](client-context.md) | Client `CLAUDE.md`, communication preferences and relations |
| [partner-context.md](partner-context.md) | Partner `CLAUDE.md`, partnership nature and relations |

### Project schema (usable in every workspace zone)

| Schema | Role |
|---|---|
| [project-brief.md](project-brief.md) | Project `README.md` or `CLAUDE.md` |

### Cross-cutting entity schemas

| Schema | Role |
|---|---|
| [person.md](person.md) | Individual person, contact, interlocutor |
| [topic.md](topic.md) | Recurring subject (technology, concept, domain) |
| [service.md](service.md) | An offer or service from your organization |

## Coverage of the workspace zones

The operational schemas and `project-brief` apply to every zone under `sources/`, whichever set the workspace keeps after setup. Zones that hold third parties carry one folder per entity, `sources/{zone}/{entity}/{project}/`; entity-less zones such as `internal` and `personal` hold their projects directly, `sources/{zone}/{project}/`.

The `client-context` and `partner-context` schemas are specific to their own zone. The cross-cutting schemas (`person`, `topic`, `service`) live at the workspace root in `atlas/people/`, `atlas/topics/`, `atlas/services/` respectively.

## Design decisions

### D1, split `context` into 2 schemas

Content requirements diverge structurally between clients (`Communication preferences`) and partners (structuring elements, `partnership_type`, `active_tracks`, `contract`, `business_referral`). Two distinct schemas rather than one polymorphic type.

### D2, `writing` kept with an extended enum

An ambiguous type historically, disciplined by an extended `writing_type(enum)` (quote, contract, newsletter, post, outline, proposal, article, pitch-deck, email-signature, bio, landing-copy, video-script, specification, terms-of-sale, legal-notice, privacy-policy, journal, letter, other).

### D3, `basic-memory/` location

The `basic-memory/` folder at the workspace root groups everything operational for Basic Memory. It is a visible folder (not a dotfolder) because Basic Memory ignores dotfolders during indexing.

Internal structure:

- `schemas/`, the canonical Picoschema schemas plus this index
- `scripts/`, the Python maintenance scripts (frontmatter fixes, symmetric relation checks, index generation, retyping, etc.)

### D4, validation warn by default

Philosophy "structure grows with you", let patterns emerge and flag inconsistencies without blocking. The stable context and entity types (client-context, partner-context, person, service, topic, project-brief) run strict, the operational types stay in warn.

### D5, numeric fields for amounts

`deliverable.amount_pre_tax` and `amount_with_tax` are typed as `number`, not strings. This allows automatic summing, revenue analytics, and filtering by threshold. Keep `amount_label` (string) for non-standard cases (subscriptions, pay-as-you-go) where a single number does not make sense.

### D6, typed relations in the Picoschema block

Critical relations (`managed_by`, `owns`, `client`, `partner`, etc.) are declared in the `schema:` block with Entity typing, not only in markdown prose. This enables validation and inference.

### D7, entity schemas that cover blind spots

These schemas exist to fill gaps that would otherwise leave the graph incomplete:

- `person` (physical people existed only as orphan wikilinks)
- `topic` (recurring subjects, avoids empty nodes in the graph)
- `service` (organization offers, needed to model `resells [[Service]]`)
- `transcript` (raw transcripts, distinct from structured reports)

### D8, wikilink convention

Wikilinks use the identity field value (`client`, `partner`, `name`) as is. For people with an identical name, use `[[First Last (Company)]]`.

### D9, `version` on a schema, `schema_version` on a note

Two levels, two keys. A schema in this folder carries `version: 1`, the key Basic Memory reads for its own version tracking. A regular note carries `schema_version: 1`, declaring which version of its schema it conforms to. Bumping a schema's `version` is then the signal to migrate the notes still declaring the previous `schema_version`.

### D10, how these schemas meet Basic Memory's native schema tooling

Verified against Basic Memory 0.21.1 and re-checked unchanged on 0.22.1. The details below belong to the package, not to this repository, so re-read the source before relying on them, a later release can move them.

- **Resolution is database driven, not path driven.** Basic Memory selects indexed notes whose type is `schema`, then matches their `entity:` value against a note's `type:` value, both normalized to permalink form. It never walks a `schema/` directory, so these files are found wherever they sit once the workspace is indexed, and the `basic-memory/schemas/` name is a free choice (see D3).
- **The parser reads five frontmatter keys**, `entity` (required), `schema` (required, a mapping), `version` (defaults to 1), `settings.validation` (defaults to `warn`), and `settings.frontmatter` (optional). Every other key is ignored, which is what makes the D9 rename load bearing and what makes extra keys such as `title` harmless.
- **`strict` is the only validation value with special behaviour**, it promotes findings to errors. Every other value, `warn` included, behaves as a warning. The strict and warn split described at the top of this file is therefore compatible as written.
- **The top-level `schema:` block is validated against the note body**, meaning observations written `- [field] value` and relations written `- field [[Target]]`. Frontmatter is validated only through a separate `settings.frontmatter:` block.

Decision taken, each schema carries the two blocks: `schema:` declares the observation categories and the `## Relations` entries of the body, `settings.frontmatter:` declares the frontmatter fields with their required and optional markers. Entity-typed fields such as `about` sit in both, written in the frontmatter (D6) and mirrored in the body relations. To add a field, pick the block first, then write it with the syntax it maps to:

```
field: string             -> observation `- [field] value`
field?(array): string     -> several `[field]` observations
field?: EntityType        -> relation `- field [[Target]]`
field?(array): EntityType -> several `field` relations
field?(enum): [values]    -> observation whose value is in the set
```

Every entry in a `schema:` block stays optional, hence the `?` on all of them. An observation is a judgement call about what a note happens to contain, never a hard requirement, and marking one required would turn every note already on disk into a validation failure. That matters most on the strict schemas, where a finding is an error rather than a warning. Evidence sits in `basic_memory/schema/parser.py` and `basic_memory/schema/validator.py`.

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
