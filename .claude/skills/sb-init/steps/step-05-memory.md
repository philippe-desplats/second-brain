---
name: step-05-memory
description: Optional Basic Memory installation and MCP wiring
prev_step: steps/step-04-personalize.md
next_step: steps/step-06-launch.md
---

# Step 5: Basic Memory (optional, recommended)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER modify `~/.basic-memory/config.json` or register MCP servers without an explicit, individual confirmation
- 🛑 NEVER store secrets in any tracked file; `.mcp.json` is gitignored by design
- ✅ ALWAYS offer the skip path; the workspace works without Basic Memory (skills fall back to file scans)
- ✅ ALWAYS explain what each system-level change does before asking

## PITCH (one paragraph, then ask)

Basic Memory adds semantic search and a knowledge graph over the markdown files: the agent can find notes by meaning ("what did we decide about hosting pricing?") instead of exact words, and follow relations between entities. It runs fully locally (SQLite + local embeddings). Ask: set it up now, or skip? Store `{bm_enabled}`.

**If skipped:** note in the CLAUDE.md profile block `Basic Memory project: not used`, and proceed to step-06.

## EXECUTION SEQUENCE (if accepted):

### 1. Install the CLI

```bash
which bm || uv tool install basic-memory
```

If `uv` is missing, offer `brew install uv` first (macOS) or point to https://docs.astral.sh/uv/. Then warm up the embedding model (downloads once):

```bash
bm doctor
```

### 2. Create the project

Derive `{bm_project}` from the workspace folder name (kebab-case). Then:

```bash
bm project add {bm_project} {absolute-workspace-path}
bm project list
```

### 3. Apply the critical configuration

Explain, then with confirmation edit `~/.basic-memory/config.json` (JSON, preserve existing keys):

| Setting | Value | Why |
|---|---|---|
| `disable_permalinks` | `true` | Stops permalink frontmatter churn and a known double-frontmatter corruption bug |
| `ensure_frontmatter_on_sync` | `false` | Prevents mass-stamping `type: note` on every file at first sync |
| `sync_changes` | `false` | Disables the live file watcher; indexing happens via explicit or scheduled `bm reindex` |

These three settings are hard-won defaults from production use; do not skip them.

### 4. Register the MCP server

Copy `.mcp.json.example` to `.mcp.json` and fill in the real values:

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "{output of: which bm}",
      "args": ["mcp", "--project", "{bm_project}"]
    }
  }
}
```

Tell the owner the server becomes available at the next Claude Code session start.

### 5. First index and smoke test

```bash
bm reindex --project {bm_project}
bm tool search-notes --query "charter"
```

The charter written in step-04 should come back. If the index is empty, check `bm status --project {bm_project}`.

### 6. Scheduled reindex (optional)

Offer a scheduled reindex so the index never goes stale:

- **macOS**: a LaunchAgent plist at `~/Library/LaunchAgents/com.{bm_project}.reindex.plist` running `bm reindex --project {bm_project}` twice a day (04:00 and 13:00), loaded with `launchctl load`.
- **Linux**: a cron line `0 4,13 * * * {bm-path} reindex --project {bm_project}`.

Individual confirmation before creating either.

### 7. Update the profile block

Set `Basic Memory project: {bm_project}` in the CLAUDE.md profile block.

## NEXT STEP:

Load `steps/step-06-launch.md`.
