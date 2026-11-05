# Changelog

Structural changes to this workspace. Content changes (notes, projects) are tracked by git history, not here.

`Unreleased` is your own section, and this file stays yours: the update recipe in [README.md](README.md#keeping-your-clone-up-to-date) never overwrites it. The numbered releases below it document what each boilerplate version changed in the infrastructure that recipe does pull, so read them before applying one.

## Unreleased

## 0.6.1

The `about` relation of emails and meetings now names their project, and the auto-link pass stops breaking tables and headings. Until this release, `add_about_relations.py` linked the client, the partner or the organization, while `basic-memory/schemas/email.md` and `meeting.md` type `about` as the project brief and the demo notes link their project, `Globex Website Redesign`. Every note it wrote got the entity in a slot meant for the project, so that meeting never reached its project through the graph. `auto_link_entities.py` wrote links with display text inside table rows, where their bare `|` splits the cell, and linked inside headings. This release ships the fixed passes, 2 more shapes in the damage check, and asks you to repair the lines the old passes wrote behind a diff, since no checkout repairs data.

- `add_about_relations.py` links the project. The target is the `title:` of the brief of the note's project folder, its `README.md`, or its `CLAUDE.md`, declaring `type: project-brief`. The entity stays carried by `client:` or `partner:`, and nothing writes an `about` link to the entity any more. A note whose project folder has no brief, a `README.md` without `type: project-brief` as the 0.4.0 briefs were, or a brief without a title, gets nothing and is listed in the report under `[NO BRIEF]` with the reason. A note whose `about` already links its project, by the brief's title or one of its aliases, is left alone, so a second `--apply` changes nothing. A note whose `about` links something else gets its project added next to it. The pass no longer reads `organization`, internal emails and meetings link their project like the others. Which folder is the project and which file is its brief now lives in `note_types.project_brief`, the rule the damage check reads too.
- The old target was written in more places than the pass covers today. The 0.5.x pass wrote an `about` link to the entity into every note of an entity folder, project briefs and deliverables included, and one to `Internal`, a note that never existed, into every internal note. The 0.6.0 pass wrote the entity into emails and meetings, internal ones getting the `organization`, which is also what phase 5 of the 0.6.0 prompts told you to put in place of `Internal`. 4 skill texts taught the same target: `.claude/skills/references/save-conventions.md`, the capture filing step, the meeting minutes format and the back-link example of `/distill`. The first 3 now name the project, the example names a topic.
- `auto_link_entities.py` writes every link inside a table row, a line whose first non-space character is `|`, as the bare title, never with display text. A bare `|` would end the cell, and Basic Memory splits the escaped `\|` form Obsidian reads on its `|` and resolves a target ending in a backslash, which exists nowhere. The cell shows the title instead of the original word, so the link resolves in both Basic Memory and Obsidian. Outside tables, a link with display text is written as before. It never links inside a heading, `#` to `######`, where a link in the H1 could end up in a title `regen_titles.py` reads from it. Code fences and inline code were already skipped, a test now holds it.
- Every reader of a wiki-link reads the escaped table form, `X\|y` between the brackets, as a link to `X`, should a human or another tool write one. No pass writes it. The pattern lives once in `check_helpers.py`, and the 2 scripts that carried their own, `add_title_aliases.py` and `check_symmetric_relations.py`, now import it. Before, the target read `X\`, so `check_consistency.py` reported the link dead, `check_orphans.py` and `propose_pruning.py` missed it, the alias pass never counted it as a citation, and a relation written that way was an asymmetry. A backslash anywhere else stays part of the target.
- `check_frontmatter_damage.py` knows 2 more shapes. `about-entity-not-project` is an `- about` line linking X, where X is the entity of the folder the note sits in, its context's `client:`, `partner:`, title or aliases, or in an internal note `Internal` or the `organization`. On an email, a meeting or a session, the 3 types whose schema types `about` as the project brief, the repair is exact when the brief exists: the link becomes the brief's title, or the line goes when the note already links its project. Without a brief it needs review. On any other type the schema gives `about` another target or none, so the check proposes removing the line and asks for review. `table-cell-split-by-link` is a link with display text in a table row, outside code, `X|y` or the escaped `X\|y`, repaired to the bare title for the reason above. A repair that removes a line prints as `replace line N with 0 lines`.
- Measured on the demo content rewritten by Basic Memory. The 0.6.0 `add_about_relations.py` wrote nothing there, every demo email and meeting already links its project. The 0.5.3 one wrote 3 entity lines, into both project briefs and the referral deliverable, which the check reports as 3 hits to review. The 0.6.0 `auto_link_entities.py` wrote 36 links in 13 files, 2 of them in headings, the H1 of the onboarding playbook and of the referral agreement, and its only link in a table was already bare. The 0.6.1 pass writes 34 links in 13 files, none in a heading. A copy of the demo seeded with 5 notes the old passes break, a meeting with no `## Relations`, an email in a project folder without a brief, an internal brief and its meeting, and a note holding a table that names 2 aliases, gave 4 hits in 3 files after the 0.6.0 passes, 2 of each new shape, 3 of them exact, and 10 hits in 8 files after the 0.5.3 passes, 8 `about` lines of which 2 exact, plus the 2 table rows. On that copy the 0.6.1 passes link 2 notes to their project, list the email without a brief, write both table links as bare titles, and a second `--apply` of either pass changes no file. Following the stock prompt below on that copy damaged by the 0.6.0 passes repaired the 3 exact hits, left the email without a brief as the prompt proposes, and its phase 5 linked the internal meeting the 0.6.0 pass had skipped. On a copy damaged by the 0.5.3 pass and then the 0.6.0 ones, the same prompt took the 10 hits to 1, the email without a brief.
- Not changed, deliberately: the schemas, the note types, the templates, the hook and its wiring, and every script's name, arguments and defaults. `add_about_relations.py` still covers emails and meetings only, still prints its usage without an argument and writes only with `--apply`, and its summary now counts the notes without a project brief instead of errors. An `about` line a human wrote to another target is never touched by the pass. `auto_link_entities.py` still scans the whole vault on every run. The new `about` shape looks under `sources/` only, so it reports neither a project `/archive` moved to `archives/` nor the links the 0.5.x pass wrote in `sources/personal/`, a project's folder name when its brief had no title and a brief linked to its own title. The readers still accept the escaped table form, which costs nothing, while no writer emits it.

### Upgrade prompt, 0.6.0 to 0.6.1

The update recipe in the README brings every fixed script and the damage check. It never touches your notes, so a line an old pass wrote stays until something repairs it. This prompt accepts a workspace on 0.6.0 only. A workspace on 0.5.3 or older runs the 0.6.0 prompt above first.

It is only for a workspace that never ran `/sb-init`. `/sb-init` personalizes `basic-memory/schemas`, `.claude/rules` and `templates`, so on an initialized workspace phase 1 always finds drift and stops. An initialized workspace uses the prompt for a customized workspace below, which keeps those edits.

Paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace to boilerplate version 0.6.1, from 0.6.0. Work through the phases in order and stop at every gate.

Rules for the whole run:
- Never delete a note, a folder, or a frontmatter field. This upgrade only adds and rewrites. A repair that reads `replace line N with 0 lines` removes 1 body line the old passes wrote, and it goes through a diff like every other repair.
- Never write into sources/, knowledge/, atlas/, archives/ or inbox/ without showing me the exact diff first and waiting for my approval.
- If a step's precondition is not met, stop and tell me. Do not improvise around it.
- Report what you changed at the end, file by file.
- Run no script with `--apply` before phase 4 is done. `add_about_relations.py --apply` would add the project link next to each entity link phase 4 is about to replace.

Phase 1, preconditions.
Run `git status --porcelain`. If it prints anything, stop and ask me to commit or stash first: I need to be able to revert this whole upgrade with one command.
Read `initialized` in `.sb-config.json`. If it is true, stop and tell me to use the upgrade prompt for a customized workspace: `/sb-init` edited my schemas, rules and templates, the drift check below would list them, and phase 2 would overwrite them.
Read `boilerplate_version` in `.sb-config.json`. It must be 0.6.0. If it says anything else, stop and tell me which version it says: a workspace on 0.5.3 or older runs the 0.6.0 upgrade prompt first.
Then fetch the tags, one check per tag:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify --quiet 'v0.6.0^{commit}'
  git rev-parse --verify --quiet 'v0.6.1^{commit}'
If either prints nothing, stop and tell me which tag is missing. Then measure how far my infrastructure has drifted from 0.6.0:
  git diff --stat v0.6.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
If that lists no file, my infrastructure is stock and the rest of this prompt applies as written.
If it lists any file, STOP. I have customized the workspace, phase 2 would overwrite that work, and this is the wrong prompt. Show me the list and tell me to use the upgrade prompt for a customized workspace instead.

Phase 2, infrastructure.
  git checkout v0.6.1 -- .claude basic-memory/schemas basic-memory/scripts templates
Show me `git diff --cached --stat`. Every path it lists must sit under those 4 directories. This release changes nothing in a data zone, so there is nothing else to check out. Outside the recipe it changes only `CHANGELOG.md`, `CONTRIBUTING.md` and `.sb-config.json`: the first 2 are upstream's own documents and I do not need them, the third you edit in phase 5.
From here on, the hook runs the 0.6.1 alias pass after each of your writes, and may add an alias to a cited note on its own, without a diff. The table repairs of phase 4 write bare links, so they can give the linked note an alias. That is expected: those writes show in the final `git diff`, and phase 4 reruns the check before every shape, so they never leave a stale line number behind.

Phase 3, find the damage. Run, from the workspace root:
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
Show me its full output. Each hit is one line, `path:line: shape: what -> repair`. If its output ends with the note that PyYAML is not importable, rerun it once with an interpreter that has PyYAML, any python3 where `python3 -c 'import yaml'` succeeds, or `uvx --with pyyaml python -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded` when `uv` is installed. If neither is available, go on without it and tell me that a frontmatter broken in a shape the check does not know was not looked for. If it exits 0, tell me no note is damaged, then in phase 4 skip the shapes and do only its last 2 paragraphs.

Phase 4, repair, one shape at a time.
Take the shapes in this order, skipping the ones the check did not report: broken-opener, type-inside-folded-title, stray-alias-items, orphan-continuation, unescaped-backslash-alias, type-inside-list, concatenated-title, unquoted-title, truncated-wikilink, undecoded-quote-in-body, about-entity-not-project, table-cell-split-by-link, observation-block-indicator, observation-truncated, detached-list-items, swallowed-key-line, pass-write-in-excluded-folder, invalid-yaml.
A workspace that ran the 0.6.0 prompt usually reports only the 2 shapes new in 0.6.1, about-entity-not-project and table-cell-split-by-link. The others are listed because the check looks for them on every run.
For each shape:
1. Rerun the check first, since a repair shifts the line numbers of the lines below it, and work from that fresh output.
2. For every hit whose repair reads `replace lines A-B with N lines: ...`, prepare the edit that replaces exactly those lines of the file with exactly those lines, each one JSON-decoded from its quoted form, `\"` back to `"` and `\\` back to `\`, and changes nothing else. `replace line N with 0 lines` means removing that line and nothing else. When one file has several hits of the shape, apply them from the bottom of the file up, so the line numbers of the others stay true.
3. For every hit that says `needs review`, show me the lines around it, run `git log -p --follow -- <path>`, and quote the commit that changed that region. Then propose a repair or propose to leave it. When the hit also carries a replacement, that replacement is your proposal. For about-entity-not-project with no replacement, the note's project folder has no usable brief and the hit says why: propose to leave the line, and tell me which folder it is, since once that folder has a `README.md` with `type: project-brief` and a `title:`, the check gives the exact repair. For about-entity-not-project with 0 lines, the proposal is to remove the line, and when nothing else sits under its `## Relations` heading, also that heading and the blank lines the same commit added around them. Hits that one commit wrote can share one quote of that commit. For detached-list-items, the commit usually shows the key that was dropped above the items, and the proposal puts the items back under that key, appended to its list when the block still holds the key higher up, so no key appears twice. For swallowed-key-line, the commit shows where the swallowed line belonged, and the proposal puts it back there. For pass-write-in-excluded-folder, if the history shows a pass wrote them, the proposal is to remove the `- about [[...]]` line, the `## Relations` heading when nothing else sits under it, and the blank lines the same commit added around them. For invalid-yaml, never propose a repair, show me the frontmatter and leave it.
4. Before writing anything, show me one diff covering every file of that shape and wait for my approval, then apply it. Never carry an approval over to the next shape. A repair the check gives as exact is still only a proposal: it goes into the diff like every other, and I can refuse it hit by hit. If one would shorten a title or rewrite a line I may have written that way on purpose, point it out in the diff.
Whatever the check found, tell me 2 things the check cannot decide, and touch neither. `auto_link_entities.py` before 0.6.0 also wrote wiki-links into the Markdown files at the workspace root, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and `GETTING-STARTED.md`, and into the excluded files the check lists under its `note:` lines. Before 0.6.1 it also linked inside headings: run `grep -rnE '^#{1,6} .*\[\[' sources knowledge atlas archives inbox` and show me what it prints. Those links look exactly like mine, `git log -p -- <path>` on each file shows which commit added which link, and removing them is my call.
When every shape is done, rerun the check. It must exit 0, or list only invalid-yaml hits and the hits I chose to leave.

Phase 5, verification and close.
Set `boilerplate_version` to "0.6.1" in `.sb-config.json`, changing nothing else in the file.
Run `python3 -I basic-memory/scripts/add_about_relations.py --dry-run` and show me its output. Its `[OK]` lines are the emails and meetings that would get `- about [[<project title>]]`, its `[NO BRIEF]` lines the ones whose project folder has no brief, with the reason. Run it with `--apply` only after my approval, then rerun the dry-run, which must report 0 modified. It comes before the checks below because a link it writes can give the alias pass a new note to modify.
Then run:
  python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
  python3 -I basic-memory/scripts/check_double_frontmatter.py
  python3 -I basic-memory/scripts/generate_indexes.py --output-dir "$(mktemp -d)"
  python3 -I basic-memory/scripts/audit_field_usage.py
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
Show me the last lines of each. The test suite must end with OK. The alias dry-run must report 0 to modify: if it lists notes, show them to me and run it with `--apply` only after my approval, then rerun it. The damage check must exit 0, or list only invalid-yaml hits and the hits I chose to leave. The 0.6.0 prompt told me to replace `[[Internal]]` with `[[<organization>]]`: this release reverses that, an internal email or meeting links its project, and phase 4 already proposed it. If `check_consistency.py` still reports `[[Internal]]` as a dead link, show me each line and propose nothing.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`, and show me the count.
Then tell me what none of this verifies. The damage check knows only the shapes the old passes are known to leave. When no interpreter with PyYAML was available in phase 3, a frontmatter broken in a shape it does not know was not looked for at all. A wiki-link `auto_link_entities.py` wrote looks exactly like one I wrote, and only the git history tells them apart. A truncated observation it repaired may have been shortened by hand on purpose. A table cell repaired to the bare title shows the title instead of the word it held, which is the price of a link both tools resolve. The about-entity-not-project shape looks under `sources/` only: a project moved to `archives/` keeps the entity links the 0.5.x pass wrote, and in `sources/personal/` the 0.5.x pass linked a project's folder name when its brief had no title, and the brief itself to its own title. Neither is reported.
```

### Upgrade prompt, 0.6.0 to 0.6.1, for a customized workspace

Use this one if phase 1 of the prompt above told you to, meaning your workspace ran `/sb-init` or `git diff` against v0.6.0 reports changes under `.claude`, `basic-memory/schemas`, `basic-memory/scripts` or `templates`. An initialized workspace always lands here, since `/sb-init` edits its schemas, rules and templates. It carries the intent of each change rather than a diff, and it allows skipping an intent your fork already covers.

```
You are upgrading this second-brain workspace to boilerplate version 0.6.1, from 0.6.0. I have customized the infrastructure, so you must NOT check out upstream files over mine. For each change below, read my version of the file first, then decide between 3 outcomes: apply, adapt, or skip because my fork already covers the intent. Justify every skip in one line.

Rules for the whole run:
- Never overwrite one of my files wholesale. Every edit is surgical and preserves what I wrote. A file I never changed may be checked out from v0.6.1, since that overwrites nothing of mine.
- Never delete a note, a folder, or a schema field. A damage repair that reads `replace line N with 0 lines` removes 1 body line an old pass wrote, behind a diff like every other.
- Group your writes by intent. For each intent, show me one diff covering every file it touches and wait for one approval. A pass that rewrites my notes keeps its own gate, dry-run first. Never apply a change I have not seen in a diff, and never carry an approval over to the next intent.
- If you cannot tell whether my fork already covers an intent, ask me instead of deciding.
- If `initialized` is true in `.sb-config.json`, `/sb-init` personalized my infrastructure, and phase 0 lists those files as changed. That drift is mine and expected. Preserve it, never undo it as if it were a fork change, and never bring back what it removed when you port an upstream change into one of those files. Of them, 0.6.1 changes only the Maintenance scripts section of `.claude/rules/frontmatter.md`.
- `boilerplate_version` in `.sb-config.json` must say 0.6.0. If it says anything else, stop and tell me: a workspace on 0.5.3 or older runs the 0.6.0 prompt for a customized workspace first.

Phase 0, map my fork. Run:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify --quiet 'v0.6.0^{commit}'
  git rev-parse --verify --quiet 'v0.6.1^{commit}'
If either prints nothing, stop and tell me which tag is missing. Then run:
  git diff --stat v0.6.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
  git diff --stat v0.6.0..v0.6.1 -- .claude basic-memory/schemas basic-memory/scripts templates
Give me the list of files I changed, a sentence on what each change appears to do, and the files both lists share: those are the ones where upstream's change and mine meet.

Phase 1, the intents. For each, tell me apply, adapt or skip, and why. Start with the copy step below, then take the intents in their numbering, with 1 constraint: run no script with `--apply` before intent 4 is done, since `add_about_relations.py --apply` would add the project link next to each entity link intent 4 replaces.
The copy step. The tests and their fixtures arrive together, so no test ever runs against a missing fixture. The 6 fixtures under `basic-memory/scripts/tests_fixtures/damage/` are new files, and every changed test file tests an upstream script:
  git checkout v0.6.1 -- basic-memory/scripts/tests_fixtures/damage $(git diff --name-only v0.6.0..v0.6.1 -- basic-memory/scripts | grep '/test_')
If phase 0 lists one of those test files as changed by me, leave it out of the command and tell me. A test file stays red while my copy of the script it tests is still the 0.6.0 one: run it by its own name, `python3 -I -m unittest discover -s basic-memory/scripts -p 'test_check_helpers.py'` for instance, once that script is at 0.6.1. The whole suite runs in phase 3.

1. One wiki-link reader, which tolerates the escaped table form. Obsidian reads `[[X\|y]]` inside a table row, and a human or another tool may write it. Upstream's readers read its target as `X\`. Upstream now defines the pattern once, `WIKILINK_PATTERN` and `WIKILINK_RE` in `basic-memory/scripts/check_helpers.py`, where the target drops only the backslash right before `|` and keeps any other, and `add_title_aliases.py` and `check_symmetric_relations.py` import it instead of carrying their own. `check_consistency.py`, `check_orphans.py`, `propose_pruning.py` and `check_frontmatter_damage.py` already read links through `check_helpers.py`. If a script of mine reads wiki-links with its own pattern, tell me, and propose porting it onto `WIKILINK_RE`. `add_title_aliases.py` now imports `check_helpers.py`, so if I forked it, it needs that sibling present. The new tests sit in `test_check_helpers.py`, `test_check_consistency.py`, `test_check_orphans.py`, `test_propose_pruning.py`, `test_add_title_aliases.py` and `test_check_symmetric_relations.py`.

2. `about` names the project, not the entity. `basic-memory/schemas/email.md`, `meeting.md` and `session.md` type `about` as a ProjectBrief, while `add_about_relations.py` linked the client, the partner or the `organization`. Upstream's pass now links the `title:` of the brief of the note's project folder, its `README.md` or its `CLAUDE.md` declaring `type: project-brief`, lists under `[NO BRIEF]` every note whose folder has none, with the reason, skips a note whose `about` already links its project by title or alias, and adds the project next to any other `about`. It no longer reads `organization`. The rule of which folder is the project and which file is its brief lives in `basic-memory/scripts/note_types.py`, read by the pass and by the damage check, in the new section headed `The project a note belongs to, and its brief`: `ENTITY_ZONES`, `PROJECT_ZONES`, `BRIEF_FILES`, `PROJECT_ABOUT_TYPES`, `entity_folder`, `project_folder`, the `Brief` dataclass and `project_brief`, plus the `from dataclasses import dataclass` import. If I never changed `note_types.py`, it is a plain checkout from v0.6.1. If I forked it, port that whole section into my version, keeping my own tables: `git diff v0.6.0..v0.6.1 -- basic-memory/scripts/note_types.py` shows all of it, and the damage check imports every one of those names. Tests: `test_add_about_relations.py`. 4 skill texts taught the old target: the paragraphs on `## Relations` in `.claude/skills/references/save-conventions.md`, the `about` line of the body in `.claude/skills/capture/steps/step-02-file.md` and the `about` line of the format in `.claude/skills/ops-meeting-minutes/steps/step-02-format.md` now name the project, and the back-link example in `.claude/skills/distill/steps/step-03-publish.md` names a topic. If my fork changed what my own project folders or briefs look like, tell me before porting: the pass and the check both depend on that layout.

3. `auto_link_entities.py` must not break tables or headings. It wrote `[[Target|text]]` inside table rows and linked inside headings, where a link in the H1 could end up in a title `regen_titles.py` reads. Upstream now writes the bare `[[Target]]` in a row whose first non-space character is `|`, never with display text, escaped or not, and skips every heading line, `#` to `######`. Basic Memory splits the escaped form on its `|` and never resolves it. The cell shows the title instead of the original word, so the link resolves in both Basic Memory and Obsidian. Tests: the `Markdown` class of `test_auto_link_entities.py`.

4. Lines the old passes wrote must be repaired. `check_frontmatter_damage.py` has 2 new shapes, and 6 new fixtures in `basic-memory/scripts/tests_fixtures/damage/`: `about-entity-*.txt`, `about-internal-meeting.txt`, `about-organization-meeting.txt` and `table-cell-split.txt`. Bring the check to 0.6.1 first, a plain checkout if I never forked it, with the `note_types.py` of intent 2 and the `check_helpers.py` of intent 1, which it imports. Its test file also runs the 0.6.1 `add_about_relations.py`, so one of its tests stays red until intent 2 is done. Then run:
     python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
   If I renamed or added note zones, or forked `corpus.py`, tell me first. If its output ends with the note that PyYAML is not importable, rerun it once with an interpreter that has PyYAML, any python3 where `python3 -c 'import yaml'` succeeds, or `uvx --with pyyaml python -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded` when `uv` is installed. If neither is available, go on without it and tell me that a frontmatter broken in a shape the check does not know was not looked for. Each hit is one line, `path:line: shape: what -> repair`. Take the shapes in this order: broken-opener, type-inside-folded-title, stray-alias-items, orphan-continuation, unescaped-backslash-alias, type-inside-list, concatenated-title, unquoted-title, truncated-wikilink, undecoded-quote-in-body, about-entity-not-project, table-cell-split-by-link, observation-block-indicator, observation-truncated, detached-list-items, swallowed-key-line, pass-write-in-excluded-folder, invalid-yaml. For each shape, rerun the check first since repairs shift line numbers. Apply every `replace lines A-B with N lines: ...` exactly, each line JSON-decoded from its quoted form, changing nothing else, `with 0 lines` meaning the line is removed, and from the bottom of a file up when it holds several hits of the shape. The hook may add an alias to a cited note between 2 of your writes, which is why the check reruns first. For every `needs review` hit, show me the lines around it, run `git log -p --follow -- <path>` and quote the commit that changed that region, then propose a repair or propose to leave it, the replacement it carries when it has one. An about-entity-not-project hit with no replacement names a project folder without a usable brief: propose to leave it and name the folder. One with 0 lines sits on a type whose schema gives `about` another target: the proposal is removing the line, and when nothing else sits under its `## Relations` heading, also that heading and the blank lines the same commit added around them. Hits that one commit wrote can share one quote of that commit. For swallowed-key-line, the commit shows where the line belonged. Never propose a repair for invalid-yaml. Show me one diff per shape and wait. A repair the check gives as exact is still only a proposal, and I can refuse it hit by hit. If my fork's own skills or passes deliberately write `about [[<entity>]]`, the check reports those lines too: tell me, and treat them as hits I choose to leave unless I say otherwise. `auto_link_entities.py` before 0.6.1 also linked inside headings: run `grep -rnE '^#{1,6} .*\[\[' sources knowledge atlas archives inbox`, show me what it prints and leave it, only `git log -p` tells its links from mine. When every shape is done, the check must exit 0, or list only invalid-yaml hits and the hits I chose to leave.

5. What upstream deliberately did NOT change, so you do not "fix" it.
   The schemas, the note types and the templates: `git diff --stat v0.6.0..v0.6.1 -- basic-memory/schemas templates` lists nothing.
   Every script keeps its name, its arguments and its defaults. `add_about_relations.py` still prints its usage without an argument and writes only with `--apply`, but its summary line now ends with the count of notes without a project brief instead of errors: if a script of mine parses that line, tell me.
   `add_about_relations.py` still covers emails and meetings only. An `about` line I wrote to another target is never touched.
   The hook and its wiring in `.claude/settings.json` are unchanged.
   `auto_link_entities.py` still scans the whole vault on every run.
   The readers still accept `[[X\|y]]`, but no script writes it, and the damage check repairs it to `[[X]]` inside a table row. Do not bring back the escaped form in a pass of mine.

Phase 2, what falls outside every intent above.
Run `git diff --name-only v0.6.0..v0.6.1` and list anything you have not already handled. For each, say in one line whether it matters for my fork. `CONTRIBUTING.md` now says what `note_types.py` holds, which matters only if I accept contributions.

Phase 3, verification. First run `python3 -I basic-memory/scripts/add_about_relations.py --dry-run` and show me its output: it lists the emails and meetings that would get their project and the ones whose folder has no brief. Run it with `--apply` only after my approval, then rerun the dry-run, which must report 0 modified. It comes before the checks below because a link it writes can give the alias pass a new note to modify. Then run these against MY workspace and show me the output:
  python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
  python3 -I basic-memory/scripts/check_double_frontmatter.py
  python3 -I basic-memory/scripts/generate_indexes.py --output-dir "$(mktemp -d)"
  python3 -I basic-memory/scripts/audit_field_usage.py
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
The tests cover upstream's scripts: a failure in a script I forked is my fork's, sort it from what this upgrade broke. The alias dry-run must report 0 to modify on every note you repaired. If it lists notes, show them to me and run it with `--apply` only after my approval. The damage check must exit 0, or list only invalid-yaml hits and the hits I chose to leave. The 0.6.0 prompt told me to replace `[[Internal]]` with `[[<organization>]]`, and this release reverses that: if `check_consistency.py` still reports `[[Internal]]` as dead, show me each line and propose nothing.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`.
Expect findings on a customized workspace, and sort them into what comes from this upgrade and what comes from my fork.

Phase 4, close. Set `boilerplate_version` to "0.6.1" in `.sb-config.json`. Write me a short record of what you skipped and why. Tell me what none of this verifies: the damage check knows only the shapes upstream's old passes left, not what a pass of my own may have written, it did not look for an unknown shape if no interpreter with PyYAML was available, and only the git history tells a link `auto_link_entities.py` wrote from one I wrote. The about-entity-not-project shape looks under `sources/` only: a project `/archive` moved to `archives/` keeps the entity links the 0.5.x pass wrote, and in `sources/personal/` the 0.5.x pass linked a project's folder name when its brief had no title, and the brief itself to its own title. Neither is reported.
```

## 0.6.0

Every script now reads and writes frontmatter through one tested module. Until this release, 19 frontmatter readers spread over 17 files each implemented part of the YAML grammar, each misread a shape Basic Memory writes on sync, and the passes that rewrite notes rewrote what they had misread. This release ships the fixed scripts, a check that finds the damage the old ones left, and asks you to repair it behind a diff, since no checkout repairs data. A workspace that already ran the 0.5.3 prompt still needs this one: that prompt repaired one shape, list items under an inline `aliases:` line, its detection command misses the indented line the 0.5.3 pass leaves under a long alias, and the 0.5.3 pass kept producing that line after every write.

- The grammar is implemented once. On sync, Basic Memory writes block lists at column 0, folds any value past 80 columns onto a second line, and breaks quoted values the same way. Each script carried its own reader, none of them tested, and each knew a different subset: one skipped column-0 lists, another read a folded value on its first line only, a third read `notes: |` as the value `|`. `frontmatter.py` now reads and writes every shape those readers met, with one quoting policy, and keeps every line it does not need to touch byte for byte. `corpus.py` gives the one walk every pass uses, `note_types.py` the one table both retyping passes read, `check_helpers.py` the schema loader and the wiki-link table the checks share. `CONTRIBUTING.md` used to require each script to duplicate its reader, it now forbids it. The suite runs with `python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'`, over 230 tests on inputs shaped the way Basic Memory writes them.
- `add_title_aliases.py` broke long aliases, and its hook made it worse on every write. Basic Memory folds an alias longer than about 76 characters over 2 lines, which is what the alias of any title past 80 columns becomes. The 0.5.3 pass read the first line only, wrote an inline list over the key, and left the second line indented under it. That is invalid YAML, and on the next run the pass read the broken list as one more alias and wrapped it into a quoted item, so the line grew by a nested copy of itself after every write. The pass also built its ambiguity guard after dropping the note excluded by the hook, so a title shared by 2 notes could get an alias, it copied a title holding a backslash without escaping it and added a copy without backslashes on every later run, leaving a frontmatter PyYAML rejects, which the damage check finds without PyYAML and rebuilds from the title, it never matched a title with escaped quotes, and on Windows its paths never matched a note zone. All 5 are fixed.
- `retype_fallback_notes.py` broke the frontmatter it retyped. It dropped the newline after the opening delimiter, so the file started `---title:` and no reader saw a frontmatter at all. It also retyped a note in `knowledge/` that declares a `subtype`, against `.claude/rules/knowledge.md`. `retype_files.py` inserted `type:` after the first line of the block, which put it inside a `tags:` list, and its second run read the result as correct. Under any other first field the same insertion landed between the key and the rest of its value: a folded title, plain, single-quoted or double-quoted, an indented list, a `|` block. YAML then reads a truncated or empty first field and `type: meeting plan for Q3` or `type: meeting - a - b`, which mostly stays valid YAML, so PyYAML sees nothing, and the 0.6.0 `retype_files.py --apply` would delete those lines for good. The damage check finds all of these from the shape alone, with or without PyYAML, and both prompts repair them before any 0.6.0 pass writes a note. The 2 passes also typed the same file differently. Both now ask `note_types.py`, where the word right after the date wins, as the naming convention says.
- `fix_double_frontmatter.py` wrote on every invocation, `--dry-run` included. When it dropped a duplicate key it kept that key's list items, which reattached to the key above, and a body that opened on a `---` rule was taken for a second frontmatter and swallowed. 4 skills ran it unconditionally after every reindex: `/archive`, `/distill`, `/moc-new` and `/curate`. It now previews by default and writes only with `--apply`, the 4 skills run `check_double_frontmatter.py` first and repair only after you approve, and `/sb-doctor` documents the same.
- `align_entity_titles.py` replaced only the first line of a folded title, so the rest reattached to the identity: `Initech` plus a stray `2026` read as `Initech 2026`, and the second run reported the note compliant. It also wrote `title: Initech: Studio` unquoted, which is invalid YAML. Both are fixed, and `regen_titles.py` no longer gives an entity context file a `{Name}, Context` title.
- `add_observations_from_frontmatter.py` lost most of what it should write once Basic Memory had rewritten a note. It ignored column-0 lists, wrote a folded value truncated at its first line, and wrote `- [notes] |` for a block scalar. It also copied a quoted value into the body as written, quotes stripped and nothing decoded, `l''atelier` for `l'atelier` and `\"` for `"`, and `add_about_relations.py` wrote the same misread name into `- about` links, which then resolved to nothing. The 0.6.0 pass decodes, so on a note it already annotated it would add the right observation next to the stale one: the damage check finds the stale ones, and the prompts repair them first. On the demo content rewritten by Basic Memory, it planned 3 of the 9 observations of `Catalog Search`, 3 of 8 for `Client Onboarding`, 3 of 7 for `Lead Sourcing`, and cut the referral terms of Proseware at "the first engagement,". The new pass plans exactly what the old one planned on the original demo, and its dry-run now lists the observations the old one skipped.
- `add_about_relations.py` and `auto_link_entities.py` wrote where no pass may write. Both ignored the exclusions of `corpus.py` and wrote into `repo-files/`, which ships to a client repository, `prompts/`, `captures/` and `tmp/`, and `auto_link_entities.py` also linked the Markdown files at the workspace root: on the demo, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and `GETTING-STARTED.md`. Every writing pass now walks corpus notes only. `add_about_relations.py` covers emails and meetings, the 2 types whose path names their entity, and stops linking internal notes to `Internal`, a note that does not exist: it uses `organization` from `.sb-config.json` and skips them while it is null.
- The checks read whole titles. `check_consistency.py` truncated a folded title, so a link to the full title was reported dead and a link to its first line resolved, the false positive 0.5.3 listed as not fixed. `check_orphans.py` and `propose_pruning.py` missed links on full titles and aliases, `generate_indexes.py` wrote truncated titles into the indexes, `auto_link_entities.py` wrote links to them into note bodies, and `check_consistency.py` ignored a `topics:` block list. `check_symmetric_relations.py` printed its usage and exited 1 when run without an argument, as `/sb-doctor` ran it, exited 0 on a real asymmetry with `--check`, never checked the partner side of `co_delivered_with`, and read a link carrying a display label as a missing target. It now runs the check without an argument and exits 1 on any asymmetry. `check_unresolved_relations.py` counted every Basic Memory project in the index, it now counts the one `basic_memory_project` names, and says so when it is null. `curation_reminder.py` wrote a note without `schema_version` and notified on every run.
- `check_frontmatter_damage.py` is new and read-only. It knows the 15 shapes the 0.5.1 to 0.5.3 passes are known to leave, including any key line swallowed by another field that the retyping and title passes now refuse to touch, prints one line per hit with the exact repair when one can be computed, and says "needs review" when the repair takes a judgement, a list item whose key was lost, an observation a human may have shortened. With `--include-excluded` it also scans the folders `corpus.py` excludes. Wiki-links that `auto_link_entities.py` inserted look exactly like yours, so it names the files that hold some and leaves the question to `git log -p`. A frontmatter PyYAML rejects in a shape it does not know is reported, never repaired, and only when PyYAML is importable. On the demo content rewritten by Basic Memory, one run of each 0.5.3 pass leaves 1 hit, the truncated Proseware observation. A copy of the demo seeded with the notes those passes break, long titles, a double frontmatter, a hand-written block scalar, an identity that needs quotes, a title with a backslash, meetings with no `type:` under a long plain or single-quoted title, an indented list or a block scalar, an entity named in single quotes with an apostrophe, then run through the 0.5.2 alias pass and every 0.5.3 pass, gave 28 hits in 23 files, the 14 known shapes, the same with and without PyYAML. Following the stock prompt below on that copy repaired all of them.
- The writing passes converge in sequence, not in one run. A pass that adds links, `auto_link_entities.py`, can create new alias candidates, so a second full cycle of the passes may still add aliases, and a third changes nothing. Measured on the demo content.
- The 0.5.3 upgrade prompts are corrected in place. Both checked the tags with `git rev-parse --verify v0.5.2 v0.5.3`, which takes a single revision and always fails, so an agent following them literally stopped at phase 1. They now check one tag per call. A workspace that never got past that step can use the prompt below directly.
- Not changed, deliberately: the schemas, the note types, the templates, when the hook fires and its wiring in `.claude/settings.json`, and every script's name, arguments and defaults, except the 2 above. The hook only asks `corpus.py` for the note zones now, instead of keeping its own copy of the list. The alias pass still writes an inline list. `auto_link_entities.py` still scans the whole vault on every run, and the hook still reruns the full alias pass after every write.

### Upgrade prompt, 0.5.3 to 0.6.0

The update recipe in the README brings every fixed script and the damage check. It never touches your notes, so a note an old pass damaged stays damaged until something repairs it. This prompt accepts a workspace on 0.5.1, 0.5.2 or 0.5.3: 0.5.2 changed no infrastructure file, and 0.5.3 changed only `basic-memory/scripts/add_title_aliases.py`.

It is only for a workspace that never ran `/sb-init`. `/sb-init` personalizes `basic-memory/schemas`, `.claude/rules` and `templates`, the service types, the category enums and every trace of a zone it prunes, so on an initialized workspace phase 1 always finds drift and stops. An initialized workspace uses the prompt for a customized workspace below, which keeps those edits.

Paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace to boilerplate version 0.6.0, from 0.5.1, 0.5.2 or 0.5.3. Work through the phases in order and stop at every gate.

Rules for the whole run:
- Never delete a note, a folder, or a frontmatter field. This upgrade only adds and rewrites.
- Never write into sources/, knowledge/, atlas/, archives/ or inbox/ without showing me the exact diff first and waiting for my approval.
- If a step's precondition is not met, stop and tell me. Do not improvise around it.
- Report what you changed at the end, file by file.
- Run no 0.6.0 script with `--apply` before phase 4 is done. The new passes read some damaged shapes as valid frontmatter, `retype_files.py --apply` would delete for good the lines of a title, a list or a block caught in type-inside-folded-title, and `add_observations_from_frontmatter.py --apply` would add the right observation next to each undecoded-quote-in-body one instead of replacing it.

Phase 1, preconditions.
Run `git status --porcelain`. If it prints anything, stop and ask me to commit or stash first: I need to be able to revert this whole upgrade with one command.
Read `initialized` in `.sb-config.json`. If it is true, stop and tell me to use the upgrade prompt for a customized workspace: `/sb-init` edited my schemas, rules and templates, the drift check below would list them, and phase 2 would overwrite them.
Read `boilerplate_version` in `.sb-config.json`. It must be 0.5.1, 0.5.2 or 0.5.3. If it says anything else, stop and tell me which version it says. The baseline for the next step is v0.5.2 when it says 0.5.1 or 0.5.2, since their infrastructure is identical, and v0.5.3 when it says 0.5.3.
Then fetch the tags, one check per tag:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify --quiet 'v0.5.2^{commit}'
  git rev-parse --verify --quiet 'v0.5.3^{commit}'
  git rev-parse --verify --quiet 'v0.6.0^{commit}'
If any of the 3 prints nothing, stop and tell me which tag is missing. Then measure how far my infrastructure has drifted from my baseline, replacing BASELINE with v0.5.2 or v0.5.3:
  git diff --stat BASELINE..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
If that lists no file, my infrastructure is stock and the rest of this prompt applies as written.
If it lists any file, STOP. I have customized the workspace, phase 2 would overwrite that work, and this is the wrong prompt. Show me the list and tell me to use the upgrade prompt for a customized workspace instead.

Phase 2, infrastructure.
It comes before any repair: the hook in `.claude/settings.json` reruns the alias pass after every write you make, and the old pass would damage more notes while you repair the first ones.
  git checkout v0.6.0 -- .claude basic-memory/schemas basic-memory/scripts templates
Show me `git diff --cached --stat`. Every path it lists must sit under those 4 directories. This release changes nothing in a data zone, so there is nothing else to check out. Outside the recipe it changes only `CHANGELOG.md`, `CONTRIBUTING.md` and `.sb-config.json`: the first 2 are upstream's own documents and I do not need them, the third you edit in phase 5.
From here on, the hook runs the fixed alias pass after each of your writes, and may add an alias to a cited note on its own, without a diff. That is expected: those writes show in the final `git diff`, and the next phase reruns the check before every shape, so they never leave a stale line number behind.

Phase 3, find the damage. Run, from the workspace root:
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
Show me its full output. Each hit is one line, `path:line: shape: what -> repair`. If its output ends with the note that PyYAML is not importable, rerun it once with an interpreter that has PyYAML, any python3 where `python3 -c 'import yaml'` succeeds, or `uvx --with pyyaml python -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded` when `uv` is installed. If neither is available, go on without it and tell me that a frontmatter broken in a shape the check does not know was not looked for. If it exits 0, tell me no note is damaged and go to phase 5.

Phase 4, repair, one shape at a time.
Take the shapes in this order, skipping the ones the check did not report: broken-opener, type-inside-folded-title, stray-alias-items, orphan-continuation, unescaped-backslash-alias, type-inside-list, concatenated-title, unquoted-title, truncated-wikilink, undecoded-quote-in-body, observation-block-indicator, observation-truncated, detached-list-items, pass-write-in-excluded-folder, invalid-yaml.
The hook is the one writer you cannot hold back, and it runs the 0.6.0 alias pass after each of your writes, which is why type-inside-folded-title comes second: until it is repaired the hook reads a truncated title, and the repair also completes any alias the hook took from it.
For each shape:
1. Rerun the check first, since a repair shifts the line numbers of the lines below it, and work from that fresh output.
2. For every hit whose repair reads `replace lines A-B with N lines: ...`, prepare the edit that replaces exactly those lines of the file with exactly those lines, each one JSON-decoded from its quoted form, `\"` back to `"` and `\\` back to `\`, and changes nothing else. When one file has several hits of the shape, apply them from the bottom of the file up, so the line numbers of the others stay true.
3. For every hit that says `needs review`, show me the lines around it, run `git log -p --follow -- <path>`, and quote the commit that changed that region. Then propose a repair or propose to leave it. When the hit also carries a replacement, that replacement is your proposal. For detached-list-items, the commit usually shows the key that was dropped above the items, and the proposal puts the items back under that key, appended to its list when the block still holds the key higher up, so no key appears twice. For pass-write-in-excluded-folder, if the history shows a pass wrote them, the proposal is to remove the `- about [[...]]` line, the `## Relations` heading when nothing else sits under it, and the blank lines the same commit added around them. For invalid-yaml, never propose a repair, show me the frontmatter and leave it.
4. Before writing anything, show me one diff covering every file of that shape and wait for my approval, then apply it. Never carry an approval over to the next shape. A repair the check gives as exact is still only a proposal: it goes into the diff like every other, and I can refuse it hit by hit. If one would shorten a title or rewrite a line I may have written that way on purpose, point it out in the diff.
Whatever the check found, tell me that `auto_link_entities.py` before 0.6.0 also wrote wiki-links into the Markdown files at the workspace root, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and `GETTING-STARTED.md`, and into the excluded files the check lists under its `note:` lines, and that those links look exactly like mine. Do not touch them: `git log -p -- <path>` on each shows which commit added which link, and removing them is my call.
When every shape is done, rerun the check. It must exit 0, or list only invalid-yaml hits and the hits I chose to leave.

Phase 5, verification and close.
Set `boilerplate_version` to "0.6.0" in `.sb-config.json`, changing nothing else in the file. Run:
  python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
  python3 -I basic-memory/scripts/check_double_frontmatter.py
  python3 -I basic-memory/scripts/generate_indexes.py --output-dir "$(mktemp -d)"
  python3 -I basic-memory/scripts/audit_field_usage.py
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
Show me the last lines of each. The test suite must end with OK. The alias dry-run must report 0 to modify: if it lists notes, show them to me and run it with `--apply` only after my approval, then rerun it. The damage check must exit 0, or list only invalid-yaml hits and the hits I chose to leave. If `check_consistency.py` reports `[[Internal]]` as a dead link, the old `add_about_relations.py` wrote it into an internal note: show me each line and propose to replace it with `[[<organization>]]`, the `organization` of `.sb-config.json`. When `organization` is null, propose to leave it until `/sb-init` sets one, and expect `check_consistency.py` to exit 1 on it until then.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`, and show me the count.
Then tell me what none of this verifies. The damage check knows only the shapes the old passes are known to leave. When no interpreter with PyYAML was available in phase 3, a frontmatter broken in a shape it does not know was not looked for at all. A wiki-link `auto_link_entities.py` wrote looks exactly like one I wrote, and only the git history tells them apart. A truncated observation it repaired may have been shortened by hand on purpose. And `python3 -I basic-memory/scripts/add_observations_from_frontmatter.py --dry-run` may now plan observations the old pass skipped: that dry-run is mine to read, and to apply with `--apply` if I want them.
```

### Upgrade prompt, 0.5.3 to 0.6.0, for a customized workspace

Use this one if phase 1 of the prompt above told you to, meaning your workspace ran `/sb-init` or `git diff` against your baseline tag reports changes under `.claude`, `basic-memory/schemas`, `basic-memory/scripts` or `templates`. An initialized workspace always lands here, since `/sb-init` edits its schemas, rules and templates. It carries the intent of each change rather than a diff, and it allows skipping an intent your fork already covers.

```
You are upgrading this second-brain workspace to boilerplate version 0.6.0, from 0.5.1, 0.5.2 or 0.5.3. I have customized the infrastructure, so you must NOT check out upstream files over mine. For each change below, read my version of the file first, then decide between 3 outcomes: apply, adapt, or skip because my fork already covers the intent. Justify every skip in one line.

Rules for the whole run:
- Never overwrite one of my files wholesale. Every edit is surgical and preserves what I wrote. A file I never changed may be checked out from v0.6.0, since that overwrites nothing of mine.
- Never delete a note, a folder, or a schema field.
- Group your writes by intent. For each intent, show me one diff covering every file it touches and wait for one approval. A pass that rewrites my notes keeps its own gate, dry-run first. Never apply a change I have not seen in a diff, and never carry an approval over to the next intent.
- If you cannot tell whether my fork already covers an intent, ask me instead of deciding.
- If `initialized` is true in `.sb-config.json`, `/sb-init` personalized my infrastructure, and phase 0 lists those files as changed: `basic-memory/schemas/service.md` and its `service_type` enum, the `category` enums of the operational schemas, and, for a zone it pruned, `basic-memory/schemas/partner-context.md` removed and that zone's fields, counts and lines gone from the other schemas, `basic-memory/schemas/README.md`, `.claude/rules/frontmatter.md`, `.claude/rules/entities.md`, `.claude/rules/atlas.md`, `templates/entity-CLAUDE-template.md` and `templates/atlas-moc-template.md`. That drift is mine and expected. Preserve it, never undo it as if it were a fork change, and never bring back what it removed when you port an upstream change into one of those files. Of them, 0.6.0 changes only the Maintenance scripts section of `.claude/rules/frontmatter.md`.
- My baseline is v0.5.2 when `boilerplate_version` in `.sb-config.json` says 0.5.1 or 0.5.2, since their infrastructure is identical, and v0.5.3 when it says 0.5.3. If it says anything else, stop and tell me.

Phase 0, map my fork. Run, replacing BASELINE with my baseline:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify --quiet 'BASELINE^{commit}'
  git rev-parse --verify --quiet 'v0.6.0^{commit}'
If either prints nothing, stop and tell me which tag is missing. Then run:
  git diff --stat BASELINE..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
  git diff --stat BASELINE..v0.6.0 -- .claude basic-memory/schemas basic-memory/scripts templates
Give me the list of files I changed, a sentence on what each change appears to do, and the files both lists share: those are the ones where upstream's change and mine meet.

Phase 1, the intents. For each, tell me apply, adapt or skip, and why. Take them in this order, which is not their numbering:
  a. The copy step of intent 1, alone: the new modules, the damage check and the tests arrive together, so no test ever runs against a half-copied set.
  b. Intent 2, the alias pass, before you write anything else: the hook reruns it after every write, and the old pass damages more notes during the repair.
  c. Intent 9, the damage check and its repair, before any 0.6.0 pass writes a note: the new passes read some damaged shapes as valid frontmatter, `retype_files.py --apply` would delete for good the lines of a title, a list or a block caught in type-inside-folded-title, and `add_observations_from_frontmatter.py --apply` would add the right observation next to each undecoded-quote-in-body one instead of replacing it.
  d. The rest of intent 1, the readers of the scripts I forked.
  e. Intents 3 to 8, then 10.
Run no test, no check and no pass before step a is done, and no script with `--apply` before step c is done. After it, `test_frontmatter.py`, `test_check_helpers.py` and `test_check_frontmatter_damage.py` pass. Every other test file tests one upstream script, and stays red while my copy of that script is still the old one: run it by its own name, `python3 -I -m unittest discover -s basic-memory/scripts -p 'test_add_title_aliases.py'` for instance, once that script is at 0.6.0. The whole suite runs in phase 3.

1. One frontmatter reader, one walk, shared by every script. This is the central intent, the others follow from it.
   Basic Memory writes block lists at column 0 and folds any value past 80 columns onto a second line. Upstream's scripts each carried their own reader, each misread some of those shapes, and the passes rewrote what they misread. Upstream replaced them with `basic-memory/scripts/frontmatter.py`, a reader and writer that keeps every untouched line byte for byte, `iter_corpus_notes` in `corpus.py`, the one walk every pass uses, `note_types.py` and `check_helpers.py`, and a test suite under `basic-memory/scripts/test_*.py` with its fixtures in `basic-memory/scripts/tests_fixtures/`.
   The copy step. `frontmatter.py`, `note_types.py`, `check_helpers.py`, `check_frontmatter_damage.py` of intent 9, the tests and their fixtures are new files. Check them out together, in one command, so the suite never meets a module without the damage check its tests import:
     git checkout v0.6.0 -- basic-memory/scripts/frontmatter.py basic-memory/scripts/note_types.py basic-memory/scripts/check_helpers.py basic-memory/scripts/check_frontmatter_damage.py basic-memory/scripts/tests_fixtures $(git ls-tree --name-only v0.6.0 basic-memory/scripts/ | grep '/test_')
   If my fork already holds a file of one of those names, stop before the command and tell me. `corpus.py` existed before: if I never changed it, add it to the same command, and if I forked it, port upstream's changes into my version, keeping my exclusions and my zones: the new `rel_posix`, the `root` parameter of `is_corpus_note` and `git_ignored`, `git ls-files -z` in `git_ignored`, and backslash paths accepted by `in_note_zone` and `is_corpus_note`. `git diff BASELINE..v0.6.0 -- basic-memory/scripts/corpus.py` shows all of it. The damage check and several passes call `is_corpus_note(rel, root)`, and against the 0.5.3 version they stop on a `TypeError`. Every script upstream ships now imports these modules. A script of mine that upstream also ships and that I never changed is a plain checkout from v0.6.0. A script I forked keeps its own reader until you port it: tell me, for each forked script, whether its reader handles a column-0 list and a value folded over 2 lines. Test it on a scratch copy of the whole workspace, never on mine: each script finds the workspace from its own path, so a note copied anywhere else is never seen. Run `D=$(mktemp -d) && cp -R . "$D/ws"`, then write `$D/ws/sources/internal/shapes/2026-07-01-note-shapes.md` with this frontmatter between its 2 `---` lines:
     title: Globex Website Redesign, discovery workshop outcomes and the content inventory
       plan for Q3
     type: note
     aliases:
     - workshop outcomes
   Run the forked script from `$D/ws/basic-memory/scripts/`, dry-run first, and read what it reports or writes for that note. If its reader misses either shape, propose porting it onto `frontmatter.py`. If my fork reads frontmatter with a real YAML parser, its reading was never affected, but check its writing: a pass that writes a line by hand can still write invalid YAML, the way upstream's wrote `title: Initech: Studio`.
   Whatever you decide here, intent 9 runs the damage check: a fork that kept its own readers needs it most.

2. The alias pass must not break long aliases. Basic Memory folds an alias past about 76 characters over 2 lines. The 0.5.3 `add_title_aliases.py` read the first line, wrote an inline list over the key and left the second line indented under it, and every later run nested the broken list into itself. Upstream also fixed 4 smaller defects in it: the ambiguity guard must see every note before the hook's `--exclude` is applied, a backslash in a title must be escaped on write, escaped quotes decoded on read, and a Windows path must match a note zone. `.claude/hooks/title_aliases.py` now asks `corpus.in_note_zone` instead of copying the zone list.

3. The retyping passes must keep the frontmatter valid and agree. `retype_fallback_notes.py` dropped the newline after the opening `---`, so the file started `---title:`. It also retyped a `knowledge/` note that declares a `subtype`. `retype_files.py` inserted `type:` inside the first list of the block. Both now read one table, `note_types.py`, where the word right after the date in the file name wins. If I added note types or folder rules of my own to either script, carry them into `note_types.py` rather than back into the scripts.

4. `fix_double_frontmatter.py` must not write unasked. It wrote on every invocation, `--dry-run` included, kept the list items of a duplicate key it dropped, and swallowed a body that opened on a `---` rule. It is now dry-run by default with `--apply` to write. The 4 skills that ran it after every reindex, `/archive`, `/distill`, `/moc-new` and `/curate`, now run `check_double_frontmatter.py` first and repair only after approval, and `/sb-doctor` documents the same. If I call it from a skill or a script of my own, add `--apply` where I really want it to write.

5. Entity titles must be replaced whole and quoted when needed. `align_entity_titles.py` replaced the first line of a folded title only, and wrote `title: Initech: Studio` unquoted. `regen_titles.py` gave a context file a `{Name}, Context` title.

6. The observation pass must read what Basic Memory writes. `add_observations_from_frontmatter.py` ignored column-0 lists, truncated folded values and wrote `- [notes] |` for a block scalar. If I changed its table of fields per type, keep my table.

7. Passes must write only into corpus notes. `add_about_relations.py` and `auto_link_entities.py` ignored `corpus.py` and wrote into `repo-files/`, `prompts/`, `captures/` and `tmp/`, and `auto_link_entities.py` linked the Markdown files at the workspace root too. Both now walk `iter_corpus_notes`. `add_about_relations.py` covers emails and meetings only, and takes the internal entity from `organization` in `.sb-config.json` instead of writing `- about [[Internal]]`. If I excluded folders of my own, they belong in `corpus.py`. If I added a note zone, declare it in `NOTE_ZONES` of `corpus.py`: that tuple is where every writing pass, the hook and the damage check learn where notes live. The `ZONES` list at the top of `add_title_aliases.py` is not the place, it only says where the pass reads wiki-links.

8. The checks must read whole titles and exit on real findings. `check_consistency.py`, `check_orphans.py`, `propose_pruning.py` and `generate_indexes.py` read a folded title on its first line. `check_symmetric_relations.py` now runs the check when given no argument, exits 1 on any asymmetry, checks both sides of `co_delivered_with` and reads `[[Target|label]]` as its target. `check_unresolved_relations.py` counts only the Basic Memory project `basic_memory_project` names. `curation_reminder.py` writes `schema_version` and notifies once. If a script or a skill of mine relies on the old exit code of `check_symmetric_relations.py`, tell me.

9. Notes the old passes damaged must be repaired. The fixed passes do not repair them. The check arrived with the copy step of intent 1. Run:
     python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
   If I renamed or added note zones, tell me first: the check walks the zones in `NOTE_ZONES` of `corpus.py`, see intent 7. If its output ends with the note that PyYAML is not importable, rerun it once with an interpreter that has PyYAML, any python3 where `python3 -c 'import yaml'` succeeds, or `uvx --with pyyaml python -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded` when `uv` is installed. If neither is available, go on without it and tell me that a frontmatter broken in a shape the check does not know was not looked for. Each hit is one line, `path:line: shape: what -> repair`. Take the shapes in this order: broken-opener, type-inside-folded-title, stray-alias-items, orphan-continuation, unescaped-backslash-alias, type-inside-list, concatenated-title, unquoted-title, truncated-wikilink, undecoded-quote-in-body, observation-block-indicator, observation-truncated, detached-list-items, pass-write-in-excluded-folder, invalid-yaml. For each shape, rerun the check first since repairs shift line numbers. type-inside-folded-title comes second because the hook, which runs the alias pass after each of your writes, reads a truncated title until it is repaired, and the repair also completes any alias the hook took from it. Apply every `replace lines A-B with N lines: ...` exactly, each line JSON-decoded from its quoted form, changing nothing else, and from the bottom of a file up when it holds several hits of the shape. The hook may add an alias to a cited note between 2 of your writes, which is why the check reruns first. For every `needs review` hit, show me the lines around it, run `git log -p --follow -- <path>` and quote the commit that changed that region, then propose a repair or propose to leave it, the replacement it carries when it has one. For pass-write-in-excluded-folder, a pass wrote the blank lines around the relation too, the same commit shows them. Never propose a repair for invalid-yaml. Show me one diff per shape and wait. A repair the check gives as exact is still only a proposal: it goes into the diff like every other, and I can refuse it hit by hit. If one would shorten a title or rewrite a line I may have written that way on purpose, point it out in the diff. Files the check names as holding wiki-links in excluded folders stay untouched: `auto_link_entities.py` also wrote there and into the Markdown files at the workspace root, and only `git log -p` tells its links from mine. When every shape is done, the check must exit 0, or list only invalid-yaml hits and the hits I chose to leave.

10. What upstream deliberately did NOT change, so you do not "fix" it.
   The schemas, the note types and the templates: `git diff --stat v0.5.3..v0.6.0 -- basic-memory/schemas templates` lists nothing.
   Every script keeps its name, its arguments and its defaults, with 2 exceptions: `fix_double_frontmatter.py` is now dry-run by default, and `check_symmetric_relations.py` runs the check without an argument and exits 1 on an asymmetry.
   The alias pass still writes an inline list, `aliases: [a, b]`. Basic Memory turning it back into a column-0 block list on sync is expected, and every pass reads that form.
   When the hook fires, and its wiring in `.claude/settings.json`, are unchanged. Only its zone test moved to `corpus.in_note_zone`, intent 2.
   The email and meeting schemas still type `about` as a project brief, while `add_about_relations.py` links the entity. That mismatch predates this release.
   `auto_link_entities.py` still scans the whole vault on every run, and the hook still reruns the whole alias pass after every write.

Phase 2, what falls outside every intent above.
Run `git diff --name-only BASELINE..v0.6.0` and list anything you have not already handled. For each, say in one line whether it matters for my fork. `CONTRIBUTING.md` now forbids duplicating the frontmatter reader, which matters only if I accept contributions.

Phase 3, verification. Run these against MY workspace and show me the output:
  python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
  python3 -I basic-memory/scripts/check_double_frontmatter.py
  python3 -I basic-memory/scripts/generate_indexes.py --output-dir "$(mktemp -d)"
  python3 -I basic-memory/scripts/audit_field_usage.py
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
The tests cover upstream's scripts: a failure in a script I forked is my fork's, sort it from what this upgrade broke. The alias dry-run must report 0 to modify on every note you repaired. If it lists notes, show them to me and run it with `--apply` only after my approval. The damage check must exit 0, or list only invalid-yaml hits and the hits I chose to leave. If `check_consistency.py` reports `[[Internal]]` as dead, the old `add_about_relations.py` wrote it: show me each line and propose to replace it with `[[<organization>]]` from `.sb-config.json`, or to leave it while `organization` is null.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`.
Expect findings on a customized workspace, and sort them into what comes from this upgrade and what comes from my fork.

Phase 4, close. Set `boilerplate_version` to "0.6.0" in `.sb-config.json`. Write me a short record of what you skipped and why. Tell me what none of this verifies: the damage check knows only the shapes upstream's old passes left, not what a pass of my own may have written, it did not look for an unknown shape if no interpreter with PyYAML was available, and only the git history tells a link `auto_link_entities.py` wrote from one I wrote.
```

## 0.5.3

The title alias pass no longer damages notes that Basic Memory has rewritten. This release ships one fixed script, and asks you to repair the notes the old pass may already have damaged, since no checkout repairs data. Reported and fixed by @dailuong-amg in [#1](https://github.com/philippe-desplats/second-brain/pull/1).

- `add_title_aliases.py` only read an indented block list. On sync, Basic Memory 1.0 rewrites `aliases:` as a block list with no indentation, `- Title` at column 0, which is valid YAML. The pass read the field as absent, wrote an inline `aliases: [Title]` over the key line and left the old items below it. The frontmatter became invalid YAML, and every synonym the note carried fell out of the list. The dry-run that followed reported 0 to modify, and the PostToolUse hook reran the pass after every write, so the damage spread with nothing pointing at it. Both readers in the script now accept a list item at any indentation.
- The fixed script does not repair a damaged note. It reads the inline list, finds the title in it and reports the note as compliant, stray lines included. The upgrade prompts below detect the shape the bug leaves and merge the stray items back into the list, behind a diff you approve.
- On the demo content, a Basic Memory style rewrite followed by one run of the 0.5.2 pass damaged 9 notes, and pushed the synonyms of 2 demo topics out of their list. Whether your own workspace is affected depends on whether Basic Memory rewrote your frontmatter, and the detection step of the prompts answers that rather than a guess.
- Not fixed here: `check_consistency.py` still reports a link as dead when its target's `title:` is folded over 2 lines. Basic Memory resolves those links, so they are false positives.

### Upgrade prompt, 0.5.2 to 0.5.3

The update recipe in the README brings the fixed script. It never touches your notes, so a note the old pass damaged stays damaged until something repairs it.

Paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace from boilerplate version 0.5.2 to 0.5.3. Work through the phases in order and stop at every gate.

Rules for the whole run:
- Never delete a note, a folder, or a frontmatter field. This upgrade only adds and rewrites.
- Never write into sources/, knowledge/, atlas/, archives/ or inbox/ without showing me the exact diff first and waiting for my approval.
- If a step's precondition is not met, stop and tell me. Do not improvise around it.
- Report what you changed at the end, file by file.

Phase 1, preconditions.
Run `git status --porcelain`. If anything is uncommitted, stop and ask me to commit or stash first: I need to be able to revert this whole upgrade with one command.
Read `boilerplate_version` in `.sb-config.json`. It must be 0.5.2 or 0.5.1. If it says anything else, stop and tell me which version it says.
Then measure how far my infrastructure has drifted from upstream. The baseline is v0.5.2 in both cases, since its infrastructure is identical to v0.5.1:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify v0.5.2 && git rev-parse --verify v0.5.3
If either tag is missing, stop and tell me. Then run:
  git diff --stat v0.5.2..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
If that lists no file, my infrastructure is stock and the rest of this prompt applies as written.
If it lists any file, STOP. I have customized the workspace, phase 2 would overwrite that work, and this is the wrong prompt. Show me the list and tell me to use the upgrade prompt for a customized workspace instead.

Phase 2, the fixed script.
It comes before any repair: the hook in `.claude/settings.json` reruns the alias pass after every write you make, and the old pass would damage more notes while you repair the first ones.
  git checkout v0.5.3 -- basic-memory/scripts/add_title_aliases.py
Show me `git diff --cached --stat`. It must list that one file and nothing else.

Phase 3, find the damage. Run, from the workspace root:
  git ls-files -z -- 'sources/*.md' 'knowledge/*.md' 'atlas/*.md' 'archives/*.md' 'inbox/*.md' | xargs -0 awk 'FNR==1{fm=($0=="---"); a=0; next} fm&&$0=="---"{fm=0} fm&&/^aliases:[ \t]*\[/{a=1; next} fm&&a&&/^[ \t]*-[ \t]/{print FILENAME": "$0; next} {a=0}'
Each line it prints is a list item sitting under an inline `aliases: [...]` line in a frontmatter, the shape the old pass left behind. That frontmatter is invalid YAML, and the stray items are the aliases the note held before the old pass ran, synonyms included.
If it prints nothing, tell me no note is damaged and go to phase 5.

Phase 4, repair.
The command prints the stray items only, so read the frontmatter of each listed file to see what sits inside the brackets.
For each file listed, rewrite its `aliases:` as one inline list: the items already inside the brackets first, in their order, then each stray item not already present, in its order, in double quotes when the value contains a comma, a colon, a bracket or a quote. Delete the stray lines. Change nothing else in the file.
Show me one diff covering every file and wait for my approval, then apply it.
If a frontmatter looks damaged in a way that does not match this shape, show it to me and leave it.
Rerun the phase 3 command, which must print nothing.

Phase 5, verification and close.
Set `boilerplate_version` to "0.5.3" in `.sb-config.json`. Run:
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
The alias dry-run must report 0 to modify on every note you repaired. If it lists notes to modify, show them to me and run it with `--apply` only after my approval.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`, and show me the count.
Then tell me what none of this verifies: the phase 3 command finds only the shape this bug leaves, not every invalid frontmatter.
```

### Upgrade prompt, 0.5.2 to 0.5.3, for a customized workspace

Use this one if phase 1 of the prompt above told you to, meaning `git diff v0.5.2..HEAD` reports changes under `.claude`, `basic-memory/schemas`, `basic-memory/scripts` or `templates`. It carries the intent of each change rather than a diff, and it allows skipping an intent your fork already covers.

```
You are upgrading this second-brain workspace from boilerplate version 0.5.2 to 0.5.3. I have customized the infrastructure, so you must NOT check out upstream files over mine. For each change below, read my version of the file first, then decide between three outcomes: apply, adapt, or skip because my fork already covers the intent. Justify every skip in one line.

Rules for the whole run:
- Never overwrite one of my files wholesale. Every edit is surgical and preserves what I wrote.
- Never delete a note, a folder, or a schema field.
- Group your writes by intent. For each intent, show me one diff covering every file it touches and wait for one approval. Never apply a change I have not seen in a diff, and never carry an approval over to the next intent.
- If you cannot tell whether my fork already covers an intent, ask me instead of deciding.
- My `boilerplate_version` may say 0.5.1. 0.5.2 changed no infrastructure file, so this prompt applies as written.

Phase 0, map my fork. Run:
  git remote get-url upstream || git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git rev-parse --verify v0.5.2 && git rev-parse --verify v0.5.3
If either tag is missing, stop and tell me. Then run:
  git diff --stat v0.5.2..HEAD -- basic-memory/scripts/add_title_aliases.py .claude/hooks .claude/settings.json
This release changes only the alias pass. Tell me whether I changed the pass, its hook or its wiring, and for each change a sentence on what it appears to do.

Phase 1, the intents. Work through them in order. For each, tell me apply, adapt or skip, and why.

1. The alias pass must read a block list at any indentation.
   On sync, Basic Memory 1.0 rewrites `aliases:` as a block list with no indentation, `- Title` at column 0, which is valid YAML. Upstream's `add_title_aliases.py` matched indented items only, in 2 places: `parse_keys()`, which reads the field, and the loop in `main()` that skips the old items when it rewrites the field. Reading the field as absent, the pass wrote an inline list over the key line and left the old items below it, which is invalid YAML. `git diff v0.5.2..v0.5.3 -- basic-memory/scripts/add_title_aliases.py` shows both regexes, `^[ \t]+-` becoming `^[ \t]*-`.
   If my script is still upstream's, check it out from v0.5.3. If I forked it, port the 2 changes. If my fork reads frontmatter with a real YAML parser, it never had the bug, so skip and say so.
   Do this intent before the next one: the hook reruns the pass after every write, and the old pass would damage more notes during the repair. If I rewired or removed the hook, tell me what it does now.

2. Notes the old pass damaged must be repaired.
   The fixed pass does not repair them: it finds the title in the inline list and reports the note as compliant. Run, from the workspace root, adapting the zone paths if I renamed or added note zones:
     git ls-files -z -- 'sources/*.md' 'knowledge/*.md' 'atlas/*.md' 'archives/*.md' 'inbox/*.md' | xargs -0 awk 'FNR==1{fm=($0=="---"); a=0; next} fm&&$0=="---"{fm=0} fm&&/^aliases:[ \t]*\[/{a=1; next} fm&&a&&/^[ \t]*-[ \t]/{print FILENAME": "$0; next} {a=0}'
   Each line it prints is a list item sitting under an inline `aliases: [...]` line, the shape the old pass left behind. The stray items are the aliases the note held before, synonyms included. If it prints nothing, say so and move on.
   The command prints the stray items only, so read the frontmatter of each listed file to see what sits inside the brackets. For each file listed, rewrite its `aliases:` as one inline list: the items already inside the brackets first, in their order, then each stray item not already present, in its order, in double quotes when the value contains a comma, a colon, a bracket or a quote. Delete the stray lines and change nothing else. Show me one diff covering every file and wait. If a frontmatter looks damaged in a way that does not match this shape, show it to me and leave it. After applying, rerun the command, which must print nothing.

3. What upstream deliberately did NOT change, so you do not "fix" it.
   `is_continuation()` still matches indented lines only. A list item at column 0 never continued a folded scalar.
   The pass still writes an inline list, `aliases: [a, b]`. Basic Memory turning it back into a block list on sync is expected, and the fixed pass now reads that form.
   The hook and its wiring in `.claude/settings.json` are unchanged.
   `check_consistency.py` still reports a link as dead when its target's `title:` is folded over 2 lines. It is a known false positive, not fixed in this release.

Phase 2, what falls outside every intent above.
Run `git diff --name-only v0.5.2..v0.5.3` and list anything you have not already handled. For each, say in one line whether it matters for my fork.

Phase 3, verification. Run these against MY workspace and show me the output:
  python3 -I basic-memory/scripts/add_title_aliases.py
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
The alias dry-run must report 0 to modify on every note you repaired. If it lists notes to modify, show them to me and run it with `--apply` only after my approval.
If `basic_memory_project` in `.sb-config.json` is not null, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`.
Expect findings on a customized workspace, and sort them into what comes from this upgrade and what comes from my fork.

Phase 4, close. Set `boilerplate_version` to "0.5.3" in `.sb-config.json`. Write me a short record of what you skipped and why. Tell me that the detection command finds only the shape this bug leaves, not every invalid frontmatter.
```

## 0.5.2

The 0.5.1 upgrade prompt for a customized workspace is corrected. A run on a forked workspace showed 3 gaps, and the prompt in the 0.5.1 section below now closes them. Nothing else changed, no rule, schema, script, hook or template.

- It never asked for the schema declarations. 0.5.1 declared `aliases` on every schema and `title` on `person`, `topic` and `service`, and a literal reading of the intents skipped all of it. Validation does not reject an undeclared field, so nothing failed, but `audit_field_usage.py` then reports both as used in notes and declared in no schema. Intents 2 and 3 now carry the declarations, and the verification phase runs that audit.
- It did not warn that a renamed zone breaks other scripts. It adapted the `ZONES` table of `align_entity_titles.py` and stopped there, while `check_symmetric_relations.py` hard-codes `sources/partners`, scans 0 partners in a renamed zone and flags every client relation as an orphan. Intent 2 now asks for a search of the old zone paths, and the verification phase names the symptom.
- It asked for an approval before every single write, more than 30 on a small fork. Approvals are now grouped by intent, one diff per intent, and each pass that rewrites notes keeps its own gate.
- A second run on a fresh fork copy found 3 smaller gaps, now closed. The zone search covered paths but not the bare zone name in the skills and `.sb-config.json`, the verification looked for an audit section that is printed only when it has entries, and the `settings.json` merge did not forbid reformatting the file.

### Upgrade prompt, 0.5.1 to 0.5.2

A stock workspace has nothing to apply: set `boilerplate_version` to "0.5.2" in `.sb-config.json`.

If you already ran the 0.5.1 prompt for a customized workspace, paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace from boilerplate version 0.5.1 to 0.5.2. This release corrects the 0.5.1 upgrade prompt for a customized workspace and changes no infrastructure file. Do not check out anything from upstream. For each step below, show me one diff covering every file it touches and wait for my approval before writing.

1. Run `git fetch upstream --tags`, then `python3 -I basic-memory/scripts/audit_field_usage.py`, and look for its section titled "Fields used in notes but declared in no schema". The audit prints it only when it has an entry, so tell me whether it appeared, even when it did not. For every `aliases` or `title` listed there, propose declaring the field in that schema with the line upstream uses, which `git show v0.5.2:basic-memory/schemas/person.md` carries for both. Also declare `aliases?` on any schema of mine that still lacks it, since the alias pass writes the field on any cited note.
2. If I renamed an entity zone, search `basic-memory/scripts` and `.claude` for the old path, for example `sources/partners`, and list every hit. Then search `.claude/skills` and `.sb-config.json` for the bare zone name, since `/ops-init-project` reads the `zones` array and takes a renamed zone for a pruned one. `check_symmetric_relations.py` is the one that fails silently. Propose the edits and wait.
3. Set `boilerplate_version` to "0.5.2" in `.sb-config.json`. Rerun the audit and `python3 -I basic-memory/scripts/check_symmetric_relations.py --check`, and show me both outputs.
```

## 0.5.1

Wiki-links now resolve, in Basic Memory and in Obsidian. This release asks for 2 gestures the update recipe cannot make for you: install the Alias Linker community plugin in Obsidian, and run the title and alias passes once over your own notes. The upgrade prompts below carry both.

- Wiki-links resolved almost nothing, and the rule file explained why wrongly. `.claude/rules/frontmatter.md` claimed a link resolves on `client:`, `partner:`, `name:` or `title:`, when Basic Memory reads `title:` alone and Obsidian reads the file basename alone. With every context file named `CLAUDE.md` and every brief named `README.md`, a correctly written link reached nothing in either tool. On the demo content, 22 of the 42 relations in the note zones pointed at nothing in Basic Memory. They all resolve now. The rule is rewritten around what each tool actually reads.
- Entity titles now equal their identity field. Basic Memory needs `title:` to match the name used in links, so `align_entity_titles.py` sets it from `client:`, `partner:` or `name:`, dry-run by default. The 6 demo entity notes are aligned, and the entity template, the 2 context schemas and `/ops-init-project` stop producing the old `{Name}, Context` title or no title at all, which would have recreated the defect on the next client. The H1 keeps its wording, only the frontmatter field moves.
- Obsidian gets its bridge. `add_title_aliases.py` copies a cited note's `title:` into its `aliases:`, and `.claude/hooks/title_aliases.py`, wired by a new project `.claude/settings.json`, reruns it after every write, so a newly cited note gets its alias in the same session. `corpus.py` holds the definition of a note both depend on. `aliases` is now declared on every schema, and `title` on `person`, `topic` and `service`, since `audit_field_usage.py` would otherwise report both as used and declared nowhere. Aliases only resolve through the Alias Linker community plugin (`johannrichard/alias-linker`), since Obsidian itself ignores them for link resolution by design. Without the plugin they sit in the frontmatter and do nothing. It is not preinstalled: `.obsidian/community-plugins.json` stays `[]`, and Bases still needs nothing.
- `check_unresolved_relations.py` measures the real damage. It reads the Basic Memory index in read-only mode and sorts each dead target into something actionable. Reindex first. The count covers the whole workspace, so the example links in `basic-memory/schemas/` and the READMEs appear in it too, and only some of them are recognized as examples.
- `check_consistency.py` called alias-reachable links dead. Its wiki-link resolver built its table from `title:`, `client:`, `partner:`, `name:` and `subject:` and never read `aliases:`, although the `topic` schema declares the field for exactly this purpose and the 3 demo topics use it. A link written on the alias `onboarding` of a topic titled `Client Onboarding` was therefore reported as resolving to nothing, and every such link inflated a count the check exists to make actionable. Both YAML spellings of the list are now read, the inline `[a, b]` the demo topics use and the block form, so a note reformatted later does not drop out of the table. A link that genuinely resolves to nothing is still reported and the check still exits non-zero. It stays permissive on purpose, so it under-reports: a link reachable only through `client:` resolves in neither tool and this check will not flag it. Use `check_unresolved_relations.py` for the real count.

### Upgrade prompt, 0.5.0 to 0.5.1

The update recipe in the README brings the rule, the 4 scripts, the hook and the corrected templates. It cannot install a plugin in your Obsidian, and it never touches your notes, so your entity titles and aliases stay as they are until something aligns them.

Paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace from boilerplate version 0.5.0 to 0.5.1. Work through the phases in order and stop at every gate.

Rules for the whole run:
- Never delete a note, a folder, or a frontmatter field. This upgrade only adds and rewrites.
- Never write into sources/, knowledge/, atlas/, archives/ or inbox/ without showing me the exact diff first and waiting for my approval.
- If a step's precondition is not met, stop and tell me. Do not improvise around it.
- Report what you changed at the end, file by file.

Phase 1, preconditions.
Run `git status --porcelain`. If anything is uncommitted, stop and ask me to commit or stash first: I need to be able to revert this whole upgrade with one command.
Read `boilerplate_version` in `.sb-config.json`. If it is not 0.5.0, stop and tell me which version it says.
Then measure how far my infrastructure has drifted from the version I cloned:
  git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git diff --stat v0.5.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
If that lists no file, my infrastructure is stock and the rest of this prompt applies as written.
If it lists any file, STOP. I have customized the workspace, phase 2 would overwrite that work, and this is the wrong prompt. Show me the list and tell me to use the upgrade prompt for a customized workspace instead.

Phase 2, infrastructure.
Phase 1 proved my infrastructure is stock, so this checkout overwrites nothing of mine:
  git checkout v0.5.1 -- .claude basic-memory/schemas basic-memory/scripts templates
Show me `git diff --stat --cached` afterwards so I can see the size of what arrived.
Tell me that `.claude/settings.json` is new and wires a hook that takes effect from my next session.

Phase 3, the plugin. This one is mine to do, you cannot.
If I use Obsidian, tell me to open Settings, Community plugins, turn off Restricted mode if it is on, then Browse, search for Alias Linker, install it and enable it. Wait until I confirm.
If I do not use Obsidian, skip this phase and say so. The aliases are harmless without it.

Phase 4, my entity titles.
Run this dry-run and show me the full output:
  python3 -I basic-memory/scripts/align_entity_titles.py
Every line it proposes changes the `title:` of one of my entity notes to its `client:`, `partner:` or `name:` value. Wait for my approval, then run it with `--apply`.
A changed title breaks any link written against the old one. For each title that changed from an old value, search my note zones for `[[old title` and show me the matches. Propose rewriting each to the new title and wait for my approval. Change nothing else in those notes.

Phase 5, my aliases.
Run this dry-run and show me the output:
  python3 -I basic-memory/scripts/add_title_aliases.py
Wait for my approval, then run it once with `--apply`. Rerun the dry-run, which must report 0 to modify. If it lists ambiguous titles, two notes share a title: show them to me and leave them, the fix is to retitle one of them and that is my call.

Phase 6, verification and close.
Set `boilerplate_version` to "0.5.1" in `.sb-config.json`. Run:
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
If Basic Memory is configured, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`, and show me the count.
Then tell me what none of this verifies: only clicking a wiki-link in Obsidian proves Alias Linker resolves it. The Backlinks pane is no proof, it mixes linked and unlinked mentions, and unlinked mentions do read aliases.
```

### Upgrade prompt, 0.5.0 to 0.5.1, for a customized workspace

Use this one if phase 1 of the prompt above told you to, meaning `git diff v0.5.0..HEAD` reports changes under `.claude`, `basic-memory/schemas`, `basic-memory/scripts` or `templates`. It carries the intent of each change rather than a diff, and it allows skipping an intent your fork already covers.

```
You are upgrading this second-brain workspace from boilerplate version 0.5.0 to 0.5.1. I have customized the infrastructure, so you must NOT check out upstream files over mine. For each change below, read my version of the file first, then decide between three outcomes: apply, adapt, or skip because my fork already covers the intent. Justify every skip in one line.

Rules for the whole run:
- Never overwrite one of my files wholesale. Every edit is surgical and preserves what I wrote.
- Never delete a note, a folder, or a schema field.
- Group your writes by intent. For each intent, show me one diff covering every file it touches and wait for one approval. A pass that rewrites my notes (titles, links, aliases) keeps its own gate, dry-run first. Never apply a change I have not seen in a diff, and never carry an approval over to the next intent.
- If you cannot tell whether my fork already covers an intent, ask me instead of deciding.

Phase 0, map my fork. Run:
  git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git diff --stat v0.5.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
Give me the list of files I changed, and for each one a sentence on what my change appears to do.

Phase 1, the intents. Work through them in order. For each, tell me apply, adapt or skip, and why.

1. The rule must describe what the tools actually read.
   Basic Memory resolves a wiki-link on `title:` alone, Obsidian on the file basename alone. Upstream rewrote the Resolution section of `.claude/rules/frontmatter.md` accordingly and added an Obsidian section. Read `git show v0.5.1:.claude/rules/frontmatter.md` and port both sections into my version of the rule, keeping any resolution convention of my own that stays true.

2. An entity note's `title:` must equal the name its links use.
   Upstream added `align_entity_titles.py` and changed what writes entity notes: the entity template, `title:` descriptions in the 2 context schemas, and `/ops-init-project`, which wrote no `title:` at all. It also declared `title?` on `person`, `topic` and `service`, which had no such field: port that declaration into my versions of those schemas. New files are a plain copy. If I renamed the entity zones, adapt the `ZONES` table at the top of the script. A zone rename also breaks scripts this upgrade does not touch, and they fail silently: `check_symmetric_relations.py` hard-codes `sources/partners`, scans 0 partners in a renamed zone and flags every client relation as an orphan, and `add_about_relations.py`, `generate_indexes.py` and `retype_files.py` hard-code it too. Search `basic-memory/scripts` and `.claude` for my old zone paths and list every hit. Then search `.claude/skills` and `.sb-config.json` for the bare zone name, `partners` for example, and list those hits too: skills compare it against the `zones` array of `.sb-config.json`, so `/ops-init-project` takes a renamed zone for a pruned one and refuses to create the entity. Fixing them is my fork's debt rather than this upgrade's, so propose the edits and wait. If my fork deliberately writes descriptive titles, tell me: the alternative is writing links against those titles, and that has to be my decision.
   Run the script as a dry-run, show me the output, and wait. After `--apply`, search my note zones for links written against each old title and propose rewriting them.

3. Obsidian needs a bridge from titles to files.
   Upstream added `add_title_aliases.py`, plus `corpus.py`, which defines what counts as a note. If my fork excludes folders of its own from the corpus, add them to `corpus.py`. Upstream also declared `aliases?` on every schema, since the pass writes the field on any cited note whatever its type: port that declaration into each of my schemas that lacks it, including any schema I added. `git diff v0.5.0..v0.5.1 -- basic-memory/schemas` shows the exact line. Validation does not reject an undeclared field, so skipping this breaks nothing visible, but `audit_field_usage.py` then reports the field as used and declared nowhere. Tell me to install the Alias Linker community plugin, which I must do myself in Obsidian, then run the pass as a dry-run, show me the output, wait, and apply it once. Skip this whole intent if I do not use Obsidian.

4. The aliases must not decay.
   Upstream added `.claude/hooks/title_aliases.py` and wired it as a PostToolUse hook on Write and Edit in `.claude/settings.json`. Copy the hook. If I already have a `.claude/settings.json`, merge the entry into my `hooks` block and leave everything else in place, never replace the file. Edit it as text: insert the new entry and leave every other line as I wrote it, since loading and dumping the JSON reformats the whole file and buries the change in the diff. If I run hooks of my own on the same event that rewrite the same notes, tell me: this one excludes the written note on a Write to avoid racing them.

5. The check must see aliases, and the real damage must be measurable.
   `check_consistency.py` now reads `aliases:` when building its wiki-link table, in both YAML spellings. If I forked that script, port the change rather than copying the file. `check_unresolved_relations.py` is new and additive: it reads the Basic Memory index in read-only mode.

6. What upstream deliberately did NOT change, so you do not "fix" it.
   Context files stay named `CLAUDE.md` and briefs stay named `README.md`. No file was renamed and no link was rewritten to `[[file|label]]`, because that would break Basic Memory.
   H1 headings keep the `{Name}, Context` wording. Only the frontmatter `title:` moved.
   `check_consistency.py` stays permissive about `client:`, `partner:`, `name:` and `subject:`.
   Alias Linker is not preinstalled, `.obsidian/community-plugins.json` stays `[]`.

Phase 2, what falls outside every intent above.
Run `git diff --name-only v0.5.0..v0.5.1` and list anything you have not already handled. For each, say in one line whether it matters for my fork. Demo notes and documentation are upstream's own and I do not need them unless I want them.

Phase 3, verification. Run these against MY workspace and show me the output:
  python3 -I basic-memory/scripts/check_consistency.py
  python3 -I basic-memory/scripts/check_orphans.py
  python3 -I basic-memory/scripts/check_symmetric_relations.py --check
  python3 -I basic-memory/scripts/audit_field_usage.py
If Basic Memory is configured, run `bm reindex` then `python3 -I basic-memory/scripts/check_unresolved_relations.py`.
The audit prints a section titled "Fields used in notes but declared in no schema" only when it has an entry, so its absence is the pass. If it appears, it must not list `aliases` or `title`. Tell me whether it appeared, even when it did not. If the symmetric check reports 0 partners scanned while I have partners, a renamed zone is the cause, see intent 2.
Expect findings on a customized workspace, and sort them into what comes from this upgrade and what comes from my fork.

Phase 4, close. Set `boilerplate_version` to "0.5.1" in `.sb-config.json`. Write me a short record of what you skipped and why. Finally, tell me to click a wiki-link in Obsidian: nothing you ran can verify that Alias Linker resolves it, and the Backlinks pane is no proof, since unlinked mentions read aliases.
```

## 0.5.0

The live indexes stop depending on a community plugin that has not shipped a commit in ten months, and the workspace gains a way to answer a question a second brain has to be able to answer: what in here did I not write myself. **Obsidian 1.10 or later is now required**, since `atlas/home.md` uses a Bases `list` view. Nothing else needs installing: Bases is a core plugin, already enabled.

- **Live indexes migrated from Dataview to Obsidian Bases.** `atlas/maps/` now ships four `.base` files, `clients-active`, `partners-active`, `projects-active` and `recent-emails`, that work in a fresh clone with nothing to install. They replace five Dataview index files that `.claude/rules/atlas.md` documented and that no code path ever created: `generate_indexes.py` only ever wrote the `-static.md` twins. A `.base` file is a query rather than a snapshot, so unlike a static index it never goes stale, which is why it can be committed to a template while the statics stay generated. The four inline Dataview blocks, two in `atlas/home.md` plus one in `templates/atlas-moc-template.md` and one in the `moc-new` skill, became inline ```base blocks, preserving each document's structure.
- **Eight dead links disappeared from the workspace hub.** `atlas/home.md` advertised five index files that nothing produced and declared three `contains` relations to the same absent targets. They resolve now, without a word of the hub's text changing.
- **`.obsidian/community-plugins.json` reset to `[]`.** It declared Dataview enabled while `.obsidian/plugins/` did not exist, so every clone announced a plugin that was not there.
- **`written_by`, who actually wrote a note.** A new optional field on the `session` and `note` schemas, values `owner` and `agent`, absent meaning `owner` so no existing note becomes invalid. It is deliberately absent from `clipping`, `email`, `transcript` and `meeting`, where the type already says the text is not yours. `inbox/` becomes the quarantine: a note carrying `written_by: agent` is never promoted straight into `knowledge/`, it goes through `/distill` and its approval gate, and approving a draft is a review rather than a transfer of authorship. The point is the question you can ask six months later, what in my distilled knowledge did I not think through myself.
- **Three fields that were load-bearing and declared nowhere.** `subtype` was prescribed by two rules and used in twelve files while belonging to no schema; it is now on `note` with the seven values actually in use, documented alongside `note_type`, which answers a different question. `title` is now declared on both context schemas and `topics` on `note` and `project-brief`. All three are read by `generate_indexes.py` or by the Bases filters, so an undeclared field meant a view that silently rendered empty.
- **Three new maintenance scripts, fifteen in total.** `check_consistency.py`, wired into `/sb-doctor` and the local test suite, catches the four defect classes that recurred across every manual review and all fail silently: a skill template emitting frontmatter the schemas reject, a Bases view reading a property no schema declares, a wiki-link resolving to nothing, and a `topics` slug naming no entry in `atlas/topics/`. `propose_pruning.py` proposes notes untouched and unlinked for a period, and never deletes, moves or edits. `audit_field_usage.py` reports the real fill rate of every declared field and surfaces fields used in notes but declared in no schema.
- **`curate` cannot delete anything, and now cannot be made to.** Pruning candidates are reported with the command you may run yourself. They never enter the validated actions, so they never reach the execution step, they are excluded from the batch threshold and from the `-a` flag, whose consent prompt only ever mentioned the three creative skills. A batch accept on deletions is the one thing this skill exists to prevent.
- **`ops-init-project` wrote notes that belonged to no schema.** A project brief without `type` or `schema_version`, a client context without either, a partner context without `schema_version`. A project or client created by the skill was therefore invisible to the Bases views, which filter on `note.type`, and to every generated index. The brief template also wrote `topics: [{topic-slug}]`, where the braces make each item a YAML mapping rather than a string.
- **The review ritual has written criteria.** `.claude/skills/references/review-rituals.md` states the four properties a ritual must keep to survive: it draws on material already written, it tolerates gaps without breaking, it stays short and offers a smaller version, and it looks forward. `curate`, `ops-weekly-pulse` and `close-session` point at it.
- **The README stopped promising a cognitive benefit.** It now states plainly that no evidence supports a second brain improving memory, output or decision quality, and narrows the promise to what is checkable: structured, portable, answerable by an agent. A new section declares which failure the three-zone structure prevents, classification, reuse and machine retrieval, and which it does not, triage by urgency and recall by numeric constraint, pointing readers with those problems at PARA and Johnny.Decimal instead. "Enforced by the tooling" became "applied by the skills that write your notes", because Obsidian enforces nothing.
- **`CONTRIBUTING.md` documented a test that validated the wrong vault.** `bm schema validate` runs against whichever Basic Memory project is configured on the machine, which is the contributor's own vault and not the clone, so the documented command returned a green result about something else. It now gives the register, validate and unregister sequence that targets the clone, names the six checks that run on a bare clone without Basic Memory at all, and states what those checks do not cover: nothing executes a skill, so following its steps is verified only by the throwaway clone.
- **Documentation corrected against the code.** `moc-new` no longer claims a non-existent `atlas/maps/mocs-static.md` gets updated. The static index frontmatter documented in `.claude/rules/atlas.md` now matches what `generate_indexes.py` writes, which also gained the `schema_version` and `date` the `note` schema requires. Five skills said "regenerate the Dataview indexes" for a script that only ever wrote `-static.md` files. `atlas/home.md` advertised thirty emails against a limit of fourteen, and a view described as "awaiting a reply" filters on direction and status and knows nothing about replies. `check_orphans.py` no longer scans `tmp/` or `__pycache__`. The `/sb-doctor` index-freshness check reported an empty `atlas/maps/` as a pass, because an empty glob matches nothing.
- **The demo teaches the convention rather than a plausible version of it.** The demo briefs carried four topic slugs of which three pointed at nothing. `atlas/topics/lead-sourcing.md` now exists and both briefs reference only real entries.
- **`status` keeps its fifteen different vocabularies, on purpose.** Obsidian types a property name once for the whole vault, so the fifteen schemas declaring `status` merge their enums into one suggested-value list and the dropdown offers values that make no sense for the note you are on. Renaming per domain would trade a correct field name for a cluttered one and break every vault already cloned. `.claude/rules/frontmatter.md` now argues the decision, alongside a new section listing the five pre-existing property collisions rather than hiding them.
- **`decisions-recent` stays static only.** It reads `- [decision]` observations from note bodies, and Bases filters on properties rather than body content. There is no `.base` equivalent and there will not be one without a different mechanism.

If you customized a schema or a script locally, re-apply your change after checking out this update, or exclude that file from the checkout. Once applied, set `boilerplate_version` to `0.5.0` by hand in `.sb-config.json`, which is yours and stays out of the update recipe. You can delete the Dataview plugin from your vault if nothing else in it uses it.

### Upgrade prompt, 0.4.0 to 0.5.0

Most of this release lands through the update recipe in the README, but three things do not: the four `.base` files live in `atlas/maps/`, which the recipe deliberately never touches; `atlas/home.md` is a file you own and customized, so it has to be merged rather than checked out; and any client or project created by the 0.4.0 `/ops-init-project` is missing the `type:` the new views filter on, so it will not appear in them until it is repaired.

Paste this into the agent that operates your workspace, from the workspace root.

```
You are upgrading this second-brain workspace from boilerplate version 0.4.0 to 0.5.0. Work through the phases in order and stop at the gate in phase 4.

Rules for the whole run:
- Never delete a note, a folder, or a frontmatter field. This upgrade only adds and rewrites.
- Never write into sources/, knowledge/, atlas/, archives/ or inbox/ without showing me the exact diff first and waiting for my approval.
- If a step's precondition is not met, stop and tell me. Do not improvise around it.
- Report what you changed at the end, file by file.

Phase 1, preconditions.
Run `git status --porcelain`. If anything is uncommitted, stop and ask me to commit or stash first: I need to be able to revert this whole upgrade with one command.
Read `boilerplate_version` in `.sb-config.json`. If it is not 0.4.0, stop and tell me which version it says.
Confirm Obsidian 1.10 or later is installed. Below that, the hub's Bases list view will not render and you should stop here.
Then measure how far my infrastructure has drifted from the version I cloned:
  git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git diff --stat v0.4.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
If that lists no file, my infrastructure is stock and the rest of this prompt applies as written.
If it lists any file, STOP. I have customized the workspace, phase 2 would overwrite that work, and this is the wrong prompt. Show me the list and tell me to use the upgrade prompt for a customized workspace instead.

Phase 2, infrastructure.
Phase 1 proved my infrastructure is stock, so this checkout overwrites nothing of mine:
  git checkout v0.5.0 -- .claude basic-memory/schemas basic-memory/scripts templates
Show me `git diff --stat --cached` afterwards so I can see the size of what arrived.

Phase 3, the new index views.
Copy the four new files, which conflict with nothing because they do not exist in my workspace yet:
  git checkout v0.5.0 -- atlas/maps/clients-active.base atlas/maps/partners-active.base atlas/maps/projects-active.base atlas/maps/recent-emails.base
If my workspace has no partners zone, delete `atlas/maps/partners-active.base` after copying: a view over a folder that does not exist renders empty and is only clutter.
Then edit `.obsidian/community-plugins.json`: remove "dataview" from the array. Leave every other plugin alone, and if I use Dataview elsewhere in this vault for my own queries, say so and leave it in place.

Phase 4, my hub. This is the one file you must merge rather than replace.
`atlas/home.md` is mine and I have edited it. Read `git show v0.5.0:atlas/home.md` and apply only these four changes to my copy, preserving everything else I wrote:
  1. The two ```dataview blocks become the ```base blocks from the v0.5.0 version, one for the maps of content, one for distilled knowledge.
  2. The generated-indexes list: the five wiki-links become [[clients-active.base|clients-active]], [[partners-active.base|partners-active]], [[projects-active.base|projects-active]], [[recent-emails.base|recent-emails]], and decisions-recent as plain text, since it stays static only.
  3. The ## Relations section: the three `contains` links get the `.base` extension, and a fourth is added for recent-emails.
  4. Any sentence naming Dataview now names Bases.
Show me the diff and wait for my approval before writing.

Phase 5, repairing my notes. This is what makes the new views actually show something.
The 0.4.0 `/ops-init-project` wrote project briefs with no `type:` and no `schema_version:`, and client contexts with the same gap, so those notes belong to no schema and no view can list them.
Find them: every `README.md` under a project folder whose frontmatter has no `type:`, and every entity `CLAUDE.md` under sources/ whose frontmatter has no `type:`.
For each one, propose adding, and nothing else:
  - a project README.md: `type: project-brief` and `schema_version: 1`, plus `last_updated` set to today and `topics: []` if absent
  - a client CLAUDE.md: `type: client-context` and `schema_version: 1`
  - a partner CLAUDE.md: `schema_version: 1`, and `type: partner-context` if absent
List every file you found with the fields you would add, and wait for my approval. Do not guess a `status:` or a `title:` that is missing; report those separately and I will fill them.

Phase 6, verification. Run these and show me the output:
  python3 basic-memory/scripts/check_consistency.py
  python3 basic-memory/scripts/check_orphans.py
  python3 basic-memory/scripts/check_symmetric_relations.py --check
  python3 basic-memory/scripts/check_double_frontmatter.py
  python3 basic-memory/scripts/generate_indexes.py
The last one regenerates the static indexes, which is what makes the workspace readable outside Obsidian.

Phase 7, close. Set `boilerplate_version` to "0.5.0" in `.sb-config.json`. Then tell me to open `atlas/home.md` in Obsidian and confirm the two embedded views render, and to open the four `.base` files and confirm each lists what it should. A view that was never rendered is not verified, and nothing you can run will tell you.
```

### Upgrade prompt, 0.4.0 to 0.5.0, for a customized workspace

Use this one if phase 1 of the prompt above told you to, meaning `git diff v0.4.0..HEAD` reports changes under `.claude`, `basic-memory/schemas`, `basic-memory/scripts` or `templates`. You have forked the infrastructure, so there is no version of this upgrade that consists of copying files over yours.

What this prompt carries instead of a diff is the **intent** of each change: the problem it solves and the shape it takes upstream. Your agent reads your version of the file, reads the intent, and re-derives the change in your dialect. Where your fork already solves the problem its own way, the right move is to skip, and the prompt says so explicitly rather than leaving the agent to guess.

```
You are upgrading this second-brain workspace from boilerplate version 0.4.0 to 0.5.0. I have customized the infrastructure, so you must NOT check out upstream files over mine. For each change below, read my version of the file first, then decide between three outcomes: apply, adapt, or skip because my fork already covers the intent. Justify every skip in one line.

Rules for the whole run:
- Never overwrite one of my files wholesale. Every edit is surgical and preserves what I wrote.
- Never delete a note, a folder, a schema field, or an enum value. When upstream narrowed something I widened, keep mine and tell me.
- Show me a diff and wait for approval before each write.
- If you cannot tell whether my fork already covers an intent, ask me instead of deciding.

Phase 0, map my fork. Run:
  git remote add upstream https://github.com/philippe-desplats/second-brain.git
  git fetch upstream --tags
  git diff --stat v0.4.0..HEAD -- .claude basic-memory/schemas basic-memory/scripts templates
Give me the list of files I changed, and for each one a sentence on what my change appears to do. That list is the map for everything below: a change landing on a file I never touched is a plain copy, a change landing on a file I did touch is a merge.

Phase 1, the intents. Work through them in order. For each, tell me apply, adapt or skip, and why.

1. Live indexes must work in a fresh clone with nothing to install.
   Upstream dropped Dataview, whose plugin has not shipped a commit in ten months, for Obsidian Bases, which is a core plugin. It ships four `.base` query files in `atlas/maps/` and converted the inline blocks in `atlas/home.md` and the MOC template.
   In my workspace: copy the four `.base` files if I have no equivalent, convert my inline blocks, and convert any index query I wrote myself. If I deliberately rely on Dataview for queries of my own, keep the plugin, convert only the shipped index views, and tell me which of my queries still need it.
   Read `git show v0.5.0:atlas/maps/clients-active.base` for the syntax. Requires Obsidian 1.10 or later for the list view.

2. A second brain must be able to say which of its notes it did not write itself.
   Upstream added `written_by` to the `session` and `note` schemas, optional, values `owner` and `agent`, absent meaning `owner`. It made `inbox/` the quarantine for machine-written material, with `/distill` and its approval gate as the only path into `knowledge/`.
   In my workspace: if I already record authorship under another name, keep mine and skip. If I renamed or split these schemas, add the field to whatever plays their role. Do not add it to `clipping`, `email`, `transcript` or `meeting`, where the type already says the text is not mine.
   Careful: Obsidian types a property name once for the whole vault. If `written_by` already means something else anywhere in my notes, stop and tell me before declaring it.

3. A field that a view or a script reads must be declared by a schema.
   Upstream declared `subtype` on `note` with seven values, `title` on both context schemas, and `topics` on `note` and `project-brief`. All three were already read by `generate_indexes.py` or by the views while belonging to no contract, which made views render empty for no visible reason.
   In my workspace: if I extended these enums, merge the upstream values into mine rather than replacing my list. If I renamed a field, declare mine, not the upstream name. Then check the reverse: any field my own views or scripts read that no schema of mine declares has the same defect, and `basic-memory/scripts/audit_field_usage.py` from this release lists them.

4. No documented path may reach an unattended mass deletion.
   Upstream added `propose_pruning.py`, which proposes stale notes and never deletes, and wired it into `/curate` as a report-only group excluded from batch mode and from the `-a` flag.
   In my workspace: if I forked `/curate`, apply the same property to my version, and verify my `-a` equivalent cannot accept deletions without me. If I added a deletion path of my own, this is the moment to check it has a human gate. Skip the script itself if I have no use for pruning; it is additive and safe either way.

5. A note a skill creates must belong to a schema.
   The 0.4.0 `/ops-init-project` wrote project briefs with no `type:` and client contexts with no `type:` or `schema_version:`, so notes it created were invisible to every index and every view. Upstream fixed the skill, and the same repair has to run over the notes it already wrote.
   In my workspace: apply the fix to my fork of the skill, whatever shape it has. Then find the notes: every project `README.md` and every entity `CLAUDE.md` under my source zones whose frontmatter has no `type:`. Propose adding `type` and `schema_version: 1` matching what the file is, plus `last_updated` and `topics: []` on a brief. Nothing else. List them all and wait. Do not invent a missing `status:` or `title:`; report those and I will fill them.

6. The defects that fail silently need a check that does not.
   Upstream added `check_consistency.py`, wired into `/sb-doctor`. It catches a skill template emitting frontmatter the schemas reject, a view reading an undeclared property, a dead wiki-link, and a `topics` slug naming no entry.
   In my workspace: copy the script, and wire it into my fork of `/sb-doctor`. Then run it. It reads my schemas and my skills, not upstream's, so on a customized workspace its first run is the most useful thing in this upgrade: it will list the places where my fork's own pieces disagree with each other.

7. What upstream deliberately did NOT change, so you do not "fix" it.
   `status` keeps fifteen different vocabularies across fifteen schemas, on purpose: each is the lifecycle of its own type. Do not harmonize them, and do not rename them per domain. If I renamed them in my fork, that was my call and you leave it alone, but tell me that upstream schemas and mine will now diverge permanently on that field.
   `decisions-recent` stays a static index with no `.base` twin, because Bases filters properties and that index reads observations from note bodies. Do not build one.

Phase 2, what falls outside every intent above.
Run `git diff --name-only v0.4.0..v0.5.0` and list anything you have not already handled. For each, say in one line whether it matters for my fork. Documentation changes to README and CONTRIBUTING are upstream's own and I do not need them unless I want them.

Phase 3, verification. Run these against MY workspace and show me the output:
  python3 basic-memory/scripts/check_consistency.py
  python3 basic-memory/scripts/check_orphans.py
  python3 basic-memory/scripts/check_symmetric_relations.py --check
  python3 basic-memory/scripts/check_double_frontmatter.py
  python3 basic-memory/scripts/audit_field_usage.py
  python3 basic-memory/scripts/generate_indexes.py
Expect findings on a customized workspace, and expect some of them to be about my fork rather than about this upgrade. Sort them into the two piles and tell me which is which.

Phase 4, close. Set `boilerplate_version` to "0.5.0" in `.sb-config.json`. Then write me a short record of what you skipped and why, so the next upgrade starts from a known divergence instead of rediscovering it. Finally, tell me to open the views in Obsidian and confirm they render: nothing you ran can verify that.
```

## 0.4.0

Fills the gaps a mapping of the workspace against the usual second-brain categories left open: the end of a session was never recorded, a captured web page had no type, and the daily journal existed only as an unused enum value. Two schemas added, one skill added, one Obsidian misconfiguration fixed.

- **Session memory, a new `session` type and the `/close-session` skill.** Closing a session writes what got done, what comes next, what is blocked and what was decided into `{project}/sessions/YYYY-MM-DD-session-slug.md`. `/ops-init-project` reads the most recent one when it reopens a project, so a session starts on a point of resumption instead of re-deriving state. It is its own type rather than a `note`, because Basic Memory filters by the `type:` field through `note_types` and never by an inner field, which would have made the memory unreachable by the one query that justifies writing it.
- **Web clippings, a new `clipping` type and a ready-made Web Clipper template.** `templates/obsidian-web-clipper.json` imports into the [Obsidian Web Clipper](https://obsidian.md/clipper) in one drag and drop; every page you clip then lands in `inbox/` already carrying `type: clipping`, its `source_url`, its author and its publication date, ready for `/capture -i` to file into a project's `clippings/` folder. Without Obsidian, pasting the URL into `/capture` does the same job one page at a time.
- **The daily journal works now.** The Daily notes core plugin was enabled with no configuration, so the first click on Obsidian's calendar icon wrote `2026-08-30.md` at the root of the vault, breaking the workspace's own filing rule before any note was taken. `.obsidian/daily-notes.json` now points at `sources/personal/journal/`, names files `YYYY-MM-DD-note-journal.md` in line with the naming convention, and fills them from `templates/journal-template.md`. The folder ships with the workspace because Obsidian does not create a missing one, it refuses with `Folder "..." not found`. `/sb-init` moves the folder and repoints the config when the `personal` zone is pruned.
- **Breaking, `journal` moved from `writing_type` to `note_type`.** It sat unused in the `writing` enum, which covers content drafted to be sent or published, and a daily entry is neither. If a note in your workspace carries `writing_type: journal`, retype it to `type: note` with `note_type: journal`.
- **Journal entries are exempt from the orphan check.** A daily entry legitimately links to nothing, so `check_orphans.py` skips the whole type rather than reporting noise on any workspace that actually journals.
- **The maintenance scripts learned the two new types.** `retype_files.py` and `retype_fallback_notes.py` map `clippings/` and `sessions/` folders, and the `clipping-` and `session-` filename prefixes, onto the right type. `/sb-doctor` picks both schemas up on its own: its validation loop enumerates the schema directory rather than a hardcoded list.
- **From a playbook to a skill, documented in `knowledge/README.md`.** Three conditions for promoting a stabilized playbook into a callable skill, and an explicit decision not to automate the conversion: writing the skill by hand is the review.
- **The demo grew a captured article, a session memory and a second topic.** The Globex project now shows a clipping with its source, the session that followed the kickoff with its open blocker, and the `Catalog Search` topic both point at, so the two new types are visible in working files rather than described in the abstract.

The workspace now ships 17 schemas and 14 skills, up from 15 and 13.

If you customized a schema or a script locally, re-apply your change after checking out this update, or exclude that file from the checkout. `.sb-config.json` is yours and stays out of the recipe, so set its `boilerplate_version` to `0.4.0` by hand once you have applied this release, otherwise it keeps reporting the version you cloned.

## 0.3.0

Realignment on Basic Memory, verified against versions 0.21.1 and 0.22.1. Basic Memory 0.21 or later is now the recommended floor, and everything below still degrades gracefully without it.

- **Schemas now carry two contracts.** `settings.frontmatter:` declares the YAML fields, `schema:` declares the body observations and relations. Basic Memory validates the top-level block against the note body, so the previous single-block shape would have reported every frontmatter field as a missing observation. Measured on the demo content shipped with the boilerplate, indexed as a real project: 20 notes across 7 types, zero error.
- **Schema version key renamed** from `schema_version:` to `version:` in the 15 schema files, the key Basic Memory actually reads. Notes keep `schema_version:`, which declares the version they conform to.
- **`/sb-doctor` goes from nine checks to eleven**, adding a graph orphan cross-check (`bm orphans`) and schema validation (`bm schema validate --strict`), both skipped when Basic Memory is absent.
- **The maintenance scripts dropped their last dependency.** All 12 run on the Python 3 standard library, PyYAML included nowhere. `generate_indexes.py` and `auto_link_entities.py` no longer fail on a clean machine.
- **`/sb-init` Basic Memory setup corrected.** The project is created with `--local`, so cloud mode never captures it silently. The embedding guidance matches reality: embeddings build at first startup, and `bm reindex --embeddings` rebuilds them. The ignore list gained the few file names that are unambiguous, and a warning that is worth more than the list: Basic Memory matches ignore patterns against a file name relative to its own parent directory, so a pattern is global whatever it looks like and a leading slash anchors nothing. Adding `README.md` there drops every project brief from the index, adding `CLAUDE.md` drops every client and partner context.
- **`CLAUDE.md` documents the search filters** that map onto the workspace frontmatter: `search_type`, `note_types`, `tags`, `status`, `after_date`, `min_similarity`.
- **Frontmatter made parseable everywhere.** Four files carried YAML a strict parser rejected, three skills and the map of content template. This matters for agents other than Claude Code, which read the same files with a standard YAML parser.
- **A demo partner ships alongside the demo client.** Proseware referred Globex, so the mandatory symmetric pair (`referred_by` on the client, `brings_lead` on the partner) is now demonstrated by real files instead of being documented in the abstract, and `check_symmetric_relations.py` has something to check. `/sb-init` removes both demos together through the manifest.
- **The schemas stopped enumerating the zones.** Each one used to list four near-identical paths, one per zone, plus prose counting them. Every enumeration broke the day a zone was pruned at setup. They now state one pattern, `sources/{zone}/{entity}/{project}/...`, followed by a concrete path from the demo content so the example stays readable. The schema count is written in exactly one place.
- **Setup adapts to the zones you keep.** `/sb-init` writes the `zones` array only after the prune has actually run, so a zone the safety gate refused to delete can never be declared absent while it still holds your data, and `/capture`, `/curate`, `/ops-init-project` and `/ops-weekly-pulse` resolve the live list from that array instead of assuming four zones.

If you customized a schema or a script locally, re-apply your change after checking out this update, or exclude that file from the checkout. `.sb-config.json` is yours and stays out of the recipe, so set its `boilerplate_version` to `0.3.0` by hand once you have applied this release, otherwise it keeps reporting the version you cloned.
