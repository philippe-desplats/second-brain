---
name: close-session
description: Close a working session by writing its memory. Captures what was actually done, what comes next, what is blocking, and what was decided, then files it as a session note in the project so the next session resumes from a point instead of a search. Triggers on "close the session", "checkpoint the session", "save where we are", "write the session memory", "handoff before I stop".
argument-hint: "[-p <project>] [-c closed] [-a auto] [free-text note to add]"
---

<objective>
The end of the daily loop, symmetric with `/ops-init-project` which opens it. A session is only worth resuming if someone wrote down where it stopped; this skill writes that down, in the project it belongs to, typed as `session` so Basic Memory can retrieve it.

It records the session, it does not summarize a document (that is `/ops-resume`) and it does not file inbound content (that is `/capture`).
</objective>

<quick_start>

```
/close-session                          # resolve the project from the session, write the memory
/close-session -p globex/website-redesign   # skip project detection
/close-session -c                       # nothing is left, close the thread
/close-session -a                       # skip the confirmation gate
/close-session the migration script is half written, see the scratch file
```

</quick_start>

<flags>

| Flag | Description |
|------|-------------|
| `-p <project>` | Target project as `{entity}/{project}` or `{project}`, skips detection |
| `-c` | Mark the thread `closed`: the work is finished, nothing is waiting |
| `-a` | Skip the confirmation gate and write directly |

**Remainder** after flags: free text the owner wants in the memory, added to what the session itself shows.
</flags>

<workflow>
1. **Scope** -> Resolve the project, read the previous session, collect the session state
2. **Write** -> Show the memory for approval, write it, link it to the previous one
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-scope.md` | Resolve the project, find the previous session, gather done/next/blocker/decision |
| 01 | `steps/step-01-write.md` | Approval gate, write the file, set the `continues` relation |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{project_path}` | string | step-00 (`sources/{zone}/{entity}/{project}`) |
| `{zone}` | string | step-00 |
| `{entity}` | string | step-00 (empty for entity-less zones) |
| `{previous_session}` | string | step-00 (title of the last session in the project, empty if none) |
| `{state}` | object | step-00 (done, next, blocker, decision, open-question lists) |
| `{status}` | enum (`open\|closed`) | step-00 |
| `{extra_note}` | string | step-00 (free text passed after the flags) |
| `{auto_mode}` | boolean | step-00 |

</state_variables>

<execution_rules>
- **Never invent.** What did not happen in the session does not go in the memory. An honest three-line memory beats a plausible twenty-line one, and a fabricated `[done]` is worse than no memory at all: the next session builds on it.
- **`[done]` means done and verified**, not attempted, not nearly finished. Work in flight is a `[next]` with its actual state.
- **A memory with no `[next]` and no `-c` is a defect.** Either something remains, and it goes in `[next]`, or the thread is closed and the status says so. Ask rather than guess.
- **The first `[next]` is the resumption point.** Write it so the next session can act on it without re-reading anything: "run the migration on staging" beats "continue the migration".
- **One session, one file.** Never append to a previous session's file; the `continues` relation is what chains them.
- **A blocker names what would unblock it.** "Waiting on Jane" is a status; "waiting on Jane for the analytics access, asked on 06-23" is a blocker someone can act on.
- **No secrets, no tokens, no credentials** in the memory, ever. Reference where they live instead.
- **Never mention automated assistance** in the written content (see `.claude/rules/communication.md`).
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-scope.md`
</entry_point>
