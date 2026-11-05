#!/usr/bin/env python3
"""Tests for generate_indexes.py, standard library only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate_indexes as gi  # noqa: E402

LONG = "Globex Website Redesign, discovery workshop outcomes and the content inventory plan"

# A project brief as Basic Memory writes it: the title folds at 80 columns.
BRIEF = (
    "---\n"
    "title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan\n"
    "aliases:\n"
    "- Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan\n"
    "type: project-brief\n"
    "category: client\n"
    "status: active\n"
    "last_updated: 2026-06-24\n"
    "---\n\n# Brief\n"
)
CLIENT = ("---\ntitle: Globex\nclient: Globex\ntype: client-context\nstatus: active\n"
          "last_updated: 2026-06-22\n---\n\n# Globex\n")
PARTNER = ("---\ntitle: Proseware\npartner: Proseware\ntype: partner-context\nstatus: active\n"
           "last_updated: 2026-06-24\n---\n\n# Proseware\n")


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.out = self.root / "out"

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def generate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gi.main(["--output-dir", str(self.out)], root=self.root), 0)

    def rows(self, name: str) -> list[str]:
        text = (self.out / f"{name}-static.md").read_text(encoding="utf-8")
        return [ln for ln in text.splitlines()
                if ln.startswith("| ") and not ln.startswith("| ---")][1:]


class Indexes(Workspace):
    def test_folded_title_is_indexed_whole(self):
        self.write("sources/clients/globex/website-redesign/README.md", BRIEF)
        self.generate()
        self.assertEqual(self.rows("projects-active"), [
            f"| [[{LONG}]] | client | sources/clients/globex/website-redesign/README.md | 2026-06-24 |",
        ])

    def test_active_entities_each_get_their_index(self):
        self.write("sources/clients/globex/CLAUDE.md", CLIENT)
        self.write("sources/partners/proseware/CLAUDE.md", PARTNER)
        self.write("sources/clients/initech/CLAUDE.md",
                   CLIENT.replace("Globex", "Initech").replace("active", "prospect"))
        self.generate()
        self.assertEqual(self.rows("clients-active"),
                         ["| [[Globex]] | sources/clients/globex/CLAUDE.md | 2026-06-22 |"])
        self.assertEqual(self.rows("partners-active"),
                         ["| [[Proseware]] | sources/partners/proseware/CLAUDE.md | 2026-06-24 |"])

    def test_null_category_prints_empty(self):
        self.write("sources/internal/ops/README.md",
                   "---\ntitle: Ops\ntype: project-brief\ncategory: null\nstatus: active\n"
                   "last_updated: 2026-06-01\n---\n")
        self.generate()
        self.assertEqual(self.rows("projects-active"),
                         ["| [[Ops]] |  | sources/internal/ops/README.md | 2026-06-01 |"])

    def test_only_corpus_notes_are_indexed(self):
        self.write("sources/clients/globex/CLAUDE.md", CLIENT)
        for rel in ("sources/clients/globex/site/prompts/CLAUDE.md",
                    "sources/clients/globex/site/repo-files/CLAUDE.md",
                    "sources/clients/globex/site/captures/CLAUDE.md",
                    "docs/CLAUDE.md", "templates/entity-CLAUDE-template.md"):
            self.write(rel, CLIENT)
        self.generate()
        self.assertEqual(self.rows("clients-active"),
                         ["| [[Globex]] | sources/clients/globex/CLAUDE.md | 2026-06-22 |"])

    def test_recent_email_subject_and_decision_are_read_whole(self):
        today = dt.date.today().isoformat()
        self.write("sources/clients/globex/site/emails/a.md",
                   f"---\ntitle: Re, the kickoff agenda and the list of every asset we still\n"
                   f"  need\ntype: email\ndate: {today}\n---\n\n- [decision] Ship it\n")
        self.generate()
        self.assertEqual(self.rows("recent-emails"), [
            f"| {today} | Re, the kickoff agenda and the list of every asset we still need"
            " | sources/clients/globex/site/emails/a.md |"])
        self.assertEqual(self.rows("decisions-recent"),
                         [f"| {today} | Ship it | sources/clients/globex/site/emails/a.md |"])

    def test_partners_index_is_skipped_when_the_zone_is_pruned(self):
        self.write("sources/clients/globex/CLAUDE.md", CLIENT)
        self.generate()
        self.assertFalse((self.out / "partners-active-static.md").exists())


if __name__ == "__main__":
    unittest.main()
