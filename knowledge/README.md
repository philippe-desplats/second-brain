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

## From a playbook to a skill

A `playbook` written down is a process you follow. A skill is a process the workspace runs for you. The jump is worth making, but only once the playbook has stopped changing.

Three conditions, all of them:

1. You have run the playbook end to end at least three times, on top of the three repetitions that justified distilling it in the first place.
2. Its steps no longer move between runs. A playbook still being edited becomes a skill that lies.
3. Its output is a file or a decision, not a judgment call you would want to make yourself each time.

When they hold, create `.claude/skills/{name}/SKILL.md`, keep the playbook as the human-readable source and the skill as its executable form, and register the skill in `.claude/skill-registry.md`. Cross-link them: the playbook says which skill runs it, the skill says which playbook documents it.

Deliberately not automated: the conversion itself. A skill that writes skills sounds efficient and produces a fleet nobody reviewed. Writing the skill by hand is the review.
