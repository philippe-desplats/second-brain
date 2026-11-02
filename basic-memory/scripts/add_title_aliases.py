#!/usr/bin/env python3
"""Make Obsidian resolve the wikilinks that Basic Memory already resolves.

Basic Memory resolves ``[[X]]`` on the ``title:`` frontmatter field. Obsidian
resolves it on the file basename only, and reads neither ``title:`` nor
``aliases:`` for resolution, by design. A vault whose links are written against
titles therefore shows Obsidian a graph made almost entirely of unresolved
ghost nodes.

The aliases this pass writes resolve only through the Alias Linker community
plugin (``johannrichard/alias-linker``), which patches Obsidian's link lookup.
Without that plugin the pass changes nothing in the graph.

This pass adds each note's own ``title:`` to its ``aliases:`` list when a
wikilink somewhere in the corpus points at that title and no file carries it as
a basename. Nothing else is touched: no file is moved, no link is rewritten, and
the ``title:`` field itself is left alone, so Basic Memory keeps resolving
exactly as before.

The pass is idempotent. A note whose aliases already contain its title is left
untouched and reported as such.

Links are counted across every zone below, documentation included, but an alias
is only ever written on a corpus note: a file under one of the five note zones
that ``corpus.is_corpus_note`` accepts. Schema definitions and documentation
carry wikilinks but are not notes a link should land on.

Wired as a PostToolUse hook on Write and Edit through
``.claude/hooks/title_aliases.py``, with ``--apply --quiet``, so a note that
becomes the target of a new wikilink gets its alias in the same session rather
than drifting back to an unresolved node in Obsidian.

Usage:
    python3 basic-memory/scripts/add_title_aliases.py                 # dry-run, full report
    python3 basic-memory/scripts/add_title_aliases.py --top 10        # dry-run on the 10 most-cited
    python3 basic-memory/scripts/add_title_aliases.py --top 10 --apply
    python3 basic-memory/scripts/add_title_aliases.py --apply --quiet   # hook mode, silent
"""

import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import in_note_zone, is_corpus_note  # noqa: E402

ZONES = ["sources", "knowledge", "atlas", "archives", "inbox", "basic-memory", "docs", "templates"]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
SCALAR_RE = re.compile(r"^([A-Za-z_][\w-]*):[ \t]*(.*)$")


