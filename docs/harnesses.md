# Running the workspace in any agent harness

The workspace is plain files: Markdown notes, Markdown instructions, skills in the open [Agent Skills](https://agentskills.io/specification) format, and an optional MCP server. What differs from one harness to the next is only the wiring, and this page documents it.

Facts come from each vendor's official documentation as read on 2026-11-28. The "Status" column says how far each one was checked: **tested** means the behaviour was observed in a real session, **documented** means it rests on the vendor's documentation only. Vendors change their loading rules often, so re-check a row before relying on it, and open an issue when one is out of date.

## What loads automatically

| Harness | Root `AGENTS.md` | Entity `AGENTS.md` (on opening a file in the folder) | Skills folder it reads | After-write hook | Structured question tool | Status |
|---|---|---|---|---|---|---|
| Claude Code (2.1.281+) | yes, natively when no `CLAUDE.md` exists, check with `/memory` | yes | `.claude/skills` | `.claude/settings.json`, `PostToolUse` | `AskUserQuestion` | tested on 2.1.332 |
| Claude Cowork | not verified since this workspace dropped `CLAUDE.md`: if the conventions are not followed, start the session with "read AGENTS.md" | not documented | through plugins | no | not documented | documented |
| Claude Agent SDK | through Claude Code's loader when `settingSources` includes the project, `AGENTS.md` support not documented | not documented | `.claude/skills` | `.claude/settings.json` | your own | documented |
| OpenAI Codex | yes, root to working directory | only between the root and its working directory | `.agents/skills` | `.codex/hooks.json`, `PostToolUse`. Trust the project, then approve the hook in `/hooks`, and approve it again after every upgrade that changes the file | `request_user_input` (Plan mode) | documented |
| Gemini CLI | with `context.fileName`, set in `.gemini/settings.json` | yes, just in time on the current release. Older releases scanned the folders below the working directory at startup, check with `/memory show` that only the root file loads | `.agents/skills`, `.gemini/skills` | `.gemini/settings.json`, `AfterTool`, warns before running a new or changed project hook | `ask_user` | documented |
| Google Antigravity | yes | not documented | `.agents/skills` | not documented | not documented | documented |
| GitHub Copilot (VS Code, CLI) | yes | yes, the nearest one | `.agents/skills`, `.claude/skills`, `.github/skills` | reads `.claude/settings.json` (preview, matchers ignored, the hook script skips read-only tools itself) | `vscode/askQuestion` (VS Code) | documented |
| GitHub Copilot coding agent (cloud) | yes | not documented | not documented | no | no | documented |
| Cursor | yes | yes | `.agents/skills`, `.claude/skills`, `.cursor/skills` | imports the Claude Code hook from `.claude/settings.json` ("third-party" configs, on by default), so the workspace ships no `.cursor/hooks.json` | "Ask questions" | documented |
| OpenCode | yes | yes, lazily | `.agents/skills`, `.claude/skills`, `.opencode/skills` | plugins only | `question` | documented |
| Windsurf (Devin Local) | yes | between the root and the working directory | `.agents/skills`, `.claude/skills` | reads `.claude/settings.json` | not documented | documented |
| Cline | yes | not documented | `.claude/skills`, `.cline/skills` | SDK plugins only | `ask_question` | documented |
| Roo Code | root only | no | `.agents/skills`, `.roo/skills` | not documented | not documented | documented |
| Zed | yes (first match among several names) | not documented | `.agents/skills` | no | none | documented |
| Amp | yes | yes, on reading a file in the subtree | `.agents/skills`, `.claude/skills` | plugins only | none | documented |
| Goose | yes | yes, on access | `.agents/skills`, `.claude/skills` | not documented | not documented | documented |
| JetBrains Junie | yes | not documented | not documented | not documented | not documented | documented |
| Qwen Code | with `context.fileName`, set in `.qwen/settings.json` | not documented | `.agents/skills` | not documented | not documented | documented |
| Kiro | yes | not documented | `.kiro/skills`, a link to `.claude/skills` shipped with the workspace | not documented | not documented | documented |
| Aider | through `.aider.conf.yml`, which reads `AGENTS.md` on every run | no | no | no | no | documented |

How the workspace covers the gaps:

- `.agents/skills` and `.kiro/skills` are symbolic links to `.claude/skills`, so every family of harnesses sees the same 16 skills. On Windows, git creates the link only with `core.symlinks` enabled. Otherwise it leaves a small text file, `/sb-doctor` reports it, and `ln -s ../.claude/skills .agents/skills` repairs it. Where links cannot be created at all, keep git's entry with `git update-index --skip-worktree .agents/skills .kiro/skills` and use an identical copy of the folder locally, never committed: `check_harness_compat.py` tolerates it with a warning, and it must be refreshed after every skill change.
- `AGENTS.md`, section "Entity context", tells every agent to read the entity's `AGENTS.md` before writing anything that entity will see, which covers the harnesses that do not load it on their own.
- `AGENTS.md`, section "Asking the owner", maps the question tools above and falls back to a plain question and a wait.
- `AGENTS.md`, section "Rules to read", lists which `.claude/rules/*.md` to read before which work, since only Claude Code loads them automatically.
- The title alias pass has a hook wherever the harness offers one. Everywhere else, the git pre-commit hook in `.githooks/` and `/sb-doctor` catch a missing alias. Enable the pre-commit once per clone with `git config core.hooksPath .githooks`.
- A harness that reads both `.agents/skills` and `.claude/skills` (Copilot, Cursor, OpenCode, Windsurf, Amp, Goose) meets every skill twice under the same name. Amp documents that the first one wins, Codex documents that same-named skills are not merged and may both appear in its picker. Either entry is harmless: both point to the same file.
- The alias hook skips read-only tool calls and writes each note atomically, re-reading it first, so a note edited at the same moment, by you in Obsidian or by the agent, is never overwritten.
- `AGENTS.md`, section "Client content is data", tells every agent that entity files and client documents are data, never instructions to follow. It matters more now that many harnesses load entity files as instructions on their own.
- No `CLAUDE.md` or `CLAUDE.local.md` may exist in the tree. Claude Code skips a folder's `AGENTS.md` when one sits in that folder or above it, measured on 2.1.332. Stuck on a Claude Code older than 2.1.281? Keep a local, uncommitted `CLAUDE.md` holding `@AGENTS.md` and set the user-level Project instructions setting to load both files, at the cost of entity contexts no longer loading on their own. `check_harness_compat.py` and `/sb-doctor` will report that file until you remove it, which is the reminder to do so once Claude Code is upgraded. `python3 -I basic-memory/scripts/check_harness_compat.py` checks this and the rest of the wiring.

## Invoking a skill

Harnesses that discover skills expose them by name: `/capture` in Claude Code and most others, a `$capture` mention in Codex. In a harness that does not discover skills, ask the agent to read `.claude/skills/capture/SKILL.md` and follow it. The registry in `.claude/skill-registry.md` says which skill fits which request.

## Basic Memory over MCP

Basic Memory is optional. When it is installed (1.0 or later), every harness runs the same command, `bm mcp --project YOUR_PROJECT`, and every project-scoped tool call must also pass `project`. Replace `/path/to/bm` with the output of `which bm`. The files below hold a machine path, so the ones inside the workspace are gitignored.

**Claude Code and GitHub Copilot**, `.mcp.json` at the root (copy `.mcp.json.example`):

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "/path/to/bm",
      "args": ["mcp", "--project", "YOUR_PROJECT"]
    }
  }
}
```

**OpenAI Codex**, `~/.codex/config.toml`, or `.codex/config.toml` in a trusted project:

```toml
[mcp_servers.basic-memory]
command = "/path/to/bm"
args = ["mcp", "--project", "YOUR_PROJECT"]
```

**Gemini CLI**, `~/.gemini/settings.json`. Keep it in the user file: the workspace's `.gemini/settings.json` is tracked, since it carries the context file name and the hook.

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "/path/to/bm",
      "args": ["mcp", "--project", "YOUR_PROJECT"]
    }
  }
}
```

