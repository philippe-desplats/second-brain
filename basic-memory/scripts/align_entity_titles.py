#!/usr/bin/env python3
"""
Align the `title:` of entity notes on their identity field.

Basic Memory resolves a wiki-link `[[Entity]]` on the note `title:` only (or on
its permalink). It does NOT resolve on `client:`, `partner:` or `name:`. Any
entity note whose `title:` differs from its identity value makes every incoming wiki-link dangle silently:
the link renders fine in Obsidian, the file is indexed, but the graph edge points
to nothing and `build_context` traversal stops there.

Scope and identity field per zone:

    atlas/people/*.md                    name
    atlas/topics/*.md                    name
    atlas/services/*.md                  name
    sources/clients/*/CLAUDE.md          client
    sources/partners/*/CLAUDE.md         partner

Conservative by design:
- Dry-run is the default, --apply is required to write.
- Only the `title:` field of the frontmatter is touched, its whole line range
  when Basic Memory folded it over several lines. The body, the H1 and every
  other field are left untouched, so no information is ever lost.
- The new value is quoted through the shared policy of `frontmatter.py`, so
  `Acme: Studio` or `Foo #2` reads back as written.
- Only corpus notes are written, `corpus.is_corpus_note` filters the globs.
- A file whose H1 no longer matches its new title is reported separately, for a
  cosmetic pass decided by a human.
- A file with no identity field, no frontmatter, or an empty identity value is
  skipped and reported.
- A `title:` declared twice, holding a list or a block, opening a quote its
  range never closes, or absorbing a list item or another field is never
  rewritten, since its range may hold lines of another field. It is listed
  under "Needs repair".

Usage:
    python3 basic-memory/scripts/align_entity_titles.py
    python3 basic-memory/scripts/align_entity_titles.py --apply
    python3 basic-memory/scripts/align_entity_titles.py --zone people --apply
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from corpus import WORKSPACE, is_corpus_note, rel_posix  # noqa: E402
from note_types import REPAIR_HINT, field_damage  # noqa: E402

# zone name -> (glob pattern relative to workspace, identity frontmatter field)
ZONES: dict[str, tuple[str, str]] = {
    "people": ("atlas/people/*.md", "name"),
    "topics": ("atlas/topics/*.md", "name"),
    "services": ("atlas/services/*.md", "name"),
    "clients": ("sources/clients/*/CLAUDE.md", "client"),
    "partners": ("sources/partners/*/CLAUDE.md", "partner"),
}

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def as_text(value) -> str:
    """A decoded scalar stripped, empty for a list, a mapping or a null."""
    return value.strip() if isinstance(value, str) else ""


def set_title(fm: F.Frontmatter, title: str) -> F.Frontmatter:
    """Set `title:`, its whole line range when present, as the first field otherwise."""
    if "title" in fm:
        return F.set_field(fm, "title", title)
    line = F.render_field("title", title)
    return F.parse("".join(ln + "\n" for ln in line + fm.lines))


@dataclass
class Result:
    path: Path
    zone: str
    identity: str
    old_title: str | None
    action: str  # "insert", "replace", "ok", "skip", "repair"
    reason: str = ""
    h1_diverges: bool = False


def process(path: Path, zone: str, identity_field: str, apply: bool,
            root: Path = WORKSPACE) -> Result:
    rel = Path(rel_posix(path, root))

    doc, fm = F.read_file(path)
    if doc is None:
        return Result(rel, zone, "", None, "skip", "no frontmatter")

    if identity_field not in fm:
        return Result(rel, zone, "", None, "skip", f"field `{identity_field}` missing")

    identity = as_text(fm.get(identity_field))
    if not identity:
        return Result(rel, zone, "", None, "skip", f"field `{identity_field}` empty")

    old_title = as_text(fm.get("title")) if "title" in fm else None

    damage = field_damage(fm, "title")
    if damage:
        return Result(rel, zone, identity, old_title, "repair", damage)

    h1_match = H1_RE.search(doc.body)
    h1 = h1_match.group(1).strip() if h1_match else ""
    h1_diverges = bool(h1) and h1 != identity

    if old_title == identity and len([f for f in fm.fields if f.key == "title"]) == 1:
        return Result(rel, zone, identity, old_title, "ok", "", h1_diverges)

    action = "insert" if old_title is None else "replace"
    if apply:
        F.write_file(path, doc, set_title(fm, identity))

    return Result(rel, zone, identity, old_title, action, "", h1_diverges)


def main(argv=None, root: Path = WORKSPACE) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="write the changes (default: dry-run)"
    )
    parser.add_argument(
        "--zone",
        choices=sorted(ZONES),
        action="append",
        help="restrict to one or more zones (default: all)",
    )
    args = parser.parse_args(argv)

    zones = args.zone or sorted(ZONES)
    results: list[Result] = []

    for zone in zones:
        pattern, identity_field = ZONES[zone]
        for path in sorted(root.glob(pattern)):
            if not is_corpus_note(rel_posix(path, root), root):
                continue
            results.append(process(path, zone, identity_field, args.apply, root))

    changed = [r for r in results if r.action in ("insert", "replace")]
    skipped = [r for r in results if r.action == "skip"]
    repairs = [r for r in results if r.action == "repair"]
    ok = [r for r in results if r.action == "ok"]

    mode = "APPLIED" if args.apply else "DRY-RUN, nothing written"
    print(f"=== Entity title alignment, {mode} ===\n")

    if changed:
        print(f"{len(changed)} file(s) to fix:\n")
        for r in changed:
            before = "(no title)" if r.old_title is None else f'"{r.old_title}"'
            print(f"  [{r.zone}] {r.path}")
            print(f"      {before}  ->  \"{r.identity}\"")
        print()

    if skipped:
        print(f"{len(skipped)} file(s) skipped:\n")
        for r in skipped:
            print(f"  [{r.zone}] {r.path}  ({r.reason})")
        print()

    if repairs:
        print(f"{REPAIR_HINT} ({len(repairs)}):\n")
        for r in repairs:
            print(f"  [{r.zone}] {r.path}  ({r.reason}, left untouched)")
        print()

    diverging = [r for r in results if r.h1_diverges and r.action != "skip"]
    if diverging:
        print(
            f"{len(diverging)} file(s) whose H1 differs from the title, "
            "a cosmetic pass to decide:\n"
        )
        for r in diverging:
            print(f"  [{r.zone}] {r.path}")
        print()

    print(
        f"Total {len(results)} file(s): {len(ok)} already compliant, "
        f"{len(changed)} to fix, {len(skipped)} skipped, {len(repairs)} need repair."
    )
    if not args.apply and changed:
        print("\nRerun with --apply to write, then `bm reindex`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
