---
name: step-00-init
description: Parse args, resolve source_path and target_path
next_step: steps/step-01-confirm.md
---

# Step 0, Initialize Archive

## MANDATORY EXECUTION RULES:

- 🛑 NEVER assume the type without a filesystem check
- ✅ ALWAYS verify that `{source_path}` physically exists
- 🚫 FORBIDDEN to archive `.claude/`, `basic-memory/`, `atlas/`, `knowledge/`, `inbox/`

## EXECUTION SEQUENCE:

### 1. Parse arguments

- **First positional argument**: `{slug}` or `{slug}/{project}`
  - If it contains `/`, set `{is_project_scope}` = true and split (`{slug}`, `{project}`)
- **Flag `-t`**: `{type}` in `{client, partner, internal, personal}`
- **Flag `--dry-run`**: `{dry_run}` = true
- **Flag `-a`**: `{auto_mode}` = true
- **Flag `-f`**: `{force_mode}` = true

### 2. Auto-deduce the type if missing

Test existence in order of likelihood:

```bash
test -d sources/clients/{slug} && type=client
test -d sources/partners/{slug} && type=partner
test -d sources/internal/{slug} && type=internal
test -d sources/personal/{slug} && type=personal
```

**If multiple matches** (the slug exists in several types):
- Ask the user via AskUserQuestion
- List all candidate paths

**If no match**:
- Fail with the message "No project/entity found for `{slug}`. Check the slug."

### 3. Resolve the paths

**If `{is_project_scope}` = false** (archive the whole entity):

```
{source_path} = sources/{type-folder}/{slug}/
{target_path} = archives/{type-folder}/{slug}/
```

With `{type-folder}` = `clients` if client, `partners` if partner, `internal` if internal, `personal` if personal.

**If `{is_project_scope}` = true** (archive only one project of an entity):

```
{source_path} = sources/{type-folder}/{slug}/{project}/
{target_path} = archives/{type-folder}/{slug}/{project}/
```

### 4. Checks

- `{source_path}` exists: `test -d {source_path}`. Otherwise, fail.
- `{source_path}` is not a protected zone:
  - Refuse if it starts with `.claude/`, `basic-memory/`, `atlas/`, `knowledge/`, `inbox/`, `templates/`
- `{target_path}` does not already exist:
  - If it does, ask via AskUserQuestion: merge, overwrite (delete + move), abandon
  - Do NOT offer to overwrite silently in `--auto` mode

### 5. Present the plan

```
Planned archive:
- Source: {source_path}
- Target: {target_path}
- Mode: {dry-run | actual}
- Type: {type}
- Scope: {full entity | project only}
```

Ask for confirmation via AskUserQuestion (except in `{auto_mode}` = true), move to step-01 for the pre-action audit.

---

## SUCCESS METRICS:

✅ `{source_path}` validated (exists + not a protected zone)
✅ `{target_path}` validated (does not exist or conflict resolved)
✅ `{type}` resolved
✅ User confirmed the plan (except auto)

## FAILURE MODES:

❌ Protected zone -> refusal
❌ Nonexistent source -> failure
❌ Existing target without resolution -> block

---

## NEXT STEP:

Load `./step-01-confirm.md`
