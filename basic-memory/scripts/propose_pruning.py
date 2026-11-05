#!/usr/bin/env python3
"""Propose notes for pruning. Never deletes anything.

Accumulation is the documented failure mode of a second brain: the archive
grows, nothing is ever removed, and the pile stops being searchable long
before anyone admits it. Deletion is the only operation that reduces that
liability, and it is the one almost no published system implements.

The criterion is the one that has actually been used in practice: a note is a
candidate when nobody has touched it and nobody has linked to it for a given
period. Editing it or linking it from anywhere clears it, so a note stays as
long as it takes part in the workspace.

Age comes from git for a tracked file with no uncommitted changes, and from
the filesystem mtime otherwise. Neither signal alone works, and neither does
taking the later of the two:

    mtime alone   git does not preserve mtimes, so on a fresh clone every note
                  dates from the clone. The run reports nothing for `--days`
                  days, then flags the whole vault at once.
    git alone     a note edited this morning but last committed in January
                  reads as untouched since January, and the tool proposes
                  deleting today's work.
    max of both   safe, but on a fresh clone the mtime always wins, so the git
                  lookup becomes dead code exactly where it was needed.

Asking git which files are dirty resolves all three: a clean tracked file uses
its commit date, a dirty or untracked one uses its mtime.

This script proposes. It never deletes, never moves, never edits a note. The
output is a list for a human to accept or reject, in line with the workspace
rule that every curation action is validated.

Protected by design and never proposed:
    - anything under archives/, templates/, docs/, basic-memory/, inbox/, .claude/
    - anything corpus.py does not count as a note: prompts, repo files, captures
    - journal entries, which are a dated log and are meant to lie still
    - generated static indexes and .base views, rebuilt rather than curated
    - structural files (README, CHANGELOG, CLAUDE.md), and atlas/home.md, the hub
    - maps and indexes (subtype moc or index), which are navigation surfaces
    - entity context files, which describe a relationship rather than a note

Usage:
    python3 basic-memory/scripts/propose_pruning.py
    python3 basic-memory/scripts/propose_pruning.py --days 365
    python3 basic-memory/scripts/propose_pruning.py --output inbox/pruning-proposal.md
    python3 basic-memory/scripts/propose_pruning.py --json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import link_targets, note_names, resolution_table, scalar  # noqa: E402
from corpus import IGNORED_SEGMENTS, WORKSPACE, iter_corpus_notes  # noqa: E402

# Read-only, it never writes a note. Only corpus notes are ever proposed, and
# of those only the ones in these zones, less the protected list of the module
# docstring: `archives/` and `inbox/` are corpus zones a human curates by hand.
PRUNABLE_ZONES = ("sources", "knowledge", "atlas")
# Inbound links are counted over the whole tree, corpus or not, so a link from
# anywhere keeps a note alive. `.claude/` is left out of that count: its skills
# and rules hold example wiki-links, which would keep any note of that name.
INBOUND_IGNORED_SEGMENTS = IGNORED_SEGMENTS | {".claude"}
STRUCTURAL = {"README.md", "CHANGELOG.md", "GETTING-STARTED.md", "AGENTS.md",
              "CLAUDE.md", "CONTRIBUTING.md", "LICENSE.md"}
# Navigation surfaces. Losing one costs more than any note it points at.
STRUCTURAL_PATHS = {"atlas/home.md"}
# Structural subtypes on the `note` type: a map or an index is navigation,
# not a disposable note, whatever its link count says.
PROTECTED_SUBTYPES = {"moc", "index"}
# Types that describe a standing relationship or entity, not a disposable note.
PROTECTED_TYPES = {"client-context", "partner-context", "person", "service",
                   "topic", "project-brief"}


@dataclass
class Note:
    path: Path
    rel: str
    text: str
    title: str = ""
    ntype: str = ""
    outgoing: set[str] = field(default_factory=set)
    names: set[str] = field(default_factory=set)
    mtime: dt.date = dt.date.min
    inbound: int = 0


def is_protected(rel: str) -> bool:
    """A corpus note this pass never proposes, by its path alone."""
    name = rel.rsplit("/", 1)[-1]
    return rel.endswith("-static.md") or name in STRUCTURAL or rel in STRUCTURAL_PATHS


def frontmatter(text: str) -> F.Frontmatter | None:
    """The parsed frontmatter, a folded title read whole, or None."""
    doc = F.split(text)
    return F.parse(doc.block) if doc is not None else None


def git_dates(root: Path) -> dict[str, dt.date]:
    """Last commit date per tracked file, in one git call.

    Git does not preserve mtimes, so on a fresh clone every file looks new.
    Without this, the script would stay silent for months and then flag the
    whole vault at once, which is the opposite of a usable pruning signal.
    Returns an empty mapping when git is unavailable or this is not a repo,
    and the caller falls back to mtime.
    """
    # `-z` keeps an accented path verbatim, where the default output quotes it
    # and escapes its bytes, so it never matched the path the walk produces.
    # Records are NUL-separated: a commit header opens with \x01, then each
    # path follows, the first one after a newline.
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-z", "--name-only", "--format=%x01%cI",
             "--no-renames"],
            capture_output=True, timeout=60, check=True,
        ).stdout.decode("utf-8", errors="surrogateescape")
    except (OSError, subprocess.SubprocessError):
        return {}
    dates: dict[str, dt.date] = {}
    current: dt.date | None = None
    for token in out.split("\0"):
        if token.startswith("\x01"):
            try:
                current = dt.date.fromisoformat(token[1:11])
            except ValueError:
                current = None
            continue
        name = token[1:] if token.startswith("\n") else token
        if name and current and name not in dates:
            # log walks newest first, so the first sighting is the latest touch
            dates[name] = current
    return dates


def git_dirty(root: Path) -> set[str]:
    """Paths with uncommitted changes, whose mtime is the honest signal.

    Without this, a clean clone would fall back to mtimes that all read as the
    clone timestamp, and the commit dates gathered above would never be used.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "-z"],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    dirty = set()
    entries = iter(out.split("\0"))
    for entry in entries:
        if len(entry) > 3:
            dirty.add(entry[3:])
            # A rename or a copy is followed by its source path, not an entry.
            if "R" in entry[:2] or "C" in entry[:2]:
                next(entries, None)
    return dirty


