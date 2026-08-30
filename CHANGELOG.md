# Changelog

Structural changes to this workspace. Content changes (notes, projects) are tracked by git history, not here.

`Unreleased` is your own section, and this file stays yours: the update recipe in [README.md](README.md#keeping-your-clone-up-to-date) never overwrites it. The numbered releases below it document what each boilerplate version changed in the infrastructure that recipe does pull, so read them before applying one.

## Unreleased

### Changed

- Live indexes migrated from Dataview to Obsidian Bases. `atlas/maps/` now ships four `.base` files (`clients-active`, `partners-active`, `projects-active`, `recent-emails`) that work in a fresh clone with nothing to install, since Bases is a core plugin. The five live Dataview index files these replace were documented but had never been created by anything.
- The four inline Dataview blocks, two in `atlas/home.md` plus one in `templates/atlas-moc-template.md` and one in the `moc-new` skill, became inline ```base blocks, preserving the documents' structure.
- `.obsidian/community-plugins.json` reset to `[]`. It declared Dataview enabled while `.obsidian/plugins/` did not exist, so every clone announced a plugin that was not there.
- `generate_indexes.py` now emits `schema_version: 1` and `date:` in the static indexes it writes, so generated files conform to the `note` schema the workspace enforces.
- `sb-doctor` index-freshness check now reports an empty `atlas/maps/` as a finding instead of passing on an empty glob.

### Added

- `written_by` frontmatter field on the `session` and `note` schemas, values `owner` and `agent`, optional and absent meaning `owner`. It answers the question a second brain has to be able to answer six months later: what in my distilled knowledge did I not write myself. Deliberately not added to `clipping`, `email`, `transcript` or `meeting`, where the type already carries that information.
- Two new sections in `.claude/rules/frontmatter.md`: one documenting that Obsidian types a property name once for the whole vault, with the five pre-existing collisions listed rather than hidden, and one defining the provenance convention and the quarantine rule.
- Promotion and quarantine rules in `.claude/rules/knowledge.md`: `inbox/` holds machine-produced material, `/distill` and its approval gate are the only path into `knowledge/`, and approving a draft is a review rather than a transfer of authorship.

- `basic-memory/scripts/audit_field_usage.py`, a read-only audit reporting per-type fill rates for every declared field, flagging required fields filled below a threshold, and surfacing fields used in notes but declared in no schema.
- `subtype` declared on the `note` schema with the seven values actually in use. It was prescribed by two rules and used in twelve files while belonging to no contract. `note_type` keeps its own axis; the two are documented side by side.
- `title` declared on both context schemas and `topics` on `note`. All three were already load-bearing, read by `generate_indexes.py` and by the MOC Bases filters, while declared nowhere.

- `basic-memory/scripts/propose_pruning.py`, which proposes notes for deletion on the documented criterion, untouched and unlinked for a period. It never deletes, moves, or edits; it produces a list the owner accepts line by line, wired into the `curate` scan as a fourth group. Journals, archives, templates, generated indexes, structural files and entity types are protected by design.
- `.claude/skills/references/review-rituals.md`, stating the four properties a review ritual must keep to survive: it draws on material already written, it tolerates gaps without breaking, it stays short and offers a smaller version, and it looks forward. `curate`, `ops-weekly-pulse` and `close-session` point at it.

- A "What this optimizes, and what it does not" section in the README, declaring which failure the three-zone structure prevents (classification, reuse, machine retrieval) and which it does not (triage by urgency, recall by numeric constraint), pointing readers with those problems at PARA and Johnny.Decimal instead.

### Changed, again

- The README no longer implies a cognitive benefit. It states plainly that no evidence supports a second brain improving memory, output or decision quality, and narrows the promise to what is checkable: structured, portable, answerable by an agent.
- "Enforced by the tooling" nuanced to "applied by the skills that write your notes". Obsidian enforces nothing; the conventions hold because the skills apply them. The weekly review is now presented as the one thing tooling cannot take over.

### Fixed, second verification round

- `propose_pruning.py` took the git commit date unconditionally, so a note edited this morning but last committed in January was proposed as untouched since January. It now takes the later of the commit date and the mtime, which counts uncommitted work as touched.
- `audit_field_usage.py` tested its skip list against absolute path segments, so any workspace living under a folder named `tmp`, `.git` or `node_modules` audited zero notes and reported "nothing measurable" for all seventeen types.
- `ops-init-project` wrote a project brief with neither `type` nor `schema_version`, so a project created by the skill belonged to no schema and appeared in no index or view. It now writes both, plus `topics` and `last_updated`, without which no map of content can ever list the project.
- The pruning group `curate` collects was never stored nor counted: its total stopped at three lists, so a vault with forty pruning candidates and nothing else reported "Clean workspace" and exited. It is now a fourth group, presented in the report and excluded from batch mode, since a batch accept on deletions is the one thing this skill exists to prevent.
- Four documentation claims that survived the first round: `atlas/home.md` still advertised thirty emails against a limit of fourteen, `.claude/rules/atlas.md` still described a view as "awaiting a reply" after it was renamed for not knowing that, `.claude/rules/frontmatter.md` listed twelve maintenance scripts when there are fourteen, and `generate_indexes.py` still claimed "the same lookups" and described emails as filtered on modification time rather than on their `date` field.

### Fixed

- Eight dead wiki-links in `atlas/home.md`, five in the index list and three in its `## Relations` section, all pointing at index files nothing produced.
- `moc-new` no longer claims that a non-existent `atlas/maps/mocs-static.md` gets updated.
- Documentation of the static index frontmatter in `.claude/rules/atlas.md` now matches what the script actually writes.
- `check_orphans.py` no longer scans `tmp/` or `__pycache__`, so scratch files in a gitignored folder stop being reported as orphan notes.
- Skill wording corrected from "regenerate the Dataview indexes" to "regenerate the static indexes" across `archive`, `distill`, `moc-new` and the `librarian` agent. The script only ever wrote `-static.md` files.

### Notes

- `decisions-recent` stays static only. It reads `- [decision]` observations from note bodies, and Bases filters on properties rather than body content.

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
