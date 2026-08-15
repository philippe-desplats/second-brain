# Basic Memory layer

Everything the second brain needs for typed, validated, searchable notes.

- `schemas/`: the canonical Picoschema note types plus the design manifest ([schemas/README.md](schemas/README.md)). Every markdown file in the workspace conforms to one of these types; the decision matrix lives in `.claude/rules/frontmatter.md`. Each schema declares two contracts, `settings.frontmatter:` for the YAML fields and `schema:` for the body observations and relations, both readable by Basic Memory's own `bm schema validate`.
- `scripts/`: 12 Python maintenance scripts (index generation, orphan detection, frontmatter repair, entity linking, relation audits, curation reminder). All support `--dry-run` style previews, and all run on the Python 3 standard library alone, with no dependency to install.

Basic Memory itself (the `bm` CLI, the MCP server, and its configuration) is installed and wired by `/sb-init`. The workspace remains fully usable without it; these schemas then serve as plain conventions and the scripts keep working on the files directly.
