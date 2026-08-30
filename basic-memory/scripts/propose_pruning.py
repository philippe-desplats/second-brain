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

Age is the LATER of the last commit date and the filesystem mtime. Neither
alone is safe: git does not preserve mtimes, so on a fresh clone a purely
mtime-based run reports nothing for months and then flags the whole vault at
once; git alone would call a note edited this morning but last committed in
January untouched since January. Taking the later date means uncommitted work
counts as touched, which is the conservative direction for a tool whose
mistakes propose deleting things.

This script proposes. It never deletes, never moves, never edits a note. The
output is a list for a human to accept or reject, in line with the workspace
rule that every curation action is validated.

Protected by design and never proposed:
    - anything under archives/, templates/, docs/, basic-memory/, inbox/, .claude/
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
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude", "tmp", "__pycache__"}
IGNORED_PATH_PREFIXES = (
    "archives/",
    "templates/",
    "basic-memory/",
    "docs/",
    "inbox/",
)
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

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?(?:#[^\]]+)?\]\]")


@dataclass
class Note:
    path: Path
    rel: str
    text: str
    title: str = ""
    ntype: str = ""
    outgoing: set[str] = field(default_factory=set)
    mtime: dt.date = dt.date.min
    inbound: int = 0


def is_ignored(rel_path: Path) -> bool:
    if any(p in IGNORED_SEGMENTS for p in rel_path.parts):
        return True
    rel = rel_path.as_posix()
    if any(rel.startswith(p) for p in IGNORED_PATH_PREFIXES):
        return True
    if rel.endswith("-static.md") or rel_path.name.endswith(".base"):
        return True
    if rel_path.name in STRUCTURAL or rel in STRUCTURAL_PATHS:
        return True
    return False


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("\"'")
    return out


def git_dates(root: Path) -> dict[str, dt.date]:
    """Last commit date per tracked file, in one git call.

    Git does not preserve mtimes, so on a fresh clone every file looks new.
    Without this, the script would stay silent for months and then flag the
    whole vault at once, which is the opposite of a usable pruning signal.
    Returns an empty mapping when git is unavailable or this is not a repo,
    and the caller falls back to mtime.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "--name-only", "--format=%x00%cI", "--no-renames"],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    dates: dict[str, dt.date] = {}
    current: dt.date | None = None
    for line in out.splitlines():
        if line.startswith("\x00"):
            try:
                current = dt.date.fromisoformat(line[1:11])
            except ValueError:
                current = None
        elif line.strip() and current and line not in dates:
            # log walks newest first, so the first sighting is the latest touch
            dates[line] = current
    return dates


def is_journal(fm: dict[str, str], rel: str) -> bool:
    """A dated log is meant to lie still; never propose one for pruning."""
    if fm.get("note_type") == "journal":
        return True
    return "/journal/" in rel or rel.endswith("-note-journal.md")


def load_notes(root: Path, git: dict[str, dt.date]) -> list[Note]:
    notes = []
    for path in sorted(root.rglob("*.md")):
        rel_path = path.relative_to(root)
        if is_ignored(rel_path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = frontmatter(text)
        rel = rel_path.as_posix()
        if is_journal(fm, rel):
            continue
        if fm.get("type") in PROTECTED_TYPES:
            continue
        if fm.get("subtype") in PROTECTED_SUBTYPES:
            continue
        notes.append(Note(
            path=path,
            rel=rel,
            text=text,
            title=fm.get("title") or path.stem,
            ntype=fm.get("type", ""),
            outgoing={m.group(1).strip() for m in WIKILINK_RE.finditer(text)},
            # The LATER of the two. Git alone would call a note edited this
            # morning but last committed in January 'untouched since January',
            # and a pruning tool that proposes today's work is worse than one
            # that proposes nothing.
            mtime=max(
                git.get(rel, dt.date.min),
                dt.date.fromtimestamp(path.stat().st_mtime),
            ),
        ))
    return notes


def count_inbound(notes: list[Note], root: Path) -> None:
    """Inbound links are counted across the WHOLE workspace, not only the
    prunable subset: a note linked from a protected context file is alive."""
    targets = {}
    for n in notes:
        for key in {n.title, n.path.stem, n.rel, n.rel[:-3]}:
            targets.setdefault(key, []).append(n)
    for path in root.rglob("*.md"):
        rel_path = path.relative_to(root)
        if any(p in IGNORED_SEGMENTS for p in rel_path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in WIKILINK_RE.finditer(text):
            for n in targets.get(m.group(1).strip(), []):
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
    notes = load_notes(WORKSPACE, git)
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
        f"_Age source: {'git history' if git else 'filesystem mtime (not a git repository)'}._",
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
            "automatically worthless; it may simply never have been wired in. Linking it is",
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
