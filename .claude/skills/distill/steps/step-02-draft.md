---
name: step-02-draft
description: Pre-fill the knowledge template with Basic Memory frontmatter + distilled body
prev_step: steps/step-01-scan.md
next_step: steps/step-03-publish.md
---

# Step 2, Draft Knowledge Note

## MANDATORY EXECUTION RULES:

- 🛑 NEVER include confidential client data (registration numbers, internal emails, etc.), anonymize
- ✅ ALWAYS cite every source via `distilled_from [[Source]]` in Relations
- ✅ ALWAYS respect the strict Basic Memory frontmatter (type: note + subtype:)
- 📋 YOU ARE a distiller, you produce markdown, you do not save

## EXECUTION SEQUENCE:

### 1. Resolve the target path

```
{draft_path} = knowledge/{target}/{short-kind}-{slug}.md
```

Where `{short-kind}` is derived from `{kind}`:
- `pattern` -> `pattern`
- `playbook` -> `playbook`
- `guide` -> `guide`
- `runbook` -> `runbook`
- `decision` -> `decision`

And `{slug}` is the `{topic}` in kebab-case.

**If the file already exists**:
- Read the existing one
- Present to the user via AskUserQuestion: update / overwrite / abandon
- If update: continue in merge mode (add the new sources, enrich)
- If overwrite: warn, ask for explicit confirmation

### 2. Load the template

Read `.claude/skills/distill/references/knowledge-template.md` (template per `{kind}`).

If there is no specific reference, use the generic template defined below:

```markdown
---
title: {Human-readable title}
type: note
schema_version: 1
subtype: {kind}
status: active
date: {YYYY-MM-DD}
topics: [{topic}, {related_topic_1}, {related_topic_2}]
---

# {Human-readable title}

_Distilled from {N} real occurrences in the workspace ({start date} -> {end date})._

## Context

{1-2 paragraphs: the when/where/why this pattern emerges}

## The pattern (or playbook/guide depending on kind)

{The main body, structured by steps or sections depending on kind}

## Sourced examples

- **[[{Source 1 title}]]** ({client/partner}, {date}), {1 sentence on what this source contributes}
- **[[{Source 2 title}]]** ({client/partner}, {date}), {1 sentence}
- **[[{Source 3 title}]]** ({client/partner}, {date}), {1 sentence}

## Anti-patterns / known pitfalls

{If relevant, what to avoid, based on the sources}

## Variants

{If relevant, contextual variants, e.g. by client size}

## External sources

{URLs, references, books if applicable}

## Relations

- about [[{Main topic}]]
{For each source in {sources_found}}:
- distilled_from [[{Source N title}]]
- contains [[{sub-pattern 1}]]
- contains [[{sub-pattern 2}]]
```

### 3. Fill the template

From `{sources_found}`:

1. **Title**: `{Capitalized kind}, {Capitalized topic}` (e.g. `Playbook, Accessibility Audit`)
2. **topics**: `{topic}` + topics detected in the sources (intersection or union depending on density)
3. **Context**: synthesis of the contexts seen in the sources, 1-2 paragraphs
4. **The pattern**: structure by `{kind}`:
   - `pattern`, code example + explanation + use cases
   - `playbook`, numbered steps (e.g. preparation, execution, validation, delivery)
   - `guide`, long thematic sections
   - `runbook`, intervention steps + decision criteria + escalation
   - `decision`, ADR-style: Context / Options / Decision / Consequences
5. **Sourced examples**: for each source in `{sources_found}`, extract the concrete element that illustrates this pattern
6. **Anti-patterns**: deduce from the errors or problematic variations seen in the sources
7. **Variants**: if several implementations legitimately diverge, document them
8. **Relations**: `distilled_from [[X]]` for EVERY source

### 4. Anonymization

Before validation:

- Replace client emails with `client@example.com`
- Remove registration numbers, bank details, phone numbers
- Remove confidential details (exact amounts, internal client team names if not public)
- Keep client/partner names if already public (LinkedIn page, website)

### 5. Self-review

Before presenting to the user, verify:

```
[ ] Complete frontmatter (title, type, subtype, status, date, topics)
[ ] At least {min_occurrences} sources cited in "Sourced examples"
[ ] Each source has a valid wiki-link [[...]]
[ ] Relations contains distilled_from for EVERY source
[ ] No registration number, bank details, or client phone number
[ ] Anti-patterns present if applicable
[ ] Naming convention: knowledge/{target}/{short-kind}-{slug}.md
```

If a check fails, fix it before step-03.

Store the generated content in `{draft_content}` and the path in `{draft_path}`.

---

## SUCCESS METRICS:

✅ `{draft_content}` complete and passed self-review
✅ Strict Basic Memory frontmatter
✅ All sources cited with wiki-links
✅ Anonymization done

## FAILURE MODES:

❌ Saving without validation (forbidden, that is step-03)
❌ Incomplete frontmatter or enum outside values
❌ Client confidentiality violated

---

## NEXT STEP:

Load `./step-03-publish.md`
