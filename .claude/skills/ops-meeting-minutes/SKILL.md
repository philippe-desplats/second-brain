---
name: ops-meeting-minutes
description: Turn raw notes, a transcript, or a dictated summary into clean meeting minutes. Extracts decisions, action items with owners and deadlines, open questions, and discussion points, then produces client-ready or internal minutes and saves them with the meeting schema frontmatter.
argument-hint: "[-e <entity>] [-i] [-s] <paste notes, @transcript.md, or describe the meeting>"
---

<objective>
Produce professional meeting minutes from raw material: pasted notes, a transcript file, or a dictated recap. The minutes capture what was decided, what happens next, and who owns it, in the entity's language. Two registers, a polished client-facing version and a franker internal version that keeps an internal notes section. The result is saved under the entity's project with the meeting frontmatter.
</objective>

<parameters>
**Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `-e <entity>` | Entity slug, skips detection and loads that entity directly. | auto-detect |
| `-i` | Internal minutes, franker, keeps an internal notes section not meant for the client. | client-facing |
| `-s` | Save silently after approval, using the inferred path. | confirm path |

**Input:** meeting notes pasted directly, a transcript file reference (`@path/to/transcript.md`), or a spoken recap to structure.

**Examples:**
```
/ops-meeting-minutes [paste your notes]
/ops-meeting-minutes -e globex @sources/clients/globex/website/transcripts/2026-07-02-transcript-weekly.md
/ops-meeting-minutes -i weekly internal sync on the hosting migration
/ops-meeting-minutes -e initech -s [paste notes]
```
</parameters>

<state_variables>
**Persist throughout all steps:**

| Variable | Type | Description |
|----------|------|-------------|
| `{raw_content}` | string | The notes, transcript, or recap |
| `{register}` | string | "client-facing" or "internal" |
| `{entity_slug}` | string | Kebab-case entity slug |
| `{entity_zone}` | string | `clients`, `partners`, `internal`, or `personal` |
| `{language}` | string | Resolved output language |
| `{meeting_date}` | string | YYYY-MM-DD |
| `{participants}` | list | Names, with role or company when known |
| `{decisions}` | list | Decisions taken |
| `{actions}` | list | Action items with owner and deadline |
| `{open_questions}` | list | Unresolved items |
| `{topics}` | list | Discussion points grouped by theme |
| `{minutes}` | string | The formatted minutes |
| `{save_silent}` | boolean | From `-s` |
</state_variables>

<writing_style>
Load `.claude/skills/references/writing-rules.md` and obey it. Write in `{language}`. Factual and concise, no interpretation, no filler. No em dashes, no en dashes, no semicolon chains, no emoji. Client-facing minutes carry no internal commentary. Internal minutes may be frank and keep a clearly separated internal notes section.
</writing_style>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Description |
|------|------|-------------|
| 0 | `steps/step-00-init.md` | Parse flags, capture raw content, set the register |
| 1 | `steps/step-01-extract.md` | Extract context, decisions, actions, questions, topics, validate |
| 2 | `steps/step-02-format.md` | Format the minutes, review, save with meeting frontmatter |
</step_files>
