#!/usr/bin/env python3
"""
Retype files currently with `type: note` fallback to a more specific type
based on path and filename patterns.

The pattern table lives in `note_types.py`, shared with `retype_files.py`, so
both passes give a file the same type. In short, first match wins: a context
file by its place, a container folder above the file (`meetings/`,
`deliverables/`, `proposals/`, `transcripts/`, `clippings/`, `sessions/`,
`emails/`), the word right after the date in `YYYY-MM-DD-{type}-slug.md`, then
a keyword in the name (`-audit-`, `-plan-`, `-roadmap-` and the like). No match
keeps the note a `note`.

A note under `knowledge/` that declares a `subtype` is never retyped, its
genre is the subtype (see `.claude/rules/knowledge.md`).

Only corpus notes are visited, through `corpus.iter_corpus_notes`, so the
pass never writes into the folders `corpus.py` excludes.

A `type: note` declared twice or spread over several lines is never
rewritten, its line range may hold lines of another field. Such a file is
listed under "Needs repair".

Usage:
    python3 basic-memory/scripts/retype_fallback_notes.py --dry-run
    python3 basic-memory/scripts/retype_fallback_notes.py --apply
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from note_types import REPAIR_HINT, classify, type_damage  # noqa: E402


def determine_target_type(rel: str, fm: F.Frontmatter) -> str:
    """The type a `type: note` file should carry, `note` when no rule applies."""
    subtype = fm.get("subtype")
    return classify(rel, subtype if isinstance(subtype, str) else None) or "note"


def find_fallback_notes(root=WORKSPACE):
    """Yield (path, rel, doc, fm) for every corpus note typed `note`."""
    for path, rel in iter_corpus_notes(root):
        doc, fm = F.read_file(path)
        if doc is not None and fm.get("type") == "note":
            yield path, rel, doc, fm


def main(argv=None, root=WORKSPACE):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in {"--dry-run", "--apply"}:
        print("Usage: python3 retype_fallback_notes.py --dry-run | --apply")
        sys.exit(1)
    apply = argv[0] == "--apply"

    files = list(find_fallback_notes(root))
    print(f"=== retype_fallback_notes, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    print(f"Files with type: note found: {len(files)}")
    print()

    counts = {}
    changes = []
    kept = []
    repairs = []
    for path, rel, doc, fm in files:
        target = determine_target_type(rel, fm)
        damage = type_damage(fm)
        if target == "note":
            kept.append(rel)
        elif damage:
            repairs.append((rel, damage))
            continue
        else:
            changes.append((path, rel, doc, fm, target))
        counts[target] = counts.get(target, 0) + 1

    print("Planned changes:")
    for path, rel, doc, fm, target in changes:
        print(f"  [{target:>11}] {rel}")
        if apply:
            F.write_file(path, doc, F.set_field(fm, "type", target))

    print()
    print(f"Kept as note ({len(kept)}):")
    for rel in kept:
        print(f"  [       note] {rel}")

    if repairs:
        print()
        print(f"{REPAIR_HINT} ({len(repairs)}):")
        for rel, damage in repairs:
            print(f"  {rel}: {damage}, left untouched")

    print()
    print("Summary by target type:")
    for t, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")
    print(f"Total scanned: {len(files)}, planned retype: {len(changes)}, kept: {len(kept)}")


if __name__ == "__main__":
    main()
