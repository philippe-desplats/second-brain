---
name: ops-weekly-pulse
description: Weekly activity review, scan the workspace and generate a structured dashboard
argument-hint: "[-p <period>] [-n]"
---

<objective>
Scan the entire workspace for recent activity (files created/modified, client work, deliverables) and generate a structured weekly pulse report. The report surfaces active clients, dormant clients, deliverable counts by type, and actionable next steps.
</objective>

<parameters>
**Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `-p <period>` | Custom time period to scan (e.g., "last 14 days", "march", "this month") | last 7 days |
| `-n` | Publish the final report to your project management tool after saving locally (if one is connected) | false |

**Examples:**
```
/ops-weekly-pulse
/ops-weekly-pulse -p "last 14 days"
/ops-weekly-pulse -p "march 2026" -n
/ops-weekly-pulse -n
```
</parameters>

<state_variables>
**Persist throughout all steps:**

| Variable | Type | Description |
|----------|------|-------------|
| `{period}` | string | Human-readable period description (e.g., "last 7 days") |
| `{period_start}` | string | Start date (YYYY-MM-DD) |
| `{period_end}` | string | End date (YYYY-MM-DD) |
| `{files_created}` | list | Files created/modified during period with path, date, type metadata |
| `{clients_active}` | list | Clients with activity during the period |
| `{clients_inactive}` | list | Active clients without recent activity |
| `{deliverables}` | list | Key deliverables produced, grouped by client/project |
| `{actions_pending}` | list | Open action items found in recent files |
| `{report}` | string | The generated pulse report (full markdown) |
| `{publish_mode}` | boolean | Whether to publish to the connected project management tool |
</state_variables>

<writing_style>
- Write in the owner's working language (see `sources/internal/CONTEXT.md`; default English)
- No emojis
- No em dashes, no en dashes
- Direct and factual tone, no filler
- Avoid AI vocabulary: "crucial", "pivotal", "highlights", "underscores", "showcases"
- Avoid AI phrasing: empty intensifier adverbs, generic transitions
- No generic positive conclusions ("a productive week")
- Concrete data: file names, dates, clients, no vague summaries
</writing_style>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Description |
|------|------|-------------|
| 0 | `steps/step-00-init.md` | Parse flags, compute period dates, set defaults |
| 1 | `steps/step-01-scan.md` | Scan workspace for activity, categorize files, detect dormant clients |
| 2 | `steps/step-02-report.md` | Generate structured pulse report, save locally, optional publish |
</step_files>
