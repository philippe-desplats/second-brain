---
name: step-01-scan
description: Scan the notes linked to the topic, group by context
prev_step: steps/step-00-init.md
next_step: steps/step-02-draft.md
---

# Step 1, Scan Notes for Topic

## MANDATORY EXECUTION RULES:

- 🛑 NEVER include a note that has no real link to the topic
- ✅ ALWAYS scan sources/, knowledge/, atlas/topics/, atlas/services/, atlas/people/
- ✅ ALWAYS validate the `{min_notes}` threshold before step-02

## EXECUTION SEQUENCE:

### 1. Multi-criteria scan

For each note source, look for links to `{topic}`:

**Frontmatter topics:**

```bash
grep -rln "^topics:.*{slug}\|^- {slug}$" --include="*.md" sources/ knowledge/ atlas/ 2>/dev/null
```

**Wiki-links to the topic (if it exists as an entity)**

```bash
grep -rln "\[\[{topic-cap}\]\]\|\[\[{topic-tit}\]\]" --include="*.md" sources/ knowledge/ atlas/ 2>/dev/null
```

**Titles and first lines**

```bash
grep -rln "^#.*{topic}\|^title:.*{topic}" --include="*.md" sources/ knowledge/ atlas/ 2>/dev/null
```

**Slugs in the paths**

```bash
find sources/ knowledge/ -type d -name "*{slug}*" 2>/dev/null
find sources/ knowledge/ -type f -name "*{slug}*" 2>/dev/null
```

**Entities already modeled in atlas/**

```bash
test -f atlas/topics/{slug}.md && echo "TOPIC ENTITY EXISTS"
ls atlas/services/ | grep "{slug}" 2>/dev/null
```

Build `{notes_found}` as a dict grouped by context:

```
{
  "clients": {"globex": [path1, path2], "initech": [path3]},
  "partners": {"hooli": [path4]},
  "internal": [path5, path6],
  "knowledge": [path7],
  "atlas_entities": {"topic": "atlas/topics/{slug}.md", "service": "atlas/services/X.md"}
}
```

### 2. Validate the threshold

Count the total: `{total_notes}` = sum of all the lists.

**If `{total_notes}` < `{min_notes}`**:

```
⚠ Only {N} notes found on the topic "{topic}".
Minimum threshold for a useful MOC: {min_notes}.

Options:
- Continue anyway (the MOC will be lighter, to enrich over time)
- Lower the threshold
- Choose a broader topic (e.g. instead of "form-validation-accessibility", try "accessibility")
- Abandon
```

AskUserQuestion except in `{auto_mode}` (which continues automatically).

### 3. Present the grouped scan

```
Scan {topic}: {total_notes} notes found

By client ({N}):
- Globex, 3 notes
- Initech, 2 notes
- ...

By partner ({N}):
- Hooli, 1 note

Internal ({N}):
- {N} notes

Distilled knowledge ({N}):
- knowledge/ops/playbook-accessibility-audit.md

Linked atlas entities:
- atlas/topics/{slug}.md (existing)
- atlas/services/accessibility-audit.md (existing)
```

### 4. Ask for the structure (except auto)

Depending on density, offer a structuring mode:

```yaml
questions:
  - header: "MOC structure"
    question: "How do you want to structure this MOC?"
    options:
      - label: "By client/partner"
        description: "Sections per entity, ideal if several client missions cut across this topic"
      - label: "By note type"
        description: "Sections per minutes/email/research/decision, ideal if dense across many types"
      - label: "By sub-theme"
        description: "Sections per axis (e.g. for an accessibility standard, by its numbered themes)"
      - label: "You decide"
        description: "Let the AI propose the best structure"
    multiSelect: false
```

Store `{structure_mode}` for step-02.

---

## SUCCESS METRICS:

✅ `{total_notes}` >= `{min_notes}` (or the user forced it)
✅ `{notes_found}` populated and grouped
✅ Structure mode chosen

## FAILURE MODES:

❌ Inventing notes
❌ Forcing an empty MOC

---

## NEXT STEP:

Load `./step-02-draft.md`
