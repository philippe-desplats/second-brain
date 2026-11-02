#!/usr/bin/env python3
"""What counts as a corpus note. One definition, called by every pass.

A corpus note is markdown a human reads. Seven shapes under the note zones are
not: a generator input read by a document generator, a `skills/` tree filed
under an entity, a skill's own state file, a file under a `prompts/` folder pasted
verbatim into a tool, a file under a `captures/` folder holding third-party
material archived verbatim, a file under a `repo-files/` folder copied as it
stands into a client repository, and a file git ignores, which exists on one
disk and in no other checkout.

This module exists so that answer is given in one place. Given in several, it
drifts, and the same file ends up deliberately excluded by one pass and
reported as a defect by the next.

Two questions live here, and only one of them:

    what a corpus note IS        this module, shared, identical everywhere
    which ones a pass CARES about    that pass's own scope, legitimately
                                     narrower, and stated where it is narrowed

A pass that ignores `archives/` and `inbox/` is the second kind. That narrowing
is expressed by passing `zones=` here, not by adding a prefix to a shared
denylist, so it stays visibly a scope decision.

Imported as a sibling, never as a package. A caller puts this directory on its
import path itself, so it also runs under `python3 -I`.
"""

from __future__ import annotations

import functools
import re
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Zones holding corpus notes. `archives/` and `inbox/` are in the list: a note
# is no less invisible for sitting in the triage buffer or in the attic. A pass
# that wants neither says so at its call site.
NOTE_ZONES = ("sources", "knowledge", "atlas", "archives", "inbox")

# Directories that hold no workspace notes at all, wherever they appear.
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", "__pycache__", "tmp",
                    ".venv", "site-packages"}

# Path prefixes holding generator inputs rather than notes: bodies read by a
# document generator and never by a human, which a maintenance pass must not
# rewrite. Add your own here, the list is deliberately empty in a fresh clone.
NOTE_SKIP_PREFIXES: tuple[str, ...] = ()
# A `skills/` tree filed under an entity holds a SKILL.md and its steps, read
# by an agent and never by a human. Same class as the generator inputs: writing a
# `type:` into one edits an executable artifact to satisfy an index.
NOTE_SKIP_SEGMENTS = ("skills",)
# A `session.md`, or a `*-session.md`, sitting outside a `sessions/` folder is
# a skill's own state file, written and reread by the run that produced it. It
# carries `task_id` and `stepsCompleted`, not prose. The `sessions/` folder is
# the exception because that is where the `session` schema's notes live.
SKILL_STATE_RE = re.compile(r"(?:^|-)session\.md$")
# A `prompts/` folder holds the verbatim text of prompts, each pasted into a
# tool as it stands. A frontmatter on one is pasted along with it, the same
# trap as a generator input. The folder is the discriminator, never the file
# name: a note ABOUT a prompt, with an H1 and prose around the text, is corpus
# like any other note.
PROMPT_SEGMENTS = ("prompts",)
# A `captures/` folder holds third-party material archived verbatim: a fetched
# web page, a policy, a regulatory text, kept as the archive of record behind a
# piece of research. Nobody in the workspace wrote it, so asking it for a
# `type:` claims authorship the workspace does not have, and stamping it would
# put a provenance field on a document whose provenance is its own header.
#
# `references/` is deliberately NOT in this list. That folder holds curated
# material a human wrote or chose, typed `research`, `note` or `transcript`, and
# excluding it wholesale would hide real notes from every index.
CAPTURE_SEGMENTS = ("captures",)
# A `repo-files/` folder holds files copied as they stand into a client's code
# repository, a licence or a notice. Same trap as `prompts/`: a frontmatter
# written on one would ship into the client's repository with it.
REPO_FILE_SEGMENTS = ("repo-files",)


@functools.lru_cache(maxsize=1)
def git_ignored() -> frozenset[str]:
    """The note-zone files git ignores, which no other checkout ever sees.

    A heavy dump kept on disk but excluded from git puts notes under a note zone
    that exist on one machine only, so counting them makes the report depend on
    whose disk it ran from.

    Returns an empty set when git is unavailable or the tree is not a
    repository: there, nothing is ignored and every note is scanned.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(WORKSPACE), "ls-files", "--others", "--ignored",
             "--exclude-standard", "--", *NOTE_ZONES],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    if out.returncode != 0:
        return frozenset()
    return frozenset(line for line in out.stdout.splitlines() if line)


def in_note_zone(rel: str) -> bool:
    """Does this workspace-relative path sit under one of the five note zones?

    Separate from `is_corpus_note` on purpose. A pass may walk from the
    repository root and needs both answers; one that already walks zone by zone
    has this one for free and asks only the other.
    """
    return rel.split("/")[0] in NOTE_ZONES


def is_corpus_note(rel: str) -> bool:
    """Is this path a note a human reads, rather than something a machine runs?

    Six shapes are not: a generator input, a skill filed under an entity, a
    skill's own state file, a file under a `prompts/` folder fed verbatim to a
    tool, a file under a `captures/` folder archiving third-party material, and
    a file under a `repo-files/` folder copied into a client repository.
    Each looks like a note and is not one, so every pass leaves all six alone
    rather than asking for a `type:` that would put machine state in the
    indexes, a frontmatter that would travel into a prompt, or an authorship
    claim over a document the workspace did not write.

    A seventh exclusion answers a different question. A file git ignores is not
    machine-consumed, it simply exists on one disk and in no other checkout,
    so counting it makes the report depend on whose machine ran it.

    Takes a path relative to the workspace root, and says nothing about
    whether that path is in a note zone; ask `in_note_zone` for that.
    """
    if rel.startswith(NOTE_SKIP_PREFIXES):
        return False
    parts = rel.split("/")
    if any(part in NOTE_SKIP_SEGMENTS for part in parts[:-1]):
        return False
    if SKILL_STATE_RE.search(parts[-1]) and "sessions" not in parts[:-1]:
        return False
    if any(part in PROMPT_SEGMENTS for part in parts[:-1]):
        return False
    if any(part in CAPTURE_SEGMENTS for part in parts[:-1]):
        return False
    if any(part in REPO_FILE_SEGMENTS for part in parts[:-1]):
        return False
    if rel in git_ignored():
        return False
    return True


def iter_corpus_notes(root: Path = WORKSPACE, zones: tuple[str, ...] = NOTE_ZONES):
    """Yield (path, rel) for every corpus note in the given zones, sorted.

    `zones` is the scope lever: a pass that has a reason to look at fewer than
    the five states that reason at its call site. `root` lets a caller walk
    another tree.

    A zone that does not exist is skipped rather than raised on, since zones
    can be pruned at setup.
    """
    for zone in zones:
        base = root / zone
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            rel_path = path.relative_to(root)
            # Test the RELATIVE parts: an absolute path containing a segment
            # named tmp or .git would otherwise silence the whole walk.
            if any(part in IGNORED_SEGMENTS for part in rel_path.parts):
                continue
            rel = rel_path.as_posix()
            if is_corpus_note(rel):
                yield path, rel
