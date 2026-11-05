#!/usr/bin/env python3
"""The YAML frontmatter grammar of the workspace. One reader, one writer, every pass.

Basic Memory writes frontmatter with `yaml.dump`: block lists at column 0,
values folded past 80 columns, quoted scalars broken over several lines. Humans
and Obsidian write something else again: indented lists, inline flow lists,
trailing comments. A pass that reads only the shape it was tested on misreads
the others, and a pass that rewrites what it misread corrupts the note. This
module exists so the grammar is implemented once, tested once, and never copied.

It is deliberately not a YAML library. It reads the top level of a mapping and
keeps every line it does not need to touch byte for byte:

    split / join        the frontmatter block and the body, BOM and CRLF kept
    parse               ordered top-level fields, each with its line range
    get / keys          values decoded to str, list[str], or None
    set_field           rewrites the full line range of one field, nothing else
    drop_field          removes the full line range of one field
    render_scalar       the one quoting policy every writer uses
    render_list         the same policy applied to a list
    quote_closed        does a quoted field close inside its own range
    swallowed_key_line  a field whose range swallowed another field's key line

A nested mapping under a key is kept verbatim, its value reads as None and its
style as "nested", and no helper rewrites it unless asked to replace it whole.

Imported as a sibling, never as a package. A caller puts this directory on its
import path itself, so it also runs under `python3 -I`:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from frontmatter import read_file, set_field, join  # noqa: E402

Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field
from pathlib import Path

BOM = "﻿"
OPENER = "---"
CLOSERS = ("---", "...")

# A top-level key: a plain key ending at the first `:` followed by a space or
# the end of the line, or a quoted key. Column 0 only, by construction.
PLAIN_KEY_RE = re.compile(r"^([^ \t#'\"\-?:,\[\]{}&*!|>%@`][^:]*?|-[^ \t:][^:]*?):(?=[ \t]|$)")
QUOTED_KEY_RE = re.compile(r"""^("(?:[^"\\]|\\.)*"|'(?:[^']|'')*')[ \t]*:(?=[ \t]|$)""")
BLOCK_HEADER_RE = re.compile(r"^([|>])([+-]?)([1-9]?)([+-]?)[ \t]*(?:#.*)?$")
ITEM_RE = re.compile(r"^([ \t]*)-(?:[ \t]+|$)")
# The key names Basic Memory, a template or a pass writes: an identifier, with
# hyphens allowed. Narrower than what the parser reads as a key, on purpose:
# prose such as `Key takeaways: ...` has a space in its key and never matches.
# Use it with `fullmatch` on a key, or through KEY_LINE_RE on a raw line.
WRITTEN_KEY_RE = re.compile(r"[A-Za-z_][\w-]*")
# A column-0 line opening a field with such a key.
KEY_LINE_RE = re.compile(r"^%s:(?:[ \t]|$)" % WRITTEN_KEY_RE.pattern)
# An item or a value that opens a nested mapping (`- key: v`, `key: v`).
MAPPING_START_RE = re.compile(r"""^(?:[^ \t#'"\-?:,\[\]{}][^:]*?|"(?:[^"\\]|\\.)*"|'(?:[^']|'')*'):(?:[ \t]|$)""")

NULLS = {"", "~", "null", "Null", "NULL"}
# Node properties before a value: an anchor `&name` and a tag `!tag`, in any order.
PROPS_RE = re.compile(r"^(?:[&!][^ \t]*(?:[ \t]+|$))+")

DOUBLE_ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n",
    "v": "\v", "f": "\f", "r": "\r", "e": "\x1b", " ": " ", '"': '"',
    "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": " ", "P": " ",
}
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}


# --------------------------------------------------------------------------
# Document level: where the block starts and ends
# --------------------------------------------------------------------------


@dataclass
class Doc:
    """A note split into its frontmatter block and its body.

    `block` is the text between the delimiter lines, every line ended by
    "\\n" whatever the file uses, so an empty block is "". `newline` is the
    line ending of the opening delimiter and is restored on `join`. `bom` says
    whether the file started with a UTF-8 byte order mark. `closer` is the
    closing delimiter as written, `---` or `...`, and `closer_eol` the line
    ending that followed it, empty when the file ends on the delimiter.
    """

    block: str
    body: str
    newline: str = "\n"
    bom: bool = False
    closer: str = "---"
    closer_eol: str | None = None


