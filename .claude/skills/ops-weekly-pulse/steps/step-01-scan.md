---
name: step-01-scan
description: Scan workspace for activity, categorize files, detect dormant clients
prev_step: steps/step-00-init.md
next_step: steps/step-02-report.md
---

# Step 1: Scan Workspace

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate the report in this step (that's step 2)
- ✅ ALWAYS scan all four workspace roots: `sources/clients/`, `sources/partners/`, `sources/internal/`, `sources/personal/`
- 📋 YOU ARE a scanner collecting raw data, not a report writer
- 💬 FOCUS on finding files, categorizing them, and identifying patterns
- 🚫 FORBIDDEN to write any output file in this step

## EXECUTION PROTOCOLS:

- 🎯 Scan files first, then categorize, then detect dormant clients
- 💾 Store all results in state variables for step 2
- 📖 Complete the full scan before loading step 2
- 🚫 FORBIDDEN to load step-02 until all scan results are compiled

## CONTEXT BOUNDARIES:

- Variables from step 0: `{period}`, `{period_start}`, `{period_end}`, `{publish_mode}`
- Workspace root: the repository root (parent of `sources/clients/`, `sources/partners/`, `sources/internal/`, `sources/personal/`)
- File naming convention: `YYYY-MM-DD-{type}-slug.md`
- Client context files: `sources/clients/{client}/CLAUDE.md`

## YOUR TASK:

Scan the entire workspace for files created or modified during the period, categorize them by client/project/type, and identify active and dormant clients.

---

## EXECUTION SEQUENCE:

### 1. Find Files by Date

**Strategy: dual approach combining filename dates and filesystem modification dates.**

**A. Filename-based detection (primary):**
- Scan `sources/clients/`, `sources/partners/`, `sources/internal/`, and `sources/personal/` for markdown files
- Extract the YYYY-MM-DD prefix from filenames
- Keep files where the date falls within `{period_start}` to `{period_end}`

**B. Filesystem modification date (secondary):**
- Use `find` with `-newer` or `-mtime` to catch files without date prefixes
- Also catches modified files (e.g., CLAUDE.md updates)
- Exclude: `.git/`, `node_modules/`, `.claude/`, `CLAUDE.md` files (unless specifically updated)

**Combine both lists, deduplicate by path.**

### 2. Categorize by Client and Project

For each file found, extract metadata from the path:

```
sources/clients/{client}/{project}/{subfolder?}/{filename}
  -> client = {client}
  -> project = {project}
  -> subfolder = emails | meetings | deliverables | (root)

sources/partners/{partner}/{project}/{subfolder?}/{filename}
  -> partner = {partner}
  -> project = {project}
  -> subfolder = emails | meetings | deliverables | (root)

sources/internal/{project}/{subfolder?}/{filename}
  -> client = "Internal"
  -> project = {project}

sources/personal/{project}/{subfolder?}/{filename}
  -> client = "Personal"
  -> project = {project}
```

Store in `{files_created}` as structured entries:
```
{
  path: string,
  date: string (YYYY-MM-DD),
  client: string,
  project: string,
  type: string (resolved by rules below),
  subfolder: string,
  filename: string
}
```

### 3. Categorize by Type

Type resolution rules (apply in order, first match wins):

1. **If file lives in an `emails/`, `mails/`, or `mailings/` subfolder** -> type = `email` (catches the canonical `YYYY-MM-DD-{seq}-{direction}-slug.md` format AND legacy `writing-` / `reply-` prefixes)
2. **If file lives in a `meetings/` subfolder** -> type = `meeting`
3. **If file lives in a `deliverables/` subfolder** -> type = `deliverable`
4. **If file lives in a `transcripts/` subfolder** -> type = `transcript`
5. **Otherwise, by filename prefix after `YYYY-MM-DD-`**:
   - `writing-` -> `writing` (deprecated, only in legacy files outside emails/)
   - `reply-` -> `email` (legacy)
   - `meeting-` -> `meeting`
   - `research-` -> `research`
   - `brainstorm-` -> `brainstorm`
   - `strategy-` -> `strategy`
   - `note-` -> `note`
   - Any digit prefix like `01-out-`, `02-in-`, `03-reply-` (canonical email format) -> `email`

Group by category:

| Type | Category label |
|------|---------------|
| `email` | Emails |
| `meeting` | Meetings / minutes |
| `deliverable` | Deliverables |
| `transcript` | Transcripts |
| `research` | Research / Audit |
| `brainstorm` | Brainstorm |
| `strategy` | Strategy |
| `writing` | Documents in progress |
| `note` | Notes |
| other | Other |

Count files per category for the summary table.

### 4. Identify Active Clients

From `{files_created}`, extract unique client names (excluding "Internal" and "Personal").

Store in `{clients_active}` with:
- Client name
- Number of files produced
- Projects touched
- Types of work done

### 5. Identify Dormant Clients

**A. List all client directories:**
- `ls sources/clients/` to get all client folder names

**B. For each client NOT in `{clients_active}`:**
- Check if `sources/clients/{client}/CLAUDE.md` exists
- If it exists, read it to check whether the client status is "active" or equivalent
- Only flag as dormant if the client appears to be an active/ongoing relationship
- Skip archived or completed clients

**C. For dormant clients, find last activity:**
- Find the most recent file (by filename date or modification date) in `sources/clients/{client}/`
- Store last activity date

Store in `{clients_inactive}`:
```
{
  client: string,
  last_activity: string (YYYY-MM-DD or "unknown"),
  status: string (from CLAUDE.md if available)
}
```

### 6. Extract Key Deliverables

From `{files_created}`, identify the most notable deliverables:
- Prioritize: research, strategy, writing (non-email), meeting files
- For each, read the first few lines to get a brief description or title
- Limit to 10-15 most significant items

Store in `{deliverables}`.

### 7. Scan for Pending Actions

In recently created/modified files, search for patterns indicating open action items:
- Lines starting with `- [ ]` (unchecked checkboxes)
- Sections titled "Actions", "Next steps", "TODO", "To do", "Follow-up"
- Lines containing "to do", "follow up", "send", "schedule", "notify"

Store found items in `{actions_pending}` with source file reference.

### 8. Invoicing Data (Optional Enrichment)

**If an accounting or invoicing tool integration is available:**
- Attempt to fetch invoices created during `{period_start}` to `{period_end}`
- Attempt to fetch estimates/quotes created during the period
- Attempt to get outstanding payment information
- Store results for the Billing section of the report

**If no accounting integration is available:**
- Skip silently; the report will omit the Billing section

### 9. Project Management Data (Optional Enrichment)

**If a project management tool integration is available:**
- Search for recently updated project records
- Look for task lists with recent modifications
- Store results for additional context in the report

**If no project management integration is available:**
- Skip silently

### 10. Present Scan Summary

Display a quick summary to the user before proceeding:

```
Scan complete ({period_start} -> {period_end}):
  {N} files found
  {M} active clients: {list}
  {K} dormant clients: {list}
  {J} pending actions detected
```

Then proceed to step 2.

---

## SUCCESS METRICS:

✅ All four workspace roots scanned (sources/clients, sources/partners, sources/internal, sources/personal)
✅ Files correctly categorized by client, project, and type
✅ Active clients identified with file counts
✅ Dormant clients identified with last activity dates
✅ Key deliverables extracted with brief descriptions
✅ Pending actions found from recent files
✅ Scan summary displayed to user
✅ All state variables populated for step 2

## FAILURE MODES:

❌ Starting to write the report
❌ Missing a workspace root in the scan
❌ Counting CONTEXT.md as a deliverable
❌ Flagging archived clients as dormant
❌ Not checking client status before flagging as dormant
❌ Empty scan results without explanation

---

## NEXT STEP:

After the scan is complete and the summary displayed, load `./step-02-report.md`

<critical>
Remember: This step produces RAW SCAN DATA only. No report generation, no formatting, no file writing. Just collect, categorize, and summarize findings in state variables.
</critical>
