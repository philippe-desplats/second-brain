---
title: Client Context
type: schema
entity: client-context
schema_version: 1
schema:
  client: string, "client full name or legal name, entity title for wikilinks"
  status(enum):
  - active
  - inactive
  - prospect
  last_updated: string, "date of last update in YYYY-MM-DD format"
  legal_form?: string, "legal form, free text, e.g. LLC, sole proprietorship, nonprofit"
  company_id?: string, "company registration number"
  vat_id?: string, "VAT or tax identification number"
  industry?: string, "industry sector"
  day_rate?: number, "daily rate applied with this client, excl. tax"
  tone?(enum):
  - professional
  - friendly
  - technical
  - direct
  - formal
  - commercial
  - educational
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
  email_format?(enum):
  - plain
  - markdown
  - html
  - standard-professional
  language?(enum):
  - fr
  - en
  - other
  constraints?(array): string, "specific communication constraints"
  managed_by?(array): PartnerContext, "partners who operationally manage the client"
  owned_by?(array): PartnerContext, "partners who are commercial owners of the client"
  referred_by?(array): PartnerContext, "referring partners"
  co_delivered_with?(array): PartnerContext, "partners with whom we co-deliver"
settings:
  validation: strict
---

# Schema, Client Context

`CLAUDE.md` file at the root of a client folder, loaded automatically as agent context. The 6 communication preference fields (tone, addressing, primary_channel, email_format, language, constraints) are promoted to the frontmatter so they can be queried directly.

## Location

- `sources/clients/{client}/CLAUDE.md`

One and only one per client.

## Communication preference notes

- `addressing` maps to how formally you speak to the contact. Some languages distinguish a familiar and a polite second person (French tu/vous, German du/Sie); `informal` and `formal` cover that split, `variable` means it depends on the person.
- `day_rate` is a plain number so it can be summed and filtered.

## Mandatory markdown sections

- **Agent instruction block** at the top of the document (after the title)
  > This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.
- `## Communication preferences` (replicated from the frontmatter in human-readable form)
- `## Identity` or `## Company` (name, legal form, registration number)
- `## Key contacts`
- `## Working relationship`

## Recommended markdown sections

- `## Technical stack` if relevant
- `## History` or `## Operational situation` if the project is complex

## Expected observations

- `[preference]` additional communication or working preference
- `[contract]` contractual element (daily rate, amendment, duration, terms)
- `[milestone]` contractual or relational milestone
- `[risk]` identified risk (churn, late payment, dissatisfaction)
- `[contact]` key person with role
- `[stack]` technical stack element

## Typed relations in the frontmatter

- `managed_by`, partner who manages operationally (e.g. a partner-owned product)
- `owned_by`, commercial owner partner (e.g. a partner-owned product)
- `referred_by`, partner who brought the lead
- `co_delivered_with`, partner with whom we co-deliver the service

## Additional relations in markdown

- `industry_peer_of [[Other client]]`, sector peer (for internal benchmarking)
- `evolved_from [[Prospect entity]]`, if the client was a prospect before
- `competes_with [[Other entity]]`, former partner turned competitor

## Wikilink naming convention

Wikilinks to this entity use the value of the `client` field as is. For example, `client: Bloom (Alex Martin)` is referenced as `[[Bloom (Alex Martin)]]`.

## Special case, client that is a partner's product

If the client is a product or an activity of a partner (e.g., a small brand owned by a white-label partner), the client CLAUDE.md must declare `owned_by` AND `managed_by` in the frontmatter. The partner CLAUDE.md must declare `owns` and `manages` as a mirror (mandatory symmetric pairs).

## Example

```yaml
---
client: Bloom (Alex Martin)
status: active
last_updated: 2026-04-08
legal_form: "sole proprietorship"
company_id: "REG-4829105"
industry: Coaching, wellness
tone: friendly
addressing: informal
primary_channel: email
email_format: "standard-professional"
language: en
constraints:
  - Avoid technical jargon
managed_by: Alex Martin
owned_by: Alex Martin
---

# Bloom, Client Context

> This file is loaded automatically as project context. Adapt tone, style, and deliverables to the communication preferences below.

## Communication preferences
Friendly and direct tone, informal address, email as the main channel. Avoid technical jargon.

## Working relationship
- [contract] Showcase website, 2-day package
- [milestone] Quote signed 2026-03-09
- [contact] Alex Martin, owner and sole decision-maker
```