def _eol(line: str) -> tuple[str, str]:
    """Split a line that may carry its own ending into (content, ending)."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def split(text: str) -> Doc | None:
    """Return the frontmatter of a note, or None when it has none.

    Frontmatter exists only when the text starts, after an optional BOM, with a
    line exactly `---`, and ends at the next line exactly `---` or `...`. A
    `---` rule further down the body is never part of the block, since the
    block stops at the first closing line.

    A block whose lines mix CRLF and LF comes back normalised to the ending of
    the opening line. The body is never touched.
    """
    bom = text.startswith(BOM)
    rest = text[1:] if bom else text
    # Split on "\n" alone. `str.splitlines` also breaks on U+2028, U+0085,
    # form feed and the like, which Basic Memory writes raw inside values.
    parts = rest.split("\n")
    lines = [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
    if not lines:
        return None
    first, newline = _eol(lines[0])
    if first != OPENER or not newline:
        return None
    block_lines = []
    for index in range(1, len(lines)):
        content, ending = _eol(lines[index])
        if content.endswith("\r") and not ending:
            content = content[:-1]
        if content in CLOSERS:
            body = "".join(lines[index + 1:])
            return Doc("".join(line + "\n" for line in block_lines), body,
                       newline, bom, content, ending)
        block_lines.append(content.rstrip("\r") if newline == "\r\n" else content)
    return None


def join(doc: Doc, fm: "Frontmatter | None" = None) -> str:
    """Rebuild the full text. Byte for byte identical when nothing changed.

    Pass `fm` to write an edited Frontmatter in place of `doc.block`.
    """
    block = render(fm) if fm is not None else doc.block
    if block and not block.endswith("\n"):
        block += "\n"
    nl = doc.newline
    eol = nl if doc.closer_eol is None else doc.closer_eol
    head = (BOM if doc.bom else "") + OPENER + nl
    return head + block.replace("\n", nl) + doc.closer + eol + doc.body


# --------------------------------------------------------------------------
# Field level
# --------------------------------------------------------------------------


@dataclass
class Field:
    """One top-level field of a frontmatter block.

    `start` and `end` are line indexes into `Frontmatter.lines`, `end`
    exclusive, covering the key line, every list item, every folded
    continuation and every block-scalar line. Interior comments and blank lines
    sit inside the range, and so does a trailing indented comment. Trailing
    blank lines and column-0 comments sit outside it.

    `style` is one of: plain, single, double, literal, folded, flow, block,
    empty, nested. `indent` is the leading whitespace of the items of a block
    list, so a rewrite keeps the list where it was. `raw` holds, for a list,
    the source text of each single-line quoted item and None for the others,
    so a rewrite keeps the quoting of the items it does not change.
    """

    key: str
    value: str | list[str] | None
    start: int
    end: int
    style: str
    indent: str = ""
    raw: list | None = None


@dataclass
class Frontmatter:
    """The parsed top level of a block: its lines and its ordered fields."""

    lines: list[str]
    fields: list[Field] = dc_field(default_factory=list)

    def field(self, key: str) -> Field | None:
        """The first field named `key`, or None."""
        for f in self.fields:
            if f.key == key:
                return f
        return None

    def get(self, key: str, default=None):
        """The decoded value of the first field named `key`.

        Returns `default` when the key is absent. A key present with an empty
        or null value returns None, which is not the default.
        """
        f = self.field(key)
        return default if f is None else f.value

    def keys(self) -> list[str]:
        """Top-level keys in file order, a duplicated key listed once."""
        seen: list[str] = []
        for f in self.fields:
            if f.key not in seen:
                seen.append(f.key)
        return seen

    def duplicates(self) -> list[str]:
        """Keys declared more than once in the block."""
        counts: dict[str, int] = {}
        for f in self.fields:
            counts[f.key] = counts.get(f.key, 0) + 1
        return [k for k, n in counts.items() if n > 1]

    def __contains__(self, key: str) -> bool:
        return self.field(key) is not None

    def to_dict(self) -> dict:
        """Every field as a plain dict, first occurrence wins."""
        out: dict = {}
        for f in self.fields:
            out.setdefault(f.key, f.value)
        return out


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _is_blank(line: str) -> bool:
    """Only YAML whitespace, space and tab, makes a line blank."""
    return not line.strip(" \t")


def _is_comment(line: str) -> bool:
    return line.lstrip(" \t").startswith("#")


def _key_of(line: str) -> tuple[str, str] | None:
    """(key, rest) when the line opens a top-level field, else None."""
    if not line or line[0] in " \t#":
        return None
    m = QUOTED_KEY_RE.match(line)
    if m:
        raw = m.group(1)
        key = _decode_double(raw[1:-1]) if raw[0] == '"' else raw[1:-1].replace("''", "'")
        return key, line[m.end():]
    m = PLAIN_KEY_RE.match(line)
    if m:
        return m.group(1).rstrip(" \t"), line[m.end():]
    return None


def _strip_comment(text: str) -> str:
    """Drop a ` #` trailing comment from a plain scalar."""
    m = re.search(r"(?:^|[ \t])#", text)
    return text[:m.start()] if m else text


def parse(block: str) -> Frontmatter:
    """Read the top level of a frontmatter block into ordered fields."""
    lines = block.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    fm = Frontmatter(lines)
    # Locate the key lines first, then give each field every line up to the
    # next key, less what trails it. A line inside an open quoted scalar or
    # flow collection is never a key, even at column 0.
    inside = _inside_spans(lines)
    starts = []
    for i, line in enumerate(lines):
        kr = None if i in inside else _key_of(line)
        if kr:
            starts.append((i, kr[0], kr[1]))
    for n, (i, key, rest) in enumerate(starts):
        limit = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        fm.fields.append(_parse_field(lines, i, limit, key, rest, inside))
    return fm


def _value_start(line: str, expect_value: bool) -> tuple[int, int] | None:
    """Where a value may open on this line, and the indent of its parent.

    A value opens after a key's colon, after a block list dash, or on a line
    of its own when the line before left its value empty. Any other line is
    the continuation of a plain scalar, where a quote opens nothing.
    """
    kr = _key_of(line)
    if kr:
        return len(line) - len(kr[1]), 0
    pos = _indent_of(line)
    parent = pos
    moved = False
    while True:
        m = ITEM_RE.match(line[pos:])
        if not m or not line[pos:].lstrip(" \t").startswith("-"):
            break
        parent = pos + len(m.group(1))
        pos += m.end()
        moved = True
    m = MAPPING_START_RE.match(line[pos:])
    if m and (moved or pos > 0):
        return pos + m.end(), pos
    if moved or expect_value:
        return pos, parent
    return None


def _flow_close(text: str) -> int | None:
    """Index just past the flow collection opening `text`, or None if it never closes."""
    depth = 0
    i, n = 0, len(text)
    prev = ""
    while i < n:
        ch = text[i]
        if ch in "\"'" and prev in ("", "[", "{", ",", ":"):
            close = _find_close(text[i + 1:], ch)
            if close is None:
                return None
            i += len(close) + 2
            prev = ch
            continue
        if ch == "#" and (i == 0 or text[i - 1] in " \t\n"):
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return i + 1
        if ch not in " \t\n":
            prev = ch
        i += 1
    return None


def _inside_spans(lines: list[str]) -> set[int]:
    """Lines that continue a quoted scalar or a flow collection opened above.

    YAML reads a quoted scalar up to its closing quote and a flow collection
    up to its closing bracket, whatever the indentation of the lines between.
    An old pass that inserted `type: meeting` inside a folded quoted title
    left exactly that shape: the inserted line belongs to the title.
    """
    inside: set[int] = set()
    i, n = 0, len(lines)
    block_parent = None
    expect_value = False
    while i < n:
        line = lines[i]
        if block_parent is not None:
            if _is_blank(line) or _indent_of(line) > block_parent:
                i += 1
                continue
            block_parent = None
        if _is_blank(line) or _is_comment(line):
            i += 1
            continue
        found = _value_start(line, expect_value)
        expect_value = False
        if found is None:
            i += 1
            continue
        pos, parent = found
        while pos < len(line) and line[pos] in " \t":
            pos += 1
        rest = line[pos:]
        props = PROPS_RE.match(rest)
        if props:
            rest = rest[props.end():]
        if not rest or rest.startswith("#"):
            expect_value = True
            i += 1
            continue
        if BLOCK_HEADER_RE.match(rest):
            block_parent = parent
            i += 1
            continue
        span = None
        if rest[0] in "\"'":
            close = _find_close("\n".join([rest[1:]] + lines[i + 1:]), rest[0])
            span = None if close is None else close.count("\n")
        elif rest[0] in "[{":
            end = _flow_close("\n".join([rest] + lines[i + 1:]))
            span = None if end is None else "\n".join([rest] + lines[i + 1:])[:end].count("\n")
        if span:
            inside.update(range(i + 1, i + 1 + span))
            i += span
        i += 1
    return inside


def _owned(lines: list[str], start: int, limit: int, column0_items: bool,
           inside: set[int] = frozenset()) -> int:
    """End of the lines a field at `start` owns, trailing blanks excluded.

    A field owns every indented line under it, and the column-0 `- ` items of
    a block list. An indented line starting with `#` is owned too: it may be
    the continuation of a quoted scalar, where nothing is a comment, and when
    it is a comment it still belongs to the field above it. A column-0
    comment is owned only when owned lines follow it. A line inside a quoted
    scalar or flow collection opened above is owned whatever its indentation.
    A column-0 line of any other kind ends the field.
    """
    end = start + 1
    for j in range(start + 1, limit):
        line = lines[j]
        if _is_blank(line) and j not in inside:
            continue
        if j in inside or line[0] in " \t" or (column0_items and ITEM_RE.match(line)):
            end = j + 1
            continue
        if _is_comment(line):
            continue
        break
    return end


def _parse_field(lines: list[str], start: int, limit: int, key: str, rest: str,
                 inside: set[int] = frozenset()) -> Field:
    head = rest.strip(" \t")
    props = PROPS_RE.match(head)
    if props:
        # `&anchor value` reads as `value`. The anchor itself is not kept on
        # a rewrite, which is harmless unless an alias elsewhere uses it.
        head = head[props.end():]
    header = BLOCK_HEADER_RE.match(head)
    if header:
        return _parse_block_scalar(lines, start, limit, key, header)
    end = _owned(lines, start, limit, not _strip_comment(head).strip(" \t"), inside)
    tail = lines[start + 1:end]
    if head.startswith('"') or head.startswith("'"):
        # Inside an open quote nothing is a comment and no line ends the
        # scalar but its closing quote.
        value, consumed, _ = _read_quoted(head, lines[start + 1:limit])
        end = max(end, start + 1 + consumed)
        return Field(key, value, start, end, "double" if head[0] == '"' else "single")
    if head.startswith("["):
        return _parse_flow(key, head, tail, start, end)
    if head.startswith("{"):
        return Field(key, None, start, end, "nested")
    plain = _strip_comment(head).strip(" \t")
    if plain:
        if plain.startswith(("&", "!", "*")):
            return Field(key, None, start, end, "nested")
        value = _fold_plain([plain] + tail)
        return Field(key, None if value in NULLS else value, start, end, "plain")
    content = [ln for ln in tail if not _is_blank(ln) and not _is_comment(ln)]
    if not content:
        return Field(key, None, start, start + 1, "empty")
    first = content[0].lstrip(" \t")
    if ITEM_RE.match(content[0]):
        return _parse_block_list(key, tail, start, end)
    if MAPPING_START_RE.match(first) or first.startswith(("?", "{", "&", "!", "*")):
        return Field(key, None, start, end, "nested")
    # A scalar starting on the line after its key.
    if first.startswith(("\"", "'")):
        offset = next(k for k, ln in enumerate(tail) if not _is_blank(ln) and not _is_comment(ln))
        value, _, _ = _read_quoted(first, tail[offset + 1:])
        return Field(key, value, start, end, "double" if first[0] == '"' else "single")
    if first.startswith("["):
        return _parse_flow(key, first, tail[1:], start, end)
    value = _fold_plain(tail)
    return Field(key, None if value in NULLS else value, start, end, "plain")


# YAML 1.1 line breaks. `\x85` folds like `\n`, the two Unicode separators are
# kept as themselves, which is what PyYAML does when it reads them raw.
BREAKS = "\r\n\x85  "
BREAK_RE = re.compile(r"\r\n|[\r\n\x85  ]")


def _scan_break(text: str, i: int) -> tuple[str, int]:
    """The normalised line break at `i` and the index after it."""
    if text.startswith("\r\n", i):
        return "\n", i + 2
    ch = text[i]
    return ("\n" if ch in "\r\n\x85" else ch), i + 1


def _scan_breaks(text: str, i: int, spaces: str = " \t") -> tuple[list[str], int]:
    """Further line breaks after a first one, each preceded by indentation.

    Stops at the first character of the next content line, with its
    indentation consumed.
    """
    breaks: list[str] = []
    n = len(text)
    while True:
        j = i
        while j < n and text[j] in spaces:
            j += 1
        if j < n and text[j] in BREAKS:
            br, i = _scan_break(text, j)
            breaks.append(br)
            continue
        return breaks, j


def _fold_at(text: str, i: int, out: list[str], spaces: str = " \t") -> int:
    """Fold the whitespace run starting at `i` into `out`, return the next index.

    The run is spaces, then possibly a line break and more breaks. Without a
    break the spaces are content. With one, trailing spaces drop, a single `\\n`
    becomes a space, n more breaks become n newlines, and a raw U+2028 or
    U+2029 stays itself. This is PyYAML's flow and plain scalar folding.
    """
    n = len(text)
    j = i
    while j < n and text[j] in spaces:
        j += 1
    if j < n and text[j] in BREAKS:
        first, j = _scan_break(text, j)
        breaks, j = _scan_breaks(text, j, spaces)
        if first != "\n":
            out.append(first)
        elif not breaks:
            out.append(" ")
        out.extend(breaks)
        return j
    out.append(text[i:j])
    return j


def _fold_plain(raw_lines: list[str]) -> str:
    """Join the lines of a plain scalar the way YAML folds them.

    Lines lose their YAML indentation (space, tab) and never any other
    whitespace, a single line break becomes a space, and each blank line in
    between becomes a newline. A comment line ends the scalar.
    """
    kept: list[str] = []
    for raw in raw_lines:
        if not _is_blank(raw) and _is_comment(raw):
            if any(not _is_blank(k) for k in kept):
                break
            continue
        kept.append(raw)
    while kept and _is_blank(kept[-1]):
        kept.pop()
    while kept and _is_blank(kept[0]):
        kept.pop(0)
    if not kept:
        return ""
    text = "\n".join(kept).strip(" \t")
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch in " \t" or ch in BREAKS:
            i = _fold_at(text, i, out)
        else:
            out.append(ch)
            i += 1
    return _strip_comment("".join(out)).strip(" \t")


def _read_quoted(first: str, more: list[str]) -> tuple[str, int, bool]:
    """Decode a quoted scalar that starts on `first` and may continue on `more`.

    Returns (value, lines consumed from `more`, closed). A quoted scalar owns
    every line up to its closing quote, whatever their indentation and even
    when one looks like a key, which is how YAML reads it. An unterminated
    scalar reads to the end of the available lines with `closed` False.
    """
    quote = first[0]
    text = first[1:]
    raw = _find_close(text, quote)
    consumed = 0
    while raw is None and consumed < len(more):
        text += "\n" + more[consumed]
        consumed += 1
        raw = _find_close(text, quote)
    if raw is None:
        return _decode_quoted(text, quote), consumed, False
    return _decode_quoted(raw, quote), consumed, True


def _find_close(text: str, quote: str) -> str | None:
    """The content of a quoted scalar up to its closing quote, or None."""
    i = 0
    while i < len(text):
        ch = text[i]
        if quote == '"' and ch == "\\":
            i += 2
            continue
        if ch == quote:
            if quote == "'" and text[i + 1:i + 2] == "'":
                i += 2
                continue
            return text[:i]
        i += 1
    return None


def _decode_quoted(raw: str, quote: str) -> str:
    """Decode the content of a single- or double-quoted scalar, folding included.

    A port of PyYAML's flow scalar scanner: `''` in single quotes, the
    backslash escapes in double quotes, an escaped line break that joins two
    lines with nothing, and the folding of every other line break.
    """
    out: list[str] = []
    i, n = 0, len(raw)
    while i < n:
        ch = raw[i]
        if quote == "'" and ch == "'" and raw[i + 1:i + 2] == "'":
            out.append("'")
            i += 2
        elif quote == '"' and ch == "\\" and i + 1 < n and raw[i + 1] in BREAKS:
            _, j = _scan_break(raw, i + 1)
            breaks, i = _scan_breaks(raw, j)
            out.extend(breaks)
        elif quote == '"' and ch == "\\":
            decoded, i = _escape_at(raw, i)
            out.append(decoded)
        elif ch in " \t" or ch in BREAKS:
            i = _fold_at(raw, i, out)
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _escape_at(text: str, i: int) -> tuple[str, int]:
    """Decode the backslash escape at `i`. An unknown one reads as itself."""
    nxt = text[i + 1:i + 2]
    if nxt and nxt in DOUBLE_ESCAPES:
        return DOUBLE_ESCAPES[nxt], i + 2
    if nxt in HEX_ESCAPES and nxt:
        width = HEX_ESCAPES[nxt]
        digits = text[i + 2:i + 2 + width]
        if re.fullmatch(r"[0-9a-fA-F]{%d}" % width, digits):
            return chr(int(digits, 16)), i + 2 + width
    return "\\", i + 1


def _decode_double(text: str) -> str:
    """Decode the backslash escapes of a one-line double-quoted YAML scalar."""
    return _decode_quoted(text, '"')


FLOW_STOP = ",[]{}"


def _scan_flow(text: str):
    """Read the flow sequence that opens `text` at index 0.

    Returns (items, raws, end): the decoded items, the source text of each
    single-line quoted item (None for the others), and the index just past the
    closing `]`. Returns None when an item nests a collection or a mapping,
    which this reader keeps verbatim instead of flattening, and when the
    sequence never closes.

    A quote opens only at the start of an item, so `l'onboarding` is one plain
    item, and inside a quoted item `\\"` and `''` never close it. Inside a
    flow sequence a plain item ends at `,` `[` `]` `{` `}`, a `#` after
    whitespace starts a comment, and a `:` followed by a space or an
    indicator makes the item a mapping.
    """
    items: list[str] = []
    raws: list[str | None] = []
    i, n = 1, len(text)

    def skip_space(k: int) -> int:
        while k < n:
            if text[k] in " \t\n":
                k += 1
            elif text[k] == "#" and (k == 0 or text[k - 1] in " \t\n"):
                while k < n and text[k] != "\n":
                    k += 1
            else:
                break
        return k

    while True:
        i = skip_space(i)
        if i >= n:
            return None
        ch = text[i]
        if ch == "]":
            return items, raws, i + 1
        if ch in "[{":
            return None
        if ch in "\"'":
            close = _find_close(text[i + 1:], ch)
            if close is None:
                return None
            raw = text[i:i + len(close) + 2]
            items.append(_decode_quoted(close, ch))
            # A quoted item folded over lines has no reusable text, "" marks it quoted.
            raws.append(raw if "\n" not in raw else "")
            i += len(close) + 2
        elif ch == ",":
            return None
        else:
            if ch in "?:" and text[i + 1:i + 2] in ("", " ", "\t", "\n"):
                return None
            k = i
            while k < n:
                c = text[k]
                if c in FLOW_STOP:
                    break
                if c == "#" and text[k - 1] in " \t\n":
                    break
                if c == ":" and (k + 1 >= n or text[k + 1] in " \t\n" + FLOW_STOP):
                    return None
                k += 1
            items.append(_fold_plain(text[i:k].split("\n")))
            raws.append(None)
            i = k
            if i < n and text[i] == "#":
                i = skip_space(i)
        i = skip_space(i)
        if i >= n:
            return None
        if text[i] == ",":
            i += 1
        elif text[i] != "]":
            return None


def _parse_flow(key: str, head: str, tail: list[str], start: int, end: int) -> Field:
    scanned = _scan_flow("\n".join([head] + tail))
    if scanned is None:
        return Field(key, None, start, end, "nested")
    items, raws, _ = scanned
    return Field(key, items, start, end, "flow", raw=raws)


def _parse_block_list(key: str, tail: list[str], start: int, end: int) -> Field:
    """Read a block sequence: items at one column, each possibly folded."""
    values: list[str] = []
    raws: list[str | None] = []
    indent = None
    j = 0
    while j < len(tail):
        line = tail[j]
        m = ITEM_RE.match(line)
        if not m or (indent is not None and m.group(1) != indent):
            j += 1
            continue
        if indent is None:
            indent = m.group(1)
        column = len(m.group(1))
        text = line[m.end():]
        # Lines deeper than the dash, up to the next item or a shallower line.
        k = j + 1
        cont = []
        while k < len(tail):
            nxt = tail[k]
            if _is_blank(nxt):
                cont.append(nxt)
                k += 1
                continue
            mi = ITEM_RE.match(nxt)
            if _indent_of(nxt) <= column and (mi or not _is_comment(nxt)):
                break
            if _is_comment(nxt) and _indent_of(nxt) <= column:
                break
            cont.append(nxt)
            k += 1
        stripped = text.strip(" \t")
        raw = None
        if stripped[:1] in ("'", '"'):
            # A quoted item runs to its closing quote, whatever the lines between.
            value, consumed, closed = _read_quoted(stripped, tail[j + 1:])
            if closed:
                k = max(k, j + 1 + consumed)
            else:
                value, _, _ = _read_quoted(stripped, cont)
            close = _find_close(stripped[1:], stripped[0])
            raw = stripped[:len(close) + 2] if close is not None else ""
        elif stripped.startswith(("[", "{", "&", "!", "*", "|", ">")) or MAPPING_START_RE.match(stripped) \
                or (not stripped and any(not _is_blank(c) for c in cont)) or ITEM_RE.match(stripped):
            return Field(key, None, start, end, "nested", indent or "")
        else:
            value = _fold_plain([stripped] + cont) if stripped else ""
        values.append(value)
        raws.append(raw)
        j = k
    return Field(key, values, start, end, "block", indent or "", raws)


def _parse_block_scalar(lines: list[str], start: int, limit: int, key: str, header) -> Field:
    """Read a `|` or `>` block scalar, chomping indicator and explicit indent included."""
    style = "literal" if header.group(1) == "|" else "folded"
    chomp = header.group(2) or header.group(4)
    explicit = header.group(3)
    end = start + 1
    for j in range(start + 1, limit):
        line = lines[j]
        if _is_blank(line):
            continue
        if line[0] in " \t":
            end = j + 1
            continue
        break
    body = lines[start + 1:end]
    trailing = 0
    if chomp == "+":
        # Keep chomping owns the blank lines that follow, they are content.
        k = end
        while k < limit and _is_blank(lines[k]):
            k += 1
        trailing = k - end
        end = k
    content_lines = [ln for ln in body if not _is_blank(ln)]
    if explicit:
        indent = int(explicit)
    elif content_lines:
        indent = _indent_of(content_lines[0])
    else:
        indent = 0
    text_lines = []
    for ln in body:
        if _is_blank(ln):
            text_lines.append("")
        elif _indent_of(ln) >= indent:
            text_lines.append(ln[indent:])
        else:
            text_lines.append(ln.lstrip(" \t"))
    # Leading and trailing empty lines are line breaks, not content lines.
    while text_lines and text_lines[-1] == "":
        text_lines.pop()
        trailing += 1
    value = _join_block(text_lines, style == "folded")
    if not text_lines:
        value = "\n" * trailing if chomp == "+" else ""
    elif chomp == "-":
        pass
    elif chomp == "+":
        value += "\n" * (trailing + 1)
    else:
        value += "\n"
    return Field(key, value, start, end, style)


def _join_block(text_lines: list[str], folded: bool) -> str:
    parts: list[str] = []
    prev = None
    breaks = 0
    for line in text_lines:
        if line == "" and prev is not None:
            breaks += 1
            continue
        if line == "" and prev is None:
            parts.append("\n")
            continue
        if prev is not None:
            plain_edge = folded and prev[:1] not in (" ", "\t") and line[:1] not in (" ", "\t")
            if plain_edge:
                parts.append(" " if breaks == 0 else "\n" * breaks)
            else:
                parts.append("\n" * (breaks + 1))
        parts.append(line)
        prev = line
        breaks = 0
    return "".join(parts)


# --------------------------------------------------------------------------
# Writing: one quoting policy
# --------------------------------------------------------------------------

# Words YAML 1.1 or 1.2 resolve to a boolean or a null, in any case.
RETYPED_WORDS = {"yes", "no", "true", "false", "on", "off", "y", "n", "null", "~"}
NUMBER_RE = re.compile(
    r"[-+]?(?:\.?[0-9][0-9_]*(?:[.:][0-9_]*)*(?:[eE][-+]?[0-9]+)?"
    r"|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|\.(?:inf|nan))",
    re.I,
)
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt \t].*)?")
# Characters that may not open a plain scalar in any context.
LEAD_INDICATORS = set("#,[]{}&*!|>'\"%@`")
# Characters that may open one only when not followed by a space, quoted always.
LEAD_SOMETIMES = set("?:-")
# Characters that end a plain scalar inside a flow collection.
FLOW_INDICATORS = set(",?[]{}")


def _printable(ch: str) -> bool:
    """YAML's printable set, less the line separators it reads as breaks."""
    o = ord(ch)
    if ch in "\x85  ﻿":
        return False
    return (0x20 <= o <= 0x7E or o == 0xA0 or 0xA1 <= o <= 0xD7FF
            or 0xE000 <= o <= 0xFFFD or 0x10000 <= o <= 0x10FFFF)


