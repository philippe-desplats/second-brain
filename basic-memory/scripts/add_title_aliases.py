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
import contextlib
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import WIKILINK_RE  # noqa: E402
from corpus import in_note_zone, is_corpus_note  # noqa: E402

# Links are counted in every zone below, documentation and templates included,
# so this walk is deliberately wider than `corpus.iter_corpus_notes`. It only
# reads. Whether a note may be written is decided note by note in `writable`.
ZONES = ["sources", "knowledge", "atlas", "archives", "inbox", "basic-memory", "docs", "templates"]



@dataclass
class Note:
    """One markdown file: its path, its frontmatter when it has one, its body."""

    rel: str
    doc: F.Doc | None
    fm: F.Frontmatter | None
    body: str


@dataclass
class Plan:
    """What the pass found for the cited titles, sorted by what it will do."""

    candidates: list = field(default_factory=list)
    changed: list = field(default_factory=list)
    already: list = field(default_factory=list)
    ambiguous: list = field(default_factory=list)
    unreadable: list = field(default_factory=list)


@dataclass
class Change:
    """One note to write: the new aliases and the block that carries them."""

    title: str
    count: int
    rel: str
    aliases: list
    edited: F.Frontmatter


def to_posix(rel):
    """A relative path with forward slashes and no leading `./`, on every platform.

    `os.path.relpath` and a path typed on Windows both use backslashes, and
    every comparison below is made on the forward-slash form.
    """
    rel = str(rel).replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def normalise_excludes(paths):
    return {to_posix(p) for p in paths}


def is_target(rel, root):
    """Can a wikilink land on this note, so its title counts as taken?"""
    rel = to_posix(rel)
    return in_note_zone(rel) and is_corpus_note(rel, Path(root))


def writable(rel, root, excluded):
    """May the pass write this note? A target the caller did not exclude."""
    return to_posix(rel) not in excluded and is_target(rel, root)


def collect(root="."):
    """Every markdown file under the zones, as sorted forward-slash relative paths."""
    files = []
    for zone in ZONES:
        for dirpath, _, filenames in os.walk(os.path.join(root, zone)):
            for name in filenames:
                if name.endswith(".md"):
                    files.append(to_posix(os.path.relpath(os.path.join(dirpath, name), root)))
    return sorted(files)


def load(root, files):
    notes = {}
    for rel in files:
        with open(os.path.join(root, rel), encoding="utf-8", newline="") as fh:
            text = fh.read()
        doc = F.split(text)
        fm = F.parse(doc.block) if doc is not None else None
        notes[rel] = Note(rel, doc, fm, doc.body if doc is not None else text)
    return notes


def count_citations(notes):
    citations = Counter()
    for note in notes.values():
        for target in WIKILINK_RE.findall(note.body):
            citations[target.strip()] += 1
    return citations


def title_of(note):
    title = note.fm.get("title") if note.fm is not None else None
    return title if isinstance(title, str) and title.strip() else None


def index_titles(notes, root):
    """Map each title to the target notes carrying it.

    Excluded notes are indexed like any other. Exclusion only stops a write,
    so a title shared with an excluded note stays ambiguous and nobody gets it.
    """
    by_title = {}
    for rel, note in notes.items():
        title = title_of(note)
        if title and is_target(rel, root):
            by_title.setdefault(title, []).append(rel)
    return by_title


def current_aliases(fm):
    """The aliases a note already declares, or None when they cannot be read safely.

    A nested mapping or a collection inside the list reads as None, and
    rewriting it would destroy what the reader did not understand.
    """
    f = fm.field("aliases")
    if f is None:
        return []
    if f.style == "nested":
        return None
    if isinstance(f.value, list):
        return list(f.value)
    return [] if f.value is None else [f.value]


def edit(note, title, aliases):
    """The block with `aliases` set right after the title, or None if it does not read back."""
    edited = F.parse(note.doc.block)
    F.set_field(edited, "aliases", aliases, after="title")
    if edited.get("aliases") != aliases or edited.get("title") != title:
        return None
    return edited


def plan(notes, by_title, citations, basenames, excluded, top):
    result = Plan()
    for title, count in citations.most_common():
        if title in basenames or title not in by_title:
            continue
        paths = by_title[title]
        if len(paths) == 1 and paths[0] in excluded:
            continue
        result.candidates.append((title, count, paths))
    if top:
        result.candidates = result.candidates[:top]

    for title, count, paths in result.candidates:
        if len(paths) > 1:
            result.ambiguous.append((title, count, paths))
            continue
        rel = paths[0]
        note = notes[rel]
        existing = current_aliases(note.fm)
        if existing is not None and title in existing:
            result.already.append((title, count, rel))
            continue
        aliases = [title] + (existing or [])
        edited = edit(note, title, aliases) if existing is not None else None
        if edited is None:
            result.unreadable.append((title, count, rel))
            continue
        result.changed.append(Change(title, count, rel, aliases, edited))
    return result


def report_changes(result):
    print("Candidate notes: %d cited titles, %d to modify, %d already compliant, %d ambiguous"
          % (len(result.candidates), len(result.changed), len(result.already), len(result.ambiguous)))
    print()
    for change in result.changed:
        print("  %6d links  %-58s %s" % (change.count, change.title, change.rel))
        print("               aliases: %s" % F.render_list(change.aliases, "flow"))


def report_leftovers(result, applied):
    if result.ambiguous:
        print()
        print("Ambiguous, several notes share the same title, to settle by hand:")
        for title, count, paths in result.ambiguous:
            print("  %6d links  %s" % (count, title))
            for p in paths:
                print("               %s" % p)
    if result.unreadable:
        print()
        print("Aliases not safely rewritable, left alone, to settle by hand:")
        for title, count, rel in result.unreadable:
            print("  %6d links  %-58s %s" % (count, title, rel))
    if result.already:
        print()
        print("Already compliant: %d" % len(result.already))
    print()
    print("APPLIED" if applied else "DRY-RUN, nothing written. Add --apply to write.")


def apply_changes(root, notes, changes):
    for change in changes:
        F.write_file(os.path.join(root, change.rel), notes[change.rel].doc, change.edited)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry-run)")
    ap.add_argument("--top", type=int, default=0, help="restrict to the N most-cited titles")
    ap.add_argument("--root", default=".", help="vault root (default: current directory)")
    ap.add_argument("--quiet", action="store_true", help="print nothing, for the hook")
    ap.add_argument("--exclude", action="append", default=[],
                    help="workspace-relative note never to write, repeatable")
    return ap.parse_args(argv)


def run(args):
    files = collect(args.root)
    basenames = {rel.rsplit("/", 1)[-1][:-3] for rel in files}
    notes = load(args.root, files)
    excluded = normalise_excludes(args.exclude)
    result = plan(notes, index_titles(notes, args.root), count_citations(notes),
                  basenames, excluded, args.top)
    report_changes(result)
    if args.apply:
        apply_changes(args.root, notes, result.changed)
    report_leftovers(result, args.apply)


def main(argv=None):
    args = parse_args(argv)
    if not args.quiet:
        run(args)
        return
    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        run(args)


if __name__ == "__main__":
    main()
