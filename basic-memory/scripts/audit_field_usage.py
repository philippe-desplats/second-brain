#!/usr/bin/env python3
"""Measure how often each schema field is actually filled in the workspace.

A schema declares a contract. This script reports whether the contract is
honoured in practice, so an oversized schema shows up as data rather than as
an opinion. It never edits anything.

For every type declared in basic-memory/schemas/, it walks the notes carrying
that type and reports, per field:

    declared   the field exists in the schema's settings.frontmatter block
    required   the schema declares it without a trailing '?'
    present    the field key appears in the note's frontmatter
    filled     the field appears AND carries a non-empty value

Two findings are surfaced explicitly because they are the ones that cost
something:

    - a REQUIRED field filled in fewer than half the notes of its type, which
      means the contract is aspirational rather than real
    - a field that appears in notes but is declared nowhere, which means the
      convention lives only in prose

Usage:
    python3 basic-memory/scripts/audit_field_usage.py
    python3 basic-memory/scripts/audit_field_usage.py --type note
    python3 basic-memory/scripts/audit_field_usage.py --threshold 0.7
    python3 basic-memory/scripts/audit_field_usage.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import load_schemas  # noqa: E402
from corpus import iter_corpus_notes  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = WORKSPACE / "basic-memory" / "schemas"

def parse_frontmatter(text: str) -> F.Frontmatter | None:
    """Return a note's parsed frontmatter, or None if absent.

    Read with `frontmatter.py`, so CRLF, a title folded over 2 lines and a
    list indented at any width all read the way YAML reads them. A note saved
    by a Windows editor is never skipped, and a skipped note is worse than a
    miscounted one because it disappears from the denominator too.
    """
    doc = F.split(text)
    return F.parse(doc.block) if doc is not None else None


def iter_notes(root: Path):
    """Yield (rel, frontmatter) for every corpus note that carries one.

    The walk is `corpus.iter_corpus_notes`, like every other pass: the five
    note zones, minus what a machine reads rather than a human (prompts,
    captures, repo files, skills and their state files, git-ignored dumps).
    A file there claims no schema, so listing it as a note without `type`
    would be noise.
    """
    for path, rel in iter_corpus_notes(root):
        try:
            with open(path, encoding="utf-8", newline="") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse_frontmatter(text)
        if fm is not None and fm.fields:
            # A note with frontmatter but no `type` is itself a finding: it
            # belongs to no schema, so it is reported rather than dropped.
            yield rel, fm


def is_placeholder(value: str) -> bool:
    """An unsubstituted template placeholder, `{client}`, is not a real value."""
    v = value.strip()
    return v in {"", "-", "{}"} or (v.startswith("{") and v.endswith("}"))


def is_filled(fm: F.Frontmatter, key: str) -> bool:
    """A key present with an empty, null or placeholder value is not filled.

    A list is filled when one of its items is. A nested mapping is filled
    unless it is the one-line `{...}` placeholder a template leaves behind.
    """
    f = fm.field(key)
    if f is None:
        return False
    if isinstance(f.value, list):
        return any(not is_placeholder(v) for v in f.value)
    if isinstance(f.value, str):
        return not is_placeholder(f.value)
    if f.style == "nested":
        head = fm.lines[f.start].partition(":")[2].strip()
        return not is_placeholder(head) if head else True
    return False


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", help="restrict the audit to one schema type")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="fill rate below which a required field is flagged (default 0.5)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args(argv)

    schemas = load_schemas(SCHEMA_DIR)

    notes_by_type: dict[str, list[tuple[str, F.Frontmatter]]] = {}
    untyped: list[str] = []
    for rel, fm in iter_notes(WORKSPACE):
        ntype = fm.get("type")
        ntype = ntype.strip() if isinstance(ntype, str) else ""
        if not ntype:
            untyped.append(rel)
            continue
        notes_by_type.setdefault(ntype, []).append((rel, fm))

    report, flagged_required, undeclared = {}, [], []

    for tname, fields in sorted(schemas.items()):
        if args.type and tname != args.type:
            continue
        notes = notes_by_type.get(tname, [])
        entry = {"note_count": len(notes), "fields": {}}
        for fname, required in sorted(fields.items()):
            filled = sum(1 for _, fm in notes if is_filled(fm, fname))
            rate = (filled / len(notes)) if notes else None
            entry["fields"][fname] = {"required": required, "filled": filled, "rate": rate}
            if required and rate is not None and rate < args.threshold:
                flagged_required.append((tname, fname, filled, len(notes), rate))
        # Keys present in notes but declared nowhere in the schema.
        seen: dict[str, int] = {}
        for _, fm in notes:
            for k in fm.keys():
                if k not in fields and k not in ("type", "schema_version"):
                    seen[k] = seen.get(k, 0) + 1
        for k, c in sorted(seen.items(), key=lambda kv: -kv[1]):
            undeclared.append((tname, k, c, len(notes)))
        entry["undeclared"] = dict(seen)
        report[tname] = entry

    orphan_types = sorted(set(notes_by_type) - set(schemas))

    if args.json:
        print(json.dumps({"report": report, "flagged_required": flagged_required,
                          "undeclared": undeclared, "types_without_schema": orphan_types,
                          "notes_without_type": untyped},
                         indent=2, ensure_ascii=False))
        return 0

    print("Field usage audit\n" + "=" * 60)
    for tname, entry in report.items():
        n = entry["note_count"]
        if n == 0:
            print(f"\n{tname}: no note of this type in the workspace, nothing measurable")
            continue
        print(f"\n{tname}  ({n} note{'s' if n > 1 else ''})")
        for fname, d in sorted(entry["fields"].items(), key=lambda kv: (kv[1]["rate"] or 0)):
            mark = "REQ" if d["required"] else "   "
            pct = f"{d['rate'] * 100:5.1f}%"
            print(f"  {mark}  {pct}  {d['filled']:>3}/{n}  {fname}")

    print("\n" + "=" * 60)
    if flagged_required:
        print(f"\nRequired fields filled below {args.threshold:.0%}, the contract is aspirational here:")
        for tname, fname, filled, total, rate in sorted(flagged_required, key=lambda r: r[4]):
            print(f"  {rate * 100:5.1f}%  {filled}/{total}  {tname}.{fname}")
    else:
        print("\nEvery required field clears the threshold.")

    if undeclared:
        print("\nFields used in notes but declared in no schema:")
        for tname, k, c, total in sorted(undeclared, key=lambda r: -r[2]):
            print(f"  {c:>3}/{total}  {tname}.{k}")

    if orphan_types:
        print("\nTypes found in notes with no matching schema:")
        for t in orphan_types:
            print(f"  {t}  ({len(notes_by_type[t])} notes)")

    if untyped:
        print(f"\nNotes with frontmatter but no `type`, so governed by no schema ({len(untyped)}):")
        for rel in untyped:
            print(f"  {rel}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