def _needs_quotes(value: str, flow: bool) -> bool:
    """Would the plain form of `value` read back as anything but this string?

    Follows the YAML 1.1 plain scalar rules as the PyYAML emitter applies
    them, on the conservative side wherever a reader could differ:

    - empty, leading or trailing space or tab, a document marker `---` or
      `...` at the start, any character outside the printable set
    - a first character among `# , [ ] { } & * ! | > ' " % @` and backtick,
      or among `? : -` whatever follows it
    - `: ` anywhere or a trailing `:`, and ` #` anywhere
    - inside a flow collection, any of `, ? [ ] { } :` anywhere, since a
      plain item ends there or turns into a mapping
    - a word YAML would retype: a boolean or null in any case, a number,
      a date
    """
    if value == "" or value[0] in " \t" or value[-1] in " \t":
        return True
    if value.startswith(("---", "...")):
        return True
    if value[0] in LEAD_INDICATORS or value[0] in LEAD_SOMETIMES:
        return True
    if any(not _printable(ch) for ch in value):
        return True
    for i, ch in enumerate(value):
        before_space = i + 1 >= len(value) or value[i + 1] in " \t"
        after_space = i > 0 and value[i - 1] in " \t"
        if ch == ":" and (before_space or flow):
            return True
        if ch == "#" and after_space:
            return True
        if flow and ch in FLOW_INDICATORS:
            return True
    if value.lower() in RETYPED_WORDS or value in ("<<", "="):
        return True
    if NUMBER_RE.fullmatch(value) or DATE_RE.fullmatch(value):
        return True
    return False


