# Template, entity CLAUDE.md

> This template defines the standard structure for entity `CLAUDE.md` files (clients and partners).
> Claude Code loads this file automatically when working in an entity folder.
> Copy it to `sources/clients/{client}/CLAUDE.md` or `sources/partners/{partner}/CLAUDE.md` and fill in each section.
> The canonical schema is `basic-memory/schemas/client-context.md` for a client and `basic-memory/schemas/partner-context.md` for a partner (both strict validation).

## Expected frontmatter, client

Required by the schema, `client`, `status`, `last_updated`. Every other field is optional.

```yaml
---
title: {Entity name}
client: {Entity name}
type: client-context
schema_version: 1
status: active | inactive | prospect
last_updated: YYYY-MM-DD
legal_form: {free text, e.g. LLC, sole proprietorship, nonprofit}
company_id: {registration_number}
vat_id: {vat_number}
industry: {sector}
day_rate: {amount, plain number}
tone: professional | friendly | technical | direct | formal | commercial | educational
addressing: formal | informal | variable
primary_channel: email | slack | teams | whatsapp | video | direct
email_format: plain | markdown | html | standard-professional
language: en | fr | other
constraints:
  - {specific constraint, e.g. do not mention AI}
---
```

The four typed relations (`managed_by`, `owned_by`, `referred_by`, `co_delivered_with`) are frontmatter fields too when they apply, see the Relations section below.

## Expected frontmatter, partner

A partner follows its own schema, not a client variant. Required by that schema, `partner`, `status`, `partnership_type`, `last_updated`, `active_tracks`. The fields below replace or add to the client block, the rest carries over unchanged.

```yaml
partner: {Entity name}
type: partner-context
status: active | inactive | prospect | ex-partner-now-competitor
partnership_type: commercial | technical | strategic | white-label | mixed
active_tracks:
  - {collaboration area}
business_referral: {who brings what to whom}
contract: affiliation | reseller | white-label | co-ownership | informal
client_facets:
  - {area where the partner is a client of ours}
vendor_facets:
  - {area where we are a client of the partner}
tone: professional | friendly | technical | direct | informal | formal
```

The partner schema declares no `industry`, no `day_rate` and no `email_format`; its typed relations are `manages`, `owns`, `brings_lead`, `co_delivered_with` and `affiliated_with`.

> Enum token values (`status`, `partnership_type`, `contract`, `tone`, `addressing`, `primary_channel`, `email_format`, `language`) are schema-controlled identifiers defined in the schema. Copy them verbatim, do not translate them, and note that `tone` does not offer the same set on both sides. `legal_form` is free text, `day_rate` a plain number.

## Claude Code instruction block (required, right after the title)

```markdown
> **Claude Code**, this file is loaded automatically. Adapt your tone, style, and deliverables to the communication preferences below.
```

## "Communication preferences" section (required, first section)

Replicate the frontmatter values in readable prose.

## Following sections

Required for a client, `## Identity` or `## Company`, `## Key contacts`, `## Working relationship`. Required for a partner, `## Partnership nature`. The others adapt per entity.

- **Identity** or **Company**, name, sector, website, legal form, registration number, address
- **Key contacts**, name / role / contact table
- **Working relationship**, since when, services provided, day rate
- **Partnership nature** (partner only), partnership type, active tracks, contract, business referral in prose
- **Active projects**, project / status / folder table
- **Technical stack** if relevant
- **Notable history**, timeline of key events

## "Observations" section (recommended for strict)

BM validation reads `- [field] value` observations that mirror the frontmatter fields; each one stays optional, even on a strict schema. The script `basic-memory/scripts/add_observations_from_frontmatter.py --apply` adds them automatically.

## "Relations" section (recommended)

Client side:

```markdown
## Relations

- managed_by [[Partner]] (if applicable)
- owned_by [[Partner]] (if applicable)
- referred_by [[Partner]] (if applicable)
- co_delivered_with [[Partner]] (if applicable)
```

Partner side, the mandatory mirror:

```markdown
## Relations

- manages [[Client]] (if applicable)
- owns [[Client]] (if applicable)
- brings_lead [[Client]] (if applicable)
- co_delivered_with [[Client]] (if applicable)
- affiliated_with [[Partner]] (if applicable)
```

## Rules

1. Never delete a section, leave it empty or "N/A" if not applicable
2. Always update `last_updated` when the file is modified
3. Keep external tool references up to date
4. Content is in English (technical terms and schema enum tokens excepted)
5. After editing, rerun `python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply` if frontmatter fields changed
