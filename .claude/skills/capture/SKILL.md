---
name: capture
description: Ingest raw inbound content into the second brain. Paste an email, a transcript, meeting notes, a document, or an idea; the skill identifies the type, resolves the target entity and project, generates schema-correct frontmatter with relations, and files it at the conventional path. Also processes aged inbox/ items one by one. Triggers on "capture this", "file this email", "ingest this", "process my inbox", "where does this go".
argument-hint: "[content or @file] [-i] [-e <entity>] [-t <type>]"
---

<objective>
The daily inbound flow of the second brain. Everything that arrives (emails, transcripts, notes, documents, ideas) gets classified, typed, and filed at a predictable path in one pass, so retrieval works later. Capture files raw artifacts faithfully: it classifies and wraps, it never rewrites content (summarizing is `/ops-resume`'s job).
</objective>

<quick_start>

```
/capture                          # then paste the content when prompted
/capture @inbox/2026-07-03-contract-draft.md
/capture -e globex                # skip entity detection
/capture -t email                 # force the content type
/capture -i                       # inbox mode: process aged inbox/ items one by one
```

</quick_start>

<flags>

| Flag | Description |
|------|-------------|
| `-i` | Inbox mode: iterate over `inbox/` items, oldest first, classify and file each |
| `-e <entity>` | Target entity slug, skips entity detection |
| `-t <type>` | Force the content type (must be one of the canonical schema types) |

**Remainder** after flags: the content itself, or an `@path` reference to a file.
</flags>

<workflow>
1. **Init** → Parse flags, acquire the content (paste, file, or inbox queue)
2. **Classify** → Detect type, entity, zone, project, date, and type-specific metadata
3. **File** → Build path and frontmatter, show the full plan, write after approval; loop in inbox mode
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-init.md` | Parse flags, acquire content or build the inbox queue |
| 01 | `steps/step-01-classify.md` | Type, entity, project, date detection with validation |
| 02 | `steps/step-02-file.md` | Path + frontmatter plan, approval gate, write, loop |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{mode}` | string | step-00 (`single` or `inbox`) |
| `{queue}` | list | step-00 (inbox mode: pending items, oldest first) |
| `{raw_content}` | string | step-00 (current item's verbatim content) |
| `{source_path}` | string | step-00 (if content came from a file; empty for paste) |
| `{entity_override}` | string | step-00 (from `-e`) |
| `{type_override}` | string | step-00 (from `-t`) |
| `{content_type}` | string | step-01 (one of the canonical schema types) |
| `{entity}` | string | step-01 (entity slug, or `internal`/`personal`) |
| `{zone}` | string | step-01 (`clients`, `partners`, `internal`, `personal`) |
| `{project}` | string | step-01 (project slug under the entity) |
| `{item_date}` | string | step-01 (YYYY-MM-DD, from content or today) |
| `{type_meta}` | object | step-01 (type-specific: direction/seq for emails, participants for meetings...) |
| `{target_path}` | string | step-02 |
| `{processed}` | list | step-02 (inbox mode: filed/skipped/deferred results) |

</state_variables>

<references>

| Reference | Purpose |
|-----------|---------|
| `references/type-signals.md` | Detection matrix: which signals identify each canonical type |

Shared workspace references this skill relies on: `.claude/skills/references/save-conventions.md` (path resolution and naming), `basic-memory/schemas/*.md` (frontmatter contracts), `.claude/rules/frontmatter.md` (decision matrix).
</references>

<execution_rules>
- **Load one step at a time**; follow the next_step directives
- **Never rewrite the captured content.** The body is preserved verbatim; capture only adds frontmatter, an optional title heading, and a Relations block
- **Human validation before every write.** The full plan (path, filename, complete frontmatter) is shown as plain text before anything touches disk; in inbox mode, each item gets its own approval
- **Never guess an entity.** If detection is ambiguous, ask; if the entity does not exist yet, offer to create its folder and CLAUDE.md from the template first
- **Respect save-conventions**: nothing at an entity root, `YYYY-MM-DD-{type}-slug.md` naming, email naming with sequence and direction, subfolders only for email/meeting/transcript/deliverable
- **Added text** (title heading, slug words) uses the owner's working language; the captured body keeps its original language
- **Inbox mode**: process oldest first, offer skip and defer per item, remove the inbox original only after its filed copy is confirmed written
- If Basic Memory is installed, suggest `bm reindex` once at the end of the session, not per file
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-init.md`
</entry_point>
