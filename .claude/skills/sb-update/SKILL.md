---
name: sb-update
description: Upgrade this second brain to a newer boilerplate release, one release at a time, running the upgrade prompt each CHANGELOG section ships with every approval gate kept. Use for "sb-update", "update my second brain", "upgrade the workspace". Not for first-time setup, use /sb-init.
---

<objective>
Bring a cloned workspace from its `boilerplate_version` to a newer release without copy-pasting prompts by hand. The skill finds every release between the two, reads the upgrade prompt each one ships in `CHANGELOG.md`, picks the stock or the customized variant, and runs it release by release with the owner approving every write into a data zone. The upgrade prompts stay the single source of truth: this skill orchestrates them and never re-implements what they do.
</objective>

<quick_start>

```
/sb-update                 # upgrade to the latest release, one release at a time
/sb-update --to v0.6.3     # stop at a given release
/sb-update --plan          # show the plan (releases, prompt variant per release) and stop
```

</quick_start>

<flags>

| Flag | Effect |
|------|--------|
| `--to vX.Y.Z` | Target release instead of the latest tag |
| `--plan` | Plan only: print the releases and the prompt picked for each, write nothing |

</flags>

<workflow>
1. **Init** → Preconditions: workspace root, clean git tree, current version, upstream remote and tags, a snapshot of this skill
2. **Plan** → Releases to walk, prompt source, stock or customized per release, owner approval of the plan
3. **Apply** → For each release in order: extract its prompt, follow it with its own gates, verify, record the commit
4. **Report** → Versions moved, per-release outcome, damage hits left on purpose, what only the owner can verify
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Preconditions, versions, upstream, skill snapshot |
| 01 | `steps/step-01-plan.md` | Release list, prompt variant per release, plan approval |
| 02 | `steps/step-02-apply.md` | Run each release's prompt in order, commit gate between releases |
| 03 | `steps/step-03-report.md` | Final summary and what remains to verify by hand |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{current_version}` | string | step-00 (`boilerplate_version` of `.sb-config.json`, updated by step-02 after each release) |
| `{target_tag}` | string | step-00 (`--to`, or the highest release tag) |
| `{plan_only}` | boolean | step-00 |
| `{snapshot}` | path | step-00 (copy of this skill, the only place later steps are read from) |
| `{releases}` | list | step-01 (tags strictly above `{current_version}` up to `{target_tag}`, ascending) |
| `{prompt_source}` | string | step-01 (always `{target_tag}`: its CHANGELOG holds every prompt corrected in place) |
| `{variant}` | map | step-01 (release to `stock` or `customized`) |
| `{outcomes}` | list | step-02 (per release: done, stopped, hits left, commit sha) |

</state_variables>

<execution_rules>
- **Read the steps from `{snapshot}` once step-00 has made it, never from `.claude/skills/sb-update/`.** Each release checks out `.claude`, which replaces this skill mid-run, and a step read after that would come from another version.
- **The upgrade prompts are the authority.** Follow each one literally, phase by phase. When this skill and a prompt disagree, the prompt wins and you say so in the report.
- **Every gate of a prompt is a gate with the owner.** "Show me the diff and wait for my approval" means AskUserQuestion with the diff, never an assumed yes. Never batch the approvals of 2 shapes or 2 intents.
- **One release at a time, in ascending order.** Never jump to the latest prompt from an older version, each prompt states the versions it accepts.
- **Never commit, push, or delete a note on your own.** Between 2 releases the next prompt needs a clean tree: ask the owner to commit, or commit with their explicit approval of the message, then continue.
- **Never write upstream.** Fetch only. If `upstream` points at a URL you did not expect, stop and ask.
- **Stop on any failed precondition** and say which one, rather than improvising around it.
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`.
</entry_point>
