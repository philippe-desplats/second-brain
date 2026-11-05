---
name: step-00-init
description: Check the preconditions, read the versions, fetch the upstream tags, snapshot this skill
next_step: steps/step-01-plan.md
---

# Step 0: Init

## Mandatory rules

- Write nothing in the workspace in this step. The snapshot goes to a temporary directory outside it.
- Stop at the first failed check, name it, and give the owner the command that fixes it.

## Sequence

### 1. Parse flags

```
Defaults: {target_tag} = none, {plan_only} = false
--to vX.Y.Z   → {target_tag} = vX.Y.Z
--plan        → {plan_only} = true
```

### 2. Workspace root and clean tree

Run from the workspace root, the directory that holds `.sb-config.json`.

```bash
git status --porcelain
```

If it prints anything, stop: the upgrade must be revertible with one command. Ask the owner to commit or stash first.

### 3. Current version

Read `boilerplate_version` in `.sb-config.json` into `{current_version}`. If the field is missing, stop: the workspace predates versioning, and the owner upgrades by hand with the README recipe and the CHANGELOG prompts.

`/sb-update` handles workspaces on 0.5.1 or later, the first release that shipped upgrade prompts. Below that, stop and point to the README section "Keeping your clone up to date".

### 4. Upstream remote and tags

```bash
git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
git fetch upstream --tags
```

Only the fetch URL matters, since this skill never pushes: read it with `git remote get-url upstream`. If it is not the URL above, show it and ask whether to use it. Never change it on your own.

If `git fetch` exits non-zero, show its error and stop. A fetch that prints nothing has succeeded.

List the release tags in ascending version order:

```bash
git tag -l 'v*' --sort=v:refname
```

If `{target_tag}` is unset, take the highest tag. Check each tag you rely on with one call per tag, never 2 tags in one call:

```bash
git rev-parse --verify --quiet "v0.6.2^{commit}"
```

Check `{target_tag}` and `v{current_version}` this way. The drift measure of step-01 needs the second one.

If `{target_tag}` is not above `{current_version}`, say the workspace is up to date and stop.

### 5. Snapshot this skill

The first release checked out replaces `.claude/skills/sb-update/`. Copy the skill as it is now, before anything changes. Run `mktemp -d`, then copy the folder that holds the `SKILL.md` you are running, wherever it is installed, into the directory `mktemp -d` printed. With the skill in the workspace and a printed directory of `/var/folders/xy/T/tmp.AbC123`, that is:

```bash
cp -R .claude/skills/sb-update /var/folders/xy/T/tmp.AbC123/
```

Set `{snapshot}` to the copied skill folder itself, here `/var/folders/xy/T/tmp.AbC123/sb-update`, the one that contains `SKILL.md` and `steps/`. From here on, read every step file from `{snapshot}/steps/`, and only when the step before it routes there. Never read a step ahead of time from the installed folder.

## Router

Load `{snapshot}/steps/step-01-plan.md`.

## Anti-patterns

- Adding or editing the `upstream` URL when one already exists.
- Running `git pull`, `git merge` or `git checkout` of anything here. This step only reads and fetches.
- Reading the next step from `.claude/skills/sb-update/` instead of `{snapshot}`.
