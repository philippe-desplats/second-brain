#!/usr/bin/env python3
"""What counts as a corpus note. One definition, called by every pass.

A corpus note is markdown a human reads. 7 shapes under the note zones are
not: a generator input read by a document generator, a `skills/` tree filed
under an entity, a skill's own state file, a file under a `prompts/` folder pasted
verbatim into a tool, a file under a `captures/` folder holding third-party
material archived verbatim, a file under a `repo-files/` folder copied as it
stands into a client repository, and a file git ignores, which exists on one
disk and in no other checkout.

This module exists so that answer is given in one place. Given in several, it
drifts, and the same file ends up deliberately excluded by one pass and
reported as a defect by the next.

2 questions live here, and only one of them:

    what a corpus note IS        this module, shared, identical everywhere
    which ones a pass CARES about    that pass's own scope, legitimately
                                     narrower, and stated where it is narrowed

A pass that ignores `archives/` and `inbox/` is the second kind. That narrowing
is expressed by passing `zones=` here, not by adding a prefix to a shared
denylist, so it stays visibly a scope decision.

Every pass that walks the notes uses `iter_corpus_notes`, the one shared walk,
rather than an `os.walk` of its own. `iter_excluded_notes` is its documented
complement, the files under the same zones that are not notes. A pass that
already holds paths, from a hook or from the command line, asks
`is_corpus_note` and `in_note_zone`, which accept a POSIX or a Windows
separator alike, and builds the relative path with `rel_posix`.

Imported as a sibling, never as a package. A caller puts this directory on its
import path itself, so it also runs under `python3 -I`:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from corpus import iter_corpus_notes  # noqa: E402
"""

from __future__ import annotations

import functools
import os
import re
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Zones holding corpus notes. `archives/` and `inbox/` are in the list: a note
# is no less invisible for sitting in the triage buffer or in the attic. A pass
# that wants neither says so at its call site.
NOTE_ZONES = ("sources", "knowledge", "atlas", "archives", "inbox")

# Directories that hold no workspace notes at all, wherever they appear. No
# walk of this module ever enters one.
NO_NOTE_SEGMENTS = frozenset({".git", "node_modules", ".obsidian", "__pycache__",
                              ".venv", "site-packages"})
# Scratch directories. What sits in one is not a corpus note, but a pass may
# have written there, so the excluded walk still visits it.
SCRATCH_SEGMENTS = frozenset({"tmp"})
# Every segment the corpus walk skips, the 2 sets above together.
IGNORED_SEGMENTS = NO_NOTE_SEGMENTS | SCRATCH_SEGMENTS

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


def rel_posix(path, root=WORKSPACE) -> str:
    """The path relative to `root`, with forward slashes on every platform.

    Every rel path this module compares is in this form. `os.path.relpath`
    alone returns backslashes on Windows, where no zone prefix would match.
    """
    p, r = Path(path), Path(root)
    try:
        rel = p.relative_to(r).as_posix() if p.is_absolute() == r.is_absolute() else None
    except ValueError:
        rel = None
    if rel is None:
        rel = os.path.relpath(str(p.resolve()), str(r.resolve()))
    return _posix(rel)


def _posix(rel: str) -> str:
    """Normalise a relative path to forward slashes, without a leading `./`."""
    rel = str(rel).replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


