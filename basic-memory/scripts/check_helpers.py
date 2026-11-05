#!/usr/bin/env python3
"""Helpers shared by the read-only checks. One schema loader, one link table.

Two answers kept drifting apart while each check carried its own copy:

    load_schemas        which fields each schema declares, and which are required
    note_names          every name a wiki-link may use to reach a note

`check_consistency.py` and `audit_field_usage.py` read the schemas through the
first. `check_consistency.py`, `check_orphans.py` and `propose_pruning.py`
resolve wiki-links through the second, so a note one check calls reachable is
never an orphan or a pruning candidate for another.

Frontmatter is read with `frontmatter.py`, the one reader of the workspace, so
a title Basic Memory folded over 2 lines is read whole and a block list at
column 0 is read like an inline one.

Imported as a sibling, never as a package:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from check_helpers import load_schemas, note_names  # noqa: E402

Standard library only.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402

# A wiki-link, its target before any `|` display text or `#` heading. The
# escaped `[[X\|y]]` Obsidian reads inside a table row also reads as `X`, should
# a human or another tool write it. No pass writes it: Basic Memory resolves its
# target as `X\`. Any other backslash belongs to the target. The pattern is
# shared, so every reader of a link agrees.
WIKILINK_PATTERN = r"\[\[((?:[^\]|#\\]|\\(?!\|))+)(?:#[^\]|]*)?(?:\\?\|[^\]]*)?\]\]"
WIKILINK_RE = re.compile(WIKILINK_PATTERN)

# The frontmatter fields a wiki-link may name a note by, beyond `aliases:`.
#
# Basic Memory resolves on `title:` alone and Obsidian on the file name, so
# `client`, `partner`, `name` and `subject` reach nothing in either tool. They
# are accepted here on purpose, and the permissiveness is documented in
# `.claude/rules/frontmatter.md`: the checks built on this table under-report a
# dead link rather than flag a note whose identity field and title merely
# disagree. `check_unresolved_relations.py` gives the strict count, from the
# index itself. For `check_orphans.py` and `propose_pruning.py` the same
# permissiveness is the safe side: a note anyone could mean is never proposed
# as an orphan or for deletion.
IDENTITY_KEYS = ("title", "client", "partner", "name", "subject")

# A schema field declaration: `name`, an optional `?`, an optional `(type)`.
FIELD_DECL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\??)(?:\([^)]*\))?\s*:")


def read_frontmatter(path) -> F.Frontmatter | None:
    """The parsed frontmatter of a note, or None when it has none or cannot be read."""
    try:
        _, fm = F.read_file(path)
    except (OSError, UnicodeDecodeError):
        return None
    return fm


def scalar(fm: F.Frontmatter | None, key: str) -> str:
    """The value of `key` as a stripped string, "" when absent, null or a list."""
    if fm is None:
        return ""
    value = fm.get(key)
    return value.strip() if isinstance(value, str) else ""


def as_list(fm: F.Frontmatter | None, key: str) -> list[str]:
    """The value of `key` as a list of strings, a lone scalar read as one item."""
    if fm is None:
        return []
    value = fm.get(key)
    if isinstance(value, list):
        return [v.strip() for v in value if v and v.strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def raw_head(fm: F.Frontmatter, key: str) -> str:
    """The text after `key:` on its own line, as written, comment included.

    For a value the reader keeps as nested, such as a `{a|b}` placeholder in a
    template, where the decoded value is None but the raw text still says
    what the author meant.
    """
    f = fm.field(key)
    if f is None:
        return ""
    return fm.lines[f.start].partition(":")[2].strip()


def link_targets(text: str):
    """Yield (target, offset) for every wiki-link in `text`, target stripped."""
    for m in WIKILINK_RE.finditer(text):
        yield m.group(1).strip(), m.start()


def note_names(fm: F.Frontmatter | None, rel: str) -> set[str]:
    """Every name a wiki-link may use to reach the note at `rel`.

    The file stem and the workspace-relative path with and without `.md`,
    which is how Obsidian resolves. Then `title:`, which is how Basic Memory
    resolves. Then every entry of `aliases:`, which the `topic` schema
    declares so a note can be reached by its short name. Then the identity
    keys in IDENTITY_KEYS, see the comment there for why they count.

    `rel` uses forward slashes.
    """
    stem = rel.rsplit("/", 1)[-1]
    if stem.endswith(".md"):
        stem = stem[:-3]
    names = {stem, rel, rel[:-3] if rel.endswith(".md") else rel}
    for key in IDENTITY_KEYS:
        names.add(scalar(fm, key))
    names.update(as_list(fm, "aliases"))
    names.discard("")
    return names


def resolution_table(entries):
    """Map each name to the entries it reaches, from (entry, names) pairs.

    A name shared by 2 notes maps to both, so a link counts for each of them.
    """
    table: dict[str, list] = {}
    for entry, names in entries:
        for name in names:
            table.setdefault(name, []).append(entry)
    return table


# Parsed by hand on purpose: frontmatter.py reads the top level only, and gives
# `settings:` back as an opaque nested line range, with no value to read.
def _frontmatter_settings(lines: list[str]) -> list[str]:
    """The lines under `settings: > frontmatter:` in a schema block, dedented."""
    out: list[str] = []
    in_settings = False
    fm_indent = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        if indent == 0:
            in_settings = line.split(":", 1)[0].strip() == "settings"
            fm_indent = None
            continue
        if not in_settings:
            continue
        if fm_indent is None:
            if line.strip() == "frontmatter:":
                fm_indent = indent
            continue
        if indent <= fm_indent:
            fm_indent = None
            if line.strip() == "frontmatter:":
                fm_indent = indent
            continue
        out.append(line)
    return out


def schema_fields(path) -> dict[str, bool]:
    """{field: required} declared in one schema's `settings.frontmatter` block.

    A field is required when its name carries no trailing `?`. Declarations
    are the children of `frontmatter:` at the indent of its first child,
    whatever that indent is, so a schema indented with 4 spaces or a tab reads
    like one indented with 2. Enum values are list items one level deeper and
    never count as fields.
    """
    _, fm = F.read_file(path)
    if fm is None:
        return {}
    settings = fm.field("settings")
    if settings is None:
        return {}
    children = _frontmatter_settings(fm.lines[settings.start:settings.end])
    fields: dict[str, bool] = {}
    if not children:
        return fields
    first = children[0]
    decl_indent = first[:len(first) - len(first.lstrip(" \t"))]
    for line in children:
        if not line.startswith(decl_indent) or line[len(decl_indent):][:1] in (" ", "\t"):
            continue
        m = FIELD_DECL_RE.match(line[len(decl_indent):])
        if m:
            fields[m.group(1)] = m.group(2) != "?"
    return fields


def load_schemas(schema_dir) -> dict[str, dict[str, bool]]:
    """{type: {field: required}} for every schema under `schema_dir`.

    The type is the file stem, which is the value notes write in `type:`.
    The README is the design manifest, not a schema.
    """
    out: dict[str, dict[str, bool]] = {}
    for path in sorted(Path(schema_dir).glob("*.md")):
        if path.stem == "README":
            continue
        out[path.stem] = schema_fields(path)
    return out
