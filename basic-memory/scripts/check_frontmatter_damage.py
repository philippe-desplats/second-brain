#!/usr/bin/env python3
"""Find the damage the passes up to 0.6.0 could leave. Read-only.

Before 0.6.0, every pass carried its own frontmatter reader, and each one
misread a shape Basic Memory writes on sync: block lists at column 0, values
folded past 80 columns. A pass that rewrites what it misread leaves a note
behind that the fixed passes no longer touch, so updating the scripts repairs
nothing. This check names every shape those passes are known to leave, with
the line it starts on and the repair, and writes nothing.

    stray-alias-items             list items left under an inline `aliases: [...]`
                                  (the 0.5.2 alias pass)
    orphan-continuation           an indented line under an inline list or a quoted
                                  scalar, which cannot continue it, nested quoted
                                  lists included (the 0.5.3 alias pass and its hook)
    broken-opener                 a file starting `---title:` (retype_fallback_notes.py)
    type-inside-list              a `type:` line between a list key and its items
                                  (retype_files.py)
    type-inside-folded-title      a `type:` line between the first line of the first
                                  field and the rest of its value, a folded title,
                                  plain or quoted, an indented list or a block
                                  scalar, so YAML reads `type: meeting plan for Q3`
                                  (retype_files.py)
    detached-list-items           list items directly under a scalar key
                                  (fix_double_frontmatter.py)
    concatenated-title            an entity title over 2 lines or more whose first
                                  line holds the identity alone, the line the pass
                                  wrote, so the old rest reattached to it
                                  (align_entity_titles.py)
    unquoted-title                a `title:` written unquoted although YAML needs
                                  quotes, `title: Initech: Studio` (align_entity_titles.py,
                                  regen_titles.py)
    unescaped-backslash-alias     a title holding a backslash copied into `aliases:`
                                  in double quotes without escaping it, plus the copy
                                  without backslashes each later run added
                                  (add_title_aliases.py)
    observation-block-indicator   `- [key] |` or `- [key] >` in the body
    observation-truncated         an observation that is a strict prefix of its
                                  frontmatter value (both add_observations_from_frontmatter.py)
    undecoded-quote-in-body       a quoted frontmatter value copied into the body as
                                  written, `l''atelier` or `\\"`, in an observation
                                  or a wiki-link (add_observations_from_frontmatter.py,
                                  add_about_relations.py)
    truncated-wikilink            a wiki-link to the first line of a title folded
                                  over 2 lines, which resolves to nothing
                                  (auto_link_entities.py, add_about_relations.py)
    about-entity-not-project      `- about [[Entity]]` in a note filed under that
                                  entity, or `[[Internal]]` and the `organization`
                                  in an internal one, where the email, meeting and
                                  session schemas want the project brief. Exact on
                                  those 3 types when the brief exists, the brief's
                                  title, or the line removed when the note already
                                  links its project. Needs review otherwise
                                  (add_about_relations.py up to 0.6.0)
    table-cell-split-by-link      `[[X|y]]` or `[[X\\|y]]` in a table row, repaired
                                  to `[[X]]`: the bare `|` ends the cell, and Basic
                                  Memory cannot resolve the escaped form
                                  (auto_link_entities.py up to 0.6.0)
    pass-write-in-excluded-folder `- about [[...]]` or `## Relations` in a folder
                                  corpus.py excludes, with --include-excluded
                                  (add_about_relations.py)
    invalid-yaml                  a frontmatter PyYAML rejects that matched none
                                  of the above, when PyYAML is importable. Never
                                  repaired, the shape is unknown.

Each hit prints as one line:

    path:line: shape: what -> repair

A repair is exact when it can be computed: the lines to replace and the lines
to put in their place, each one JSON-quoted, 0 lines when the line goes. It
says "needs review" when it takes a judgement, a list item whose key was lost,
an observation a human may have shortened on purpose, an `about` line on a
note whose schema gives it another target.

Wiki-links that auto_link_entities.py wrote into excluded folders, and into
the Markdown files at the workspace root, look exactly like links a human
wrote. No check can tell them apart, `git log -p -- <path>` can.

Usage:
    python3 -I basic-memory/scripts/check_frontmatter_damage.py
    python3 -I basic-memory/scripts/check_frontmatter_damage.py --include-excluded
    python3 -I basic-memory/scripts/check_frontmatter_damage.py --json

Frontmatter is read through `frontmatter.py`. Line helpers stay only to see raw
damage the parser normalises or refuses: `locate_block` a glued opener,
`_is_quoted_whole` orphan lines under a quoted value, `_innermost_flow` a
self-nested list.

Exit status: 1 when anything is found, 0 otherwise. Standard library only,
PyYAML used when present.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import IDENTITY_KEYS, WIKILINK_RE, as_list, note_names, scalar  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes, iter_excluded_notes  # noqa: E402
from note_types import (NOTE_TYPES, PROJECT_ABOUT_TYPES, classify, entity_folder,  # noqa: E402
                        project_brief, project_folder)

try:
    import yaml
except ImportError:  # the check degrades, it does not fail
    yaml = None

OPENER_GLUED_RE = re.compile(r"^---(\S.*)$")
OBSERVATION_RE = re.compile(r"^(\s*-\s+\[([^\]]+)\]\s+)(.*?)\s*$")
OBSERVATIONS_HEADING_RE = re.compile(r"^##\s+Observations\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s")
ABOUT_RE = re.compile(r"^\s*-\s+about\s+\[\[")
RELATIONS_RE = re.compile(r"^##\s+Relations\s*$")
FENCE_RE = re.compile(r"^\s*```")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
# The display text of a wiki-link, `|y` or the escaped `\|y`, up to the closing brackets.
DISPLAY_TEXT_RE = re.compile(r"\\?\|[^\]]*(?=\]\]$)")
ABOUT_PREFIX_RE = re.compile(r"^\s*-\s+about\s+(?=\[\[)")
# The internal entity the 0.5.x add_about_relations.py linked, a note that never existed.
OLD_INTERNAL_ENTITY = "Internal"

# Which field an entity note is named by, as align_entity_titles.py reads it.
IDENTITY_BY_TYPE = {"client-context": "client", "partner-context": "partner",
                    "person": "name", "topic": "name", "service": "name"}

WIKILINK_NOTE = ("auto_link_entities.py before 0.6.0 also wrote wiki-links into the "
                 "Markdown files at the workspace root and into the folders corpus.py "
                 "excludes. They cannot be told apart from yours, so no hit is reported "
                 "for them: `git log -p -- <path>` shows which commit added each one.")


@dataclass
class Hit:
    path: str
    line: int
    shape: str
    what: str
    end_line: int | None = None
    replacement: list[str] | None = None
    needs_review: bool = False

    def repair(self) -> str:
        if self.replacement is None:
            return "needs review, nothing proposed" if self.shape == "invalid-yaml" else "needs review"
        end = self.end_line or self.line
        span = "line %d" % self.line if end == self.line else "lines %d-%d" % (self.line, end)
        n = len(self.replacement)
        text = "replace %s with %d line%s" % (span, n, "" if n == 1 else "s")
        if n:
            text += ": " + ", ".join(json.dumps(r, ensure_ascii=False) for r in self.replacement)
        return text + (", needs review" if self.needs_review else "")

    def render(self) -> str:
        return "%s:%d: %s: %s -> %s" % (self.path, self.line, self.shape, self.what, self.repair())


# --------------------------------------------------------------------------
# Reading the block, raw, with file line numbers
# --------------------------------------------------------------------------


def _lines(text: str) -> list[str]:
    if text.startswith(F.BOM):
        text = text[1:]
    return [ln[:-1] if ln.endswith("\r") else ln for ln in text.split("\n")]


def locate_block(lines: list[str]):
    """(block lines, file line number of the first block line, closer index, glued).

    `glued` is the text glued to a `---` opener, None when the opener is
    whole. Returns None when the file has no frontmatter at all.
    """
    if not lines:
        return None
    glued = None
    if lines[0] != F.OPENER:
        m = OPENER_GLUED_RE.match(lines[0])
        if not m or ":" not in m.group(1):
            return None
        glued = m.group(1)
    for i in range(1, len(lines)):
        if lines[i] in F.CLOSERS:
            block = ([glued] if glued is not None else []) + lines[1:i]
            first_line = 1 if glued is not None else 2
            return block, first_line, i, glued
    return None


def _key(line: str):
    fm = F.parse(line + "\n")
    return fm.fields[0] if fm.fields and fm.fields[0].start == 0 else None


def _flow_items(key: str, head: str) -> list[str] | None:
    fm = F.parse("%s: %s\n" % (key, head))
    f = fm.field(key)
    return list(f.value) if f is not None and f.style == "flow" else None


def _is_quoted_whole(head: str) -> bool:
    head = head.strip()
    if len(head) < 2 or head[0] not in "\"'" or head[-1] != head[0]:
        return False
    if head[0] == '"':
        tail = len(head[1:-1]) - len(head[1:-1].rstrip("\\"))
        return tail % 2 == 0
    return True


def _dedupe(values):
    out = []
    for v in values:
        if v and v not in out:
            out.append(v)
    return out


def _innermost_flow(head: str) -> list[str] | None:
    """The innermost list of a flow list the 0.5.3 hook nested into itself.

    Each run wrapped the previous list into a quoted item, escaping its quotes
    once more, with a backslash the YAML reader then misreads. Dropping every
    backslash before a quote recovers the text, and the innermost `[...]` is
    the list as the first damaging run wrote it.
    """
    flat = re.sub(r'\\+"', '"', head)
    start = flat.rfind("[")
    end = flat.find("]", start)
    if start < 0 or end < 0:
        return None
    return _flow_items("aliases", flat[start:end + 1])


# --------------------------------------------------------------------------
# The shapes
# --------------------------------------------------------------------------


def _alias_repair(fm: F.Frontmatter, head: str, cont: list[str], items: list[str]):
    """The alias list a damaged `aliases:` field held, and whether it is certain."""
    title = fm.get("title") if isinstance(fm.get("title"), str) else None
    inline = _innermost_flow(head)
    if inline is None:
        return None, True
    tail = " ".join(c.strip() for c in cont)
    inline = [v for v in inline if not v.startswith("[")]
    known = set(items) | ({title} if title else set())
    values, review = [], False
    if tail:
        truncated = [v for v in inline if v not in known and (v + " " + tail) in known]
        if truncated:
            inline = [v for v in inline if v not in truncated]
        else:
            # The continuation completes an alias that is not the title.
            rest = [v for v in inline if v != title]
            if not rest:
                return None, True
            inline = [v + " " + tail if v == rest[0] else v for v in inline]
            review = True
    values = _dedupe(([title] if title and title in inline + items else []) + inline + items)
    return values, review


def check_block(block: list[str], first_line: int, rel: str, fm: F.Frontmatter) -> list[Hit]:
    hits: list[Hit] = []
    n = len(block)

    def ln(i):
        return first_line + i

    # Top-level key lines, by raw index.
    keys = []
    for i, line in enumerate(block):
        f = _key(line) if line and line[0] not in " \t#-" else None
        if f is not None:
            keys.append((i, f.key, line[len(line) - len(line.lstrip()):].split(":", 1)[1] if ":" in line else ""))
    for pos, (i, key, _) in enumerate(keys):
        limit = keys[pos + 1][0] if pos + 1 < len(keys) else n
        head = block[i].split(":", 1)[1].strip() if ":" in block[i] else ""
        if block[i].startswith(('"', "'")):
            continue
        body = list(range(i + 1, limit))
        cont = [j for j in body if block[j].strip() and block[j][0] in " \t"
                and not block[j].lstrip().startswith("#") and not F.ITEM_RE.match(block[j])]
        items = [j for j in body if F.ITEM_RE.match(block[j]) and block[j][0] not in " \t"]
        indented_items = [j for j in body if F.ITEM_RE.match(block[j]) and block[j][0] in " \t"]
        flow = head.startswith("[") and head.rstrip().endswith("]")
        if flow and (cont or items or indented_items):
            all_items = items + indented_items
            values = [block[j][F.ITEM_RE.match(block[j]).end():] for j in sorted(all_items)]
            values = [F.parse("x: %s\n" % v).get("x") or v for v in values]
            last = max(cont + all_items)
            if key == "aliases":
                if cont:
                    merged, review = _alias_repair(fm, head, [block[j] for j in cont], values)
                    hits.append(Hit(rel, ln(i), "orphan-continuation",
                                    "%d indented line(s) and %d list item(s) left under an inline `aliases:` list"
                                    % (len(cont), len(all_items)),
                                    ln(last), None if merged is None else ["aliases: " + F.render_list(merged)],
                                    review or merged is None))
                else:
                    inline = _flow_items(key, head) or []
                    merged = _dedupe(inline + values)
                    hits.append(Hit(rel, ln(i), "stray-alias-items",
                                    "%d list item(s) left under an inline `aliases:` list" % len(all_items),
                                    ln(last), ["aliases: " + F.render_list(merged)]))
            elif cont:
                hits.append(Hit(rel, ln(cont[0]), "orphan-continuation",
                                "indented line under the inline list of `%s`, which cannot continue it" % key,
                                ln(cont[-1]), None, True))
            else:
                hits.append(Hit(rel, ln(min(all_items)), "detached-list-items",
                                "list items under the inline list of `%s`" % key,
                                ln(max(all_items)), None, True))
            continue
        if head and _is_quoted_whole(head) and cont:
            hits.append(Hit(rel, ln(i), "orphan-continuation",
                            "indented line under the quoted value of `%s`, which cannot continue it" % key,
                            ln(cont[-1]), None, True))
            continue
        if head and not head.startswith(("[", "{", "|", ">")) and items:
            prev = keys[pos - 1] if pos > 0 else None
            prev_empty = prev is not None and prev[0] == i - 1 and not block[prev[0]].split(":", 1)[1].strip()
            if key == "type" and prev_empty and items[0] == i + 1:
                run = [j for j in range(i + 1, limit) if F.ITEM_RE.match(block[j]) or not block[j].strip()]
                last = max(j for j in run if block[j].strip())
                moved = [block[prev[0]]] + [block[j] for j in range(i + 1, last + 1)] + [block[i]]
                hits.append(Hit(rel, ln(prev[0]), "type-inside-list",
                                "`type:` written between `%s:` and its items" % prev[1],
                                ln(last), moved))
            else:
                hits.append(Hit(rel, ln(items[0]), "detached-list-items",
                                "list items directly under the scalar `%s: %s`, their own key was lost; "
                                "`git log -p -- %s` shows the key they belonged to" % (key, head, rel),
                                ln(items[-1]), None, True))
    hits.extend(_check_title(block, first_line, rel, fm))
    hits.extend(_check_quoting(first_line, rel, fm))
    hits.extend(_check_type_fold(block, first_line, rel, fm))
    hits.extend(_check_backslash_alias(first_line, rel, fm))
    if not any(h.shape == "type-inside-folded-title" for h in hits):
        hits.extend(_check_swallowed_key(first_line, rel, fm))
    return hits


def _check_swallowed_key(first_line, rel, fm) -> list[Hit]:
    """A key line swallowed by a field that no shape above knows how to repair.

    The retyping and title passes refuse such a note and send the owner here,
    so it is reported even when no repair can be computed.
    """
    for f in fm.fields:
        for i in range(f.start + 1, f.end):
            if F.KEY_LINE_RE.match(fm.lines[i]):
                return [Hit(rel, first_line + f.start, "swallowed-key-line",
                            "`%s:` reads the line `%s` as part of its value; "
                            "`git log -p -- %s` shows where it belonged" % (f.key, fm.lines[i].strip(), rel),
                            first_line + f.end - 1, None, True)]
    return []


def _check_type_fold(block, first_line, rel, fm) -> list[Hit]:
    """`type:` inserted after the first line of the block, inside the first field.

    The old retype_files.py put `type:` on the second line whatever the first
    field was: a folded plain, single-quoted or double-quoted title, an
    indented list, a `|` or `>` block. The lines of that field then sit under
    `type:`, and YAML reads them as its value, `type: meeting - a - b`, which
    stays valid YAML, so only the shape gives it away. A `type:` never carries
    indented lines of its own once written by a pass, which always wrote the
    value on the key line.

    The hook of 0.6.0 may since have written an alias between the 2, from the
    truncated title: the repair completes that alias too.
    """
    head = fm.fields[0] if fm.fields else None
    if head is not None and head.start == 0 and head.style in ("single", "double") and head.end > 1:
        # A quoted scalar runs to its closing quote, so YAML reads the inserted
        # `type:` line as part of the title. The shape is a column-0 `type:`
        # line inside the title's own line range.
        inner = [j for j in range(1, head.end) if re.match(r"type:[ \t]", block[j])]
        if inner:
            t = inner[0]
            replacement = [block[0]] + block[1:t] + block[t + 1:head.end] + [block[t]]
            return [Hit(rel, first_line, "type-inside-folded-title",
                        "`%s` sits inside the quoted `%s:`, YAML reads it as part of the title"
                        % (block[t], head.key), first_line + head.end - 1, replacement)]
    tf = fm.field("type")
    if tf is None or head is None or head is tf or head.start != 0 or head.end != 1:
        return []
    if not block[tf.start].split(":", 1)[1].strip():
        return []
    tail = list(range(tf.start + 1, tf.end))
    cont = [j for j in tail if block[j].strip() and not block[j].lstrip().startswith("#")]
    if not cont or any(block[j][:1] not in " \t" for j in cont):
        return []
    moved = [block[j] for j in tail]
    truncated = fm.get(head.key)
    full = F.parse("".join(ln + "\n" for ln in [block[0]] + moved)).get(head.key)
    between = []
    for line in block[1:tf.start]:
        f = _key(line)
        if (isinstance(truncated, str) and isinstance(full, str) and full != truncated and f is not None
                and f.key == "aliases" and f.style == "flow" and truncated in (f.value or [])):
            values = _dedupe([full if v == truncated else v for v in f.value])
            line = "aliases: " + F.render_list(values)
        between.append(line)
    replacement = [block[0]] + moved + between + [block[tf.start]]
    return [Hit(rel, first_line, "type-inside-folded-title",
                "`type:` sits between `%s:` and %d line(s) of its value, YAML reads `type:` as %s"
                % (head.key, len(cont), json.dumps(fm.get("type"), ensure_ascii=False)),
                first_line + tf.end - 1, replacement)]


def _check_backslash_alias(first_line, rel, fm) -> list[Hit]:
    """A title with a backslash, copied into `aliases:` unescaped, then copied again.

    The old alias pass escaped `"` but not `\\` when it quoted the title, and
    its own reader took the backslash for an escape, so every later run added
    the title without its backslashes. Found from the raw line, with no YAML
    library: the damaged item is the title written between double quotes.
    """
    title = fm.get("title")
    af = fm.field("aliases")
    if not isinstance(title, str) or "\\" not in title or af is None or af.end - af.start != 1:
        return []
    raw = fm.lines[af.start].split(":", 1)[1].strip()
    bad = '"' + title.replace('"', '\\"') + '"'
    if bad == F.render_scalar(title, flow=True) or bad not in raw or not raw.startswith("["):
        return []
    misread = F.parse("x: [%s]\n" % bad).get("x")
    misread = misread[0] if misread else None
    stripped = re.sub(r"\\(.)", r"\1", title)
    values = F.parse("aliases: %s\n" % raw).get("aliases")
    if not isinstance(values, list):
        return []
    fixed = _dedupe([title if v in (misread, title) else v for v in values if v != stripped or v == title])
    if title not in fixed:
        fixed.insert(0, title)
    dropped = len(values) - len(fixed)
    return [Hit(rel, first_line + af.start, "unescaped-backslash-alias",
                "`aliases:` holds the title with its backslash unescaped%s"
                % (", and %d %s of it without backslashes" % (dropped, "copy" if dropped == 1 else "copies")
                   if dropped > 0 else ""),
                first_line + af.start, ["aliases: " + F.render_list(fixed)])]


def _check_quoting(first_line, rel, fm) -> list[Hit]:
    field = fm.field("title")
    value = fm.get("title")
    if field is None or field.style != "plain" or field.end - field.start != 1 or not isinstance(value, str):
        return []
    raw = fm.lines[field.start].split(":", 1)[1].strip()
    rendered = F.render_scalar(value)
    if rendered == raw or not rendered.startswith('"') or raw[:1] in "\"'":
        return []
    return [Hit(rel, first_line + field.start, "unquoted-title",
                "`title: %s` needs quotes, YAML does not read it as written" % raw,
                first_line + field.start, F.render_field("title", value))]


def _check_title(block, first_line, rel, fm) -> list[Hit]:
    identity_key = IDENTITY_BY_TYPE.get(fm.get("type") if isinstance(fm.get("type"), str) else "")
    if identity_key is None:
        return []
    identity, title = fm.get(identity_key), fm.get("title")
    field = fm.field("title")
    if not isinstance(identity, str) or not isinstance(title, str) or field is None:
        return []
    identity, title = identity.strip(), title.strip()
    if title == identity or not title.startswith(identity) or field.end - field.start < 2:
        return []
    # The damage shape exactly: the first line holds the identity and nothing
    # else, the line the old pass wrote, with the old continuation under it. A
    # long title that merely starts with the name is a title somebody chose.
    first = F.parse(fm.lines[field.start] + "\n").get("title")
    if not isinstance(first, str) or first.strip() != identity:
        return []
    return [Hit(rel, first_line + field.start, "concatenated-title",
                "`title:` reads %s, its first line was replaced by `%s:` and the rest reattached"
                % (json.dumps(title, ensure_ascii=False), identity_key),
                first_line + field.end - 1, F.render_field("title", identity))]


def _one_line(value: str) -> str:
    return " ".join(value.split())


def _old_reading(fm: F.Frontmatter, key: str) -> str | None:
    """What a 0.5.x pass read for a quoted one-line value, when it differs from the value.

    The old passes stripped the quote characters from both ends and decoded
    nothing, so `'l''atelier'` read as `l''atelier` and `"C:\\\\d \\"x\\""` as
    `C:\\\\d \\"x\\`. None when the field is not quoted or reads the same.
    """
    f = fm.field(key)
    value = fm.get(key)
    if f is None or f.style not in ("single", "double") or f.end - f.start != 1 or not isinstance(value, str):
        return None
    raw = fm.lines[f.start].split(":", 1)[1].strip()
    misread = raw.strip().strip('"').strip("'")
    return misread if misread and misread != value else None


def check_observations(lines: list[str], body_start: int, rel: str, fm: F.Frontmatter) -> list[Hit]:
    hits = []
    inside = False
    for i in range(body_start, len(lines)):
        line = lines[i]
        if OBSERVATIONS_HEADING_RE.match(line):
            inside = True
            continue
        if HEADING_RE.match(line):
            inside = False
            continue
        if not inside:
            continue
        m = OBSERVATION_RE.match(line)
        if not m or m.group(2) not in fm:
            continue
        prefix, key, value = m.group(1), m.group(2), m.group(3)
        fv = fm.get(key)
        if not isinstance(fv, str) or not fv.strip():
            continue
        full = _one_line(fv)
        misread = _old_reading(fm, key)
        if misread is not None and value == misread:
            hits.append(Hit(rel, i + 1, "undecoded-quote-in-body",
                            "the observation of `%s` copies the quoted value undecoded, as written in the frontmatter"
                            % key, i + 1, [prefix + full]))
        elif F.BLOCK_HEADER_RE.match(value):
            hits.append(Hit(rel, i + 1, "observation-block-indicator",
                            "the observation of `%s` holds the block indicator `%s`, not the value" % (key, value),
                            i + 1, [prefix + full]))
        elif value and value != full and full.startswith(value):
            hits.append(Hit(rel, i + 1, "observation-truncated",
                            "the observation of `%s` stops where its frontmatter value was folded" % key,
                            i + 1, [prefix + full], True))
    return hits


@dataclass
class LinkTables:
    """Every name a link may use, the first line of each folded name, each misread quoted name."""

    names: set
    truncated: dict
    undecoded: dict


def link_tables(notes) -> LinkTables:
    """Built from (rel, Frontmatter or None) pairs, every note of the scan."""
    names, truncated, undecoded = set(), {}, {}
    for rel, fm in notes:
        names |= note_names(fm, rel)
        if fm is None:
            continue
        for key in IDENTITY_KEYS:
            misread = _old_reading(fm, key)
            if misread is not None:
                undecoded.setdefault(misread, set()).add(fm.get(key))
        for key in IDENTITY_KEYS:
            f = fm.field(key)
            full = fm.get(key)
            if f is None or f.end - f.start < 2 or f.style != "plain" or not isinstance(full, str):
                continue
            first = F.parse(fm.lines[f.start] + "\n").get(key)
            if isinstance(first, str) and first and first != full and full.startswith(first):
                truncated.setdefault(first, set()).add(full)
    return LinkTables(names, truncated, undecoded)


def check_links(lines: list[str], body_start: int, rel: str, tables: LinkTables) -> list[Hit]:
    hits = []
    for i in range(body_start, len(lines)):
        line = lines[i]
        new, found, misread, shift = line, [], [], 0
        for m in WIKILINK_RE.finditer(line):
            target = m.group(1).strip()
            if target in tables.names:
                continue
            fulls = tables.truncated.get(target, ())
            decoded = tables.undecoded.get(target, ())
            if len(fulls) == 1:
                full, bucket = next(iter(fulls)), found
            elif len(decoded) == 1:
                full, bucket = next(iter(decoded)), misread
            else:
                continue
            a, b = m.start(1) + shift, m.end(1) + shift
            new = new[:a] + full + new[b:]
            shift += len(full) - (b - a)
            bucket.append(target)
        if found:
            hits.append(Hit(rel, i + 1, "truncated-wikilink",
                            "%d wiki-link(s) to the first line of a folded title, %s"
                            % (len(found), ", ".join(json.dumps(f, ensure_ascii=False) for f in found)),
                            i + 1, [new]))
        elif misread:
            hits.append(Hit(rel, i + 1, "undecoded-quote-in-body",
                            "%d wiki-link(s) to a quoted name copied undecoded, %s"
                            % (len(misread), ", ".join(json.dumps(f, ensure_ascii=False) for f in misread)),
                            i + 1, [new]))
    return hits


@dataclass
class AboutTables:
    """What an `about` link to an entity, rather than to a project, looks like.

    `entities` maps an entity folder to the names of its context file,
    `internal` holds the names the old passes gave the internal zone, and
    `frontmatter_of` reads a note of the scan for `note_types.project_brief`.
    """

    entities: dict
    internal: set
    frontmatter_of: object


def about_tables(notes, root: Path = WORKSPACE) -> AboutTables:
    """Built from (rel, Frontmatter or None) pairs, every note of the scan."""
    by_rel = dict(notes)
    entities = {}
    for rel, fm in notes:
        folder = entity_folder(rel)
        if folder is not None and rel == folder + "/CLAUDE.md" and fm is not None:
            names = {scalar(fm, key) for key in IDENTITY_KEYS} | set(as_list(fm, "aliases"))
            entities[folder] = names - {""}
    internal = {OLD_INTERNAL_ENTITY}
    try:
        config = json.loads((root / ".sb-config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        config = None
    organization = config.get("organization") if isinstance(config, dict) else None
    if isinstance(organization, str) and organization.strip():
        internal.add(organization.strip())
    return AboutTables(entities, internal, by_rel.get)


def check_about(lines: list[str], body_start: int, rel: str, fm: F.Frontmatter | None,
                about: AboutTables) -> list[Hit]:
    """`- about [[Entity]]` in a note filed under that entity, or `[[Internal]]` in an internal one.

    Every add_about_relations.py before 0.6.1 linked the entity. The 0.5.x
    pass did it on every note of an entity folder and gave internal notes
    `[[Internal]]`, the 0.6.0 one on emails and meetings, internal ones getting
    the `organization`. The email, meeting and session schemas type `about` as
    the project brief, and `client:` or `partner:` already carries the entity.
    On those 3 types the repair is exact when the project has a brief: the
    link becomes the brief's title, or the line goes when the note already
    links its project. On any other type the schema gives `about` another
    target, or none, so the line is proposed for removal and needs review.
    """
    if not rel.startswith("sources/"):
        return []
    zone = rel.split("/")[1] if "/" in rel else ""
    names = about.internal if zone == "internal" else about.entities.get(entity_folder(rel) or "", set())
    if not names:
        return []
    relations = []
    for i, line in body_lines(lines, body_start):
        prefix = ABOUT_PREFIX_RE.match(line)
        link = WIKILINK_RE.match(line, prefix.end()) if prefix else None
        if link is not None:
            relations.append((i, line, link))
    if not relations:
        return []
    brief, why = project_brief(project_folder(rel), about.frontmatter_of)
    project = brief.names if brief is not None else frozenset()
    linked = any(m.group(1).strip() in project for _, _, m in relations)
    kind = fm.get("type") if fm is not None and fm.get("type") in NOTE_TYPES else classify(rel)
    hits = []
    for i, line, m in relations:
        target = m.group(1).strip()
        if target not in names or target in project:
            continue
        what = "`%s` links %s, not the project" % (
            line.strip(), "the internal zone" if zone == "internal" else "the entity")
        if kind not in PROJECT_ABOUT_TYPES:
            hits.append(Hit(rel, i + 1, "about-entity-not-project",
                            "%s. The %s schema does not give `about` the project as its target, "
                            "so the line is proposed for removal" % (what, kind or "unknown"), i + 1, [], True))
        elif brief is None:
            hits.append(Hit(rel, i + 1, "about-entity-not-project",
                            "%s, and %s, so there is no project title to link" % (what, why), None, None, True))
        elif linked:
            hits.append(Hit(rel, i + 1, "about-entity-not-project",
                            "%s, and the note already links its project [[%s]]" % (what, brief.title),
                            i + 1, []))
        else:
            hits.append(Hit(rel, i + 1, "about-entity-not-project",
                            "%s, the brief `%s` names it [[%s]]" % (what, brief.rel, brief.title),
                            i + 1, [line[:m.start()] + "[[%s]]" % brief.title + line[m.end():]]))
            linked = True
    return hits


def body_lines(lines: list[str], body_start: int):
    """Yield (index, line) for every body line outside a code fence."""
    fenced = False
    for i in range(body_start, len(lines)):
        if FENCE_RE.match(lines[i]):
            fenced = not fenced
            continue
        if not fenced:
            yield i, lines[i]


def check_table_links(lines: list[str], body_start: int, rel: str) -> list[Hit]:
    """A wiki-link with display text inside a table row.

    auto_link_entities.py before 0.6.1 wrote `[[X|y]]` there, whose bare `|`
    ends the cell. The escaped `[[X\\|y]]` Obsidian reads is no better, Basic
    Memory splits the target on the `|` and resolves `X\\`, which exists
    nowhere. The repair is the bare `[[X]]` in both cases: the cell shows the
    title instead of the word, and the link resolves in both tools. Inline code
    is left as written.
    """
    hits = []
    for i, line in body_lines(lines, body_start):
        if not line.lstrip().startswith("|"):
            continue
        code = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
        spans = [m.span() for m in WIKILINK_RE.finditer(code) if DISPLAY_TEXT_RE.search(m.group(0))]
        if not spans:
            continue
        new = line
        for a, b in reversed(spans):
            new = new[:a] + DISPLAY_TEXT_RE.sub("", new[a:b]) + new[b:]
        hits.append(Hit(rel, i + 1, "table-cell-split-by-link",
                        "%d wiki-link(s) with display text in a table row: a bare `|` ends the cell, "
                        "and Basic Memory cannot resolve the escaped `\\|` form" % len(spans),
                        i + 1, [new]))
    return hits


def check_excluded(lines: list[str], rel: str) -> list[Hit]:
    hits = []
    for i, line in enumerate(lines):
        if RELATIONS_RE.match(line):
            hits.append(Hit(rel, i + 1, "pass-write-in-excluded-folder",
                            "`## Relations` heading in a folder corpus.py excludes, a pass may have written it",
                            None, None, True))
        elif ABOUT_RE.match(line):
            hits.append(Hit(rel, i + 1, "pass-write-in-excluded-folder",
                            "`%s` in a folder corpus.py excludes, add_about_relations.py wrote it there "
                            "unless you did" % line.strip(), None, None, True))
    return hits


def check_text(text: str, rel: str, excluded: bool = False,
               tables: LinkTables | None = None, about: AboutTables | None = None) -> list[Hit]:
    """Every damage hit in one file's text, links checked when `tables` is given,
    `about` relations when `about` is."""
    lines = _lines(text)
    hits: list[Hit] = []
    found = locate_block(lines)
    body_start = 0
    fm = None
    if found is not None:
        block, first_line, closer, glued = found
        body_start = closer + 1
        fm = F.parse("".join(b + "\n" for b in block))
        if glued is not None:
            hits.append(Hit(rel, 1, "broken-opener",
                            "the frontmatter opener has `%s` glued to it" % glued[:40],
                            1, [F.OPENER, glued]))
        hits.extend(check_block(block, first_line, rel, fm))
        hits.extend(check_observations(lines, body_start, rel, fm))
        if yaml is not None and not hits:
            try:
                yaml.safe_load("\n".join(block))
            except yaml.YAMLError as exc:
                mark = getattr(exc, "problem_mark", None)
                at = first_line + mark.line if mark is not None else first_line
                problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
                hits.append(Hit(rel, at, "invalid-yaml",
                                "PyYAML rejects the frontmatter (%s), a shape this check does not know" % problem,
                                None, None, True))
    if tables is not None:
        hits.extend(check_links(lines, body_start, rel, tables))
    hits.extend(check_table_links(lines, body_start, rel))
    if about is not None and not excluded:
        hits.extend(check_about(lines, body_start, rel, fm, about))
    if excluded:
        hits.extend(check_excluded(lines, rel))
    hits.sort(key=lambda h: h.line)
    return hits


# --------------------------------------------------------------------------
# Walking the workspace
# --------------------------------------------------------------------------


def scan(root: Path = WORKSPACE, include_excluded: bool = False):
    hits, linked = [], []
    walks = [(p, r, False) for p, r in iter_corpus_notes(root)]
    if include_excluded:
        walks += [(p, r, True) for p, r in iter_excluded_notes(root)]
    texts = []
    for path, rel, excluded in walks:
        try:
            texts.append((rel, excluded, path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
    parsed = []
    for rel, _, text in texts:
        doc = F.split(text)
        parsed.append((rel, F.parse(doc.block) if doc is not None else None))
    tables = link_tables(parsed)
    about = about_tables(parsed, root)
    for rel, excluded, text in texts:
        hits.extend(check_text(text, rel, excluded, tables, about))
        if excluded and WIKILINK_RE.search(text):
            linked.append(rel)
    return hits, linked


def main(argv=None, root: Path = WORKSPACE) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--include-excluded", action="store_true",
                    help="also scan the folders corpus.py excludes, where 0.5.x passes wrote relations")
    ap.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    args = ap.parse_args(argv)
    hits, linked = scan(root, args.include_excluded)
    if args.json:
        print(json.dumps({"hits": [dict(asdict(h), repair=h.repair()) for h in hits],
                          "excluded_with_wikilinks": linked,
                          "wikilink_caveat": WIKILINK_NOTE if args.include_excluded else None,
                          "yaml_checked": yaml is not None}, ensure_ascii=False, indent=2))
    else:
        for h in hits:
            print(h.render())
        if args.include_excluded:
            print("note: %s" % WIKILINK_NOTE)
            if linked:
                print("note: %d excluded file(s) hold wiki-links:" % len(linked))
            for rel in linked:
                print("note:   %s" % rel)
        if yaml is None:
            print("note: PyYAML is not importable, so invalid YAML of an unknown shape was not looked for. "
                  "Rerun with a python3 that has it, `uvx --with pyyaml python -I "
                  "basic-memory/scripts/check_frontmatter_damage.py --include-excluded` for one, "
                  "or accept this gap.")
        print("%d hit(s) in %d file(s)." % (len(hits), len({h.path for h in hits})))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