def _valid_double(raw: str) -> bool:
    """Is a double-quoted source text made only of escapes YAML knows?"""
    i, body = 0, raw[1:-1]
    while i < len(body):
        if body[i] != "\\":
            i += 1
            continue
        nxt = body[i + 1:i + 2]
        if nxt in HEX_ESCAPES:
            width = HEX_ESCAPES[nxt]
            if not re.fullmatch(r"[0-9a-fA-F]{%d}" % width, body[i + 2:i + 2 + width]):
                return False
            i += 2 + width
        elif nxt and nxt in DOUBLE_ESCAPES:
            i += 2
        else:
            return False
    return True


def _reusable(raw) -> bool:
    """Can a list item's source text be written back as it stands?"""
    if not raw:
        return False
    return raw[0] == "'" or (raw[0] == '"' and _valid_double(raw))


def _field_is_clean(f: Field) -> bool:
    """Would the field's current lines read back, under YAML, as its value?

    A no-op `set_field` keeps lines only when this holds, so a value written
    unquoted where it needed quotes is repaired the first time a pass sets it.
    """
    if f.style == "plain":
        return f.value is None or not _needs_quotes(f.value, False)
    if f.style in ("flow", "block"):
        raws = f.raw or [None] * len(f.value)
        for value, raw in zip(f.value, raws):
            if raw is None and _needs_quotes(value, f.style == "flow"):
                return False
            if raw and raw[0] == '"' and not _valid_double(raw):
                return False
        return True
    return f.style != "nested"


