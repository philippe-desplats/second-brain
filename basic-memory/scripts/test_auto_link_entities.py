#!/usr/bin/env python3
"""Tests for auto_link_entities.py, standard library only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auto_link_entities as autolink  # noqa: E402

LONG = "Globex Website Redesign, discovery workshop outcomes and the content inventory plan"

# A topic as Basic Memory writes it: title folded at 80 columns, aliases as a
# column-0 block list.
LONG_TOPIC = (
    "---\n"
    "title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan\n"
    "name: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan\n"
    "type: topic\n"
    "---\n\n# Topic\n"
)
CATALOG_TOPIC = (
    "---\ntitle: Catalog Search\nname: Catalog Search\ntype: topic\n"
    "aliases:\n- Catalog Search\n- product search\n---\n\n# Catalog Search\n"
)


def note(body: str, title: str = "Some note") -> str:
    return f"---\ntitle: {title}\ntype: note\n---\n\n{body}"


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.write("atlas/topics/long.md", LONG_TOPIC)
        self.write("atlas/topics/catalog-search.md", CATALOG_TOPIC)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def plan(self, include_emails=False):
        _linked, _ambiguous, new_texts = autolink.collect(self.root, include_emails)
        return {path.relative_to(self.root).as_posix(): text for path, text in new_texts.items()}

    def main(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return autolink.main(list(argv), root=self.root)


class Titles(Workspace):
    def test_folded_title_is_linked_whole(self):
        self.write("sources/internal/pricing/2026-01-01-note-a.md", note(f"We read {LONG} today.\n"))
        planned = self.plan()["sources/internal/pricing/2026-01-01-note-a.md"]
        self.assertIn(f"We read [[{LONG}]] today.\n", planned)

    def test_block_list_alias_links_to_the_title(self):
        self.write("sources/internal/pricing/2026-01-01-note-a.md", note("A product search box.\n"))
        planned = self.plan()["sources/internal/pricing/2026-01-01-note-a.md"]
        self.assertIn("A [[Catalog Search|product search]] box.\n", planned)

    def test_frontmatter_is_never_rewritten(self):
        text = ("---\ntitle: About Catalog Search, a review of every\n  Catalog Search idea\n"
                "type: note\n---\n\nCatalog Search wins.\n")
        self.write("sources/internal/pricing/2026-01-01-note-a.md", text)
        planned = self.plan()["sources/internal/pricing/2026-01-01-note-a.md"]
        self.assertEqual(planned, text.replace("\nCatalog Search wins.", "\n[[Catalog Search]] wins."))


class Scope(Workspace):
    def test_only_corpus_notes_are_rewritten(self):
        body = note("Catalog Search here.\n")
        self.write("sources/internal/pricing/2026-01-01-note-a.md", body)
        for rel in ("sources/clients/acme/site/prompts/p.md",
                    "sources/clients/acme/site/repo-files/LICENSE.md",
                    "sources/clients/acme/site/captures/c.md",
                    "sources/clients/acme/site/tmp/t.md",
                    "sources/clients/acme/skills/s/SKILL.md",
                    "docs/guide.md", "README.md", "templates/note.md",
                    "atlas/maps/MOC-search.md", "inbox/x-static.md"):
            self.write(rel, body)
        self.assertEqual(list(self.plan()), ["sources/internal/pricing/2026-01-01-note-a.md"])

    def test_emails_are_skipped_unless_asked(self):
        rel = "sources/clients/acme/site/emails/2026-01-01-01-in-a.md"
        self.write(rel, note("Catalog Search here.\n"))
        self.assertEqual(self.plan(), {})
        self.assertIn(rel, self.plan(include_emails=True))


class Modes(Workspace):
    def setUp(self):
        super().setUp()
        self.text = note("Catalog Search here.\n")
        self.path = self.write("sources/internal/pricing/2026-01-01-note-a.md", self.text)

    def test_dry_run_is_the_default(self):
        self.assertEqual(self.main(), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), self.text)

    def test_explicit_dry_run_writes_nothing(self):
        self.assertEqual(self.main("--dry-run"), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), self.text)

    def test_apply_writes_and_a_second_apply_changes_nothing(self):
        self.main("--apply")
        once = self.path.read_text(encoding="utf-8")
        self.assertEqual(once, note("[[Catalog Search]] here.\n"))
        self.main("--apply")
        self.assertEqual(self.path.read_text(encoding="utf-8"), once)

    def test_every_mention_of_a_line_is_linked_in_one_run(self):
        self.path.write_text(note(f"Catalog Search and {LONG}, then product search again.\n"),
                             encoding="utf-8")
        self.main("--apply")
        once = self.path.read_text(encoding="utf-8")
        self.assertEqual(once, note(f"[[Catalog Search]] and [[{LONG}]], then"
                                    " [[Catalog Search|product search]] again.\n"))
        self.main("--apply")
        self.assertEqual(self.path.read_text(encoding="utf-8"), once)

    def test_dry_run_reports_each_mention_and_the_final_line(self):
        self.path.write_text(note("Catalog Search, product search.\n"), encoding="utf-8")
        linked, _ambiguous, new_texts = autolink.collect(self.root)
        self.assertEqual([m.matched for m in linked[self.path]], ["Catalog Search", "product search"])
        self.assertEqual(new_texts[self.path],
                         note("[[Catalog Search]], [[Catalog Search|product search]].\n"))


if __name__ == "__main__":
    unittest.main()
