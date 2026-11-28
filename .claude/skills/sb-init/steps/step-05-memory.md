---
name: step-05-memory
description: Harness selection, then optional Basic Memory installation and MCP wiring
prev_step: steps/step-04-personalize.md
next_step: steps/step-06-launch.md
---

# Step 5: Harnesses and Basic Memory (Basic Memory optional, recommended)

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER modify `~/.basic-memory/config.json` or register MCP servers without an explicit, individual confirmation
- 🛑 NEVER store secrets or machine paths in any tracked file; every MCP config that holds the `bm` path stays gitignored (`.mcp.json` is by design, check each other harness file against `.gitignore` before writing it)
- ✅ ALWAYS offer the skip path; the workspace works without Basic Memory (skills fall back to file scans)
- ✅ ALWAYS explain what each system-level change does before asking

## HARNESSES (always asked, even when Basic Memory is skipped)

The workspace is harness-neutral: `AGENTS.md` and the skills in `.claude/skills/` (mirrored at `.agents/skills/`) work in Claude Code, Codex, Gemini CLI, Copilot, Cursor, OpenCode, Windsurf and others. Ask the owner (see AGENTS.md, Asking the owner) which harnesses they use. A question holds at most 4 options, so ask in 4 rounds, each multi-select, each skippable with "none of these", and recommend the harness they are running right now:

1. Claude Code (2.1.281 or later, earlier releases may ignore `AGENTS.md`, confirm with `/memory`), Codex, Gemini CLI, Copilot
2. Cursor, OpenCode, Windsurf, Qwen Code
3. Cline, Roo Code, Kiro, Zed
4. Amp, Goose, Junie, other (free text)

These cover every harness `docs/harnesses.md` documents an MCP config for. Store the answer as `{harnesses}`, a list of lowercase slugs (`claude-code`, `codex`, `gemini-cli`, `copilot`, `cursor`, `opencode`, `windsurf`, `qwen-code`, `cline`, `roo-code`, `kiro`, `zed`, `amp`, `goose`, `junie`, `other`), and write it to `.sb-config.json` as the array `harnesses` (an empty array if they pick none). For `other`, point at `docs/harnesses.md` and `AGENTS.md`, which any tool reading the AGENTS.md standard follows.

If the owner has Basic Memory (see below), section 5 wires each selected harness to it.

Also offer, with a confirmation of its own, the pre-commit safety net: `git config core.hooksPath .githooks`. It runs `basic-memory/scripts/add_title_aliases.py --check` before each commit and refuses a commit that would leave a wiki-link title without its alias. The setting is local to this clone, so say that it has to be repeated on another machine. Skip silently if `.githooks/pre-commit` does not exist.

## PITCH (one paragraph, then ask)

Basic Memory adds semantic search and a knowledge graph over the markdown files: the agent can find notes by meaning ("what did we decide about hosting pricing?") instead of exact words, and follow relations between entities. It runs fully locally (SQLite + local embeddings). Ask: set it up now, or skip? Store `{bm_enabled}`.

**If skipped:** note in the AGENTS.md profile block `Basic Memory project: not used`, set `basic_memory_project` to `"not used"` in `.sb-config.json`, and proceed to step-06.

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

Tell the owner what the first index will still write, because no setting prevents it since 1.0: Basic Memory adds a `permalink:` line to the frontmatter of every note that has frontmatter, folds long values and rewrites inline lists as block lists. On the demo content that is about 40 files in one pass, and a second pass changes nothing. The workspace's scripts read that grammar, so nothing breaks, but the diff is large. Suggest committing the workspace before section 4 (Create the project) so the rewrite lands as its own reviewable change. The `disable_permalinks` setting that used to prevent it is retired and ignored.

### 3. Exclude non-note folders from indexing

