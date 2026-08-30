---
name: step-02-file
description: Build the path and frontmatter plan, gate on approval, write, loop in inbox mode
prev_step: steps/step-01-classify.md
next_step: null
---

# Step 2: File

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER write before the full plan was shown and approved
- 🛑 NEVER alter the captured body: frontmatter, title heading, and Relations block only (a `clipping` also gets the provenance line, the empty Observations prompts and the `## Source` heading, see step 2; the captured text itself is still untouched)
- ✅ ALWAYS compute the email sequence number from what already exists on disk
- ✅ ALWAYS remove an inbox original only AFTER its filed copy is confirmed on disk
- 📋 YOU ARE A FILING CLERK with a checklist, not an editor

## EXECUTION SEQUENCE:

### 1. Build the target path and filename

Apply `.claude/skills/references/save-conventions.md`:

| Type | Destination |
|---|---|
| email | `sources/{zone}/{entity}/{project}/emails/{item_date}-{seq}-{direction}-{slug}.md` |
| meeting | `sources/{zone}/{entity}/{project}/meetings/{item_date}-meeting-{slug}.md` |
| transcript | `sources/{zone}/{entity}/{project}/transcripts/{item_date}-transcript-{slug}.md` |
| clipping | `sources/{zone}/{entity}/{project}/clippings/{item_date}-clipping-{slug}.md`, or a watch project such as `sources/internal/watch/clippings/` when it belongs to no project |
| research / brainstorm / strategy / note | `sources/{zone}/{entity}/{project}/{item_date}-{type}-{slug}.md` |
| internal / personal | same patterns under `sources/internal/{project}/` or `sources/personal/{project}/` |

Email sequence: `ls sources/.../emails/{item_date}-*.md 2>/dev/null | wc -l` + 1, zero-padded (`01`, `02`).
Binary files: same destination folder, original filename prefixed with `{item_date}-`, no markdown wrapping.
Slug: 3-6 kebab-case words in the owner's working language, concrete not generic.

### 2. Generate the frontmatter

Read the matching schema in `basic-memory/schemas/{content_type}.md` and produce a complete frontmatter block: `title`, `type`, required fields, `{type_meta}` fields, `category` matching the zone. Then the body structure:

```markdown
---
{schema-correct frontmatter}
---

# {Title in the working language}

{raw_content, verbatim}

## Relations

- about [[{Entity display name}]]
{other detected relations: replies_to, follows, meeting_ref}
```

**Set `written_by: agent` when the type declares it.** `session` and `note` carry that field; the other types do not, because their type already says the text is not the owner's own writing. Capture writes on the owner's behalf, so the value is always `agent`, never `owner`.

**Leave a relation out rather than approximating it.** `about` is optional on every type that declares it. When no existing `atlas/topics/` entry actually covers the subject, omit `about`; capture does not create topics, and a near-miss topic quietly mislabels the note for good. Mention the gap in the approval gate so the owner can create the topic if it is worth one.

**Relations follow the schema, not this generic shape.** Read which target type each relation expects in `basic-memory/schemas/{content_type}.md`. On a `clipping`, for instance, `about` points at a `Topic` and the entity is carried by `client` or `partner`, so a literal `about [[{Entity}]]` would be wrong.

**A `clipping` uses its own body**, identical to what the Web Clipper writes through `templates/obsidian-web-clipper.json`. Two clippings sitting in the same folder must not have two shapes depending on which door they came through:

```markdown
---
{schema-correct frontmatter}
---

# {title}

> Captured from [{site}]({source_url}) on {date}. Personal working copy, kept for retrieval.

## Observations

<!-- [quote] a passage worth keeping verbatim -->
<!-- [takeaway] what this changes for us, in our own words -->
<!-- [question] a question this raises -->

## Relations

- client [[{Client}]] or partner [[{Partner}]], when the clip was captured for one
- about [[{Topic}]]

---

## Source

{raw_content, verbatim}
```

The observation prompts stay as comments: capture files, it does not read, so it has nothing truthful to put there. The owner fills them when the clip is worth more than a bookmark.

### 3. Approval gate

Show the FULL plan as plain text and end the turn:

```
Target : {target_path}
{complete frontmatter block}
Body   : verbatim ({N} lines) + Relations block
{If new entity: + creation of sources/{zone}/{entity}/CLAUDE.md from template}
{If new project: + creation of sources/{zone}/{entity}/{project}/}
```

On the next turn, apply the user's verdict: approve → write; adjust → fix and re-show; skip (inbox mode) → mark skipped, jump to 5.

### 4. Write and verify

Create missing directories (entity, project, subfolder), write the file, then verify: `test -f {target_path}` and re-read the frontmatter for YAML validity. Record the result in `{processed}`.

**Inbox cleanup**: if `{source_path}` is inside `inbox/`, remove the original now (`git rm` if tracked, `rm` otherwise), and note it in `{processed}`.

### 5. Loop or finish

**Inbox mode with remaining `{queue}` items**: take the next item, load its content, and go back to step-01 for that item. Deferred items stay in `inbox/` untouched.

**Otherwise, final summary:**

```
✓ Captured
| # | Item | → | Path | Status |
{one row per processed item: filed / skipped / deferred}

{If anything was filed and Basic Memory is installed:}
Suggestion: bm reindex   (refresh the search index once)
{If any inbox item remains}: {n} item(s) still in inbox/, oldest is {age} days.
```

## FAILURE MODES:

❌ Writing without the approval gate
❌ Summarizing or "cleaning up" the captured body
❌ Deleting an inbox original before the filed copy is verified
❌ Guessing the email sequence instead of counting existing files

<critical>
Capture's whole value is trust: the user must know that what went in is exactly what got filed, at a path they could have predicted.
</critical>