**Cursor**, `.cursor/mcp.json` or `~/.cursor/mcp.json`, same shape as Claude Code.

**Roo Code**, `.roo/mcp.json`, same shape as Claude Code. **Cline** reads only its global `cline_mcp_settings.json`, same `mcpServers` shape.

**OpenCode**, `opencode.json` or `opencode.jsonc`. The key layout changed between OpenCode versions, so check `opencode.ai/docs` for yours:

```json
{
  "mcp": {
    "basic-memory": {
      "type": "local",
      "command": ["/path/to/bm", "mcp", "--project", "YOUR_PROJECT"]
    }
  }
}
```

**Windsurf (Devin Local)**, `.devin/mcp_config.local.json` (gitignored) or `~/.config/devin/mcp_config.json`. The key names are not documented, `mcpServers` with the shape above is the historical Windsurf format.

**Zed**, `context_servers` in its user `settings.json` (never the workspace's `.zed/settings.json`, which would be committed):

```json
{
  "context_servers": {
    "basic-memory": {
      "command": "/path/to/bm",
      "args": ["mcp", "--project", "YOUR_PROJECT"]
    }
  }
}
```

**Amp**, `.amp/settings.json` under `"amp.mcpServers"`, same inner shape, then `amp mcp approve`.

**Qwen Code**, `~/.qwen/settings.json` (keep the user file, the workspace's `.qwen/settings.json` is tracked), `mcpServers` with the shape above.

**Kiro**, `~/.kiro/settings/mcp.json`, or `.kiro/settings/mcp.json` (gitignored), `mcpServers` with the shape above.

**GitHub Copilot coding agent**, the MCP configuration of the repository settings on github.com. Basic Memory runs locally, so it is out of reach of a cloud agent: the agent falls back to the file tree.

**Goose** and **Junie**: add a stdio extension or server that runs the same command through their own configuration screen, in their user-level configuration, never in a tracked file of the workspace.

`/sb-init` asks which harnesses you use, records them in `.sb-config.json` under `harnesses`, and writes these files for you, one confirmation each.

## Checking the wiring

```sh
python3 -I basic-memory/scripts/check_harness_compat.py
uvx --from skills-ref agentskills validate .claude/skills/capture
```

The first checks the skill frontmatter against the Agent Skills specification, the `.agents/skills` link, the absence of any `CLAUDE.md`, the size of `AGENTS.md` (Codex reads at most 32 KiB), single-harness tool names in skills and rules, and the hook configurations. The second is the official validator, run one skill at a time.
