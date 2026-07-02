#!/usr/bin/env python3
"""
Scan the full workspace for files with double YAML frontmatter blocks.

Previous version relied on `git diff --name-only` which only reports
uncommitted changes. This version walks the whole workspace to catch
already-committed corruptions introduced by the BM `update_frontmatter()`
bug after each reindex.

Usage:
    python3 basic-memory/scripts/check_double_frontmatter.py
"""

from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude"}


def has_double_frontmatter(content: str) -> bool:
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        return False
    end_first = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end_first = i
            break
    if end_first is None:
        return False
    j = end_first + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j >= len(lines) or lines[j] != "---":
        return False
    for k in range(j + 1, len(lines)):
        if lines[k] == "---":
            return True
    return False


def iter_markdown(root: Path):
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if any(seg in IGNORED_SEGMENTS for seg in parts):
            continue
        yield path


def main():
    corrupted = []
    for path in iter_markdown(WORKSPACE):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if has_double_frontmatter(content):
            corrupted.append(path)
    print(f"Total files with DOUBLE frontmatter: {len(corrupted)}")
    for path in corrupted:
        print(f"  {path.relative_to(WORKSPACE)}")


if __name__ == "__main__":
    main()
