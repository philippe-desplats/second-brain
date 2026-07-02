---
title: Partner Context
type: schema
entity: partner-context
schema_version: 1
schema:
  partner: string, "partner's full name or legal entity name"
  status(enum):
  - active
  - inactive
  - prospect
  - ex-partner-now-competitor
  partnership_type(enum):
  - commercial
  - technical
  - strategic
  - white-label
  - mixed
  last_updated: string, "date of last update in YYYY-MM-DD format"
  active_tracks(array): string, "concrete collaboration areas"
  business_referral?: string, "who brings what to whom"
  contract?(enum):
  - affiliation
  - reseller
  - white-label
  - co-ownership
  - informal
  client_facets?(array): string, "areas where the partner is a client of ours"
  vendor_facets?(array): string, "areas where we are a client of the partner"
  legal_form?: string, "legal form, free text, e.g. LLC, sole proprietorship, nonprofit"
  company_id?: string, "company registration number"
  vat_id?: string, "VAT or tax identification number"
  tone?(enum):
  - professional
  - friendly
  - technical
  - direct
  - informal
  - formal
  addressing?(enum):
  - informal
  - formal
  - variable
  primary_channel?(enum):
  - email
  - slack
  - teams
  - whatsapp
  - video
  - direct
  language?(enum):
  - fr
  - en
  - other
  constraints?(array): string, "specific constraints"
  manages?(array): ClientContext, "clients operationally managed by the partner"
  owns?(array): ClientContext, "clients owned by the partner"
  brings_lead?(array): ClientContext, "leads brought by the partner"
  co_delivered_with?(array): ClientContext, "clients we co-deliver to"
  affiliated_with?(array): PartnerContext, "other affiliated partners"
settings:
  validation: strict
---

# Schema, Partner Context

The `CLAUDE.md` file at the root of a partner folder. Canonical source of the rules, `.claude/rules/entities.md`. The 4 structuring elements (`partnership_type`, `active_tracks`, `contract`, `business_referral`) are captured in the frontmatter; `partnership_type` and `active_tracks` are strictly required, while `contract` and `business_referral` are optional to allow progressive declaration.

This schema enforces `partner:` as the identity field (not `client:`).

## Location

- `sources/partners/{partner}/CLAUDE.md`

## Required markdown sections

- **Agent instruction block** at the top of the document
  > This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.
- `## Communication preferences`
- `## Partnership nature`, summarizes `partnership_type`, `active_tracks`, `contract`, `business_referral` in prose

## Recommended markdown sections

- `## Profile` or `## Identity`
- `## Key contacts`
- `## Ongoing projects`
- `## Validated framework` or `## Points of vigilance` if complex

## Mixed partner, client facet

Some partners are also our clients on certain areas (e.g. a partner on automation who is also a client on infrastructure). The `client_facets` and `vendor_facets` fields capture this duality without a separate `client-context` file.

## Expected observations

- `[active-track]` detail of a collaboration area
- `[business-referral]` detail of a business flow
- `[contact]` key person
- `[preference]` additional preference
- `[risk]` risk (misalignment, dependency, indirect competition)

## Typed relations in the frontmatter

- `manages`, client managed by this partner
- `owns`, client owned by this partner
- `brings_lead`, lead brought
- `co_delivered_with`, co-delivered client, symmetric to `client-context.co_delivered_with`
- `affiliated_with`, other affiliated partner

## Additional relations in markdown

- `resells [[Service]]`, service resold
- `competes_with [[Other entity]]`, direct competitor

## Required symmetric pairs

Any relation declared on one side must be declared as a mirror:

| Client side | Partner side |
|---|---|
| `managed_by` | `manages` |
| `owned_by` | `owns` |
| `referred_by` | `brings_lead` |
| `co_delivered_with` | `co_delivered_with` |

Full detail in [README.md](README.md), mandatory symmetric pairs section.

## Example

```yaml
---
partner: Alex Martin
type: partner-context
status: active
partnership_type: white-label
last_updated: 2026-04-08
active_tracks:
  - White label, we deliver technically for Alex's marketing clients
  - Prospect sourcing, Alex brings qualified leads
business_referral: Prospects brought by Alex, billing via us with a rebate to be defined
contract: "white-label"
legal_form: "sole proprietorship"
company_id: "REG-4829105"
tone: friendly
addressing: informal
primary_channel: email
language: en
manages:
  - Bloom (Alex Martin)
owns:
  - Bloom (Alex Martin)
brings_lead:
  - Taylor Brooks
  - Jordan Kim
---

# Alex Martin, Partner Context

> This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.

## Communication preferences
Friendly and direct tone, informal address, email and video channel.

## Partnership nature
White label type. Alex brings marketing leads, we deliver technically under their brand. Active tracks on white label and prospect sourcing.
```
