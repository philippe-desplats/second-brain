#!/usr/bin/env python3
"""
Detect orphaned notes: no incoming nor outgoing wiki-link.

A note is orphan iff:
- It has no [[Link]] in its body or frontmatter relations.
- No other note in the workspace links to it, by any name `check_helpers.note_names`
  gives it: basename, path, title, aliases, or an identity key.

Walks the whole workspace (excluding .git, .obsidian, .claude, node_modules,
archives/*, templates/, basic-memory/scripts/, atlas/maps/*-static.md).

Output:
- Plain text list with rel-path of each orphan.
- Summary count at the end.

Usage:
    python3 basic-memory/scripts/check_orphans.py
    python3 basic-memory/scripts/check_orphans.py --output /tmp/orphans.txt
    python3 basic-memory/scripts/check_orphans.py --format markdown
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import link_targets, note_names, resolution_table, scalar  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent.parent
# Read-only, and wider than the corpus on purpose: a link from a root file or
# from a folder corpus.py excludes still makes its target reachable, so the walk
# is the tree less the zones listed here.
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude", "tmp", "__pycache__"}
IGNORED_PATH_PREFIXES = (
    "archives/",
    "templates/",
    "basic-memory/scripts/",
    "basic-memory/schemas/",
    "docs/",
)

@dataclass
class Note:
    path: Path
    text: str
    title: str = ""
    outgoing: set[str] = field(default_factory=set)
    names: set[str] = field(default_factory=set)


def is_ignored(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(p in IGNORED_SEGMENTS for p in parts):
        return True
    rel_str = rel_path.as_posix()
    if any(rel_str.startswith(p) for p in IGNORED_PATH_PREFIXES):
        return True
    if rel_str.endswith("-static.md"):
        return True
    # structural files, not knowledge notes: never meaningful as "orphans"
    structural = {"README.md", "CHANGELOG.md", "GETTING-STARTED.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"}
    if rel_path.name in structural and len(parts) <= 2:
        return True
    return False


def frontmatter_of(text: str) -> F.Frontmatter | None:
    doc = F.split(text)
    return F.parse(doc.block) if doc is not None else None


def extract_links(text: str) -> set[str]:
    return {target for target, _ in link_targets(text)}


def is_journal(fm: F.Frontmatter | None) -> bool:
    """True when the note declares note_type: journal in its frontmatter.

    A daily journal entry legitimately links to nothing. Flagging it would fill
    the report with noise on any workspace that actually journals, so the whole
    type is out of scope rather than each entry having to earn an exemption.
    """
    return scalar(fm, "note_type") == "journal"


def load_notes(root: Path) -> list[Note]:
    notes: list[Note] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if is_ignored(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        fm = frontmatter_of(text)
        if is_journal(fm):
            continue
        notes.append(Note(path=path, text=text, title=scalar(fm, "title") or path.stem,
                          outgoing=extract_links(text), names=note_names(fm, rel.as_posix())))
    return notes


def build_index(notes: list[Note]) -> dict[str, list[Note]]:
    """Map every name a link may use (see check_helpers.note_names) to its notes."""
    return resolution_table((n, n.names) for n in notes)


def find_orphans(notes: list[Note]) -> list[Note]:
    by_name = build_index(notes)

    incoming: dict[Path, int] = {n.path: 0 for n in notes}
    for n in notes:
        for link_target in n.outgoing:
            for target in by_name.get(link_target, []):
                if target.path != n.path:
                    incoming[target.path] += 1

    orphans = []
    for n in notes:
        if incoming[n.path] == 0 and not n.outgoing:
            orphans.append(n)
    return orphans


def render_text(orphans: list[Note]) -> str:
    lines = [f"Orphans found: {len(orphans)}", ""]
    for n in sorted(orphans, key=lambda x: x.path):
        lines.append(n.path.relative_to(WORKSPACE).as_posix())
    return "\n".join(lines) + "\n"


def render_markdown(orphans: list[Note]) -> str:
    lines = [
        "# Orphan notes",
        "",
        f"_{len(orphans)} note(s) with no incoming or outgoing wiki-link._",
        "",
    ]
    if not orphans:
        lines.append("No orphans. The graph is densely linked.")
        return "\n".join(lines) + "\n"

    lines.append("| Path | Title |")
    lines.append("| --- | --- |")
    for n in sorted(orphans, key=lambda x: x.path):
        rel = n.path.relative_to(WORKSPACE).as_posix()
        title = (n.title or "(no title)").replace("|", "\\|")
        lines.append(f"| `{rel}` | {title} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write to file (default: stdout).")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text).",
    )
    args = parser.parse_args(argv)

    notes = load_notes(WORKSPACE)
    print(f"Scanned {len(notes)} notes.", file=sys.stderr)
    orphans = find_orphans(notes)

    rendered = render_text(orphans) if args.format == "text" else render_markdown(orphans)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)

    total = len(notes)
    pct = (len(orphans) / total * 100) if total else 0.0
    print(f"Orphan ratio: {len(orphans)}/{total} = {pct:.1f}%", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
