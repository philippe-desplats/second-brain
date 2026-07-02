---
name: ops-email
description: Write a human-sounding professional email, new or reply, in the owner's voice and the entity's language. Resolves the recipient, loads their communication preferences, calibrates register from prior emails, drafts, self-audits against the shared writing rules, and saves following the email convention.
argument-hint: "[-r] [-e <entity>] [-s] <brief, or paste the thread to reply to>"
---

<objective>
Draft a professional email that reads as written by a person, not generated. The email adopts the owner identity from the workspace profile, the tone and addressing of the recipient's entity, and the register learned from earlier outgoing emails. It supports two modes, a new email and a reply to a pasted thread, and always ends by saving the email under the entity's project.
</objective>

<parameters>
**Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `-r` | Reply mode. The input is the email thread being answered. | false (new email) |
| `-e <entity>` | Entity slug, skips recipient detection and loads that entity directly. | auto-detect |
| `-s` | Save silently after approval, using the inferred path without a confirming question. | false (confirm path) |

**Input:** a short brief of what to write, or the pasted email thread to reply to.

**Examples:**
```
/ops-email chase Globex about the January invoice
/ops-email -r [paste the thread] confirm the meeting and propose a slot next week
/ops-email -e initech ask whether the staging deploy is done
/ops-email -s send the kickoff summary to Jane Doe at Acme
```
</parameters>

<state_variables>
**Persist throughout all steps:**

| Variable | Type | Description |
|----------|------|-------------|
| `{mode}` | string | "new" or "reply" |
| `{entity_slug}` | string | Kebab-case entity slug |
| `{entity_zone}` | string | `clients`, `partners`, `internal`, or `personal` |
| `{entity_prefs}` | object | tone, addressing, primary_channel, email_format, language, constraints |
| `{language}` | string | Resolved output language |
| `{recipient_name}` | string | Who the email is addressed to |
| `{recipient_context}` | string | Relationship and relevant background |
| `{purpose}` | string | What the email must accomplish |
| `{key_points}` | list | Points to cover |
| `{thread}` | string | The pasted email being answered (reply mode) |
| `{voice_sample}` | string | Register reference from calibration |
| `{draft}` | string | Current email draft |
| `{save_silent}` | boolean | From `-s` |
</state_variables>

<writing_style>
Load `.claude/skills/references/writing-rules.md` before drafting and obey it in full. Core bans: no em dashes, no en dashes, no semicolon chains, no emoji, no markdown inside the email body, no corporate cliches, no AI tells. Write in `{language}`, match the entity `addressing`, honor every entity constraint. Sign with the owner identity from the root `CLAUDE.md` profile block.
</writing_style>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Description |
|------|------|-------------|
| 0 | `steps/step-00-init.md` | Parse flags, set mode, prepare state |
| 1 | `steps/step-01-context.md` | Resolve entity, load preferences, gather recipient, purpose, key points |
| 2 | `steps/step-02-calibrate.md` | Calibrate register from prior emails, a pasted sample, or entity preferences |
| 3 | `steps/step-03-draft.md` | Draft, self-audit, present, iterate, save |
</step_files>
