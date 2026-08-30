# Frontmatter, Basic Memory manifesto

This file is the **single entry point** for everything related to the YAML frontmatter of the workspace's markdown files. It points to the 17 Picoschema schemas that are the **canonical source** of truth for each note type.

## Fundamental rule

**Every new markdown file must have YAML frontmatter conforming to one of the 17 schemas in `basic-memory/schemas/`.**

Inside a schema, the frontmatter contract lives in its `settings.frontmatter:` block, while the top-level `schema:` block describes the note body.

## The 17 canonical types

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

### Operational schemas (11, warn validation)

| Type | Schema | Location | Key observations |
|---|---|---|---|
| meeting | [meeting.md](../../basic-memory/schemas/meeting.md) | `{entity}/{project}/meetings/` | `[decision]`, `[action]`, `[risk]`, `[milestone]`, `[question]` |
| transcript | [transcript.md](../../basic-memory/schemas/transcript.md) | `{entity}/{project}/transcripts/` | Raw meeting or recording transcript |
| email | [email.md](../../basic-memory/schemas/email.md) | `{entity}/{project}/emails/` | `[decision]`, `[action]`, `[commitment]`, `[question]` |
| clipping | [clipping.md](../../basic-memory/schemas/clipping.md) | `{entity}/{project}/clippings/` | `[quote]`, `[takeaway]`, `[question]` |
| research | [research.md](../../basic-memory/schemas/research.md) | Project root | `[finding]`, `[source]`, `[question]`, `[hypothesis]`, `[recommendation]` |
| brainstorm | [brainstorm.md](../../basic-memory/schemas/brainstorm.md) | Project root | `[idea]`, `[question]`, `[pro]`, `[con]`, `[decision]` |
| strategy | [strategy.md](../../basic-memory/schemas/strategy.md) | Project root | `[goal]`, `[milestone]`, `[decision]`, `[risk]`, `[kpi]` |
| writing | [writing.md](../../basic-memory/schemas/writing.md) | Project root | `[claim]`, `[proof]`, `[cta]` |
| note | [note.md](../../basic-memory/schemas/note.md) | Project root or `notes/` | free categories |
| session | [session.md](../../basic-memory/schemas/session.md) | `{entity}/{project}/sessions/` | `[done]`, `[next]`, `[blocker]`, `[decision]`, `[open-question]` |
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
| Is it a web page or article captured from outside? | `clipping` |
| Is it sourced research (audit, benchmark, monitoring)? | `research` |
| Is it an ideation session? | `brainstorm` |
| Is it an action plan, roadmap, or strategy? | `strategy` |
| Is it content being drafted? | `writing` |
| Is it the memory of a working session, what got done and what is next? | `session` |
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

## `subtype` and `note_type`, two axes on the same type

`note` is the catch-all, so it carries two classification fields that answer different questions. Both are optional and they do not compete.

- **`subtype`** names the *genre* of a structural note: `moc`, `index`, `pattern`, `playbook`, `guide`, `runbook`, `decision`. It is what `atlas/` and `knowledge/` sort on, and what the Bases views filter on.
- **`note_type`** names the *shape* of an ordinary note: `summary`, `context`, `cheatsheet`, `reading`, `journal`, `history`, `checkpoint`, `reminder`, `todo`, `other`.

A note in `knowledge/` uses `subtype`. A daily journal entry uses `note_type`. Most notes use neither. Never set `subtype: note`, which says nothing; if no genre fits, leave the field out.

## One property name, one meaning, vault-wide

Obsidian assigns **a single type per property name across the entire vault**, not per note and not per schema. Two schemas using the same name for different things do not produce two local behaviours, they produce one global collision, and the Properties panel merges their suggested values into a single list.

This constrains every schema change:

- **Never reuse an existing name for a different meaning.** `author` already means "author of the captured source" in `clipping`; a field meaning "who wrote this note" must not be called `author`.
- **Check the name against every schema before adding it**, not only against the one you are editing.
- Known deliberate overlaps that predate this rule and are documented rather than fixed: `client` and `partner` are a required identity in the context schemas and an optional relation in eleven others; `about` targets a `Topic` in some schemas and a `ProjectBrief` in others; `implements` targets `Research` in `strategy` and `Strategy` in `deliverable`; `status` carries fourteen incompatible enums across fifteen schemas.

## Provenance of the writing hand

`written_by` records who actually wrote a note, with two values, `owner` and `agent`. It is optional everywhere and **absent means `owner`**, so no existing note becomes invalid.

It is declared on exactly two types, `session` and `note`. `note` is the catch-all, so it also covers everything under `knowledge/`.

It is deliberately **not** on `clipping`, `email`, `transcript` or `meeting`. On those, the type itself already tells you the text is not the owner's own writing, and a field that restates the type is the metadata over-engineering this workspace avoids. The field earns its place only where machine-written prose could be mistaken for the owner's thinking.

The point is not bookkeeping, it is the question you can ask six months later: *what in my distilled knowledge did I not write myself?* A second brain whose owner can no longer tell their own thinking from generated text has lost the thing that made it worth keeping.

Three rules follow from it:

1. **Mark it.** A note drafted or rewritten by an agent carries `written_by: agent`. Approving a draft does not change that value; approval is a review, not authorship.
2. **Quarantine it.** `inbox/` is where generated material lands. A note carrying `written_by: agent` is never promoted straight into `knowledge/`; it goes through `/distill`, whose human gate is the review.
3. **Split the labour.** The agent files, tags, repairs links, and formats. Every judgement call stays with the owner.

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

In `basic-memory/scripts/` (12 scripts):

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
- `curation_reminder.py`, drops a reminder note in `inbox/` and fires a best effort OS notification; scheduled via launchd, cron, or Task Scheduler, idempotent at one reminder per day, and never runs the assistant itself

Double frontmatter was a legacy Basic Memory sync bug; the `disable_permalinks: true` setting applied by `/sb-init` prevents it. No routine run is needed: `/sb-doctor` includes the detection check, and `fix_double_frontmatter.py --apply` repairs the rare occurrence.

## Observations and tags, convention

Observations in the markdown body follow the syntax:

```
- [category] free text #optional-tag
```

For the most common categories, see the type table above. The categories expected for a given type are declared in that type's `schema:` block in `basic-memory/schemas/`, which is the block validated against the note body. You can invent an ad hoc category when a case fits none of them, but keep it concise and reusable.

## References

- `basic-memory/schemas/README.md`, design manifest: the 17 schemas, relation vocabulary, symmetric pairs, design decisions
- `.claude/rules/emails.md`, `.claude/rules/entities.md`, specific process rules
- `.claude/rules/communication.md`, tone and writing rules
- Basic Memory documentation, https://docs.basicmemory.com