def _escape_double(value: str) -> str:
    out = []
    reverse = {"\0": "0", "\a": "a", "\b": "b", "\t": "t", "\n": "n", "\v": "v",
               "\f": "f", "\r": "r", "\x1b": "e", '"': '"', "\\": "\\",
               "\x85": "N", " ": "L", " ": "P"}
    for ch in value:
        if ch in reverse:
            out.append("\\" + reverse[ch])
        elif _printable(ch) or ch == "\xa0":
            out.append(ch)
        elif ord(ch) <= 0xFF:
            out.append("\\x%02X" % ord(ch))
        elif ord(ch) <= 0xFFFF:
            out.append("\\u%04X" % ord(ch))
        else:
            out.append("\\U%08X" % ord(ch))
    return '"' + "".join(out) + '"'


def render_scalar(value, flow: bool = False) -> str:
    """Render one value so YAML reads it back as the same string.

    Plain when the plain form round-trips, double-quoted with `\\` and `"`
    escaped otherwise. Quoted: an empty string, leading or trailing space,
    a leading indicator character, `: ` or ` #` inside, a control character,
    and any word YAML would retype (`yes no true false on off y n null ~` in
    any case, numbers, dates). With `flow=True`, for an item inside `[...]`,
    `,` `[` `]` `{` `}` anywhere force quotes too.

    None renders as `null`. Anything else is rendered as `str(value)`.
    """
    if value is None:
        return "null"
    value = str(value)
    return _escape_double(value) if _needs_quotes(value, flow) else value


