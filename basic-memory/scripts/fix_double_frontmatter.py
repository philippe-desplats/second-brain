#!/usr/bin/env python3
"""
Merge the two frontmatter blocks of files corrupted by Basic Memory's
`update_frontmatter()` bug. Walks the entire workspace (not just git diff).

Strategy, keep the first occurrence of each top-level key across both blocks,
drop duplicates.

Usage:
    python3 basic-memory/scripts/fix_double_frontmatter.py
"""

import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude"}


def iter_markdown(root: Path):
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if any(seg in IGNORED_SEGMENTS for seg in parts):
            continue
        yield path


def fix_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
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
    end_second = None
    for k in range(j + 1, len(lines)):
        if lines[k] == "---":
            end_second = k
            break
    if end_second is None:
        return False
    first_fm_lines = lines[1:end_first]
    second_fm_lines = lines[j + 1:end_second]
    seen_keys = set()
    merged = []
    for fm_line in first_fm_lines + second_fm_lines:
        stripped = fm_line.lstrip()
        if ":" in stripped and not stripped.startswith(("- ", "#")):
            key = stripped.split(":", 1)[0].strip()
            if key in seen_keys:
                continue
            seen_keys.add(key)
        merged.append(fm_line)
    body = lines[end_second + 1:]
    new_content = "---\n" + "\n".join(merged) + "\n---\n" + "\n".join(body)
    path.write_text(new_content, encoding="utf-8")
    return True


def main():
    fixed = []
    errors = 0
    for path in iter_markdown(WORKSPACE):
        try:
            if fix_file(path):
                fixed.append(path)
        except Exception as e:
            print(f"ERROR on {path}: {e}", file=sys.stderr)
            errors += 1
    print(f"Fixed {len(fixed)} files")
    if errors:
        print(f"{errors} errors")


if __name__ == "__main__":
    main()
