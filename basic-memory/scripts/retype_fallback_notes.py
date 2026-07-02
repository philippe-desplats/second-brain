#!/usr/bin/env python3
"""
Retype files currently with `type: note` fallback to a more specific type
based on path and filename patterns.

Rules applied in order, first match wins:
    1. proposals/ or deliverables/           → deliverable
    2. *-transcript-*, *-recorder-*, transcripts/  → transcript
    3. *-research-*, *-audit-*, *-benchmark-* → research
    4. *-strategy-*, *-roadmap-*, *-plan-*    → strategy
    5. *-brainstorm-*                          → brainstorm
    6. *-writing-*                             → writing
    7. *-meeting-*, meetings/                  → meeting
    8. archive/                                → keep as note
    9. (no match)                              → keep as note

Usage:
    python3 basic-memory/scripts/retype_fallback_notes.py --dry-run
    python3 basic-memory/scripts/retype_fallback_notes.py --apply
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent


def parse_frontmatter(path: Path):
    """Return (raw_fm_str, body, has_fm)."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return "", content, False
    end = content.find("\n---", 4)
    if end == -1:
        return "", content, False
    return content[4:end], content[end + 4:], True


def get_type(fm_raw: str) -> str:
    """Extract top-level `type:` scalar."""
    for ln in fm_raw.split("\n"):
        if ln.startswith("type:"):
            return ln.partition(":")[2].strip().strip('"').strip("'")
    return ""


def determine_target_type(path: Path) -> str:
    """Return target type based on path and filename, or 'note' if no specific match."""
    rel = str(path.relative_to(WORKSPACE))
    parts = rel.split("/")
    name = path.stem.lower()

    if "proposals" in parts or "deliverables" in parts:
        return "deliverable"
    if "transcripts" in parts or "-transcript-" in name or "-recorder-" in name:
        return "transcript"
    if "-research-" in name or "-audit-" in name or "-benchmark-" in name:
        return "research"
    if "-strategy-" in name or "-roadmap-" in name or "-plan-" in name:
        return "strategy"
    if "-brainstorm-" in name:
        return "brainstorm"
    if "-writing-" in name:
        return "writing"
    if "meetings" in parts or "-meeting-" in name:
        return "meeting"
    if "archive" in parts:
        return "note"
    return "note"


def find_fallback_notes():
    """Return list of Path for files with type: note."""
    results = []
    for md in WORKSPACE.rglob("*.md"):
        if any(p.startswith(".") for p in md.relative_to(WORKSPACE).parts):
            continue
        if "node_modules" in md.parts or "basic-memory" in md.parts:
            continue
        if "templates" in md.parts:
            continue
        fm_raw, _, has_fm = parse_frontmatter(md)
        if not has_fm:
            continue
        if get_type(fm_raw) == "note":
            results.append(md)
    return sorted(results)


def rewrite_type(path: Path, new_type: str, apply: bool):
    """Replace `type: note` with `type: {new_type}` in the frontmatter."""
    content = path.read_text(encoding="utf-8")
    end = content.find("\n---", 4)
    fm_raw = content[4:end]
    body = content[end + 4:]
    new_fm_raw = re.sub(
        r"^type:\s*note\s*$",
        f"type: {new_type}",
        fm_raw,
        count=1,
        flags=re.MULTILINE,
    )
    new_content = "---" + new_fm_raw + "\n---" + body
    if apply:
        path.write_text(new_content, encoding="utf-8")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 retype_fallback_notes.py --dry-run | --apply")
        sys.exit(1)
    apply = sys.argv[1] == "--apply"

    files = find_fallback_notes()
    print(f"=== retype_fallback_notes, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    print(f"Files with type: note found: {len(files)}")
    print()

    counts = {}
    changes = []
    kept = []
    for path in files:
        target = determine_target_type(path)
        if target == "note":
            kept.append(path)
        else:
            changes.append((path, target))
        counts[target] = counts.get(target, 0) + 1

    print("Planned changes:")
    for path, target in changes:
        rel = path.relative_to(WORKSPACE)
        print(f"  [{target:>11}] {rel}")
        if apply:
            rewrite_type(path, target, True)

    print()
    print(f"Kept as note ({len(kept)}):")
    for path in kept:
        rel = path.relative_to(WORKSPACE)
        print(f"  [       note] {rel}")

    print()
    print("Summary by target type:")
    for t, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")
    print(f"Total scanned: {len(files)}, planned retype: {len(changes)}, kept: {len(kept)}")


if __name__ == "__main__":
    main()
