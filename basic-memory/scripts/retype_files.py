#!/usr/bin/env python3
"""
Retype files: update frontmatter `type:` based on path/filename patterns.

Usage:
    python3 basic-memory/scripts/retype_files.py --dry-run
    python3 basic-memory/scripts/retype_files.py --apply

The pattern table lives in `note_types.py`, shared with
`retype_fallback_notes.py`. In short, first match wins:
    sources/clients/{X}/CLAUDE.md                     -> client-context
    sources/partners/{X}/CLAUDE.md                    -> partner-context
    sources/{any}/{project}/README.md or CLAUDE.md    -> project-brief
    emails/ mails/ meetings/ deliverables/ proposals/
    transcripts/ clippings/ sessions/ above the file  -> that folder's type
    YYYY-MM-DD-{type}-*.md                            -> {type}
    YYYY-MM-DD-{seq}-{direction}-*.md                 -> email
    a `-audit-`, `-plan-`, ... keyword in the name    -> its type

Only corpus notes are visited, through `corpus.iter_corpus_notes`, so the
pass never writes into the folders `corpus.py` excludes. A file whose `type:`
is already correct is left untouched (idempotent). A file with a specific
type that the table contradicts is reported and skipped, except under a
container folder, which forces its type.

An existing `type:` is rewritten only when it reads as one of the 17 types on
a single line. A damaged one, a duplicated one, or a value the pass cannot
vouch for is listed under "Needs repair" and never written, since its line
range may hold lines of another field. So is any note where a quoted scalar
or a flow collection swallowed a column-0 `key:` line. The exit code does not
change.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from note_types import (REPAIR_HINT, classify, field_damage, is_forced,  # noqa: E402
                        swallowed_key_line, type_damage, unknown_type)


def current_type(fm: F.Frontmatter) -> str:
    """The declared `type:` as a string, empty when absent or not a scalar."""
    value = fm.get("type")
    return value if isinstance(value, str) else ""


def set_type(fm: F.Frontmatter, new_type: str) -> F.Frontmatter:
    """Set `type:` to `new_type`.

    An existing `type:` has its line range replaced. A missing one is inserted
    right after the full range of `title:`, or after the last field when there
    is no title, never inside a list or a folded value.
    """
    return F.set_field(fm, "type", new_type, after="title")


def plan(root=WORKSPACE):
    """Yield (path, rel, doc, fm, current, target, action) for every typed note.

    `action` is UPDATE, OK, SKIP_CONFLICT, NO_PATTERN or NEEDS_REPAIR, the
    last one with the reason in place of `current`.
    """
    for path, rel in iter_corpus_notes(root):
        doc, fm = F.read_file(path)
        if doc is None:
            yield path, rel, None, None, "", None, "NO_FRONTMATTER"
            continue
        subtype = fm.get("subtype")
        target = classify(rel, subtype if isinstance(subtype, str) else None)
        current = current_type(fm)
        if target is None:
            action = "NO_PATTERN"
        elif current == target:
            action = "OK"
        elif current and current != "note" and not is_forced(rel):
            action = "SKIP_CONFLICT"
        else:
            action = "UPDATE"
        swallowed = swallowed_key_line(fm)
        if swallowed:
            action, current = "NEEDS_REPAIR", swallowed
        elif action in ("UPDATE", "SKIP_CONFLICT"):
            damage = repair_reason(fm, action)
            if damage:
                action, current = "NEEDS_REPAIR", damage
        yield path, rel, doc, fm, current, target, action


def repair_reason(fm: F.Frontmatter, action: str) -> str | None:
    """Why `set_type` must not touch this block, None when it may.

    A damaged `type:` is never rewritten, since its range may cover lines of
    another field. Nor is a single-line value outside the 17 types, which the
    pass did not write and cannot vouch for. A missing `type:` goes after
    `title:`, so a damaged title blocks the insertion too.
    """
    if "type" not in fm:
        damage = field_damage(fm, "title")
        return f"{damage}, `type:` would land inside it" if damage else None
    damage = type_damage(fm)
    if damage or action == "SKIP_CONFLICT":
        return damage
    return unknown_type(fm)


def main(argv=None, root=WORKSPACE):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in {"--dry-run", "--apply"}:
        print("Usage: python3 retype_files.py --dry-run | --apply")
        sys.exit(1)

    dry_run = argv[0] == "--dry-run"

    stats = {
        "total_scanned": 0,
        "already_correct": 0,
        "no_frontmatter": 0,
        "no_pattern": 0,
        "would_update": 0,
        "updated": 0,
        "by_target": {},
    }
    changes = []

    for path, rel, doc, fm, current, target, action in plan(root):
        stats["total_scanned"] += 1
        if action == "NO_FRONTMATTER":
            stats["no_frontmatter"] += 1
            continue
        if action == "NO_PATTERN":
            stats["no_pattern"] += 1
            continue
        if action == "OK":
            stats["already_correct"] += 1
            continue
        if action in ("SKIP_CONFLICT", "NEEDS_REPAIR"):
            changes.append({"path": rel, "current": current, "target": target,
                            "action": action})
            continue

        stats["would_update"] += 1
        stats["by_target"][target] = stats["by_target"].get(target, 0) + 1
        changes.append({"path": rel, "current": current or "(none)", "target": target,
                        "action": "UPDATE"})

        if not dry_run:
            if F.write_file(path, doc, set_type(fm, target)):
                stats["updated"] += 1

    # Report
    print(f"=== Retype report ({'DRY RUN' if dry_run else 'APPLIED'}) ===")
    print(f"Total scanned: {stats['total_scanned']}")
    print(f"Already correct: {stats['already_correct']}")
    print(f"No frontmatter: {stats['no_frontmatter']}")
    print(f"No pattern: {stats['no_pattern']}")
    print(f"Would update: {stats['would_update']}" if dry_run else f"Updated: {stats['updated']}")
    print("")
    print("By target type:")
    for t, n in sorted(stats["by_target"].items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")
    print("")
    conflicts = [c for c in changes if c["action"] == "SKIP_CONFLICT"]
    if conflicts:
        print(f"Skipped {len(conflicts)} conflicts (non-note → other):")
        for c in conflicts[:10]:
            print(f"  {c['path']}: {c['current']} -> {c['target']}")
    repairs = [c for c in changes if c["action"] == "NEEDS_REPAIR"]
    if repairs:
        print(f"{REPAIR_HINT} ({len(repairs)}):")
        for c in repairs:
            print(f"  {c['path']}: {c['current']}, left untouched")
    if dry_run and stats["would_update"] > 0:
        print(f"\nSample updates (first 10):")
        for c in [c for c in changes if c["action"] == "UPDATE"][:10]:
            print(f"  {c['path']}: {c['current']} -> {c['target']}")


if __name__ == "__main__":
    main()
