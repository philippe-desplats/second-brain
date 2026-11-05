#!/usr/bin/env python3
"""Which note type a path implies. One table, read by both retyping passes.

`retype_files.py` and `retype_fallback_notes.py` used to carry a table each,
and they disagreed: the same file came out a meeting from one and a research
note from the other. The answer now lives here, and both passes ask `classify`.

The rules, first match wins:

    1. an entity or project context file, by its place
         sources/clients/{X}/CLAUDE.md                   client-context
         sources/partners/{X}/CLAUDE.md                  partner-context
         sources/{zone}/{project}/.../CLAUDE.md          project-brief
         sources/{zone}/{project}/.../README.md          project-brief
    2. a container folder anywhere above the file, which forces its type
         emails/ mails/                                  email
         meetings/                                       meeting
         deliverables/ proposals/                        deliverable
         transcripts/                                    transcript
         clippings/                                      clipping
         sessions/                                       session
    3. the word right after the date, `YYYY-MM-DD-{type}-slug.md`, the naming
       convention of the root CLAUDE.md, and `YYYY-MM-DD-{seq}-{direction}-`
       for an email filed outside its folder
    4. a keyword in the name, `-audit-` or `-plan-` and the like, only when
       the name carries no type word after its date

A note under `knowledge/` that declares a `subtype` is never retyped: its
genre is the subtype, and `.claude/rules/knowledge.md` keeps it a `note`.

The module also holds the guard the rewriting passes ask before writing a
field, `field_damage` and `type_damage`. They only word a refusal: the facts
they rest on, a swallowed key line and an unclosed quote, are grammar and live
in `frontmatter.py`, where the read-only damage check finds them too.

Imported as a sibling, never as a package, like `frontmatter.py`.

Standard library only.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
# Re-exported: a grammar fact, kept importable from here for the passes that
# already import their guards from this module.
from frontmatter import swallowed_key_line  # noqa: E402,F401

# The 17 canonical types, one per schema in `basic-memory/schemas/`.
NOTE_TYPES = frozenset({
    "client-context", "partner-context", "project-brief", "person", "topic",
    "service", "meeting", "transcript", "email", "clipping", "research",
    "brainstorm", "strategy", "writing", "note", "session", "deliverable",
})

# Rule 2. Ordered, the first folder of the list found above the file wins.
FOLDER_TYPES: tuple[tuple[str, str], ...] = (
    ("emails", "email"),
    ("mails", "email"),
    ("meetings", "meeting"),
    ("deliverables", "deliverable"),
    ("proposals", "deliverable"),
    ("transcripts", "transcript"),
    ("clippings", "clipping"),
    ("sessions", "session"),
)
FORCING_FOLDERS = frozenset(folder for folder, _ in FOLDER_TYPES)

# Rule 3. The `{type}` word of `YYYY-MM-DD-{type}-slug.md`.
DATED_WORDS = frozenset({
    "meeting", "research", "brainstorm", "strategy", "writing", "note",
    "clipping", "session",
})
DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(.*)$")
DATED_EMAIL_RE = re.compile(r"^\d{2}-(?:out|in|reply)-")

# Rule 4. Ordered, the first keyword found in `-{word}-` form wins.
KEYWORD_TYPES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("transcript", "recorder"), "transcript"),
    (("clipping",), "clipping"),
    (("session",), "session"),
    (("research", "audit", "benchmark"), "research"),
    (("strategy", "roadmap", "plan"), "strategy"),
    (("brainstorm",), "brainstorm"),
    (("writing",), "writing"),
    (("meeting",), "meeting"),
)


def _context_type(parts: list[str]) -> str | None:
    """Rule 1, for a CLAUDE.md or a README.md."""
    name = parts[-1]
    if parts[0] != "sources":
        return None
    if name == "CLAUDE.md":
        if len(parts) == 4 and parts[1] == "clients":
            return "client-context"
        if len(parts) == 4 and parts[1] == "partners":
            return "partner-context"
        if len(parts) >= 4:
            return "project-brief"
        return None
    if len(parts) >= 3 and parts[1] in {"clients", "partners", "internal", "personal"}:
        return "project-brief"
    return None


def dated_word(stem: str) -> str | None:
    """The type the date prefix of a file name declares, or None."""
    m = DATED_RE.match(stem)
    if not m:
        return None
    after = m.group(1)
    word = after.split("-", 1)[0]
    if word in DATED_WORDS:
        return word
    if DATED_EMAIL_RE.match(after):
        return "email"
    return None


def keyword_type(stem: str) -> str | None:
    """The type a `-{word}-` keyword in the name suggests, or None."""
    padded = "-" + stem.lower() + "-"
    for words, note_type in KEYWORD_TYPES:
        if any("-%s-" % word in padded for word in words):
            return note_type
    return None


def classify(rel: str, subtype=None) -> str | None:
    """The type a workspace-relative path implies, or None when no rule applies.

    `rel` uses forward slashes. `subtype` is the note's `subtype:` value,
    which protects a distilled note under `knowledge/` from any retyping.

    A forcing folder wins over the word after the date, deliberately: a file
    in `meetings/` is a meeting note whatever its name says, so
    `meetings/2026-01-02-note-x.md` is a `meeting`, not a `note`.
    """
    parts = rel.split("/")
    name = parts[-1]
    if parts[0] == "knowledge" and subtype:
        return None
    if name == "CONTEXT.md":
        return None
    if name in ("CLAUDE.md", "README.md"):
        return _context_type(parts)
    ancestors = set(parts[:-1])
    for folder, note_type in FOLDER_TYPES:
        if folder in ancestors:
            return note_type
    stem = name[:-3] if name.endswith(".md") else name
    return dated_word(stem) or keyword_type(stem)


def is_forced(rel: str) -> bool:
    """Does a container folder above the file force its type over the current one?"""
    return bool(set(rel.split("/")[:-1]) & FORCING_FOLDERS)


# --------------------------------------------------------------------------
# The guard of every pass that rewrites a field it did not create.
#
# A pass replaces a field's whole line range. On a block damaged by an older
# pass, that range can cover lines that belong to another field: the items of
# a list above, the folded tail of a quoted title, the lines of a `|` block.
# Rewriting it would delete them silently, so a pass asks first and reports
# the file instead.
# --------------------------------------------------------------------------

SCALAR_STYLES = frozenset({"plain", "single", "double", "empty"})
REPAIR_HINT = "Needs repair, run check_frontmatter_damage.py"


def field_damage(fm, key: str) -> str | None:
    """Why the note must not have `key` written, None when it may.

    A note any of whose fields swallowed a key line is never written. Otherwise
    an absent key may be added, and an existing one may be rewritten when it is
    declared once, holds one scalar, closes its quote, and, when plain and
    folded, absorbs no line that reads as a list item or as another field.
    """
    swallowed = swallowed_key_line(fm)
    if swallowed:
        return swallowed
    fields = [f for f in fm.fields if f.key == key]
    if not fields:
        return None
    if len(fields) > 1:
        return f"`{key}:` declared {len(fields)} times"
    f = fields[0]
    if f.style not in SCALAR_STYLES or isinstance(f.value, list):
        return f"`{key}:` is not a single value"
    if f.style in ("single", "double") and not F.quote_closed(fm, f):
        return f"`{key}:` opens a quote its range never closes"
    if f.style == "plain":
        for line in fm.lines[f.start + 1:f.end]:
            stripped = line.lstrip(" \t")
            if F.ITEM_RE.match(stripped) or F.KEY_LINE_RE.match(stripped):
                return f"`{key}:` absorbs the line `{line.strip()}`"
    return None


def type_damage(fm) -> str | None:
    """`field_damage` for `type:`, which must also sit on a single line."""
    damage = field_damage(fm, "type")
    if damage:
        return damage
    f = fm.field("type")
    if f is not None and f.end - f.start > 1:
        return f"`type:` spans {f.end - f.start} lines"
    return None


def unknown_type(fm) -> str | None:
    """Why a single-line `type:` is not one a pass may replace, None when it is."""
    value = fm.get("type")
    if value is None or value in NOTE_TYPES:
        return None
    return f"`type: {value}` is not a note type"
