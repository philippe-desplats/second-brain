#!/usr/bin/env python3
"""
Scan the full workspace for files with double YAML frontmatter blocks.

Previous version relied on `git diff --name-only` which only reports
uncommitted changes. This version walks the whole workspace to catch
already-committed corruptions introduced by the BM `update_frontmatter()`
bug after each reindex.

The detection is `fix_double_frontmatter.find_extra_blocks`, imported, so this
check reports exactly what the fix would merge. A body that opens on a `---`
horizontal rule is not a second frontmatter.

Read-only, so it scans wider than the corpus: Basic Memory syncs every
markdown file of the project, templates and skill files under the note zones
included, and the bug can hit any of them. A file outside the corpus is
flagged, since `fix_double_frontmatter.py` never writes there and it has to
be repaired by hand.

Usage:
    python3 basic-memory/scripts/check_double_frontmatter.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import IGNORED_SEGMENTS, WORKSPACE, in_note_zone, is_corpus_note, rel_posix  # noqa: E402
from fix_double_frontmatter import find_extra_blocks  # noqa: E402

# `.claude/` holds skills and rules, never synced as notes.
SKIPPED_SEGMENTS = IGNORED_SEGMENTS | {".claude"}


def has_double_frontmatter(content: str) -> bool:
    return find_extra_blocks(content) is not None


def iter_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(seg in SKIPPED_SEGMENTS for seg in parts):
            continue
        yield path


def main(root: Path = WORKSPACE):
    corrupted = []
    for path in iter_markdown(root):
        try:
            with open(path, encoding="utf-8", newline="") as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        if has_double_frontmatter(content):
            corrupted.append(rel_posix(path, root))
    print(f"Total files with DOUBLE frontmatter: {len(corrupted)}")
    for rel in corrupted:
        outside = not (in_note_zone(rel) and is_corpus_note(rel, root))
        print(f"  {rel}" + ("  (outside the corpus, repair by hand)" if outside else ""))


if __name__ == "__main__":
    main()
