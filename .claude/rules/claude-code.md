# Claude Code specifics

The workspace instructions live in `AGENTS.md` at the root, which Claude Code reads natively. Use 2.1.281 or later: before it, sessions on Bedrock, Vertex, Foundry or with telemetry disabled read `CLAUDE.md` only, and the first session after upgrading from 2.1.276 or earlier may skip `AGENTS.md`. Run `/memory` to confirm `AGENTS.md` is listed. This file holds only what is specific to Claude Code. It loads automatically with the other `.claude/rules/*.md` files.

- **NEVER** create a `CLAUDE.md` anywhere in this workspace, at the root or in any folder.
  - A `CLAUDE.md` in a folder or above it makes Claude Code skip that folder's `AGENTS.md`. Measured on 2.1.332: with a root `CLAUDE.md`, even one reduced to `@AGENTS.md`, an entity's `AGENTS.md` context was not loaded when a file in its folder was read.
  - Put Claude-only guidance in this file instead, and workspace guidance in `AGENTS.md`.
  - Example: a new client context is `sources/clients/acme/AGENTS.md`, never `sources/clients/acme/CLAUDE.md`.

- **ALWAYS** use `AskUserQuestion` when `AGENTS.md`, section "Asking the owner", or a skill asks the owner to choose.
  - It is Claude Code's structured question tool, and the question blocks in the skills are written for its shape (header, 2 to 4 options, recommendation first).
  - Example: a skill's YAML question block becomes one `AskUserQuestion` call with the same header and options.

- **ALWAYS** invoke a skill through the Skill tool or its `/name` command when a skill tells you to run another one.
  - Example: `/curate` delegating a distillation calls the `distill` skill, it never redoes the work inline.

- The `librarian` subagent in `.claude/agents/librarian.md` preloads the `librarian` skill, which carries the curation role for every harness.
- The `PostToolUse` hook in `.claude/settings.json` reruns the title alias pass after every Write or Edit in the note zones. Other harnesses wire the same script, see `docs/harnesses.md`.
