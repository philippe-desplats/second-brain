---
name: step-02-report
description: Generate structured pulse report, save locally, optional publish
prev_step: steps/step-01-scan.md
---

# Step 2: Generate Pulse Report

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER re-scan files (that's done in step 1)
- ✅ ALWAYS generate the complete report before saving
- 📋 YOU ARE a report generator, assembling scan data into a structured document
- 💬 FOCUS on data-driven, actionable output in the owner's working language
- 🚫 FORBIDDEN to skip any section of the report template
- 🚫 FORBIDDEN to use em dashes, en dashes, semicolons, or emojis in the report content

## EXECUTION PROTOCOLS:

- 🎯 Assemble report from scan data, don't re-derive
- 💾 Save the report locally first, then publish if the -n flag is set
- 📖 Complete the full report before presenting to user
- 🚫 FORBIDDEN to present partial reports

## CONTEXT BOUNDARIES:

- Variables from previous steps: ALL state variables
- `{files_created}` = categorized files from step 1
- `{clients_active}` = clients with activity
- `{clients_inactive}` = dormant active clients
- `{deliverables}` = key deliverables produced
- `{actions_pending}` = open action items
- `{period}`, `{period_start}`, `{period_end}` = time range
- `{publish_mode}` = whether to publish to the connected project management tool

## YOUR TASK:

Assemble all scan data into a structured, polished pulse report in the owner's working language and save it.

---

## EXECUTION SEQUENCE:

### 1. Generate Report

**Report template (all sections mandatory unless marked conditional):**

```markdown
# Weekly Pulse: {period_start} > {period_end}

**Generated on:** {today}
**Period:** {period description}

---

## Activity of the week

**{N} deliverables** produced for **{M} active clients**

### By client

| Client | Project | Deliverables | Types |
|--------|---------|--------------|-------|
| {client} | {project} | {count} | {types} |

### By type

| Type | Count |
|------|-------|
| Emails | {n} |
| Meetings / minutes | {n} |
| Research / Audit | {n} |
| Documents / Contracts | {n} |
| Notes | {n} |

---

## Key deliverables

{For each active client, list notable deliverables with one-line descriptions}

### {Client Name}

- **{filename}**: {brief description from file content}

---

## Billing & Business

{CONDITIONAL: only include if invoicing data was retrieved in step 1}

| Indicator | Value |
|-----------|-------|
| Estimates sent | {n} for {total} excl. tax |
| Invoices issued | {n} for {total} excl. tax |
| Payments outstanding | {total} |

---

## Dormant clients

{List of active clients without recent activity}

| Client | Last activity | Status |
|--------|---------------|--------|
| {client} | {last_activity_date} | {status from CLAUDE.md} |

{If no dormant clients: "All active clients had activity during the period."}

---

## Next week

{Based on {actions_pending}, open items found in CLAUDE.md, pending emails, and meeting follow-ups}

- {action item with source reference}
- {action item with source reference}

{If no pending actions found: "No pending actions detected in recent files."}

---

## Notes

{Observations about the period:}
- Workload balance (heavy/light week)
- Client concentration (all effort on one client vs. spread)
- Types of work (operational vs. strategic)
- Any patterns worth noting
```

### 2. Writing Rules

Apply these rules when generating report content:

- **Data-driven, not narrative.** Tables over prose wherever possible.
- **Actionable.** Dormant clients = follow-up opportunity. Pending actions = concrete next steps.
- **Honest.** If the week was light, say so clearly. Do not inflate activity.
- **Owner's working language.** The entire report is in the owner's working language (see `sources/internal/CONTEXT.md`; default English).
- **No em dashes or en dashes.** Use commas or restructure sentences instead.
- **No semicolons.** Use periods or commas.
- **No emojis.** Professional tone throughout.
- **Concise.** Each deliverable description is one line maximum.

### 3. Save Report Locally

**ALWAYS save the report.** Follow `.claude/skills/references/save-conventions.md`:

1. **Target path:** `sources/internal/weekly-pulse/YYYY-MM-DD-note-weekly-pulse.md`
   - Use today's date for the filename (not the period dates)
2. **Verify** the folder exists, create if needed (`mkdir -p`)
3. **Write** the full report to the file
4. **Confirm:** "Report saved to `{path}`"

### 4. Publish to Project Management Tool (if -n flag)

**If `{publish_mode}` = true:**

If a project management tool integration is available:
1. Locate a "Weekly Pulse" page or list in the tool
2. Create a new entry titled "Weekly Pulse: {period_start} > {period_end}"
3. Paste the report content adapted to the tool's format
4. Report the resulting URL to the user

If no project management integration is available, note that the report was saved locally only.

**If `{publish_mode}` = false:**
-> Skip this step silently

### 5. Present Summary

Show the user:
- Where the report was saved (full local path)
- Published URL (if applicable)
- The key numbers: N deliverables, M active clients, K dormant clients
- Top 3 pending actions (if any)
- Ask if adjustments are needed

---

## SUCCESS METRICS:

✅ All report sections generated (or conditional sections properly skipped)
✅ Every active client appears in the "By client" table
✅ Deliverable descriptions are specific, not generic
✅ Dormant clients listed with last activity dates
✅ Pending actions sourced from actual file content
✅ Report saved to `sources/internal/weekly-pulse/`
✅ Published (if -n flag)
✅ Summary presented to user

## FAILURE MODES:

❌ Missing report sections
❌ Generic descriptions ("work done", "documents produced")
❌ Em dashes, en dashes, semicolons, or emojis in report text
❌ Not saving the report locally
❌ Publishing without the -n flag
❌ Inflating activity or inventing deliverables not found in the scan
❌ Not presenting summary to user

## REPORT PROTOCOLS:

- Write the report in the owner's working language
- Use clear headers and consistent formatting
- Keep the "By client" table readable (abbreviate project names if needed)
- The "Notes" section should be genuinely analytical, not filler
- If the period produced zero files, still generate the report stating that no activity was detected

---

## WORKFLOW COMPLETE

After the report is saved and presented, the workflow is finished.

<critical>
Remember: The pulse report is an INTERNAL tool for the owner to track activity rhythm. It must be honest, data-driven, and actionable. Never fabricate activity. If the week was empty, say so. Every dormant client is a signal to follow up.
</critical>
