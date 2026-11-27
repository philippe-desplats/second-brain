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
bm --version
```

This workspace targets Basic Memory 1.0 or later. If `bm --version` reports an older release, offer `uv tool upgrade basic-memory`, and warn that the upgrade changes the MCP tool names for every project on the machine (see the 0.7.0 section of `CHANGELOG.md`).

If `uv` is missing, offer `brew install uv` first (macOS) or point to https://docs.astral.sh/uv/. Semantic search is on by default and embeddings build automatically at first startup, no warm-up step is needed. To rebuild embeddings later, run `bm reindex --embeddings`.

### 2. Apply the critical configuration, before the project exists

Order matters: `bm project add` indexes the folder immediately, so a setting applied after it comes too late for the first pass. Explain, then with confirmation run:

```bash
bm config set ensure_frontmatter_on_sync false
bm config set index_changes false
```

| Setting | Value | Why |
|---|---|---|
| `ensure_frontmatter_on_sync` | `false` | Prevents mass-stamping `title:` and `type: note` frontmatter on every file without one at first index |
| `index_changes` | `false` | Disables the live file watcher, indexing happens via explicit or scheduled `bm reindex`. Named `sync_changes` before 0.23, the old key is migrated automatically |

These settings are hard-won defaults from production use, do not skip them. `bm config list` shows the effective values.

Tell the owner what the first index will still write, because no setting prevents it since 1.0: Basic Memory adds a `permalink:` line to the frontmatter of every note that has frontmatter, folds long values and rewrites inline lists as block lists. On the demo content that is about 40 files in one pass, and a second pass changes nothing. The workspace's scripts read that grammar, so nothing breaks, but the diff is large. Suggest committing the workspace before step 4 so the rewrite lands as its own reviewable change. The `disable_permalinks` setting that used to prevent it is retired and ignored.

### 3. Exclude non-note folders from indexing

Basic Memory reads its ignore list from `~/.basic-memory/.bmignore` (gitignore syntax, GLOBAL file, not per workspace). Dotfolders like `.claude/` and `.obsidian/` are ignored by default, but `templates/` is not and would pollute the search index with placeholder text. With confirmation, append if absent:

```
templates/
AGENTS.md
CONTRIBUTING.md
CHANGELOG.md
GETTING-STARTED.md
```

**NEVER add a bare `README.md` or `CLAUDE.md` to this file**, since a bare file name matches at every depth: `CLAUDE.md` drops every `sources/{zone}/{entity}/CLAUDE.md`, meaning every client and partner context, the highest value entities in the graph, and `README.md` drops every project brief the same way.

Since 1.0 a leading slash anchors a pattern to each project root, as in gitignore: verified on 1.0.0, `/CLAUDE.md` drops only the root file and keeps the entity contexts, and `/basic-memory/README.md` drops exactly that file. Before 1.0 it did not: on 0.21.1 and 0.22.1 every pattern was matched against the file name relative to its own parent directory, so `/CLAUDE.md` silently deleted the entity graph. Check `bm --version` before relying on an anchored pattern, and remember the file is global, so `/README.md` also drops the root README of every other project on the machine.

The default stays the list above: the workspace's own documentation (`README.md`, `CLAUDE.md`, the zone READMEs) stays indexed as untyped notes. It adds a little noise to semantic search and shows up as a schema warning on a validation run. Offer anchored patterns for the root files only if the owner wants that noise gone and has no other project whose root files must stay indexed.

### 4. Create the project

Derive `{bm_project}` from the workspace folder name (kebab-case). This workspace targets local routing; Basic Memory Cloud is an optional hosted product this setup does not use. Then:

```bash
bm project add {bm_project} {absolute-workspace-path} --local
bm project list
```

The add runs the first index. Now run `bm doctor` as a smoke test, it reports problems in every project with the command that fixes each one, and runs a sandboxed write, index and search self-test:

```bash
bm doctor
```

If it fails with `Cannot delete default project 'doctor-{hex}'. This is the only project in your configuration.`, doctor's own temporary project got stuck as the default; run `bm project list` then `bm project default {bm_project}` to point the default back at the real project.

### 5. Register the MCP server

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

Tell the owner the server becomes available at the next Claude Code session start. Since 1.0 it exposes only the `bm_*` tools (`bm_search`, `bm_context`, `bm_read`, `bm_project`, ...), and every project-scoped call needs `project` set to `{bm_project}`, even though `--project` restricts the server to it.

### 6. Reindex and smoke test

```bash
bm reindex --project {bm_project}
bm tool search "charter" --project {bm_project}
```

(The query is a positional argument; there is no `--query` option. Before 1.0 the subcommand was `search-notes`.) The charter written in step-04 should come back. If the index is empty, check `bm status --project {bm_project}`.

### 7. Scheduled reindex (optional)

Offer a scheduled reindex so the index never goes stale:

- **macOS**: a LaunchAgent plist at `~/Library/LaunchAgents/com.{bm_project}.reindex.plist` running `bm reindex --project {bm_project}` twice a day (04:00 and 13:00), loaded with `launchctl load`.
- **Linux**: a cron line `0 4,13 * * * {bm-path} reindex --project {bm_project}`.
- **Windows**: two Task Scheduler entries via `schtasks /create /tn "bm-reindex-{bm_project}-am" /tr "{bm-path} reindex --project {bm_project}" /sc daily /st 04:00` (and a second task with `-pm` and `/st 13:00`). Use the full path from `where bm`.

Individual confirmation before creating any of them.

### 8. Update the config and profile block

Set `basic_memory_project` to `{bm_project}` in `.sb-config.json` (or the string `"not used"` if skipped), and mirror `Basic Memory project: {bm_project}` in the CLAUDE.md profile block.

## NEXT STEP:

Load `steps/step-06-launch.md`.
