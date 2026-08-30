# Changelog

Structural changes to this workspace. Content changes (notes, projects) are tracked by git history, not here.

`Unreleased` is your own section, and this file stays yours: the update recipe in [README.md](README.md#keeping-your-clone-up-to-date) never overwrites it. The numbered releases below it document what each boilerplate version changed in the infrastructure that recipe does pull, so read them before applying one.

## Unreleased

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
