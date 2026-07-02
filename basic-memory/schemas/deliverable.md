---
title: Deliverable
type: schema
entity: deliverable
schema_version: 1
schema:
  date: string, "deliverable date in YYYY-MM-DD format"
  title: string, "deliverable title"
  deliverable_type(enum):
  - contract
  - quote
  - proposal
  - invoice
  - credit-note
  - newsletter
  - post
  - pitch-deck
  - audit
  - report
  - document
  - code
  - slides
  - spec
  - mockup
  - roadmap
  - specification
  - terms-of-sale
  - legal-notice
  - privacy-policy
  category?(enum):
  - client
  - partner
  - internal
  - personal
  client?: ClientContext, "recipient client if client-scoped"
  partner?: PartnerContext, "recipient partner if partnership-scoped"
  reference?: string, "quote number, contract, or billing reference"
  amount_pre_tax?: number, "pre-tax amount as a number, optional"
  amount_with_tax?: number, "with-tax (gross) amount as a number, optional"
  currency?: string, "currency, EUR by default"
  vat_regime?(enum):
  - pre-tax
  - with-tax
  - vat-exempt
  amount_label?: string, "free-form label for non-standard or recurring cases"
  status?(enum):
  - draft
  - review
  - sent
  - signed
  - invoiced
  - paid
  - cancelled
  - archived
  sent_date?: string, "sent date in YYYY-MM-DD format"
  due_date?: string, "due date in YYYY-MM-DD format"
  paid_date?: string, "actual payment date in YYYY-MM-DD format"
  billing_ref?: string, "reference in an external billing tool if synced"
  repo_url?: string, "repo URL if deliverable_type is code, spec, roadmap"
  commit_sha?: string, "commit SHA if deliverable_type is code"
  implements?: Strategy, "strategy implemented"
  succeeds?: Deliverable, "previous deliverable in a sequence"
settings:
  validation: warn
---

# Schema, Deliverable

Finalized document, delivered or archived as a reference. Covers 3 families:

1. **Commercial deliverables** (client, partner), signed contract, sent quote, proposal, invoice, credit note, newsletter, social post, audit report, terms of sale, legal notice, privacy policy, specification
2. **Internal deliverables**, technical spec, pitch slides, strategy document, code (index file or README pointing to repo), mockup, roadmap
3. **Personal deliverables**, training slides, documents, etc.

## Typical location

- `sources/clients/{client}/{project}/deliverables/YYYY-MM-DD-{type}-slug.md`
- `sources/partners/{partner}/{project}/deliverables/YYYY-MM-DD-{type}-slug.md`
- `sources/internal/{project}/deliverables/YYYY-MM-DD-{type}-slug.md`
- `sources/personal/{project}/deliverables/YYYY-MM-DD-{type}-slug.md`

## Reference examples

- `sources/clients/initech/contracting/deliverables/2026-03-11-contract-hosting-services.md` (contract)
- `sources/clients/initech/google-ads-conversion/deliverables/2026-03-26-quote-technical-work.md` (quote)
- `sources/partners/highline/support/deliverables/2026-04-01-proposal-local-committee.md` (proposal)
- `sources/clients/umbrella/deliverables/2026-04-02-invoice-march-2026.md` (invoice)
- `sources/partners/dimwave/support/deliverables/2026-04-06-newsletter-dimwave.md` (newsletter)

## Difference from writing

A `deliverable` is the final, tracked version of a delivered or archived document. A `writing` is content still being drafted. The transition, a writing becomes a deliverable when `status` changes to `sent` or `signed`.

## Financial fields

Amounts are typed as `number` (not string) to allow automatic summing and analytical queries. The VAT fields (`amount_pre_tax`, `amount_with_tax`, `vat_regime`) are all optional. Keep `amount_label` for atypical billing cases (monthly subscription, pay-as-you-go, etc.) where a single number does not make sense.

## Expected observations

- `[commitment]` commitment made in the contract, quote, or proposal
- `[clause]` legal or conditional clause to remember
- `[item]` billing line or item
- `[risk]` risk identified at delivery time
- `[spec]` technical specification (for deliverable_type document, code, spec, mockup)

## Typed relations in the frontmatter

- `client` or `partner`, recipient
- `implements`, strategy the deliverable implements
- `succeeds`, previous deliverable in the sequence

## Additional relations in markdown

- `for [[Client | Partner | Internal]]` beneficiary
- `based_on [[Research]]` source

## Example 1, commercial deliverable

```yaml
---
date: 2026-03-11
title: Initech hosting and associated services contract
deliverable_type: contract
category: client
client: Initech
reference: CONTRACT-2026-INI-001
amount_pre_tax: 189.90
currency: EUR
vat_regime: pre-tax
amount_label: 189.90 EUR excl. tax monthly, recurring billing
status: signed
sent_date: 2026-03-09
due_date: 2026-03-11
billing_ref: "INV-1234567"
implements: Initech commercial proposal 2026-02
---

# Hosting and associated services contract

## Observations
- [commitment] Managed hosting, 99.5% SLA
- [clause] 12-month term, automatic renewal, 30-day notice
- [item] Monthly service 189.90 EUR excl. tax

## Relations
- for [[Initech]]
- succeeds [[Initech hosting quote]]
```

## Example 2, internal deliverable

```yaml
---
date: 2026-03-15
title: Internal wiki v2 architecture spec
deliverable_type: spec
category: internal
reference: ACME-SPEC-WIKI-V2
status: signed
repo_url: https://git.example.com/internal/internal-wiki-v2
implements: Internal wiki v2 architecture strategy
---

# Internal wiki v2 architecture spec

## Observations
- [spec] 21 databases with cross-database relations
- [spec] Calculated formulas for cross-cutting metrics
- [commitment] Delivery to staff by the end of March

## Relations
- for [[Acme]]
```
