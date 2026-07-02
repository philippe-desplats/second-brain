# Basic Memory layer

Everything the second brain needs for typed, validated, searchable notes.

- `schemas/`: the 15 canonical Picoschema note types plus the design manifest ([schemas/README.md](schemas/README.md)). Every markdown file in the workspace conforms to one of these types; the decision matrix lives in `.claude/rules/frontmatter.md`.
- `scripts/`: 11 Python maintenance scripts (index generation, orphan detection, frontmatter repair, entity linking, relation audits). All support `--dry-run` style previews; only `auto_link_entities.py` and `generate_indexes.py` need PyYAML, the rest are standard library.

Basic Memory itself (the `bm` CLI, the MCP server, and its configuration) is installed and wired by `/sb-init`. The workspace remains fully usable without it; these schemas then serve as plain conventions and the scripts keep working on the files directly.