def render_list(values, style: str = "flow", indent: str = "") -> str:
    """Render a list under the one quoting policy.

    `flow` gives `[a, "b, c"]`, the text after `key: `. `block` gives one
    `{indent}- item` line per value joined by newlines, the lines after `key:`.
    An empty list is `[]` in both styles, since a block list cannot be empty.
    """
    values = list(values)
    if style == "flow" or not values:
        return "[" + ", ".join(render_scalar(v, flow=True) for v in values) + "]"
    if style == "block":
        return "\n".join("%s- %s" % (indent, render_scalar(v)) for v in values)
    raise ValueError("unknown list style: %r" % style)


def _render_key(key: str) -> str:
    return key if _key_of(key + ": x") == (key, " x") else _escape_double(key)


def render_field(key: str, value, style: str | None = None, indent: str = "",
                 keep: dict | None = None) -> list[str]:
    """The lines of one field, under the one quoting policy.

    `keep` maps a list item to the quoted source text it had, written back
    as it stands instead of re-rendered.
    """
    k = _render_key(key)
    if isinstance(value, (list, tuple)):
        keep = keep or {}
        if style == "block" and value:
            return [k + ":"] + ["%s- %s" % (indent, keep.get(v) or render_scalar(v)) for v in value]
        items = [keep.get(v) or render_scalar(v, flow=True) for v in value]
        return ["%s: [%s]" % (k, ", ".join(items))]
    return ["%s: %s" % (k, render_scalar(value))]


