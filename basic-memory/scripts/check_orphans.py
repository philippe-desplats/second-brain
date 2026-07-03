#!/usr/bin/env python3
"""
Detect orphaned notes: no incoming nor outgoing wiki-link.

A note is orphan iff:
- It has no [[Link]] in its body or frontmatter relations.
- No other note in the workspace links to it (by title, slug, or basename).

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
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude"}
IGNORED_PATH_PREFIXES = (
    "archives/",
    "templates/",
    "basic-memory/scripts/",
    "basic-memory/schemas/",
)

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?(?:#[^\]]+)?\]\]")


@dataclass
class Note:
    path: Path
    text: str
    title: str = ""
    outgoing: set[str] = field(default_factory=set)


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
    if rel_path.name in {"README.md", "CHANGELOG.md", "GETTING-STARTED.md", "AGENTS.md", "CLAUDE.md"} and len(parts) <= 2:
        return True
    return False


def extract_title(text: str, fallback: str) -> str:
    if text.startswith("---"):
        lines = text.split("\n")
        for i in range(1, len(lines)):
            if lines[i] == "---":
                break
            m = re.match(r"^title:\s*(.+?)\s*$", lines[i])
            if m:
                return m.group(1).strip('"\'')
    return fallback


def extract_links(text: str) -> set[str]:
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(text)}


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
        title = extract_title(text, path.stem)
        outgoing = extract_links(text)
        notes.append(Note(path=path, text=text, title=title, outgoing=outgoing))
    return notes


def build_index(notes: list[Note]) -> dict[str, list[Note]]:
    """Map a queryable name (title, basename) to notes that match."""
    index: dict[str, list[Note]] = {}
    for n in notes:
        for key in {n.title, n.path.stem}:
            if not key:
                continue
            index.setdefault(key, []).append(n)
    return index


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
