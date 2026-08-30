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
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = WORKSPACE / "basic-memory" / "schemas"

# Directories that hold no workspace notes.
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", "tmp"}
# Paths whose notes are documentation about the workspace, not notes in it.
SKIP_PREFIXES = ("basic-memory/schemas", ".claude", "docs", "templates")


def load_schema_fields(path: Path) -> tuple[dict[str, bool], str]:
    """Return {field_name: required} from a schema's settings.frontmatter block."""
    text = path.read_text(encoding="utf-8")
    fields: dict[str, bool] = {}

    match = re.search(r"^  frontmatter:\n((?:    .*\n|\n)*)", text, re.MULTILINE)
    if not match:
        return fields, path.stem

    for line in match.group(1).splitlines():
        # Field declarations sit at exactly four spaces; enum values are list items.
        decl = re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*)(\??)(?:\(.*\))?\s*:", line)
        if decl:
            fields[decl.group(1)] = decl.group(2) != "?"
    return fields, path.stem


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return {key: raw_value} for a note's frontmatter, or None if absent.

    CRLF is normalised first: a note saved by a Windows editor would otherwise
    be silently skipped, and a skipped note is worse than a miscounted one
    because it disappears from the denominator too.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None

    out: dict[str, str] = {}
    current: str | None = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # A list item continues the previous key.
        if line.startswith(("  - ", "- ")):
            if current:
                out[current] = (out.get(current, "") + " x").strip()
            continue
        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:(.*)$", line)
        if kv:
            current = kv.group(1)
            out[current] = kv.group(2).strip()
    return out


def iter_notes(root: Path):
    for path in sorted(root.rglob("*.md")):
        rel_path = path.relative_to(root)
        rel = rel_path.as_posix()
        # Test the RELATIVE parts: an absolute path containing a segment named
        # tmp or .git would otherwise silence the whole audit.
        if any(part in SKIP_DIRS for part in rel_path.parts):
            continue
        if rel.startswith(SKIP_PREFIXES):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse_frontmatter(text)
        if fm:
            # A note with frontmatter but no `type` is itself a finding: it
            # belongs to no schema, so it is reported rather than dropped.
            yield rel, fm


def is_filled(value: str) -> bool:
    """A key present with an empty or placeholder value is not filled."""
    v = value.strip().strip("\"'")
    if not v or v in {"[]", "{}", "null", "~", "-"}:
        return False
    # Unsubstituted template placeholders do not count as real values.
    return not (v.startswith("{") and v.endswith("}"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", help="restrict the audit to one schema type")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="fill rate below which a required field is flagged (default 0.5)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args(argv)

    schemas = {}
    for p in sorted(SCHEMA_DIR.glob("*.md")):
        if p.stem == "README":
            continue
        fields, name = load_schema_fields(p)
        schemas[name] = fields

    notes_by_type: dict[str, list[tuple[str, dict]]] = {}
    untyped: list[str] = []
    for rel, fm in iter_notes(WORKSPACE):
        ntype = (fm.get("type") or "").strip()
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
            filled = sum(1 for _, fm in notes if fname in fm and is_filled(fm[fname]))
            rate = (filled / len(notes)) if notes else None
            entry["fields"][fname] = {"required": required, "filled": filled, "rate": rate}
            if required and rate is not None and rate < args.threshold:
                flagged_required.append((tname, fname, filled, len(notes), rate))
        # Keys present in notes but declared nowhere in the schema.
        seen: dict[str, int] = {}
        for _, fm in notes:
            for k in fm:
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
