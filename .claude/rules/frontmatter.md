# Frontmatter, Basic Memory manifesto

This file is the **single entry point** for everything related to the YAML frontmatter of the workspace's markdown files. It points to the 15 Picoschema schemas that are the **canonical source** of truth for each note type.

## Fundamental rule

**Every new markdown file must have YAML frontmatter conforming to one of the 15 schemas in `basic-memory/schemas/`.**

## The 15 canonical types

### Context schemas (2, strict validation)

| Type | Schema | Location | Key observations |
|---|---|---|---|
| client-context | [client-context.md](../../basic-memory/schemas/client-context.md) | `sources/clients/{X}/CLAUDE.md` | `[preference]`, `[contact]`, `[contract]`, `[milestone]`, `[risk]`, `[stack]` |
| partner-context | [partner-context.md](../../basic-memory/schemas/partner-context.md) | `sources/partners/{X}/CLAUDE.md` | `[active-track]`, `[business-referral]`, `[contact]`, `[preference]`, `[risk]` |

### Project schema (1, strict validation)

| Type | Schema | Location |
|---|---|---|
| project-brief | [project-brief.md](../../basic-memory/schemas/project-brief.md) | `{project}/README.md` or `CLAUDE.md` |

### Cross-cutting schemas (3, strict validation)

| Type | Schema | Location |
|---|---|---|
| person | [person.md](../../basic-memory/schemas/person.md) | `atlas/people/{slug}.md` |
| topic | [topic.md](../../basic-memory/schemas/topic.md) | `atlas/topics/{slug}.md` |
| service | [service.md](../../basic-memory/schemas/service.md) | `atlas/services/{slug}.md` |

### Operational schemas (9, warn validation)

| Type | Schema | Location | Key observations |
|---|---|---|---|
| meeting | [meeting.md](../../basic-memory/schemas/meeting.md) | `{entity}/{project}/meetings/` | `[decision]`, `[action]`, `[risk]`, `[milestone]`, `[question]` |
| transcript | [transcript.md](../../basic-memory/schemas/transcript.md) | `{entity}/{project}/transcripts/` | Raw meeting or recording transcript |
| email | [email.md](../../basic-memory/schemas/email.md) | `{entity}/{project}/emails/` | `[decision]`, `[action]`, `[commitment]`, `[question]` |
| research | [research.md](../../basic-memory/schemas/research.md) | Project root | `[finding]`, `[source]`, `[question]`, `[hypothesis]`, `[recommendation]` |
| brainstorm | [brainstorm.md](../../basic-memory/schemas/brainstorm.md) | Project root | `[idea]`, `[question]`, `[pro]`, `[con]`, `[decision]` |
| strategy | [strategy.md](../../basic-memory/schemas/strategy.md) | Project root | `[goal]`, `[milestone]`, `[decision]`, `[risk]`, `[kpi]` |
| writing | [writing.md](../../basic-memory/schemas/writing.md) | Project root | `[claim]`, `[proof]`, `[cta]` |
| note | [note.md](../../basic-memory/schemas/note.md) | Project root or `notes/` | free categories |
| deliverable | [deliverable.md](../../basic-memory/schemas/deliverable.md) | `{entity}/{project}/deliverables/` | `[commitment]`, `[clause]`, `[item]`, `[risk]` |

## Decision matrix, which type to choose?

| Guiding question | If yes, choose |
|---|---|
| Is it a client's `CLAUDE.md`? | `client-context` |
| Is it a partner's `CLAUDE.md`? | `partner-context` |
| Is it a project's `README.md` or `CLAUDE.md`? | `project-brief` |
| Is it a real person (contact, decision-maker)? | `person` |
| Is it a recurring subject (technology, concept, domain)? | `topic` |
| Is it a service or offer you provide? | `service` |
| Is it a structured meeting report? | `meeting` |
| Is it a raw transcript (recording, call)? | `transcript` |
| Is it an email sent or received? | `email` |
| Is it sourced research (audit, benchmark, monitoring)? | `research` |
| Is it an ideation session? | `brainstorm` |
| Is it an action plan, roadmap, or strategy? | `strategy` |
| Is it content being drafted? | `writing` |
| Is it a finalized deliverable (signed contract, sent quote, invoice)? | `deliverable` |
| None of the above types fit? | `note` (catch-all) |

## Wikilink convention

### Resolution

`[[Entity]]` wikilinks resolve to a note where one of these fields matches the value:
- `client:` (for `sources/clients/{X}/CLAUDE.md`)
- `partner:` (for `sources/partners/{X}/CLAUDE.md`)
- `name:` (for `person`, `topic`, `service`)
- `title:` (fallback for everything else)

### Collision case

If two entities share the same name (for example a person who is also a partner), disambiguate in parentheses:
- `[[Jane Doe]]` (by default, points to the commercial entity, the partner)
- `[[Jane Doe (person)]]` (points to the person file)
- `[[First Last (Company)]]` for namesake people

### Creating cross wiki-links

Whenever a file mentions a modeled entity (client, partner, person, topic, service), use the `[[...]]` wikilink rather than plain text. This feeds the Obsidian graph and enables Basic Memory navigation.

## Mandatory symmetric pairs

A relation declared on one side must be mirrored on the other side. Golden rule.

| Client side | Partner side | Meaning |
|---|---|---|
| `managed_by` | `manages` | Operational management |
| `owned_by` | `owns` | Commercial ownership |
| `referred_by` | `brings_lead` | Lead sourcing |
| `co_delivered_with` | `co_delivered_with` | Mixed delivery (auto-symmetric) |

Check via `python3 basic-memory/scripts/check_symmetric_relations.py --check`.

## Maintenance scripts

In `basic-memory/scripts/` (11 scripts):

- `check_double_frontmatter.py`, detects files with double frontmatter (Basic Memory bug to work around)
- `fix_double_frontmatter.py`, automatically fixes doubles by merging them
- `retype_files.py`, reclassifies the `type:` based on the path and naming prefix
- `retype_fallback_notes.py`, retypes `note` fallback to a more specific type based on path
- `regen_titles.py`, regenerates the `title:` from the H1 when unusable
- `add_about_relations.py`, injects `about [[Entity]]` into emails/meetings/projects from the path
- `add_observations_from_frontmatter.py`, generates the markdown observations from frontmatter fields
- `auto_link_entities.py`, converts plain-text mentions of modeled entities into `[[wikilinks]]` in note bodies
- `check_symmetric_relations.py`, audits symmetric pairs
- `check_orphans.py`, flags notes with no inbound or outbound relations
- `generate_indexes.py`, regenerates the `*-static.md` indexes in `atlas/maps/`

Double frontmatter was a legacy Basic Memory sync bug; the `disable_permalinks: true` setting applied by `/sb-init` prevents it. No routine run is needed: `/sb-doctor` includes the detection check, and `fix_double_frontmatter.py --apply` repairs the rare occurrence.

## Observations and tags, convention

Observations in the markdown body follow the syntax:

```
- [category] free text #optional-tag
```

For the most common categories, see the type table above. You can invent an ad hoc category when a case fits none of them, but keep it concise and reusable.

## References

- `basic-memory/schemas/README.md`, design manifest: the 15 schemas, relation vocabulary, symmetric pairs, design decisions
- `.claude/rules/emails.md`, `.claude/rules/entities.md`, specific process rules
- `.claude/rules/communication.md`, tone and writing rules
- Basic Memory documentation, https://docs.basicmemory.com
