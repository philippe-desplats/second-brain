---
name: step-06-launch
description: Smoke test the wedge flow, set the maintenance ritual, hand over
prev_step: steps/step-05-memory.md
next_step: null
---

# Step 6: Launch

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER end the session with an empty workspace; the first real note gets filed NOW
- ✅ ALWAYS exercise the wedge flow from the charter, not a generic demo
- ✅ ALWAYS leave the owner with exactly one ritual, not a list of ten habits
- 📋 YOU ARE A COACH handing over the keys

## EXECUTION SEQUENCE:

### 1. File the first real note (the wedge flow)

Take the `{charter}` wedge flow and do it for real, right now:

- **Emails**: "Paste the last important email you sent or received." File it at the right path with the right name (`YYYY-MM-DD-01-{direction}-slug.md`) and full frontmatter. Create the entity folder and its `CLAUDE.md` from `templates/entity-CLAUDE-template.md` on the way if needed.
- **Meeting notes**: "Give me your latest meeting notes, even rough ones." Same treatment via `meetings/`.
- **Client context**: "Name your most important client." Create `sources/clients/{client}/CLAUDE.md` from the template, interviewing for the communication preferences.
- **Reusable knowledge**: "What is the thing you re-explain most often?" Draft it as the first `knowledge/` note, with a provenance line.

In quick mode, or if the owner has nothing at hand or is away: do NOT fabricate an entity or invent preferences. Point at the demo content as the working model (if it was kept) and record "create your first real entity context" as the top next step in the final summary. A fabricated client would poison the workspace's trust from day one.

### 2. Show what just happened

Point at the created file(s): the path (predictable), the frontmatter (typed), the wiki-links (relations). One minute, no lecture. If Basic Memory is enabled, run one search that finds the new note.

### 3. Set the maintenance ritual

Explain the single ritual:

> "Once a week, run `/curate -w 7`. It scans what accumulated, and proposes what to distill into knowledge, what to archive, what deserves a map. You approve or reject each suggestion. That is the whole discipline; everything else follows from it."

Ask which day suits them, set `curation_ritual` in `.sb-config.json` (e.g. `"friday, /curate -w 7"`), and mirror a line in the CLAUDE.md profile block: `Curation ritual: {day}, /curate -w 7`.

Then offer to automate the REMINDER (optional, individual confirmation, same pattern as the Basic Memory reindex in step 5). The scheduled job never runs the assistant: it executes `basic-memory/scripts/curation_reminder.py`, which drops a reminder note in `inbox/` and fires an OS notification. The owner then opens Claude Code and runs `/curate -w 7` themselves (`-r` if they just want the report file first).

```bash
python3 {workspace-path}/basic-memory/scripts/curation_reminder.py
```

- **macOS**: LaunchAgent `~/Library/LaunchAgents/com.{workspace-slug}.curate-reminder.plist` running the command above weekly on {day} at 09:00.
- **Linux**: cron line `0 9 * * {day-number} python3 {workspace-path}/basic-memory/scripts/curation_reminder.py`.
- **Windows**: `schtasks /create /tn "curate-reminder-{workspace-slug}" /tr "python {workspace-path}\basic-memory\scripts\curation_reminder.py" /sc weekly /d {DAY} /st 09:00`.

Use the full python path from `which python3` (or `where python`) so the job survives PATH differences in scheduled contexts.

### 4. Suggest the first commit

Recommend committing the initialized state (do not run it without approval):

```bash
git add -A && git commit -m "chore: initialize second brain workspace"
```

### 5. Final summary

```
✅ Your second brain is ready.

| Setting | Value |
|---|---|
| Profile | {profile} ({zones}) |
| Working language | {working_language} |
| Charter | sources/internal/second-brain-charter.md |
| Business context | sources/internal/CONTEXT.md |
| First note | {path of the note filed in 1} |
| Basic Memory | {bm_project or "not used"} |
| Ritual | {day}: /curate -w 7 |

Where to go from here:
- File things as they happen; when unsure, drop them in inbox/ (7-day rule).
- Read atlas/home.md when you feel lost; it is the map.
- The system earns trust through the wedge flow: {wedge_flow}. Feed it first.
```

## WORKFLOW COMPLETE
