# Template, entity CLAUDE.md

> This template defines the standard structure for entity `CLAUDE.md` files (clients and partners).
> Claude Code loads this file automatically when working in an entity folder.
> Copy it to `sources/clients/{client}/CLAUDE.md` or `sources/partners/{partner}/CLAUDE.md` and fill in each section.
> The canonical schema is `basic-memory/schemas/client-context.md` for a client and `basic-memory/schemas/partner-context.md` for a partner (both strict validation).

## Expected frontmatter

```yaml
---
title: {Entity name}, Context
client: {Entity name}          # for a partner, use `partner:` instead
type: client-context           # for a partner, use `partner-context`
schema_version: 1
status: active
last_updated: YYYY-MM-DD
legal_form: company | sole-proprietor | individual | nonprofit | other
company_id: {registration_number}
vat_id: {vat_number}
industry: {sector}
day_rate: {amount}
tone: professional | friendly | technical | direct | formal | commercial | pedagogical
addressing: formal | informal | variable
primary_channel: email | chat | call | in-person
email_format: plain | markdown | html | standard-professional
language: en | fr | other
constraints:
  - {specific constraint, e.g. do not mention AI}
---
```

> Enum token values (`legal_form`, `tone`, `addressing`, `email_format`, `language`, ...) are schema-controlled identifiers defined in the schema. Keep them as-is, do not translate them.

## Claude Code instruction block (required, right after the title)

```markdown
> **Claude Code**, this file is loaded automatically. Adapt your tone, style, and deliverables to the communication preferences below.
```

## "Communication preferences" section (required, first section)

Replicate the frontmatter values in readable prose.

## Following sections (adapt per entity)

- **Identity**, name, sector, website, legal form, registration number, address
- **Key contacts**, name / role / contact table
- **Relationship**, since when, services provided, day rate
- **Active projects**, project / status / folder table
- **Technical stack** if relevant
- **Notable history**, timeline of key events

## "Observations" section (recommended for strict)

BM strict validation expects `- [field] value` observations that mirror the frontmatter fields. The script `basic-memory/scripts/add_observations_from_frontmatter.py --apply` adds them automatically.

## "Relations" section (recommended)

```markdown
## Relations

- managed_by [[Partner]] (if applicable)
- owned_by [[Partner]] (if applicable)
- referred_by [[Partner]] (if applicable)
- co_delivered_with [[Partner]] (if applicable)
```

## Rules

1. Never delete a section, leave it empty or "N/A" if not applicable
2. Always update `last_updated` when the file is modified
3. Keep external tool references up to date
4. Content is in English (technical terms and schema enum tokens excepted)
5. After editing, rerun `python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply` if frontmatter fields changed