def is_journal(fm: F.Frontmatter | None, rel: str) -> bool:
    """A dated log is meant to lie still, never propose one for pruning."""
    if scalar(fm, "note_type") == "journal":
        return True
    return "/journal/" in rel or rel.endswith("-note-journal.md")


def load_notes(root: Path, git: dict[str, dt.date], dirty: set[str]) -> list[Note]:
    notes = []
    for path, rel in iter_corpus_notes(root, zones=PRUNABLE_ZONES):
        if is_protected(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = frontmatter(text)
        if is_journal(fm, rel):
            continue
        if scalar(fm, "type") in PROTECTED_TYPES:
            continue
        if scalar(fm, "subtype") in PROTECTED_SUBTYPES:
            continue
        notes.append(Note(
            path=path,
            rel=rel,
            text=text,
            title=scalar(fm, "title") or path.stem,
            ntype=scalar(fm, "type"),
            outgoing={target for target, _ in link_targets(text)},
            names=note_names(fm, rel),
            # Commit date for a clean tracked file, mtime when it is dirty or
            # untracked. See the module docstring for why neither signal alone,
            # nor the later of the two, gets this right.
            mtime=(
                dt.date.fromtimestamp(path.stat().st_mtime)
                if rel in dirty or rel not in git
                else git[rel]
            ),
        ))
    return notes


def count_inbound(notes: list[Note], root: Path) -> None:
    """Inbound links are counted across the WHOLE workspace, not only the
    prunable subset: a note linked from a protected context file is alive."""
    # Every name check_helpers.note_names gives a note: path, title, aliases
    # and identity keys, so a note reachable by any of them stays.
    targets = resolution_table((n, n.names) for n in notes)
    for path in root.rglob("*.md"):
        rel_path = path.relative_to(root)
        if any(p in INBOUND_IGNORED_SEGMENTS for p in rel_path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for target, _ in link_targets(text):
            for n in targets.get(target, []):
                if n.path != path:
                    n.inbound += 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=180,
                    help="untouched for this many days to qualify (default 180)")
    ap.add_argument("--output", type=Path, help="write the proposal to a file instead of stdout")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    today = dt.date.today()
    cutoff = today - dt.timedelta(days=args.days)

    git = git_dates(WORKSPACE)
    dirty = git_dirty(WORKSPACE)
    notes = load_notes(WORKSPACE, git, dirty)
    count_inbound(notes, WORKSPACE)

    candidates = [n for n in notes
                  if n.mtime < cutoff and n.inbound == 0 and not n.outgoing]
    candidates.sort(key=lambda n: n.mtime)

    if args.json:
        print(json.dumps({
            "generated": today.isoformat(),
            "days": args.days,
            "scanned": len(notes),
            "candidates": [{"path": n.rel, "title": n.title, "type": n.ntype,
                            "last_modified": n.mtime.isoformat(),
                            "age_days": (today - n.mtime).days} for n in candidates],
        }, indent=2, ensure_ascii=False))
        return 0

    lines = [
        f"# Pruning proposal, {today.isoformat()}",
        "",
        f"_Age source: {'commit dates, with mtime for uncommitted work' if git else 'filesystem mtime (not a git repository)'}._",
        "",
        f"_Scanned {len(notes)} prunable notes. {len(candidates)} candidate"
        f"{'s' if len(candidates) != 1 else ''} untouched for {args.days}+ days,"
        " with no inbound and no outbound links._",
        "_Nothing has been deleted. Accept or reject each line yourself._",
        "",
    ]
    if not candidates:
        lines += ["No candidate. Every note is either linked or has been touched recently.", ""]
    else:
        lines += ["| Last modified | Age | Type | Note |", "| --- | --- | --- | --- |"]
        for n in candidates:
            age = (today - n.mtime).days
            lines.append(f"| {n.mtime.isoformat()} | {age}d | {n.ntype or 'untyped'} | `{n.rel}` |")
        lines += [
            "",
            "Before accepting a line, ask what the note was for. An unlinked note is not",
            "automatically worthless, it may simply never have been wired in. Linking it is",
            "as valid an outcome as deleting it, and often the better one.",
            "",
        ]

    text = "\n".join(lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Proposal written to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
