---
name: step-00-scope
description: Resolve the project, find the previous session, gather the session state
next_step: steps/step-01-write.md
---

# Step 0: Scope

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write anything to disk in this step
- 🛑 NEVER invent state the session did not produce
- ✅ ALWAYS show the scope card before proceeding
- 📋 YOU ARE READING THE SESSION, not narrating it
- 💬 FOCUS on: what got done, what is next, what is stuck

## EXECUTION SEQUENCE:

### 1. Parse the flags

`-p <project>`, `-c`, `-a`. Everything after the flags is `{extra_note}`.

### 2. Resolve the project

If `-p` is set, resolve it and verify the directory exists. `{entity}/{project}` and a bare `{project}` are both accepted; a bare slug is searched across the zones present in `.sb-config.json`. Otherwise:

1. Look at what the session actually touched: files read or written, entity names, project vocabulary.
2. One dominant project -> propose it.
3. Several -> AskUserQuestion listing them, most-touched first.
4. **None** -> say so plainly and offer two options: attach the memory to a project the owner names, or write nothing. Do not invent a project folder to have somewhere to write; a session about nothing in particular does not need a memory.

Set `{project_path}`, `{zone}`, `{entity}`.

### 3. Find the previous session

```bash
ls -1 {project_path}/sessions/ 2>/dev/null | sort | tail -1
```

If a file exists, read it: its `[next]` items are the checklist this session was supposed to advance, and its title becomes `{previous_session}` for the `continues` relation. If the folder does not exist, this is the first session on the project.

### 4. Gather the state

Read back the session and sort what happened into five buckets. Nothing goes in a bucket because it would look good there.

| Bucket | What qualifies | What does not |
|---|---|---|
| `[done]` | completed and verified | attempted, started, "should work" |
| `[next]` | the next concrete action | a vague intention |
| `[blocker]` | what stops progress, plus what would release it | a status with no lever |
| `[decision]` | an arbitration made, with what it rules out | an option that was merely discussed |
| `[open-question]` | asked and unanswered | answered during the session |

**`[blocker]` and `[open-question]` overlap constantly**, because most blockers are questions. Sort by consequence, not by grammar: if the answer is what unlocks the next step, it is a `[blocker]`; if the work continues either way, it is an `[open-question]`. Never write the same item twice.

**When you cannot tell whether a carried item is still live, carry it.** Losing a real next step costs a thread; carrying a dead one costs a line someone deletes in two seconds.

Cross-check against the previous session's `[next]` items: each one is either done (goes to `[done]`), still pending (carried into `[next]`), or dropped (say so, ideally as a `[decision]`). A carried item that silently disappears is how a thread rots.

Two things the carry-over must not do. **It must not resurrect a dead deadline**: when a carried item names a date that has passed, carry the item and say the date lapsed, rather than reprinting it as if it still held. And **it must not turn into an archive**: a project where several threads alternate accumulates `[next]` items the work has moved past, so drop those with a one-line reason instead of relisting them at every checkpoint. An item untouched because the session was about something else is still live and gets carried; an item nobody intends to do is dropped, out loud.

Append `{extra_note}` to the relevant bucket, or to the prose if it fits none.

### 5. Decide the status

`closed` if `-c` was passed, or if there is genuinely nothing left. Otherwise `open`, which requires at least one `[next]`. If the state has no `[next]` and `-c` was not passed, ask; do not silently close a live thread.

### 6. Show the scope card

```
┌─ Checkpoint ────────────────────────────────────────┐
│ project    {entity}/{project} ({zone})              │
│ previous   {previous_session or "first session"}    │
│ status     {status}                                 │
│ state      {n} done, {n} next, {n} blocked          │
└─────────────────────────────────────────────────────┘
```

## NEXT STEP:

Load `steps/step-01-write.md`.

<critical>
A memory that flatters the session is worse than none: the next session trusts it, builds on it, and discovers the gap at the worst moment. Write what happened.
</critical>
