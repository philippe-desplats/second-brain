---
name: step-03-report
description: Summarize the run and list what only the owner can verify
prev_step: steps/step-02-apply.md
---

# Step 3: Report

## Mandatory rules

- Report what happened, not what the prompts promised. A release that stopped is reported as stopped, with the reason.
- Write nothing in this step.

## Sequence

### 1. Summary

In the owner's language:

- the move: from the version read in step-00 to `{current_version}`, and whether `{target_tag}` was reached
- per release from `{outcomes}`: done or stopped, the prompt variant, commit sha or "not committed"
- the damage hits the owner chose to leave, file and shape, so they can come back to them
- any point where a prompt and this skill disagreed, and which one you followed

### 2. What no command verifies

Repeat the closing caveats the prompts gave, without adding new ones. Typically: clicking a wiki-link in Obsidian proves Alias Linker resolves it, and `bm reindex` is the owner's to run when Basic Memory is configured.

### 3. Clean up

Give the path of `{snapshot}`, the temporary copy of this skill made in step-00. It sits outside the workspace and the system removes it on its own.

## Anti-patterns

- Declaring the workspace up to date when a release stopped half way.
- Restating every phase of every prompt. The summary is per release, one line each.
