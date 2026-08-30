# Known debt

Things that are wrong, understood, and deliberately not fixed yet. Each entry says what it is, what it costs today, and what fixing it would break, so the next person arbitrates rather than rediscovers.

An entry here is not a bug report waiting to be triaged. It has already been triaged: someone looked, decided the cure was worse than the disease for now, and wrote down why. Fixing one is a decision, not a chore.

## `status` carries fourteen incompatible vocabularies

`status` is declared on fifteen of the seventeen schemas, and almost every one gives it a different enum: `active|inactive|prospect` on a client context, `draft|review|sent|signed|invoiced|paid|cancelled|archived` on a deliverable, `open|closed` on a session, `unread|read|archived` on a clipping, and so on.

**What it costs.** Obsidian assigns one property type per name for the whole vault, and merges the suggested values into a single list. Opening the `status` dropdown on a client note offers `paid`, `converged` and `ex-partner-now-competitor`. It is an annoyance in the Properties panel, nothing more: every value is a string, nothing breaks, and no query is affected.

**What fixing it would break.** Renaming per domain (`deliverable_status`, `clipping_status`) means rewriting fifteen schemas, every note that carries the field, the scripts that filter on it, the Bases views, and the rules. Every vault already cloned from this template breaks at once, for a cosmetic gain.

**Verdict.** Documented in `.claude/rules/frontmatter.md`, not corrected. Worth doing only inside a deliberate major version, alongside a migration script.

## `bm schema validate` does not validate this repository

`CONTRIBUTING.md` documents it as a local test. It runs against whichever Basic Memory project is configured on the machine, which is almost never this repository.

**What it costs.** A contributor runs the documented command, sees `389/389 valid`, and concludes the template validates. They have validated their own vault.

**What fixing it would break.** Nothing, but it needs a decision: either the command gets a project argument pointing at the clone, or the repository stops claiming to be testable that way and relies on `check_consistency.py` plus the strict YAML parse instead. The second is probably right, since a template is not a Basic Memory project until `/sb-init` has run.

**Verdict.** Recorded, not fixed. Needs an arbitration, not an edit.

## The MOC view depends on a field nothing forces

`templates/atlas-moc-template.md` filters projects on `note.topics`. The field is declared on `project-brief` and `note`, and `ops-init-project` now writes it into the template, but nothing verifies that an owner fills it or that the slug matches an entry in `atlas/topics/`.

**What it costs.** A MOC whose "Active projects" view is empty, with no error and no clue why. The two demo briefs carry real slugs so the pattern is at least demonstrated correctly.

**What fixing it would break.** A check that every `topics` slug resolves to a real topic file would be easy to write and would flag legitimate work in progress: someone writes a brief today and creates the topic next week. A warning is defensible, an error is not.

**Verdict.** Left as is. Reconsider if the empty MOC turns out to confuse people in practice.

## Skill instructions and rules are not tested end to end

Skills are prose that an agent follows. `check_consistency.py` validates the frontmatter examples they contain, but nothing verifies that following a skill's steps produces what the skill claims, or that two skills agree with each other.

**What it costs.** This is where most of the defects found in this repository have lived: a step referring to a file that no longer exists, a skill declaring it never writes while instructing a deletion, a count of three groups where a fourth was added. Each of them was found by a human or an agent reading closely, never by a check.

**What fixing it would break.** Nothing, but it is genuinely hard. Executing a skill in a sandbox and asserting on the resulting tree is the only real answer, and it is a test harness, not a script.

**Verdict.** Open. The most valuable thing anyone could add to this repository, and the largest.
