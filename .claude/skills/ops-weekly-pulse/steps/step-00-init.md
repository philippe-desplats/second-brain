---
name: step-00-init
description: Parse flags, compute period dates, set defaults
next_step: steps/step-01-scan.md
---

# Step 0: Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER start scanning files in this step
- ✅ ALWAYS compute exact start/end dates before proceeding
- 📋 YOU ARE an initializer, not a scanner
- 💬 FOCUS on parsing flags and setting up state variables
- 🚫 FORBIDDEN to read any workspace files beyond what's needed for setup

## EXECUTION PROTOCOLS:

- 🎯 Parse flags first, then compute dates, then confirm
- 💾 Store all state variables for subsequent steps
- 📖 Complete initialization before loading step 1
- 🚫 FORBIDDEN to load step-01 until dates are computed and confirmed

## CONTEXT BOUNDARIES:

- User input: raw command with optional flags
- Today's date: use `date +%Y-%m-%d` to get the current date
- No workspace scanning happens here

## YOUR TASK:

Parse user input to extract flags (-p, -n), compute the period start/end dates, and prepare state for the scan step.

---

## DEFAULTS CONFIGURATION:

```yaml
period: "last 7 days"
period_start: "{today - 7 days}"
period_end: "{today}"
publish_mode: false
```

---

## INITIALIZATION SEQUENCE:

### 1. Get Current Date

Run `date +%Y-%m-%d` to determine today's date. This is the reference for all period calculations.

### 2. Parse Flags

**Step 1: Load defaults from config above**

**Step 2: Parse user input and override defaults:**
```
Enable flags:
  -n          -> {publish_mode} = true
  -p <period> -> parse period string (see below)

No remainder expected (this skill takes no positional arguments)
```

### 3. Compute Period Dates

**If no `-p` flag (default):**
- `{period}` = "last 7 days"
- `{period_end}` = today
- `{period_start}` = today - 7 days

**If `-p` flag with a relative duration:**
- "last 14 days" -> today - 14 to today
- "last 30 days" -> today - 30 to today
- "this week" -> Monday of the current week to today

**If `-p` flag with a named month:**
- "march" / "march 2026" -> 2026-03-01 to 2026-03-31
- "february" -> compute the correct start/end for that month/year

**If `-p` flag with a named period:**
- "this month" -> first day of current month to today
- "last month" -> first to last day of the previous month

Use `date` commands to compute exact YYYY-MM-DD values for `{period_start}` and `{period_end}`.

### 4. Confirm Configuration

**Display to user:**

```
Pulse configuration:
  Period: {period}
  From {period_start} to {period_end}
  Publish: {yes/no}
```

Then proceed directly to step 1.

---

## SUCCESS METRICS:

✅ Flags correctly parsed (-p and -n)
✅ Period dates computed as valid YYYY-MM-DD
✅ `{period_start}` is before `{period_end}`
✅ Configuration displayed to user
✅ All state variables initialized

## FAILURE MODES:

❌ Starting to scan or read workspace files
❌ Invalid date computation (start after end)
❌ Missing state variables
❌ Unrecognized period string with no fallback

---

## NEXT STEP:

After initialization, load `./step-01-scan.md`

<critical>
Remember: This step is ONLY about parsing flags and computing dates. Do NOT scan any workspace files. Do NOT read client contexts. That happens in step 1.
</critical>