def _reparse(fm: Frontmatter, lines: list[str]) -> Frontmatter:
    fresh = parse("".join(line + "\n" for line in lines))
    fm.lines = fresh.lines
    fm.fields = fresh.fields
    return fm


def set_field(fm: Frontmatter, key: str, value, after: str | None = None,
              style: str | None = None) -> Frontmatter:
    """Set `key` to `value`, rewriting only that field's line range.

    An existing key has its whole range replaced, every list item and folded
    line included, so a list or a folded scalar is never split. Later
    duplicates of the key are removed, otherwise YAML would read the last one.
    A new key is inserted after the full range of `after`, or at the end of
    the block when `after` is None or absent.

    Setting a value the field already holds leaves its lines untouched, so a
    pass run twice writes once, unless those lines would not read back as
    that value under YAML (an unquoted `What changed in Q3?` in a flow list),
    in which case they are rewritten. A list keeps the style of the list it
    replaces, block with the same item indent or flow, unless `style` is
    given, and every item it keeps keeps its original quoting. A new list is
    flow.

    Edits `fm` in place and returns it.
    """
    if isinstance(value, tuple):
        value = list(value)
    current = [f for f in fm.fields if f.key == key]
    lines = list(fm.lines)
    if current:
        first = current[0]
        same = first.value == value and len(current) == 1 and _field_is_clean(first)
        if same and (style is None or style == first.style or not isinstance(value, list)):
            return fm
        indent = first.indent
        if style is None and isinstance(value, list):
            style = "block" if first.style == "block" else "flow"
        keep = {}
        if isinstance(value, list) and isinstance(first.value, list) and first.raw:
            for item, raw in zip(first.value, first.raw):
                if _reusable(raw) and item not in keep:
                    keep[item] = raw
        new = render_field(key, value, style, indent, keep)
        for dup in reversed(current[1:]):
            del lines[dup.start:dup.end]
        lines[first.start:first.end] = new
        return _reparse(fm, lines)
    new = render_field(key, value, style or "flow", "")
    anchor = fm.field(after) if after else None
    if anchor is not None:
        at = anchor.end
    else:
        at = len(lines)
        while at > 0 and _is_blank(lines[at - 1]):
            at -= 1
        if fm.fields:
            # Never inside the last field, whose range may own trailing
            # blank lines (a `|+` block).
            at = max(at, fm.fields[-1].end)
    lines[at:at] = new
    return _reparse(fm, lines)


