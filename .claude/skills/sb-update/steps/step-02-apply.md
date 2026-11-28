---
name: step-02-apply
description: Run each release's upgrade prompt in order, with its own gates, and a commit gate between releases
prev_step: steps/step-01-plan.md
next_step: steps/step-03-report.md
---

# Step 2: Apply

## Mandatory rules

- One release at a time, ascending. Finish a release, including its verification phase and the commit gate, before reading the next prompt.
- Follow the prompt literally. Its rules (never delete a note, diff before any write into a data zone, stop on an unmet precondition) are your rules for that release.
- Every "wait for my approval" in a prompt is a question to the owner (see AGENTS.md, Asking the owner), carrying the exact diff or list it asks you to show. Never approve on the owner's behalf.
- The prompt speaks as the owner ("my workspace", "tell me"). Read "me" as the owner you are talking to.

## Sequence

For each release `X.Y.Z` in `{releases}`:

### 1. Extract the prompt

From `git show {prompt_source}:CHANGELOG.md`, take the fenced block under the heading picked for this release in step-01. Show the owner the heading you are about to run, then run it.

For a `manual` release, do what its section says, usually setting `boilerplate_version` to `X.Y.Z` in `.sb-config.json`, and show the diff before writing.

### 2. Run it

Work through its phases in order. Where it names a tag, use the tags you fetched in step-00. Where it says stop, stop the whole run, record the reason in `{outcomes}`, and go to the report.

If a command of the prompt fails, show the exact error and ask the owner how to proceed. Do not rewrite the command into something that runs.

Anything that installs or downloads outside the workspace is a gate of its own, even when the prompt offers it. A prompt may suggest `uvx --with pyyaml` to get PyYAML: ask the owner before running it, and accept the documented gap when they decline.

Instruction files and infrastructure paths. A release may check out `AGENTS.md`, `.claude`, `.agents`, `.codex`, `.gemini`, `.qwen`, `.kiro`, `.githooks` and `.aider.conf.yml`. Treat them as follows, whatever the prompt does not spell out:

- `AGENTS.md` carries the owner's profile block between `<!-- sb-init:profile -->` and `<!-- /sb-init:profile -->`. Never overwrite it blindly: show the diff, keep the owner's block as it is, and take only the changes outside the markers.
- A workspace upgraded from before 0.8.0 has a root `CLAUDE.md` holding that profile block, and entity contexts named `CLAUDE.md`. The prompt moves them to `AGENTS.md`. Never restore a `CLAUDE.md` afterwards, and never leave one next to its `AGENTS.md`: Claude Code stops loading the `AGENTS.md` of any folder at or below a `CLAUDE.md`.
- `.agents/skills` and `.kiro/skills` are symlinks to `../.claude/skills`. Symlink preferred. A real folder whose `SKILL.md` files are identical to `.claude/skills` is tolerated with a warning (Windows without symlink support), and a drifted copy, a text file or a missing path is a defect to report. The repair is `ln -s ../.claude/skills .agents/skills` (and the same for `.kiro/skills`), run only with the owner's approval. When git cannot create the symlinks on this machine, keep the index entries with `git update-index --skip-worktree .agents/skills .kiro/skills` and never stage a copied folder in the commit gate: check `git status --short` for regular files under those 2 paths before the commit and leave them out.
- A release prompt runs under the copy of this skill already installed (the snapshot of step-00), not under the version the release ships. A prompt therefore carries its own rules for anything this skill does not know yet, and this skill never assumes a rule a later release added.
- `.githooks` is inert until `git config core.hooksPath .githooks` is set. Never set it without asking, it is the owner's choice and local to the clone.

If the stock prompt tells you the workspace is customized and sends you to the other prompt, switch to the customized prompt of the same release and say so.

### 3. Verify

The prompt ends with its own verification phase. Its pass criteria are the only ones: a check it runs without stating a criterion is reported as it printed, never turned into a failure or a success by you. Keep for the report the test suite summary, the result of each check, the `check_frontmatter_damage.py` count, and any hit the owner chose to leave.

Then confirm `boilerplate_version` now reads `X.Y.Z`, and set `{current_version}` = `X.Y.Z`.

### 4. Commit gate

Reach this gate only once the prompt is finished, its last phase included, since that phase usually sets `boilerplate_version`. The next release needs a clean tree. Show `git status --short`, then ask the owner (see AGENTS.md, Asking the owner):

- commit now with the message `chore: upgrade workspace to X.Y.Z`, which you run only on that answer, staging first with `git add -u` plus every new path of the release named explicitly, since a checkout leaves some files staged and others not. Never `git add -A`: on a clone without symlink support, `.agents/skills` and `.kiro/skills` may be local copies that must never be committed
- they commit themselves, and you wait until `git status --porcelain` is empty
- stop here, the tree stays as it is

Record the release in `{outcomes}`: done or stopped, hits left, commit sha if any.

### 5. Before the next release

If the run is customized, it stays customized. If it is stock, measure the drift again as step-01 describes, against `v{current_version}`, the tag of the version just reached. Then continue with the next release.

## Router

When every release is done, or the run stopped, load `{snapshot}/steps/step-03-report.md`.

## Anti-patterns

- Running 2 releases' prompts back to back without the commit gate between them.
- Skipping a gate because the diff "looks safe".
- Fixing a failing prompt command on your own. A failing command is a defect of the release, and the owner decides.
- Pushing anything.