Basic Memory reads its ignore list from `$BASIC_MEMORY_CONFIG_DIR/.bmignore` when that variable is set, otherwise from `~/.basic-memory/.bmignore` (gitignore syntax, GLOBAL file, not per workspace). Dotfolders like `.claude/` and `.obsidian/` are ignored by default, but `templates/` is not and would pollute the search index with placeholder text. With confirmation, append if absent:

```
templates/
/AGENTS.md
CONTRIBUTING.md
CHANGELOG.md
GETTING-STARTED.md
```

**Locate and clean the file first.** Decide on the file's existence (`test -f`), never on `command -v bm`: `bm` is often installed by `uv` outside the agent shell PATH, so a missing command says nothing about the file. If the file exists, look for a line that is exactly `AGENTS.md` or `CLAUDE.md`. A 0.7.0 setup wrote a bare `AGENTS.md`, which now matches every entity context and drops them all from the index. On a rerun (`/sb-init -r`) and on a first run alike, show the lines found and, with confirmation, delete them. Then, on Basic Memory 1.0 or later, keep or add `/AGENTS.md`. Below 1.0, add nothing for the root file.

**NEVER add a bare `README.md` or `AGENTS.md` to this file**, since a bare file name matches at every depth: `AGENTS.md` drops every `sources/{zone}/{entity}/AGENTS.md`, meaning every client and partner context, the highest value entities in the graph, and `README.md` drops every project brief the same way. This is why the entry above is `/AGENTS.md`, anchored to the project root, and not the bare name an earlier release listed: entity contexts are now `AGENTS.md` files, so the bare name would remove all of them from the index.

Since 1.0 a leading slash anchors a pattern to each project root, as in gitignore: verified on 1.0.0, `/AGENTS.md` drops only the root file and keeps the entity contexts, and `/basic-memory/README.md` drops exactly that file. Before 1.0 it did not: on 0.21.1 and 0.22.1 every pattern was matched against the file name relative to its own parent directory, so an anchored pattern silently deleted the entity graph. That is why 1.0 is the floor of this setup. Check `bm --version` before relying on an anchored pattern, and remember the file is global, so `/AGENTS.md` also drops the root `AGENTS.md` of every other project on the machine, and `/README.md` the root README.

The rest of the list stays as is: the workspace's own documentation (`README.md`, the zone READMEs) stays indexed as untyped notes. It adds a little noise to semantic search and shows up as a schema warning on a validation run. Offer an anchored `/README.md` only if the owner wants that noise gone and has no other project whose root README must stay indexed.

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

### 5. Register the MCP server, per harness

For each harness in `{harnesses}`, write its Basic Memory MCP config following `docs/harnesses.md` (the section of that harness gives the file, the format and the key names). Explain the file and its content first, then ask for an individual confirmation per harness, never one confirmation for all of them. Before writing, check that the file is not tracked and that a file holding the real `bm` path is covered by `.gitignore`, and add the entry if it is not.

For Claude Code, copy `.mcp.json.example` to `.mcp.json` and fill in the real values:

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

Zed, Goose and Junie keep their MCP config at user level only: offer the user-level file from `docs/harnesses.md`, never a tracked project file. Any other harness whose config lives outside the workspace follows the same rule as the Basic Memory config: hand over the exact command or snippet and write it only on explicit confirmation. Skip `other`, and tell the owner that `docs/harnesses.md` lists what to register by hand.

Tell the owner the server becomes available at the next session start of each harness. Since 1.0 it exposes only the `bm_*` tools (`bm_search`, `bm_context`, `bm_read`, `bm_project`, ...), and every project-scoped call needs `project` set to `{bm_project}`, even though `--project` restricts the server to it.

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

Set `basic_memory_project` to `{bm_project}` in `.sb-config.json` (or the string `"not used"` if skipped), and mirror `Basic Memory project: {bm_project}` in the AGENTS.md profile block. `harnesses` was already written at the start of this step.

## NEXT STEP:

Load `steps/step-06-launch.md`.