def drop_field(fm: Frontmatter, key: str) -> Frontmatter:
    """Remove every occurrence of `key`, its whole line range each time.

    Edits `fm` in place and returns it. An absent key is not an error.
    """
    lines = list(fm.lines)
    for f in reversed([f for f in fm.fields if f.key == key]):
        del lines[f.start:f.end]
        before = [g for g in fm.fields if g.end == f.start]
        if before and _keeps_trailing(fm, before[-1]):
            # Blank lines that followed the dropped field would now trail a
            # `|+` block and become part of its value. They go with the field.
            while f.start < len(lines) and _is_blank(lines[f.start]):
                del lines[f.start]
    return _reparse(fm, lines)


def _keeps_trailing(fm: Frontmatter, f: Field) -> bool:
    """Is this field a block scalar with keep chomping, `|+` or `>+`?"""
    if f.style not in ("literal", "folded"):
        return False
    kr = _key_of(fm.lines[f.start])
    header = BLOCK_HEADER_RE.match(kr[1].strip(" \t")) if kr else None
    return bool(header) and "+" in (header.group(2), header.group(4))


# --------------------------------------------------------------------------
# Damage facts: what the grammar says about a block an older pass damaged.
#
# A pass that rewrites a field replaces its whole line range. On a damaged
# block that range may cover lines of another field, so every guard asks these
# 2 questions before writing, and the read-only damage check asks them too.
# --------------------------------------------------------------------------


def quote_closed(fm: Frontmatter, f: Field) -> bool:
    """Does the quoted scalar of `f` close inside its range, with only a comment after?

    False when the closing quote is missing from the range, or when anything
    but blank lines and comments follows it there.
    """
    text = "\n".join(fm.lines[f.start:f.end])
    after = text.split(":", 1)[1].lstrip()
    raw = _find_close(after[1:], after[:1])
    if raw is None:
        return False
    rest = after[len(raw) + 2:].split("\n")
    return all(not ln.strip() or ln.strip().startswith("#") for ln in rest)


def swallowed_key_line(fm: Frontmatter) -> str | None:
    """A column-0 `key:` line inside the range of another field, or None.

    A quoted scalar or a flow collection owns every line up to its closing
    quote or bracket, as PyYAML reads it. When an older pass inserted a field
    inside one, the inserted line now sits in that range, at column 0, and the
    value reads it as text. Nothing else puts a column-0 `key:` line past the
    first line of a range: block scalars and folded plain scalars are indented.
    Returns the reason, worded for a report.
    """
    for f in fm.fields:
        for line in fm.lines[f.start + 1:f.end]:
            if KEY_LINE_RE.match(line):
                return f"`{f.key}:` swallows the key line `{line.strip()}`"
    return None


def render(fm: Frontmatter) -> str:
    """The block text of `fm`, every line ended by "\\n", ready for `join`."""
    return "".join(line + "\n" for line in fm.lines)


def read_file(path) -> tuple[Doc, Frontmatter] | tuple[None, None]:
    """Read a note and parse its frontmatter, or (None, None) when it has none.

    Reads with universal newlines off, so a CRLF file comes back CRLF on
    `write_file`.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    doc = split(text)
    if doc is None:
        return None, None
    return doc, parse(doc.block)


def write_file(path, doc: Doc, fm: Frontmatter | None = None) -> bool:
    """Write `doc`, with `fm` as its block when given. True when the file changed."""
    text = join(doc, fm)
    p = Path(path)
    with open(p, encoding="utf-8", newline="") as fh:
        old = fh.read()
    if old == text:
        return False
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return True
