#!/usr/bin/env python3
"""
Report wiki-links that resolve to nothing in the Basic Memory graph.

A wiki-link `[[Entity]]` that matches no note title is indexed as a relation
whose target is NULL. Nothing warns about it: the link renders fine in Obsidian,
the source file is valid, the note is searchable, but the graph edge is dead and
`build_context` traversal stops there. This is invisible to every other check in
this repo, check_orphans.py only looks at whether a note has any link at all, and
check_symmetric_relations.py compares strings without verifying the target exists.

The script reads the Basic Memory SQLite index directly, in read-only mode, and
classifies each dead target so the output is actionable rather than a flat list:

    missing-entity   looks like a real entity with no note (create the note)
    case-or-accent   a note exists whose title differs only by case or accents
    schema-example   linked only from basic-memory/schemas/, example syntax (to ignore)
    slug-link        targets a filename instead of a title
    other            anything else, usually a heading used as a wiki-link

Only the Basic Memory project named by `basic_memory_project` in
`.sb-config.json` is counted, matched on its name or its permalink. When the
key is null, as in a fresh clone, every project in the index is counted and
the report says so in one line.

Usage:
    python3 basic-memory/scripts/check_unresolved_relations.py
    python3 basic-memory/scripts/check_unresolved_relations.py --min 3
    python3 basic-memory/scripts/check_unresolved_relations.py --format markdown
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path.home() / ".basic-memory" / "memory.db"
WORKSPACE = Path(__file__).resolve().parent.parent.parent
CONFIG = WORKSPACE / ".sb-config.json"
# A dead link written only in these files is example syntax, derived from where
# the link sits rather than from a list of names, so a real note naming a real
# missing `Client` is still reported as a missing entity.
SCHEMA_PREFIX = "basic-memory/schemas/"


def normalize(value: str) -> str:
    """Lowercase and strip accents, to detect near-miss titles."""
    decomposed = unicodedata.normalize("NFD", value)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped.lower().strip()


def configured_project() -> str | None:
    """The `basic_memory_project` of .sb-config.json, or None when unset or absent."""
    try:
        value = json.loads(CONFIG.read_text(encoding="utf-8")).get("basic_memory_project")
    except (OSError, ValueError, AttributeError):
        return None
    return value.strip() if isinstance(value, str) and value.strip() else None


def classify(target: str, sources: set[str], titles_norm: dict[str, str], slugs: set[str]) -> str:
    if "|" in target or (sources and all(s.startswith(SCHEMA_PREFIX) for s in sources)):
        return "schema-example"
    if normalize(target) in titles_norm:
        return "case-or-accent"
    if target in slugs:
        return "slug-link"
    # A plausible entity name: capitalized, more than one character, not a heading
    if target[:1].isupper() and len(target) > 2 and not target.isupper():
        return "missing-entity"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min", type=int, default=1, help="only report targets seen at least N times"
    )
    parser.add_argument(
        "--format", choices=("text", "markdown"), default="text", help="output format"
    )
    parser.add_argument("--db", type=Path, default=DB_PATH, help="path to memory.db")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Database not found: {args.db}", file=sys.stderr)
        return 1

    project = configured_project()
    # Basic Memory keeps every project in one index: `project` holds one row
    # per project, `relation.project_id` and `entity.project_id` point to it.
    where_r, where_e, params = "", "", ()
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        if project is not None:
            row = conn.execute("SELECT id FROM project WHERE name = ? OR permalink = ?",
                               (project, project)).fetchone()
            if row is None:
                print(f"Basic Memory project not found in {args.db}: {project} "
                      "(basic_memory_project in .sb-config.json)", file=sys.stderr)
                return 1
            where_r, where_e, params = " AND r.project_id = ?", " WHERE project_id = ?", (row[0],)
        total = conn.execute("SELECT COUNT(*) FROM relation r WHERE 1 = 1" + where_r,
                             params).fetchone()[0]
        dead = conn.execute(
            "SELECT r.to_name, e.file_path FROM relation r "
            "LEFT JOIN entity e ON e.id = r.from_id "
            "WHERE r.to_id IS NULL" + where_r, params
        ).fetchall()
        entities = conn.execute("SELECT title, file_path FROM entity" + where_e, params).fetchall()
    finally:
        conn.close()

    titles_norm = {normalize(t): t for t, _ in entities if t}
    slugs = {Path(p).stem for _, p in entities}

    counts: Counter[str] = Counter()
    sources: dict[str, set[str]] = defaultdict(set)
    for target, source in dead:
        counts[target] += 1
        if source:
            sources[target].add(source)
    rows = list(counts.items())

    unresolved = sum(count for _, count in rows)
    buckets: dict[str, Counter[str]] = defaultdict(Counter)
    for target, count in rows:
        buckets[classify(target, sources[target], titles_norm, slugs)][target] = count

    ratio = (unresolved / total * 100) if total else 0.0
    header = (
        f"Unresolved relations: {unresolved} / {total} ({ratio:.1f} percent), "
        f"{len(rows)} distinct targets."
    )

    scope = (f"Project: {project}." if project is not None else
             "Counting every Basic Memory project in the index, "
             "basic_memory_project is not set in .sb-config.json.")

    if args.format == "markdown":
        print(f"# Unresolved relations\n\n{header}\n\n_{scope}_\n")
    else:
        print(header)
        print(scope + "\n")

    order = [
        ("missing-entity", "Probable entity with no note, create the note"),
        ("case-or-accent", "A note exists, case or accent differs"),
        ("slug-link", "The link targets a filename instead of a title"),
        ("schema-example", "Example syntax from the schemas, to ignore"),
        ("other", "Other, usually a section heading used as a wiki-link"),
    ]

    for bucket, label in order:
        items = [(t, c) for t, c in buckets[bucket].most_common() if c >= args.min]
        if not items:
            continue
        subtotal = sum(c for _, c in items)
        if args.format == "markdown":
            print(f"\n## {label}\n\n_{len(items)} targets, {subtotal} links_\n")
            print("| Target | Links |")
            print("|---|---|")
            for target, count in items:
                print(f"| `[[{target}]]` | {count} |")
        else:
            print(f"\n{label}  ({len(items)} targets, {subtotal} links)")
            for target, count in items:
                near = titles_norm.get(normalize(target))
                hint = f"   -> exists as \"{near}\"" if near else ""
                print(f"  {count:>4}  [[{target}]]{hint}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
