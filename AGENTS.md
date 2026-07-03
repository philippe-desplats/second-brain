# AGENTS.md

Orientation file for AI coding agents (Codex CLI, OpenCode, Gemini CLI, Cursor, and any tool that reads the [AGENTS.md](https://agents.md/) standard). The canonical, always-up-to-date instructions for this workspace live in `CLAUDE.md` at the repository root: **read that file first and follow it**. This file only tells you where everything is.

## What this workspace is

This is NOT a code project. It is a second brain: a markdown workspace for capturing, organizing, and retrieving everything about the owner's work. Your job here is filing, retrieving, distilling, and writing, not compiling.

## Where the truth lives

| File | Role |
|---|---|
| `CLAUDE.md` | Canonical instructions: owner profile, zones, filing rules, conventions |
| `.sb-config.json` | Machine-readable workspace configuration |
| `.claude/rules/*.md` | Detailed rules: frontmatter, emails, entities, knowledge, atlas, communication |
| `.claude/skill-registry.md` | Catalog of the 13 workflow skills and when to use each |
| `basic-memory/schemas/*.md` | The 15 canonical frontmatter schemas every note conforms to |
| `sources/{zone}/{entity}/CLAUDE.md` | Per-entity context and communication preferences; read before writing anything that entity will see |

If `CLAUDE.md` says the profile is NOT CONFIGURED, stop and tell the owner to run the setup skill (`.claude/skills/sb-init/`) first.

## Skills

Workflow skills live in `.claude/skills/{name}/SKILL.md` and follow the open [SKILL.md standard](https://www.agensi.io/learn/agent-skills-open-standard): plain markdown instructions, no binaries. If your tool does not auto-discover them, invoke one by reading its `SKILL.md` and following it step by step (they chain through `steps/*.md` files). Consult `.claude/skill-registry.md` to pick the right skill for a request.

## Basic Memory (semantic search) via MCP

The optional semantic search layer is [Basic Memory](https://docs.basicmemory.com), exposed as a standard MCP server (`bm mcp`). Claude Code reads `.mcp.json` (see `.mcp.json.example`). For other tools, wire the same command:

**Codex CLI** (`~/.codex/config.toml`):

```toml
[mcp_servers.basic-memory]
command = "/path/to/bm"   # run: which bm
args = ["mcp", "--project", "YOUR_PROJECT_NAME"]
```

**OpenCode** (`opencode.json`):

```json
{
  "mcp": {
    "basic-memory": {
      "type": "local",
      "command": ["/path/to/bm", "mcp", "--project", "YOUR_PROJECT_NAME"]
    }
  }
}
```

**Gemini CLI** (`~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "/path/to/bm",
      "args": ["mcp", "--project", "YOUR_PROJECT_NAME"]
    }
  }
}
```

## Non-negotiable rules (summary, details in CLAUDE.md)

- Never invent context about an entity; search the files first, ask when missing.
- Nothing at an entity root except its `CLAUDE.md`; every artifact goes in a project subfolder.
- Every new markdown file gets YAML frontmatter conforming to a schema in `basic-memory/schemas/`.
- File naming: `YYYY-MM-DD-{type}-slug.md`; emails: `YYYY-MM-DD-{seq}-{direction}-slug.md`.
- Write generated content in the owner's working language (see the `CLAUDE.md` profile block); structural files stay in English.
- Never mention AI assistance in client-facing content, and never use em dashes in generated text.
