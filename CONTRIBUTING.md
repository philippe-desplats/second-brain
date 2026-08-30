# Contributing to Second Brain Structure

Thanks for taking the time to contribute. This document explains how to report issues, propose changes, and the requirements a contribution must meet to be merged.

## Reporting bugs and requesting features

Open a [GitHub issue](https://github.com/philippe-desplats/second-brain/issues). For a bug, include which Claude surface you use (Claude Code terminal or desktop, Cowork, or another agent), the skill or script involved, what you asked, and what you expected versus what happened. Excerpts of the skill's output help a lot; strip any personal or client data from them first.

## Proposing a change

1. Fork the repository and create a branch from `main`.
2. Make your change.
3. Test it in a throwaway clone: run the affected skill end to end in a fresh copy of the workspace (never in your live second brain) and check the resulting files against the schemas in `basic-memory/schemas/`.
4. Open a pull request describing what changed and why. Link the issue it addresses if there is one.

Small fixes (typos, docs, obvious bugs) can go straight to a pull request. For larger changes, a new skill, a schema change, or a new zone concept, open an issue first to discuss the direction before investing time.

## What makes a good contribution here

This repository is a workspace template, not application code. The quality bar is about conventions staying coherent:

- **Skills** follow the existing structure: a `SKILL.md` entry point, `steps/*.md` chained by `next_step`, explicit execution rules, human validation before any write. Register new skills in `.claude/skill-registry.md`.
- **Schemas** in `basic-memory/schemas/` are the single source of truth for frontmatter. A schema change must update the decision matrix in `.claude/rules/frontmatter.md` and any template that uses it. `check_consistency.py` catches the templates you forgot: it validates every frontmatter example inside a skill against the schemas, which is how three of them were found writing notes that belonged to no type.
- **Scripts** in `basic-memory/scripts/` are Python 3 standard library only, no dependencies, and must degrade gracefully on pruned zones (missing `sources/partners/` must never crash them). Each one stays runnable on its own, so a helper two scripts need is duplicated rather than extracted: `parse_frontmatter_yaml` exists in both `generate_indexes.py` and `auto_link_entities.py` and the two copies must stay identical.
- **Placeholders**: demo and example content uses fictional names only (Acme for the owner organization, Globex and Initech for clients, Jane Doe for people, `example.com` domains). Never use real people, companies, or paths.
- **Language**: structural files (skills, rules, schemas, templates, docs) are written in English. No em dashes in prose.
- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `revert`.
- **Cross-platform**: the workspace targets macOS, Linux, and Windows. Anything scheduler-related needs the three variants (LaunchAgent, cron, schtasks).
- **No AI or vendor attribution** in commits, code comments, or documentation.
- **Privacy first**: nothing in this repository may ever contain real client data, credentials, or tokens. `.mcp.json` stays gitignored; only `.mcp.json.example` is tracked.

## Local testing

There is no build. To validate a change:

```sh
python3 basic-memory/scripts/check_consistency.py
python3 basic-memory/scripts/check_orphans.py
python3 basic-memory/scripts/check_symmetric_relations.py --check
python3 basic-memory/scripts/check_double_frontmatter.py
python3 basic-memory/scripts/generate_indexes.py --output-dir /tmp/idx-test
python3 basic-memory/scripts/audit_field_usage.py
```

Those six run on a bare clone and validate this repository. They are the ones that matter.

**`bm schema validate` does not validate this repository unless you make it.** It runs against whichever Basic Memory project is configured on your machine, which is your own vault, not the clone. Running it without registering the clone first returns a green result about something else entirely. To actually validate the clone:

```sh
bm project add sb-clone .          # register this working copy
for t in $(ls basic-memory/schemas/*.md | xargs -n1 basename | sed 's/\.md$//' | grep -v README); do
  bm schema validate "$t" --project sb-clone --strict
done
bm project remove sb-clone         # leave your machine as you found it
```

The type argument is not optional either: omitting it validates nothing and still exits 0.

For skill changes, clone the repo to a scratch folder, run `/sb-init` there with a fictional persona, and exercise the skill you touched. The demo client (Globex) gives you a filed workspace to test retrieval against.

### What the checks cover, and what they do not

`check_consistency.py` validates the frontmatter examples inside skills, the properties their views read, the links they contain, and the topic slugs they reference. That is the static surface, and it is where most defects have been found.

It does not execute a skill. Nothing verifies that following a skill's steps in order produces what the skill claims, that two skills agree with each other, or that a step still refers to a file the last change did not move. Those defects exist and have all been found by a human or an agent reading closely, never by a check.

So the throwaway clone above is not optional ceremony for a skill change. It is the only test that covers the behaviour, and running the skill end to end there is what stands between a plausible-looking instruction and a working one.

## Cutting a release

Every release ships an upgrade prompt in its `CHANGELOG.md` section and in its GitHub release notes, under the heading `### Upgrade prompt, X to Y`. It is a copy-paste block a cloner hands to the agent that operates their workspace.

It exists because the git recipe in the README covers only part of a release. The recipe checks out `.claude`, `basic-memory/schemas`, `basic-memory/scripts` and `templates`, and deliberately never touches a data zone. Three kinds of change fall outside it, and every release so far has had at least one:

- **Files that live in a data zone.** The 0.5.0 Bases views ship in `atlas/maps/`, so the recipe pulls none of them. New files conflict with nothing and can be checked out by name, but somebody has to say which.
- **Files the cloner owns and has edited.** `atlas/home.md` is their hub. It cannot be checked out without destroying their work, so the change has to be described well enough that an agent can merge it.
- **Their own notes, written against the old contract.** The 0.4.0 `/ops-init-project` emitted project briefs with no `type:`, which the 0.5.0 views filter on. No git operation repairs data, and a migration script cannot ask the questions a half-typed note raises.

Write the prompt against the real diff, not from memory: `git diff --name-only vX..vY | grep -vE '^(\.claude/|basic-memory/(schemas|scripts)/|templates/)'` lists exactly what the recipe misses. Four properties are not negotiable, since this prompt runs unattended against somebody's only copy of their notes:

1. **It refuses to start on a dirty tree**, so the whole upgrade stays revertible with one command.
2. **It never deletes.** An upgrade adds and rewrites; anything else is a decision the owner makes themselves.
3. **It gates on a diff before writing into a data zone**, and waits.
4. **It ends with the check scripts, and with what they cannot check.** A Bases view that was never opened in Obsidian is not verified, and no script will ever say so.

Test it the way a cloner will meet it: check out the previous tag into a scratch folder, run `/sb-init`, create a project so there is real data to migrate, then paste the prompt and follow it without correcting it. What you have to correct by hand is a defect in the prompt.

## License

By contributing, you agree that your contributions are licensed under the project's [MIT License](LICENSE).
