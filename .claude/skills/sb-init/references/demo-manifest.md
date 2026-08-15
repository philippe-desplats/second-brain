# Demo Content Manifest

Demo content created with the boilerplate. It exists so a new user can SEE the second brain working (a fictional client, a fictional partner who referred that client, projects, emails, a meeting, a signed agreement, a distilled playbook, a person, and a topic, all schema-correct and cross-linked) before filling the workspace with their own material.

`/sb-init` offers to remove it during initialization. Deleting every path listed here removes all traces of the demo. All content is fictional (client "Globex", partner "Proseware", contacts "Jane Doe" and "Morgan Ellis", domains `globex-example.com` and `proseware-example.com`).

## Removal roots

Deleting these five roots removes the demo content itself:

- `sources/clients/globex/` (client context, project brief, emails, meeting)
- `sources/partners/proseware/` (partner context, project brief, signed referral agreement)
- `atlas/people/jane-doe.md`
- `atlas/topics/client-onboarding.md`
- `knowledge/ops/playbook-client-onboarding.md`

Removing the partner leaves one dangling line in the client file: `sources/clients/globex/CLAUDE.md` declares `referred_by [[Proseware]]` under `## Relations`. If Globex is kept and Proseware removed, drop that line too. Keep `sources/partners/.gitkeep`, it is workspace structure, not demo content.

This manifest (`.claude/skills/sb-init/references/demo-manifest.md`) is a skill reference, not demo content; remove it last, once the paths above are gone.

## Files

sources/clients/globex/CLAUDE.md
sources/clients/globex/website-redesign/README.md
sources/clients/globex/website-redesign/emails/2026-06-15-01-in-kickoff-questions.md
sources/clients/globex/website-redesign/emails/2026-06-16-01-reply-kickoff-answers.md
sources/clients/globex/website-redesign/meetings/2026-06-22-meeting-kickoff.md
sources/partners/proseware/CLAUDE.md
sources/partners/proseware/lead-sourcing/README.md
sources/partners/proseware/lead-sourcing/deliverables/2026-06-05-contract-referral-agreement.md
knowledge/ops/playbook-client-onboarding.md
atlas/people/jane-doe.md
atlas/topics/client-onboarding.md
.claude/skills/sb-init/references/demo-manifest.md
