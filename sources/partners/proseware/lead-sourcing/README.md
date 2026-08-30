---
title: Proseware Lead Sourcing
type: project-brief
schema_version: 1
category: partner
partner: Proseware
created: 2026-05-22
status: active
last_updated: 2026-06-24
topics: [lead-sourcing, partnerships]
owner: Sam Rivera
---

# Proseware Lead Sourcing

## Objective

Run the referral flow with Proseware end to end: log the leads each side sends, keep the commercial terms in one place, and make sure a referred account never falls between the two contracts.

## Context

Proseware integrates ERP and order-management systems for industrial SMEs and does not build customer-facing front ends. We build front ends and do not touch ERP. That gap is the partnership: each side sends the work it cannot take, and the accounts where both systems meet get coordinated instead of contested. This folder holds the agreement and the referral log. The delivery work a referral turns into lives in that client's own folder, not here.

## Planned activities

- [x] Agree the referral terms and sign the affiliation contract
- [x] Qualify and convert the first referral from Proseware
- [ ] Send one lead back, the ERP replacement we cannot take
- [ ] Invoice the referral fee once the first engagement is paid
- [ ] Review the terms after three referrals, the fee asymmetry included

## Structure

```
lead-sourcing/
  README.md       this brief
  deliverables/   signed agreement and any amendment
```

## Decisions and notes

- 2026-05-22: track opened after the third conversation about sending each other work, the arrangement needed terms before a real lead arrived
- 2026-06-05: mutual referral agreement signed, 10% on the first engagement of a lead Proseware sends
- 2026-06-09: Proseware introduced [[Globex]] by email, scope confirmed with the client the same week
- 2026-06-22: Globex redesign kicked off, the first referral is converted and the fee becomes due on payment

## Observations

- [goal] Keep every referral traceable from introduction to invoice
- [goal] Protect shared accounts from scope collisions between the two contracts
- [milestone] Agreement signed 2026-06-05
- [milestone] First referral converted 2026-06-22
- [decision] The fee applies to the first engagement only, never to renewals, extensions, or maintenance
- [decision] Each side keeps its own contract with a shared account, no subcontracting in either direction

## Relations

- parent [[Proseware]]
- produces [[Proseware mutual referral agreement]]
