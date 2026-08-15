---
title: Service
type: schema
entity: service
version: 1
schema:
  feature?(array): string, "included feature or deliverable"
  target?(array): string, "client target"
  kpi?(array): string, "key indicator on the service, number of subscribers, revenue, margin"
  risk?(array): string, "strategic risk on the offer"
  sold_to?(array): ClientContext, "client who subscribed"
  resold_by?(array): PartnerContext, "partner who resells"
  replaces?: Service, "previous offer this service replaces"
  bundles?(array): Service, "offer combined with others"
settings:
  validation: strict
  frontmatter:
    name: string, "commercial name of the offer or service"
    service_type(enum):
    - consulting
    - development
    - hosting
    - maintenance
    - audit
    - training
    - retainer
    - other
    status(enum):
    - active
    - pilot
    - deprecated
    - archived
    price_model?(enum):
    - fixed-fee
    - recurring
    - day-rate
    - commission
    - other
    price?: number, "price excl. tax if applicable"
    currency?: string, "currency, EUR by default"
    launch_date?: string, "launch date in YYYY-MM-DD format"
---

# Schema, Service

Represents an offer, service or product from your organization. Allows querying "which clients have offer X", "what is the recurring revenue on the hosting plan", "which partner resells what".

The `service_type` enum above is a generic starting set. `/sb-init` customizes it to match your actual catalog.

## Typical location

- `atlas/services/{slug}.md` at the workspace root (create the folder if needed)

Concrete example, `atlas/services/managed-hosting.md`, the offer used in the example at the bottom of this file.

## Why this schema

Documenting services as entities makes it possible to link a client to a specific offer, to track the evolution of the catalog, or to model the services resold by partners (`resells [[Service]]`). Without a schema, service names only exist in prose.

## Expected observations

- `[feature]` included feature or deliverable
- `[target]` client target
- `[kpi]` key indicator on the service (number of subscribers, revenue, margin)
- `[risk]` strategic risk on the offer

## Additional relations in markdown

- `sold_to [[Client]]`, client who subscribed
- `resold_by [[Partner]]`, partner who resells
- `replaces [[Old service]]`, replaces a previous offer
- `bundles [[Other service]]`, offer combined with others

## Example

```yaml
---
name: Managed Hosting
type: service
schema_version: 1
service_type: hosting
status: active
price_model: recurring
price: 189.90
currency: EUR
launch_date: 2023-01-01
---

# Managed Hosting

## Observations
- [feature] Optimized shared hosting
- [feature] Maintenance included, automatic updates
- [target] SMBs and freelancers with a website to run
- [kpi] 53 active subscriptions at the end of 2025
- [kpi] 2279 EUR annual per recurring client

## Relations
- sold_to [[Bloom]]
- sold_to [[Initech]]
```
