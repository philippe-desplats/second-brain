---
name: step-01-scan
description: Scan sources/ for occurrences of the topic, group, score
prev_step: steps/step-00-init.md
next_step: steps/step-02-draft.md
---

# Step 1, Scan Sources

## MANDATORY EXECUTION RULES:

- 🛑 NEVER invent occurrences, only report what really exists
- ✅ ALWAYS verify the `{min_occurrences}` threshold before moving to step-02
- 📋 YOU ARE a scanner, not a writer

## EXECUTION SEQUENCE:

### Mode `topic` (default)

Look for occurrences of `{topic}` by these criteria, in order:

1. **Frontmatter `topics:`** containing `{topic}` (or slug variations)
2. **Wiki-links** `[[{topic}]]` or `[[{Capitalized Topic}]]`
3. **Keywords in the title** or the first 5 lines of the body
4. **Path slug** containing `{topic}` (e.g. `sources/clients/X/accessibility-audit/`)

Scope:
- `sources/clients/**/*.md`
- `sources/partners/**/*.md`
- `sources/internal/**/*.md`
- `sources/personal/**/*.md` (optional, depends on `{target}`; personal is often outside knowledge/ ops/tech/business)

Exclusions: `archives/`, `inbox/`, `basic-memory/`, `.claude/`, `templates/`, `atlas/maps/*-static.md` (generated).

Tools:

```bash
# Frontmatter topics scan
grep -rln "topics:.*{topic}\|topics:.*-.*{topic}" --include="*.md" sources/

# Wiki-links scan
grep -rln "\[\[{topic}\]\]\|\[\[{topic-cap}\]\]" --include="*.md" sources/

# Title and first lines scan (5 lines after frontmatter)
grep -rln "^#.*{topic}\|^---\$" --include="*.md" sources/ | xargs head -20 | grep -i "{topic}"

# Path slug scan
find sources -type d -name "*{topic}*" 2>/dev/null
```

Build `{sources_found}` as a list of `{path, title, type, excerpt_3_lines}`.

### Mode `auto` (discovery)

Scan ALL of sources/ to propose distillation candidates:

1. Count the frequent tags in frontmatter `topics:` everywhere
2. Count the outgoing wiki-links toward modeled entities (atlas/topics)
3. Count the recurring folder names (`audit`, `proposal`, `wordpress`, etc.)
4. For each candidate with >= `{min_occurrences}` occurrences, propose it

Present the top 10 via AskUserQuestion (multi-select), then for each selected candidate, restart step-01-scan in `topic` mode with that candidate.

### Threshold validation

- If `len({sources_found})` < `{min_occurrences}`:
  - Present the report: "Found only N/min occurrences for `{topic}`"
  - Ask the user via AskUserQuestion:
    - Continue anyway (force the distillation, the pattern will be weaker)
    - Retry with a lower threshold
    - Abandon
- If >= `{min_occurrences}`: OK, move to step-02

### Present the scan

Before step-02, present:

```
Scan {topic}:
- {N} occurrences found (threshold {min_occurrences} OK)
- Clients/partners involved: {list}
- Note types: {N research, N meeting, N decision, etc.}
- First excerpts:
  - [[{title 1}]] ({path 1}), "{excerpt}"
  - [[{title 2}]] ({path 2}), "{excerpt}"
  - ...
```

Ask for confirmation to move to step-02 (except `{auto_mode}` = true).

---

## SUCCESS METRICS:

✅ At least `{min_occurrences}` sources found (or the user forced it)
✅ `{sources_found}` populated with path, title, excerpt
✅ `{occurrence_count}` numeric
✅ User validated the scan

## FAILURE MODES:

❌ Inventing sources
❌ Silently forcing a threshold that is too low
❌ Skipping user validation in non-auto mode

---

## NEXT STEP:

Load `./step-02-draft.md`
