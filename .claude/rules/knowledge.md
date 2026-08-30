# Knowledge Rules

## When to use knowledge/

This zone is reserved for **distilled knowledge reusable outside a client/partner context**. If a piece of information is only useful for a client project, it stays in `sources/clients/{X}/`. If it can serve several missions, it gets distilled into `knowledge/`.

Three questions guide where it goes:

1. **Is it a raw artifact** (email, transcript, meeting notes, deliverable)? -> `sources/`
2. **Is it distilled, reusable knowledge** (pattern, playbook, guide, runbook, decision)? -> `knowledge/`
3. **Is it an index, a map, an entity**? -> `atlas/`

## Structure

- `knowledge/ops/`, operational processes (client onboarding, billing workflow, weekly review methodology, audit procedures)
- `knowledge/tech/`, technical patterns (deployment pipelines, infrastructure, frameworks, APIs, automation)
- `knowledge/business/`, strategy, pricing, commercial methodology, standard proposals

## Naming convention

`{short-subtype}-{slug}.md`, for example:

- `knowledge/ops/playbook-client-onboarding.md`
- `knowledge/tech/pattern-deployment-pipeline.md`
- `knowledge/business/guide-pricing-landing-page.md`
- `knowledge/tech/runbook-incident-recovery.md`
- `knowledge/business/decision-pricing-2026-q2.md`

## Frontmatter

The Basic Memory type is `note`, the subtype lives in the `subtype:` field:

```yaml
---
title: {Pattern or Guide name}
type: note
schema_version: 1
subtype: pattern | playbook | guide | runbook | decision
status: active | deprecated | draft
date: YYYY-MM-DD
topics: [topic1, topic2]
---
```

Allowed `subtype:` values in `knowledge/`:

- `pattern`, reusable technical motif (code, architecture, configuration)
- `playbook`, step-by-step operational process
- `guide`, long-form reference document
- `runbook`, intervention procedure for an incident or recurring operation
- `decision`, ADR-style, a documented decision with context/options/consequences

## Distillation

When a pattern emerges across several missions (for example "how to run a client onboarding"), it deserves to be distilled into `knowledge/ops/playbook-client-onboarding.md`. The trigger is the **3rd repetition**. Before 3 occurrences, keep it in the project context.

Ritualize it with a weekly review: "what did I learn this week that deserves a reusable note?"

## Relations

`knowledge/` notes must reference their sources via wiki-links:

```markdown
## Relations

- distilled_from [[Globex Onboarding]]
- used_by [[Initech Onboarding]]
- about [[Client Onboarding]]
```

## Provenance line

Every distilled note carries a one-line provenance at the top of its body stating where it came from and when it was distilled, so the chain back to the raw source is never lost:

```markdown
_Distilled from Globex and Initech onboardings on 2026-07-02. See Relations for sources._
```

## Promotion and the quarantine rule

Nothing reaches `knowledge/` without a human deciding it should. Two mechanisms enforce it.

**The gate.** `/distill` is the only skill that writes into `knowledge/`, and it shows the draft for approval before saving. `archive` is forbidden from touching the zone, `moc-new` writes only to `atlas/maps/`, and `curate` writes nowhere itself. Approving a draft is a review, not a claim of authorship: the note keeps `written_by: agent`.

**The quarantine.** `inbox/` is where machine-produced material lands while it waits to be classified. A note carrying `written_by: agent` is never moved straight into `knowledge/`; it goes through `/distill` like any other candidate, which means it must also clear the three-occurrence threshold.

The reason is the failure mode this zone exists to prevent. A distilled note is read months later as settled understanding. If the owner can no longer tell which of those notes they actually thought through, the zone stops being knowledge and becomes a pile of plausible text.

## Forbidden rules

- No confidential client information in `knowledge/` (always anonymized or abstracted)
- No raw email, transcript, or meeting notes (these artifacts live in `sources/`)
- No untested or still-being-discovered pattern (they stay in the source project until validated)
