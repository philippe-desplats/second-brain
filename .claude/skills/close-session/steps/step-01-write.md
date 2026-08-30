---
name: step-01-write
description: Approval gate, write the session memory, set the continues relation
prev_step: steps/step-00-scope.md
---

# Step 1: Write

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write before showing the plan, unless `-a`
- 🛑 NEVER append to a previous session file
- ✅ ALWAYS conform to `basic-memory/schemas/session.md`
- ✅ ALWAYS write the content in the workspace working language
- 📋 YOU ARE WRITING ONE FILE, nothing else

## EXECUTION SEQUENCE:

### 1. Build the path

```
{project_path}/sessions/YYYY-MM-DD-session-{slug}.md
```

Date is today. `{slug}` is kebab-case and names the session's subject, not its nature: `content-inventory`, not `work-session`. Create `sessions/` if it does not exist.

If that exact filename is already taken, a second session ran today on the same subject: suffix with `-02`, `-03`. Do not overwrite, and do not merge into the existing file.

### 2. Build the frontmatter

Follow `basic-memory/schemas/session.md`. `type: session` and `schema_version: 1` are mandatory; without `type`, Basic Memory cannot resolve the schema and the memory becomes unretrievable, which defeats the whole point.

```yaml
---
date: {today}
title: {one line naming what the session was about}
type: session
schema_version: 1
status: {open|closed}
category: {internal|client|partner|personal}
duration: {optional}
client: {if client-scoped}
partner: {if partnership-scoped}
tags: [{free keywords}]
about: {project title}
written_by: agent
---
```

### 3. Build the body

```markdown
# Session, {title}

{Two to five lines of prose: what this session was for, and where it actually landed. Prose carries the nuance the buckets cannot.}

## Observations
- [done] ...
- [next] ...
- [blocker] ...
- [decision] ...
- [open-question] ...

## Relations
- about [[{Project}]]
- continues [[{previous session title}]]
- client [[{Client}]] or partner [[{Partner}]]
```

Omit an empty bucket rather than writing an empty bullet. Omit `continues` on a first session.

### 4. Approval gate

Show the full path and the complete file content, then wait. Skip only under `-a`.

Corrections here cost one edit; corrections after the next session has built on a wrong memory cost the thread.

### 5. Write and confirm

Write the file, print the path, and state in one line what the next session should pick up first. That line is the whole return on the exercise.

### 6. Reindex

If Basic Memory is installed, `bm reindex --project {project}` so the memory is retrievable immediately rather than at the next session start (there is no `bm sync` command; `reindex` is the verb). If it is absent, skip silently: the file on disk is already the durable artifact.

## NEXT STEP:

None, the skill ends here.

<critical>
The memory is written for a reader who has forgotten everything, including the obvious. Name entities in full, spell out the acronyms the session invented, and never write "as discussed above": there is no above.
</critical>
