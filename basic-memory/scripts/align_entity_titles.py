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
- Only the `title:` line of the frontmatter is touched. The body, the H1 and
  every other field are left untouched, so no information is ever lost.
- A file whose H1 no longer matches its new title is reported separately, for a
  cosmetic pass decided by a human.
- A file with no identity field, no frontmatter, or an empty identity value is
  skipped and reported.

Usage:
    python3 basic-memory/scripts/align_entity_titles.py
    python3 basic-memory/scripts/align_entity_titles.py --apply
    python3 basic-memory/scripts/align_entity_titles.py --zone people --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# zone name -> (glob pattern relative to workspace, identity frontmatter field)
ZONES: dict[str, tuple[str, str]] = {
    "people": ("atlas/people/*.md", "name"),
    "topics": ("atlas/topics/*.md", "name"),
    "services": ("atlas/services/*.md", "name"),
    "clients": ("sources/clients/*/CLAUDE.md", "client"),
    "partners": ("sources/partners/*/CLAUDE.md", "partner"),
}

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def field_re(field: str) -> re.Pattern[str]:
    """Match a top-level `field: value` line inside the frontmatter block."""
    return re.compile(rf"^{re.escape(field)}:[ \t]*(.*?)[ \t]*$", re.MULTILINE)


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def needs_quoting(value: str) -> bool:
    """A YAML scalar needs quoting when it starts with a reserved indicator."""
    return bool(value) and value[0] in "&*!|>%@`{}[],#?-:"


def yaml_scalar(value: str) -> str:
    if needs_quoting(value) or value != value.strip():
        return '"' + value.replace('"', r"\"") + '"'
    return value


@dataclass
class Result:
    path: Path
    zone: str
    identity: str
    old_title: str | None
    action: str  # "insert", "replace", "ok", "skip"
    reason: str = ""
    h1_diverges: bool = False


def process(path: Path, zone: str, identity_field: str, apply: bool) -> Result:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(WORKSPACE)

    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return Result(rel, zone, "", None, "skip", "no frontmatter")

    block = fm_match.group(1)
    id_match = field_re(identity_field).search(block)
    if not id_match:
        return Result(rel, zone, "", None, "skip", f"field `{identity_field}` missing")

    identity = unquote(id_match.group(1))
    if not identity:
        return Result(rel, zone, "", None, "skip", f"field `{identity_field}` empty")

    title_match = field_re("title").search(block)
    old_title = unquote(title_match.group(1)) if title_match else None

    h1_match = H1_RE.search(text[fm_match.end():])
    h1 = h1_match.group(1).strip() if h1_match else ""
    h1_diverges = bool(h1) and h1 != identity

    if old_title == identity:
        return Result(rel, zone, identity, old_title, "ok", "", h1_diverges)

    new_line = f"title: {yaml_scalar(identity)}"
    if title_match:
        new_block = (
            block[: title_match.start()] + new_line + block[title_match.end():]
        )
        action = "replace"
    else:
        new_block = new_line + "\n" + block
        action = "insert"

    if apply:
        new_text = text[: fm_match.start(1)] + new_block + text[fm_match.end(1):]
        path.write_text(new_text, encoding="utf-8")

    return Result(rel, zone, identity, old_title, action, "", h1_diverges)


def main() -> int:
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
    args = parser.parse_args()

    zones = args.zone or sorted(ZONES)
    results: list[Result] = []

    for zone in zones:
        pattern, identity_field = ZONES[zone]
        for path in sorted(WORKSPACE.glob(pattern)):
            results.append(process(path, zone, identity_field, args.apply))

    changed = [r for r in results if r.action in ("insert", "replace")]
    skipped = [r for r in results if r.action == "skip"]
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
        f"{len(changed)} to fix, {len(skipped)} skipped."
    )
    if not args.apply and changed:
        print("\nRerun with --apply to write, then `bm reindex`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
