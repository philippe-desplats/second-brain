---
name: step-01-classify
description: Detect content type, entity, project, date, and type-specific metadata
prev_step: steps/step-00-init.md
next_step: steps/step-02-file.md
---

# Step 1: Classify

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER guess an entity when signals conflict; ask
- 🛑 NEVER write anything to disk in this step
- ✅ ALWAYS show the classification card before proceeding
- 📋 YOU ARE A CLASSIFIER, not a writer
- 💬 FOCUS on: what is it, who is it about, when did it happen

## EXECUTION SEQUENCE:

### 1. Detect the content type

If `{type_override}` is set, use it. Otherwise load `references/type-signals.md` and match `{raw_content}` against the signal matrix. Every capture resolves to exactly one canonical schema type (typical inbound: `email`, `transcript`, `meeting`, `note`, `research`, `brainstorm`).

Confidence rule: one dominant signal set → proceed; two plausible types → ask with AskUserQuestion (two options plus Other).

### 2. Resolve the entity and zone

If `{entity_override}` is set, verify `sources/*/{entity_override}/` exists and use it. Otherwise:

1. List candidate entities: `ls -d sources/*/*/` (entity zones present on disk, e.g. clients and partners when kept; internal and personal are project-based, not entity-based).
2. Match signals from the content against each entity's `CLAUDE.md`: entity name, contact names, email domains, project vocabulary.
3. Decide the zone:
   - Matched entity → its zone (`clients`, or `partners` when that zone exists)
   - Owner-internal content (strategy, infra, own business) → `internal`
   - Private, non-business content → `personal`
4. One confident match → propose it. Several or none → AskUserQuestion listing the top candidates plus "internal", "personal", and "new entity".
5. **New entity path**: if the content concerns an entity with no folder, offer to create `sources/{zone}/{slug}/` and its `CLAUDE.md` from `templates/entity-CLAUDE-template.md` (minimal interview: tone, addressing, language). This happens in step-02 as part of the write plan, not here.

### 3. Resolve the project

```bash
ls -d sources/{zone}/{entity}/*/ 2>/dev/null
```

- Exactly one project → propose it.
- Several → match content signals against project names; ask if unclear.
- None (or the content clearly starts something new) → propose a new project slug (kebab-case, in the owner's working language).

### 4. Extract date and type-specific metadata into `{type_meta}`

| Type | Metadata to extract |
|---|---|
| email | `direction` (in/out/reply, from the header orientation relative to the owner), `from`, `to[]`, `cc[]`, `subject`, sent date and time |
| meeting | `participants[]`, meeting date, format (notes vs report) |
| transcript | `participants[]`, recording date, `duration` if visible, `language` |
| research / brainstorm / note | topic keywords for the slug and `topics[]` |

`{item_date}` = the date the artifact happened (email sent date, meeting date), NOT today, unless nothing is detectable; then today with a note.

### 5. Show the classification card

```
┌─ Classification ────────────────────────────────────┐
│ type       {content_type}                           │
│ entity     {entity} ({zone})                        │
│ project    {project} {(new) if applicable}          │
│ date       {item_date}                              │
│ meta       {compact type_meta summary}              │
└─────────────────────────────────────────────────────┘
```

Corrections are cheap here and expensive later: accept free-text adjustments before moving on.

## NEXT STEP:

Load `steps/step-02-file.md`.

<critical>
A wrong classification poisons retrieval forever. When in doubt, ask; never force a fit.
</critical>