def split_frontmatter(text):
    """Return (frontmatter_body, rest, end_offset) or (None, text, 0)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text, 0
    return m.group(1), text[m.end():], m.end()


def parse_keys(fm_body):
    """Very small YAML reader: top-level scalars plus block sequences."""
    out = {}
    current = None
    for line in fm_body.split("\n"):
        m = SCALAR_RE.match(line)
        if m:
            current = m.group(1)
            out[current] = m.group(2).strip()
            continue
        item = re.match(r"^[ \t]+-[ \t]+(.*)$", line)
        if item and current:
            out.setdefault(current + "__list", []).append(item.group(1).strip())
            continue
        # A long scalar folded over several lines. Read only its first line
        # and the alias inherits a truncated title, then lands inside it.
        cont = re.match(r"^[ \t]+(\S.*)$", line)
        if cont and current and current + "__list" not in out:
            out[current] = (out[current] + " " + cont.group(1).strip()).strip()
    return out


def is_continuation(line):
    """An indented line that is not a list item continues the scalar above it."""
    return bool(re.match(r"^[ \t]+\S", line)) and not re.match(r"^[ \t]+-[ \t]+", line)


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def split_inline_list(raw):
    """Split a YAML flow sequence body on commas that sit outside quotes.

    A naive ``raw.split(",")`` shreds any quoted value containing a comma, and
    a title like ``Globex, Context`` is exactly that.
    The reader then believes the alias is absent, and a second run appends a
    mangled one. Splitting quote-aware is what makes this pass idempotent.
    """
    items, buf, quote, escaped = [], [], None, False
    for ch in raw:
        if escaped:
            buf.append(ch)
            escaped = False
        elif ch == "\\" and quote:
            escaped = True
        elif quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return [unquote(x) for x in items if x.strip()]


def read_aliases(keys):
    inline = keys.get("aliases", "")
    if inline.startswith("[") and inline.endswith("]"):
        return split_inline_list(inline[1:-1])
    if inline:
        return [unquote(inline)]
    return [unquote(x) for x in keys.get("aliases__list", [])]


def needs_quoting(value):
    return bool(re.search(r"[:\[\]{},&*#?|<>=!%@`\"']", value)) or value != value.strip()


def render_alias_list(values):
    rendered = []
    for v in values:
        rendered.append('"%s"' % v.replace('"', '\\"') if needs_quoting(v) else v)
    return "aliases: [%s]" % ", ".join(rendered)


def collect(root="."):
    files = []
    for zone in ZONES:
        for dirpath, _, filenames in os.walk(os.path.join(root, zone)):
            for name in filenames:
                if name.endswith(".md"):
                    files.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry-run)")
    ap.add_argument("--top", type=int, default=0, help="restrict to the N most-cited titles")
    ap.add_argument("--root", default=".", help="vault root (default: current directory)")
    ap.add_argument("--quiet", action="store_true", help="print nothing, for the hook")
    ap.add_argument("--exclude", action="append", default=[],
                    help="workspace-relative note never to write, repeatable")
    args = ap.parse_args()
    if args.quiet:
        sys.stdout = open(os.devnull, "w")

    files = collect(args.root)
    basenames = {os.path.basename(p)[:-3] for p in files}

    docs = {}
    for rel in files:
        with open(os.path.join(args.root, rel), encoding="utf-8") as fh:
            text = fh.read()
        fm_body, rest, _ = split_frontmatter(text)
        docs[rel] = (text, fm_body, parse_keys(fm_body) if fm_body else {})

    citations = Counter()
    for rel, (text, fm_body, _) in docs.items():
        body = text if fm_body is None else text[len(text) - len(split_frontmatter(text)[1]):]
        for target in WIKILINK_RE.findall(body):
            citations[target.strip()] += 1

    by_title = {}
    for rel, (_, fm_body, keys) in docs.items():
        if not fm_body:
            continue
        if not (in_note_zone(rel) and is_corpus_note(rel)) or rel in args.exclude:
            continue
        title = unquote(keys.get("title", ""))
        if title:
            by_title.setdefault(title, []).append(rel)

    candidates = []
    for title, count in citations.most_common():
        if title in basenames or title not in by_title:
            continue
        paths = by_title[title]
        candidates.append((title, count, paths))

    if args.top:
        candidates = candidates[: args.top]

    changed, already, ambiguous = [], [], []
    for title, count, paths in candidates:
        if len(paths) > 1:
            ambiguous.append((title, count, paths))
            continue
        rel = paths[0]
        text, fm_body, keys = docs[rel]
        if title in read_aliases(keys):
            already.append((title, count, rel))
            continue
        changed.append((title, count, rel))

    print("Candidate notes: %d cited titles, %d to modify, %d already compliant, %d ambiguous"
          % (len(candidates), len(changed), len(already), len(ambiguous)))
    print()

    for title, count, rel in changed:
        text, fm_body, keys = docs[rel]
        existing = read_aliases(keys)
        new_line = render_alias_list([title] + [a for a in existing if a != title])
        print("  %6d links  %-58s %s" % (count, title, rel))
        print("               %s" % new_line)

        if not args.apply:
            continue

        lines = fm_body.split("\n")
        out_lines, skipping, inserted = [], False, False
        for line in lines:
            if skipping:
                if re.match(r"^[ \t]+-[ \t]+", line) or line.strip() == "":
                    continue
                skipping = False
            m = SCALAR_RE.match(line)
            if m and m.group(1) == "aliases":
                out_lines.append(new_line)
                inserted = True
                if not m.group(2).strip():
                    skipping = True
                continue
            out_lines.append(line)
            if m and m.group(1) == "title" and not inserted:
                pass
        if not inserted:
            # place it right after title:, which every candidate carries
            # and after the last line of a folded title, never inside it
            rebuilt, pending = [], False
            for line in out_lines:
                if pending and not is_continuation(line):
                    rebuilt.append(new_line)
                    inserted, pending = True, False
                rebuilt.append(line)
                m = SCALAR_RE.match(line)
                if m and m.group(1) == "title" and not inserted:
                    pending = True
            if pending:
                rebuilt.append(new_line)
                inserted = True
            out_lines = rebuilt

        assert inserted, "aliases not inserted in %s" % rel
        rest = split_frontmatter(text)[1]
        with open(os.path.join(args.root, rel), "w", encoding="utf-8") as fh:
            fh.write("---\n" + "\n".join(out_lines) + "\n---\n" + rest)

    if ambiguous:
        print()
        print("Ambiguous, several notes share the same title, to settle by hand:")
        for title, count, paths in ambiguous:
            print("  %6d links  %s" % (count, title))
            for p in paths:
                print("               %s" % p)

    if already:
        print()
        print("Already compliant: %d" % len(already))

    print()
    print("APPLIED" if args.apply else "DRY-RUN, nothing written. Add --apply to write.")


if __name__ == "__main__":
    main()
