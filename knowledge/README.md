# knowledge/

Distilled, reusable knowledge that is independent of any single client or project. If something you learned can serve several missions, it gets abstracted and promoted here. If it only matters for one client, it stays in `sources/`.

## Zones

| Path | What goes there |
|---|---|
| `knowledge/ops/` | Operational processes (client onboarding, billing workflow, audit procedures) |
| `knowledge/tech/` | Technical patterns (deployment, infrastructure, frameworks, APIs, automation) |
| `knowledge/business/` | Strategy, pricing, commercial methodology, standard proposals |

## Conventions

- Notes are `type: note` with a `subtype:` of `pattern`, `playbook`, `guide`, `runbook`, or `decision`.
- Named `{short-subtype}-{slug}.md`, for example `playbook-client-onboarding.md`.
- Promote a pattern on its **third repetition**, not before.
- Never store confidential client data, anonymize or abstract it. Never store raw artifacts.
- Full rules: `.claude/rules/knowledge.md`.
