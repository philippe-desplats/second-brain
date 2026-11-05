---
name: step-01-plan
description: List the releases to walk, pick the stock or customized prompt for each, get the plan approved
prev_step: steps/step-00-init.md
next_step: steps/step-02-apply.md
---

# Step 1: Plan

## Mandatory rules

- Write nothing in the workspace in this step.
- The plan is approved by the owner before step-02 starts, even when it holds a single release.

## Sequence

### 1. Releases to walk

`{releases}` = every tag from step-00 strictly above `v{current_version}` and up to `{target_tag}`, ascending. A release that changed no infrastructure (its CHANGELOG says so) stays in the list: its prompt still moves `boilerplate_version`.

### 2. Prompt source

Read every prompt from the CHANGELOG of `{target_tag}`, never from the tag of the release itself:

```bash
git show {target_tag}:CHANGELOG.md
```

Releases sometimes correct an older prompt in place, and only the newest CHANGELOG carries the corrected text. Set `{prompt_source}` = `{target_tag}`.

For each release `X.Y.Z` in `{releases}`, find its section `## X.Y.Z` and, inside it, the 2 prompt headings. Match each heading as a whole line, never as a prefix, because the stock heading is a prefix of the customized one:

- stock: a line that starts with `### Upgrade prompt, ` and ends with ` to X.Y.Z`
- customized: the same line followed by `, for a customized workspace`

Each prompt is the first fenced block under its heading. If a release has no such heading, its section says what to do instead (often only a version bump): note it as `manual` and show that text in the plan.

### 3. Stock or customized

A workspace is customized when either is true:

- `.sb-config.json` says `"initialized": true`. `/sb-init` personalizes schemas, rules and templates, so an initialized workspace always differs from upstream.
- The infrastructure differs from the release it came from:

```bash
git diff --stat v{current_version}..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
```

Only those 4 paths count. Commits that touch notes only, after the tag, change nothing.

Once a release runs customized, every later release of the run is customized too, since a fork stays a fork. A workspace that starts stock is measured again before each later release in step-02, against the tag of the version it has just reached, and stays stock only while that diff is empty.

### 4. Present the plan

If `{plan_only}` is true, show the plan below and stop there, without asking anything.

Otherwise show, in one message:

- the move, `{current_version}` to `{target_tag}`, and the number of releases
- per release: its version, the prompt picked (stock, customized, or manual), and the one-line intro of its CHANGELOG section
- that every write into a data zone will be shown as a diff first, and that the owner commits between releases

Then ask with AskUserQuestion: proceed, or stop here. This one approval covers the plan only. Each prompt keeps its own gates, one per intent or per damage shape, asked in step-02.

## Router

Load `{snapshot}/steps/step-02-apply.md`.

## Anti-patterns

- Reading a release's prompt from its own tag, which misses the corrections later releases made in place.
- Picking the stock prompt for an initialized workspace because the drift diff of a single folder looked empty.
- Paraphrasing a prompt in the plan instead of naming it.
