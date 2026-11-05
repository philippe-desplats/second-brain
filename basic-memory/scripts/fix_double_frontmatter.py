#!/usr/bin/env python3
"""
Merge the frontmatter blocks of files corrupted by Basic Memory's
`update_frontmatter()` bug, which writes a second block right under the first.

What counts as a second block is defined once, by `find_extra_blocks`, which
`check_double_frontmatter.py` imports: a `---` block that directly follows the
first one, blank lines allowed in between, whose every non-blank line belongs
to a top-level `key: value` field, and which holds at least one key Basic
Memory writes (`title`, `type`, `permalink`, `tags`) or a key the blocks above
already have. A body that opens on a `---` horizontal rule and holds prose, or
a single label such as `Summary: ...`, is therefore never taken for
frontmatter.

Strategy, keep the first occurrence of each top-level key across all blocks,
and drop every later one with its whole line range: list items, folded
continuations and block-scalar lines go with their key.

Only corpus notes are visited, through `corpus.iter_corpus_notes`, so the pass
never writes into the folders `corpus.py` excludes. Dry-run is the default, it
prints what it would change. `--apply` writes.

Usage:
    python3 basic-memory/scripts/fix_double_frontmatter.py            # dry-run
    python3 basic-memory/scripts/fix_double_frontmatter.py --dry-run  # same
    python3 basic-memory/scripts/fix_double_frontmatter.py --apply
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402

# Keys Basic Memory writes into the block its bug stacks. A valid key name is
# not enough on its own: a body line `Summary: ...` between two rules has one.
SCHEMA_KEYS = frozenset({"title", "type", "permalink", "tags"})


def looks_like_frontmatter(block: str, known_keys: set[str]) -> bool:
    """Is `block` a real frontmatter stacked under one holding `known_keys`?

    Every key must be one Basic Memory or a template would write,
    `frontmatter.WRITTEN_KEY_RE`, so a body line of prose such as
    `Key takeaways: ...` never passes for a key. Every non-blank line must
    belong to a top-level `key: value` field, as the key itself, a list item or
    a continuation. And at least one key must be a Basic Memory schema key or a
    key the blocks above already hold.
    """
    fm = F.parse(block)
    if not fm.fields or not all(F.WRITTEN_KEY_RE.fullmatch(f.key) for f in fm.fields):
        return False
    owned = set()
    for f in fm.fields:
        owned.update(range(f.start, f.end))
    for i, line in enumerate(fm.lines):
        if line.strip() and i not in owned:
            return False
    keys = {f.key for f in fm.fields}
    return bool(keys & (SCHEMA_KEYS | known_keys))


def find_extra_blocks(text: str) -> tuple[F.Doc, list[F.Doc]] | None:
    """The first frontmatter and the blocks stacked right under it, or None.

    Returns None when the note has no frontmatter or a single block. The last
    Doc of the list carries the real body.
    """
    doc = F.split(text)
    if doc is None:
        return None
    extras: list[F.Doc] = []
    known = {f.key for f in F.parse(doc.block).fields}
    rest = doc.body
    while True:
        lines = rest.splitlines(keepends=True)
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        nxt = F.split("".join(lines[i:]))
        if nxt is None or not looks_like_frontmatter(nxt.block, known):
            break
        extras.append(nxt)
        known |= {f.key for f in F.parse(nxt.block).fields}
        rest = nxt.body
    return (doc, extras) if extras else None


def merge(doc: F.Doc, extras: list[F.Doc]) -> tuple[F.Doc, list[str]]:
    """One Doc holding every block merged, and the duplicate keys dropped."""
    lines: list[str] = []
    for block in [doc.block] + [e.block for e in extras]:
        lines.extend(F.parse(block).lines)
    fm = F.parse("".join(line + "\n" for line in lines))
    seen: set[str] = set()
    dropped: list[F.Field] = []
    for f in fm.fields:
        if f.key in seen:
            dropped.append(f)
        seen.add(f.key)
    for f in reversed(dropped):
        del lines[f.start:f.end]
    last = extras[-1]
    merged = dataclasses.replace(doc, block="".join(line + "\n" for line in lines),
                                 body=last.body, closer=last.closer,
                                 closer_eol=last.closer_eol)
    names = []
    for f in dropped:
        if f.key not in names:
            names.append(f.key)
    return merged, names


def fix_text(text: str) -> tuple[str, int, list[str]] | None:
    """(fixed text, blocks merged, duplicate keys dropped), or None when clean."""
    found = find_extra_blocks(text)
    if found is None:
        return None
    doc, extras = found
    merged, dropped = merge(doc, extras)
    return F.join(merged), len(extras) + 1, dropped


def fix_file(path: Path, apply: bool) -> tuple[int, list[str]] | None:
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    result = fix_text(text)
    if result is None:
        return None
    new_text, blocks, dropped = result
    if apply:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_text)
    return blocks, dropped


def main(argv=None, root: Path = WORKSPACE) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true",
                      help="write the merged frontmatter (default: dry-run)")
    mode.add_argument("--dry-run", action="store_true",
                      help="report only, the default, accepted for explicitness")
    args = parser.parse_args(argv)

    fixed = []
    errors = 0
    for path, rel in iter_corpus_notes(root):
        try:
            result = fix_file(path, args.apply)
        except (OSError, UnicodeDecodeError) as e:
            print(f"ERROR on {rel}: {e}", file=sys.stderr)
            errors += 1
            continue
        if result is not None:
            fixed.append((rel, *result))

    verb = "Fixed" if args.apply else "Would fix"
    print(f"{verb} {len(fixed)} files" + ("" if args.apply else " (dry-run, nothing written)"))
    for rel, blocks, dropped in fixed:
        detail = f"merge {blocks} blocks"
        if dropped:
            detail += ", drop duplicate keys: " + ", ".join(dropped)
        print(f"  {rel}: {detail}")
    if errors:
        print(f"{errors} errors")
    if fixed and not args.apply:
        print("\nRerun with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