@functools.lru_cache(maxsize=None)
def git_ignored(root: Path = WORKSPACE) -> frozenset[str]:
    """The note-zone files git ignores, which no other checkout ever sees.

    A heavy dump kept on disk but excluded from git puts notes under a note zone
    that exist on one machine only, so counting them makes the report depend on
    whose disk it ran from.

    Paths come back relative to `root`, with forward slashes. `-z` keeps an
    accented path verbatim, where the default output quotes it and escapes
    its bytes, so it would never match the path a walk produces.

    Returns an empty set when git is unavailable or the tree is not a
    repository: there, nothing is ignored and every note is scanned.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--others", "--ignored",
             "--exclude-standard", "--", *NOTE_ZONES],
            capture_output=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    if out.returncode != 0:
        return frozenset()
    names = out.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return frozenset(name for name in names if name)


def in_note_zone(rel: str) -> bool:
    """Does this workspace-relative path sit under one of the 5 note zones?

    Separate from `is_corpus_note` on purpose. A pass may walk from the
    repository root and needs both answers, one that already walks zone by zone
    has this one for free and asks only the other.

    Accepts forward slashes or backslashes, so a Windows path answers too.
    """
    return _posix(rel).split("/")[0] in NOTE_ZONES


def is_corpus_note(rel: str, root: Path = WORKSPACE) -> bool:
    """Is this path a note a human reads, rather than something a machine runs?

    6 shapes are not: a generator input, a skill filed under an entity, a
    skill's own state file, a file under a `prompts/` folder fed verbatim to a
    tool, a file under a `captures/` folder archiving third-party material, and
    a file under a `repo-files/` folder copied into a client repository.
    Each looks like a note and is not one, so every pass leaves all 6 alone
    rather than asking for a `type:` that would put machine state in the
    indexes, a frontmatter that would travel into a prompt, or an authorship
    claim over a document the workspace did not write.

    A seventh exclusion answers a different question. A file git ignores is not
    machine-consumed, it simply exists on one disk and in no other checkout,
    so counting it makes the report depend on whose machine ran it.

    Takes a path relative to `root`, the workspace by default, with forward
    slashes or backslashes, and says nothing about whether that path is in a
    note zone: ask `in_note_zone` for that.
    """
    rel = _posix(rel)
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
    if rel in git_ignored(Path(root)):
        return False
    return True


def _walk(root: Path, zones: tuple[str, ...]):
    """Yield (path, rel, segments) for every Markdown file the 2 walks may see.

    `segments` is the set of scratch segments in the relative path. A file
    under a segment of NO_NOTE_SEGMENTS is never yielded.
    """
    for zone in zones:
        base = root / zone
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if not path.is_file():
                continue
            rel_path = path.relative_to(root)
            # Test the RELATIVE parts: an absolute path containing a segment
            # named tmp or .git would otherwise silence the whole walk.
            parts = set(rel_path.parts)
            if parts & NO_NOTE_SEGMENTS:
                continue
            yield path, rel_path.as_posix(), parts & SCRATCH_SEGMENTS


def iter_corpus_notes(root: Path = WORKSPACE, zones: tuple[str, ...] = NOTE_ZONES):
    """Yield (path, rel) for every corpus note in the given zones, sorted.

    The shared walk. Every pass that visits the notes calls this one rather
    than walking the tree itself, so the definition above holds everywhere.
    `rel` is relative to `root`, with forward slashes on every platform.

    `zones` is the scope lever: a pass that has a reason to look at fewer than
    the 5 states that reason at its call site. `root` lets a caller walk
    another tree.

    A zone that does not exist is skipped rather than raised on, since zones
    can be pruned at setup.
    """
    for path, rel, scratch in _walk(root, zones):
        if not scratch and is_corpus_note(rel, root):
            yield path, rel


def iter_excluded_notes(root: Path = WORKSPACE, zones: tuple[str, ...] = NOTE_ZONES):
    """Yield (path, rel) for every Markdown file under the zones that is NOT a corpus note.

    The complement of `iter_corpus_notes` over the same zones: every Markdown
    file there is yielded by exactly one of the 2 walks, except a file under a
    folder that holds no notes at all, `.git` and the like, which neither
    yields. A scratch folder, `tmp/`, is excluded from the corpus and yielded
    here. Only a pass that audits what other passes wrote outside the corpus
    has a reason to call it.
    """
    for path, rel, scratch in _walk(root, zones):
        if scratch or not is_corpus_note(rel, root):
            yield path, rel
