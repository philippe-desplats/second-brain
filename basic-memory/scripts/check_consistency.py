#!/usr/bin/env python3
"""Check that the workspace agrees with itself.

Four defect classes kept recurring across manual reviews of this repository,
and all four are mechanically detectable. This script exists so they are
caught by a command rather than by whoever happens to look closely.

    1. A skill emits frontmatter that would not validate.
       A skill that writes a note the schemas reject produces material the
       whole system then ignores. Found three times by hand: the project brief
       template, then the client context and partner context templates ninety
       lines above it in the same file, each missing `type` or `schema_version`.
       A client created that way is invisible to every index and every view.

    2. A view reads a property no schema declares.
       The `.base` files and inline base blocks filter, order and sort on
       frontmatter properties. When a property is used but declared nowhere,
       the view still renders, silently returning nothing or an empty column.
       Found three times by hand: `title` on the context schemas, `topics` on
       note and project-brief, `subtype` on note.

    3. A wiki-link points at nothing.
       Found nine times by hand, eight of them in the workspace hub, all
       pointing at index files that no code path ever created.

    4. A `topics` slug names no entry in atlas/topics/.
       The MOC views filter on `note.topics`, so a slug resolving to nothing
       produces a view that renders empty with no error. Found once by hand:
       three of the four slugs on the demo briefs were invented. Reported as a
       warning, since writing a brief before its topic note is legitimate.

Read-only. It reports and exits non-zero on findings, it changes nothing.

Usage:
    python3 basic-memory/scripts/check_consistency.py
    python3 basic-memory/scripts/check_consistency.py --only templates
    python3 basic-memory/scripts/check_consistency.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import (as_list, link_targets, load_schemas as load_schema_table,  # noqa: E402
                           note_names, raw_head, read_frontmatter, scalar)

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = WORKSPACE / "basic-memory" / "schemas"
SKILL_DIR = WORKSPACE / ".claude" / "skills"

# This check reads wider than the corpus on purpose: skill templates under
# `.claude/`, the `.base` views and the documentation are exactly what it
# audits, so it walks the whole tree rather than `corpus.iter_corpus_notes`.
# It never writes.
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", "__pycache__", "tmp"}

# Meta fields every note carries, declared in no schema's frontmatter block.
META_FIELDS = {"type", "schema_version"}
# Properties Bases resolves itself, they are never frontmatter.
FILE_PROPERTIES_PREFIX = ("file.", "formula.", "note.file.")

FENCE_RE = re.compile(r"```(markdown|yaml)?\n(.*?)```", re.S)
BASE_FENCE_RE = re.compile(r"```base\n(.*?)```", re.S)
# note.x, or a bare identifier used as a column or sort key
PROP_RE = re.compile(r"note\.([a-z_][a-z0-9_]*)")


def load_schemas() -> dict[str, set[str]]:
    """Return {type_name: declared field names} from settings.frontmatter."""
    return {name: set(fields) for name, fields in load_schema_table(SCHEMA_DIR).items()}


def iter_files(root: Path, pattern: str):
    for path in sorted(root.rglob(pattern)):
        if any(part in IGNORED_SEGMENTS for part in path.relative_to(WORKSPACE).parts):
            continue
        yield path


def parse_frontmatter_keys(text: str) -> tuple[str | None, set[str]] | None:
    """Return (type value, keys) for a frontmatter block, or None if not one.

    A `type:` the reader keeps as nested, a `{note|meeting}` placeholder, is
    returned as written so the caller can recognise the placeholder.
    """
    doc = F.split(text.lstrip())
    if doc is None:
        return None
    fm = F.parse(doc.block)
    ntype = scalar(fm, "type") or raw_head(fm, "type").strip("\"'") or None
    return ntype, set(fm.keys())


def check_skill_templates(schemas: dict[str, set[str]]) -> list[dict]:
    """Frontmatter examples inside skills must be writable as real notes."""
    findings = []
    for path in iter_files(SKILL_DIR, "*.md"):
        text = path.read_text(encoding="utf-8")
        for fence in FENCE_RE.finditer(text):
            parsed = parse_frontmatter_keys(fence.group(2))
            if not parsed:
                continue
            ntype, keys = parsed
            line = text[:fence.start()].count("\n") + 1
            rel = path.relative_to(WORKSPACE).as_posix()
            if ntype is None:
                # A frontmatter example with no type at all: only a finding when
                # it carries an identity field, meaning it is a real note shape
                # rather than a fragment illustrating one key.
                if keys & {"title", "client", "partner", "name"}:
                    findings.append({"check": "templates", "file": rel, "line": line,
                                     "issue": "frontmatter example declares no `type`, "
                                              "so a note written from it belongs to no schema",
                                     "keys": sorted(keys)})
                continue
            if "|" in ntype or "{" in ntype:
                continue  # a placeholder enumerating the choices, not a type
            if ntype not in schemas:
                findings.append({"check": "templates", "file": rel, "line": line,
                                 "issue": f"`type: {ntype}` matches no schema in basic-memory/schemas/"})
                continue
            if "schema_version" not in keys:
                findings.append({"check": "templates", "file": rel, "line": line,
                                 "issue": f"`type: {ntype}` example omits `schema_version`"})
            unknown = keys - schemas[ntype] - META_FIELDS
            if unknown:
                findings.append({"check": "templates", "file": rel, "line": line,
                                 "issue": f"`type: {ntype}` example writes fields declared in no schema: "
                                          + ", ".join(sorted(unknown))})
    return findings


def check_view_properties(schemas: dict[str, set[str]]) -> list[dict]:
    """Every property a Bases view reads must be declared by some schema."""
    declared = set().union(*schemas.values()) | META_FIELDS
    findings = []
    sources = [(p, p.read_text(encoding="utf-8")) for p in iter_files(WORKSPACE, "*.base")]
    for path in iter_files(WORKSPACE, "*.md"):
        text = path.read_text(encoding="utf-8")
        for m in BASE_FENCE_RE.finditer(text):
            sources.append((path, m.group(1)))
    for path, body in sources:
        rel = path.relative_to(WORKSPACE).as_posix()
        used = set(PROP_RE.findall(body))
        # Bare names in `order:` and `sort:` are note properties too.
        for m in re.finditer(r"^\s+-\s+(?:property:\s+)?([a-z_][a-z0-9_]*)\s*$", body, re.M):
            used.add(m.group(1))
        for prop in sorted(used - declared):
            if prop.startswith(FILE_PROPERTIES_PREFIX):
                continue
            findings.append({"check": "views", "file": rel,
                             "issue": f"view reads `{prop}`, declared in no schema, "
                                      "so the column stays empty or the filter never matches"})
    return findings


def strip_fences(text: str) -> str:
    """Blank out fenced blocks, keeping line count so line numbers stay true.

    A wiki-link inside a code fence illustrates a shape, it does not promise
    the target exists. Counting those as dead links buries the real ones.

    Scanned line by line rather than with a regex: a nested example is fenced
    with four backticks to hold a three-backtick block inside it, and a regex
    pairing delimiters by proximity closes the outer fence on the inner one.
    Only the opening delimiter's length says where a block really ends.
    """
    out, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"\s*(`{3,})", line)
        if fence is None:
            if marker:
                fence = len(marker.group(1))
                out.append("")
                continue
            out.append(line)
        else:
            # A closing delimiter is at least as long as the one that opened.
            if marker and len(marker.group(1)) >= fence:
                fence = None
            out.append("")
    return "\n".join(out)


def check_wikilinks() -> list[dict]:
    """A link to a file nothing creates is a promise the workspace breaks."""
    targets: set[str] = set()
    for path in iter_files(WORKSPACE, "*.md"):
        rel = path.relative_to(WORKSPACE).as_posix()
        # Title, aliases and the identity keys, the documented permissive
        # table in check_helpers.IDENTITY_KEYS: this check under-reports on
        # purpose, check_unresolved_relations.py gives the strict count.
        targets |= note_names(read_frontmatter(path), rel)
    for path in iter_files(WORKSPACE, "*.base"):
        rel = path.relative_to(WORKSPACE).as_posix()
        targets |= {path.name, path.stem, rel}

    findings = []
    for path in iter_files(WORKSPACE, "*.md"):
        rel = path.relative_to(WORKSPACE).as_posix()
        if rel.startswith((".claude/", "docs/", "templates/", "basic-memory/schemas/")):
            continue  # documentation and templates link to illustrative names
        text = strip_fences(path.read_text(encoding="utf-8"))
        for target, offset in link_targets(text):
            if "{" in target or target in targets:
                continue
            findings.append({"check": "links", "file": rel,
                             "line": text[:offset].count("\n") + 1,
                             "issue": f"wiki-link `[[{target}]]` resolves to nothing"})
    return findings


def check_topic_slugs() -> list[dict]:
    """Every `topics` slug should name a file in atlas/topics/.

    Not an error: a brief written before its topic note is normal order of
    work. Worth surfacing anyway, because the MOC views filter on this field
    and an unresolved slug produces a view that renders empty and reads like
    an empty vault rather than a broken filter.
    """
    topics = {p.stem for p in (WORKSPACE / "atlas" / "topics").glob("*.md")
              if p.stem != "README"}
    findings = []
    for path in iter_files(WORKSPACE, "*.md"):
        rel = path.relative_to(WORKSPACE).as_posix()
        if rel.startswith((".claude/", "docs/", "templates/", "basic-memory/", "archives/")):
            continue
        # Inline `[a, b]` and the block list Basic Memory writes read alike.
        for slug in as_list(read_frontmatter(path), "topics"):
            if "{" not in slug and slug not in topics:
                findings.append({"check": "topics", "file": rel, "severity": "warning",
                                 "issue": f"`topics` names `{slug}`, no entry in atlas/topics/, "
                                          "so a MOC view filtering on it stays empty"})
    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["templates", "views", "links", "topics"],
                    help="run a single check")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    schemas = load_schemas()
    findings: list[dict] = []
    if args.only in (None, "templates"):
        findings += check_skill_templates(schemas)
    if args.only in (None, "views"):
        findings += check_view_properties(schemas)
    if args.only in (None, "links"):
        findings += check_wikilinks()
    if args.only in (None, "topics"):
        findings += check_topic_slugs()

    if args.json:
        print(json.dumps({"finding_count": len(findings), "findings": findings},
                         indent=2, ensure_ascii=False))
        return 1 if [f for f in findings if f.get("severity") != "warning"] else 0

    if not findings:
        print("Consistency check: nothing to report.")
        print("  skill templates would produce valid notes")
        print("  every property a view reads is declared by a schema")
        print("  every wiki-link resolves")
        print("  every topic slug names a real entry")
        return 0

    by_check: dict[str, list[dict]] = {}
    for f in findings:
        by_check.setdefault(f["check"], []).append(f)
    labels = {"templates": "Skill templates that would produce invalid notes",
              "views": "Properties read by a view but declared in no schema",
              "links": "Wiki-links that resolve to nothing",
              "topics": "Topic slugs naming no entry in atlas/topics/ (warning)"}
    errors = [f for f in findings if f.get("severity") != "warning"]
    print(f"Consistency check: {len(errors)} error{'s' if len(errors) != 1 else ''}, "
          f"{len(findings) - len(errors)} warning{'s' if len(findings) - len(errors) != 1 else ''}\n")
    for check, items in by_check.items():
        print(f"{labels[check]} ({len(items)})")
        for f in items:
            loc = f"{f['file']}:{f['line']}" if "line" in f else f["file"]
            print(f"  {loc}")
            print(f"    {f['issue']}")
        print()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
