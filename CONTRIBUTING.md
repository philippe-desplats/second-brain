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
- **Schemas** in `basic-memory/schemas/` are the single source of truth for frontmatter. A schema change must update the decision matrix in `.claude/rules/frontmatter.md` and any template that uses it.
- **Scripts** in `basic-memory/scripts/` are Python 3 standard library only, no dependencies, and must degrade gracefully on pruned zones (missing `sources/partners/` must never crash them).
- **Placeholders**: demo and example content uses fictional names only (Acme for the owner organization, Globex and Initech for clients, Jane Doe for people, `example.com` domains). Never use real people, companies, or paths.
- **Language**: structural files (skills, rules, schemas, templates, docs) are written in English. No em dashes in prose.
- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `revert`.
- **Cross-platform**: the workspace targets macOS, Linux, and Windows. Anything scheduler-related needs the three variants (LaunchAgent, cron, schtasks).
- **No AI or vendor attribution** in commits, code comments, or documentation.
- **Privacy first**: nothing in this repository may ever contain real client data, credentials, or tokens. `.mcp.json` stays gitignored; only `.mcp.json.example` is tracked.

## Local testing

There is no build. To validate a change:

```sh
python3 basic-memory/scripts/check_orphans.py
python3 basic-memory/scripts/check_symmetric_relations.py --check
python3 basic-memory/scripts/check_double_frontmatter.py
python3 basic-memory/scripts/generate_indexes.py --output-dir /tmp/idx-test
```

For skill changes, clone the repo to a scratch folder, run `/sb-init` there with a fictional persona, and exercise the skill you touched. The demo client (Globex) gives you a filed workspace to test retrieval against.

## License

By contributing, you agree that your contributions are licensed under the project's [MIT License](LICENSE).
