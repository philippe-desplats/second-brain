---
name: step-01-scan
description: Detect distill / archive / moc candidates with numeric criteria
prev_step: steps/step-00-init.md
next_step: steps/step-02-report.md
---

# Step 1, Scan Candidates

## MANDATORY EXECUTION RULES:

- 🛑 NEVER invent a candidate without numeric data (count, date, ratio)
- ✅ ALWAYS produce a score and a reason for each candidate
- ✅ ALWAYS respect `{only_filter}`, scan only the requested types

## EXECUTION SEQUENCE:

### 1. Scan `/distill` candidates (recurring patterns not yet distilled)

**Criterion**: a topic or slug appears in 3+ source notes but 0 or 1 time in `knowledge/`.

```bash
# Most represented topics in sources/
grep -rh "^topics:" --include="*.md" sources/ 2>/dev/null \
  | sed 's/^topics: *//; s/\[//; s/\]//' \
  | tr ',' '\n' \
  | sed 's/^ *//; s/ *$//' \
  | sort | uniq -c | sort -rn | head -30
```

For each topic with >= 3 occurrences:

```bash
# Check the presence in knowledge/
grep -rln "topics:.*{topic}\|- {topic}$" --include="*.md" knowledge/ 2>/dev/null | wc -l
```

If `knowledge_count` < 1 (or < 2 for very dense topics, > 10 sources):

Add to `{candidates_distill}`:

```json
{
  "topic": "accessibility-audit",
  "source_count": 7,
  "knowledge_count": 0,
  "score": 7,
  "reason": "7 occurrences in sources/, 0 in knowledge/. Recurring pattern not yet distilled.",
  "suggested_kind": "playbook",
  "suggested_command": "/distill accessibility-audit --kind playbook"
}
```

**Suggested kind heuristic**:
- If the sources are mostly `subtype: meeting` -> `playbook` (process)
- If mostly `subtype: research` -> `guide` (synthesis)
- If lots of `subtype: strategy` -> `decision` (ADR)
- If lots of technical tags (n8n, k8s, code) -> `pattern`
- If lots of operational `subtype: deliverable` -> `runbook`
- Default -> `pattern`

### 2. Scan `/archive` candidates (dormant entities)

**Criterion**: `last_updated` of the `CLAUDE.md` or the last modified file > `{min_inactive_months}` months.

```bash
# For each client and partner
for dir in sources/clients/*/ sources/partners/*/ sources/internal/*/; do
  test -d "$dir" || continue
  last=$(find "$dir" -type f -name "*.md" -exec stat -f "%m" {} \; 2>/dev/null | sort -rn | head -1)
  now=$(date +%s)
  if [ -n "$last" ]; then
    months=$(echo "($now - $last) / (30 * 86400)" | bc)
    echo "$months $dir"
  fi
done | sort -rn
```

For each entity with `months >= {min_inactive_months}`:

Check that it is not already in `archives/` (by convention it is not, since we scan sources/).

Check incoming references:

```bash
# How many external notes still reference this entity?
slug=$(basename {dir})
grep -rln "\[\[{slug}\]\]\|{dir}" --include="*.md" sources/ atlas/ knowledge/ 2>/dev/null \
  | grep -v "^{dir}" | wc -l
```

Add to `{candidates_archive}`:

```json
{
  "path": "sources/clients/globex/",
  "slug": "globex",
  "months_inactive": 14,
  "incoming_refs": 2,
  "score": 14,
  "reason": "14 months without activity, 2 historical incoming refs (2024 meeting minutes).",
  "suggested_command": "/archive sources/clients/globex/ --reason \"14 months inactive\""
}
```

**Additional filter**: if the entity has a `status: active` in its frontmatter, lower the score by 50% (explicit intent to keep it active).

### 3. Scan `/moc-new` candidates (dense topics without a MOC)

**Criterion**: a topic present in 10+ notes but without `atlas/maps/MOC-{slug}.md`.

```bash
# Most represented topics (reuse the command from step 1)
# For each topic with >= 10 occurrences:
test -f atlas/maps/MOC-{slug}.md && echo "MOC EXISTS" || echo "MOC MISSING"
ls atlas/maps/ | grep -i {slug} | head -5
```

If the MOC is missing and `note_count >= 10`:

Add to `{candidates_moc}`:

```json
{
  "topic": "ai-agents",
  "slug": "ai-agents",
  "note_count": 14,
  "moc_exists": false,
  "score": 14,
  "reason": "14 notes on the topic, no MOC. Dense enough to deserve a navigation hub.",
  "suggested_command": "/moc-new ai-agents"
}
```

**Additional filter**: if a note `atlas/topics/{slug}.md` exists and already has a rich "Linked notes" section, lower the score (the topic entity already acts as a hub).

### 4. Optional scan, stale MOCs (update suggestion)

If the scope includes `topics` or `full`, also scan existing MOCs:

```bash
ls atlas/maps/MOC-*.md 2>/dev/null
```

For each MOC, check `last_updated` in the frontmatter (or the last git modification date):

```bash
git log -1 --format="%at" -- atlas/maps/MOC-{slug}.md 2>/dev/null
```

If > 3 months AND the topic gained > 3 new notes since:

Add to `{candidates_moc}` (category "update"):

```json
{
  "topic": "accessibility-audits",
  "moc_path": "atlas/maps/MOC-accessibility-audits.md",
  "moc_age_months": 5,
  "new_notes_since": 6,
  "score": 6,
  "reason": "MOC updated 5 months ago, 6 new notes on the topic since. Update recommended.",
  "suggested_command": "/moc-new accessibility-audits (update mode)"
}
```

### 5. Sort by descending score

For each list, sort by descending `score`. The most "obvious" candidates rise to the top.

### 6. Synthesis

Store the 3 lists in the state variables:
- `{candidates_distill}`
- `{candidates_archive}`
- `{candidates_moc}`

Present a minimal summary in step-01 (the detail is in step-02):

```
Curation scan complete:
- {N1} distill candidates detected
- {N2} archive candidates detected
- {N3} MOC candidates detected (new or update)

Total: {N1 + N2 + N3} suggested actions.
```

If total = 0:

```
Clean workspace, no curation action needed right now.
Keep enriching, I will come back at the next review.
```

And exit without calling step-02.

---

## SUCCESS METRICS:

✅ Every candidate has a score and a numeric reason
✅ The 3 lists are sorted by relevance
✅ `{only_filter}` respected
✅ Summary presented

## FAILURE MODES:

❌ Inventing a candidate without data
❌ Including an already-processed candidate (entity already in archives/, MOC already existing and fresh)
❌ Ignoring the only filter

---

## NEXT STEP:

Load `./step-02-report.md`
