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

## Forbidden rules

- No confidential client information in `knowledge/` (always anonymized or abstracted)
- No raw email, transcript, or meeting notes (these artifacts live in `sources/`)
- No untested or still-being-discovered pattern (they stay in the source project until validated)
