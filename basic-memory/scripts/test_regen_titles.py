#!/usr/bin/env python3
"""Tests for `regen_titles.py`.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import frontmatter as F  # noqa: E402
import regen_titles  # noqa: E402
from test_retype_files import DAMAGED, Workspace, block_of, run, yaml  # noqa: E402

HEADER = "Needs repair, run check_frontmatter_damage.py"


def title_of(text: str):
    return F.parse(block_of(text)).get("title")


class EntityContext(unittest.TestCase):
    """B6: an entity context file takes its identity, never its H1."""

    def test_client_title_is_identity(self):
        ws = Workspace(self)
        rel = "sources/clients/hooli/CLAUDE.md"
        ws.write(rel, "---\ntitle: CLAUDE\nclient: Hooli\ntype: client-context\n---\n\n# Hooli, Context\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel),
                         "---\ntitle: Hooli\nclient: Hooli\ntype: client-context\n---\n\n# Hooli, Context\n")

    def test_partner_title_is_identity(self):
        ws = Workspace(self)
        rel = "sources/partners/proseware/CLAUDE.md"
        ws.write(rel, "---\ntitle: CLAUDE\npartner: 'Proseware: Labs'\n---\n\n# Proseware, Context\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(title_of(ws.read(rel)), "Proseware: Labs")
        if yaml is not None:
            self.assertEqual(yaml.safe_load(block_of(ws.read(rel)))["title"], "Proseware: Labs")

    def test_entity_without_identity_is_skipped(self):
        ws = Workspace(self)
        rel = "sources/clients/hooli/CLAUDE.md"
        text = "---\ntitle: CLAUDE\n---\n\n# Hooli, Context\n"
        ws.write(rel, text)
        out = run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), text)
        self.assertIn("No identity field (skip): 1", out)

    def test_project_brief_still_uses_h1(self):
        ws = Workspace(self)
        rel = "sources/clients/hooli/web/README.md"
        ws.write(rel, "---\ntitle: README\n---\n\n# Hooli Website\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(title_of(ws.read(rel)), "Hooli Website")


class Quoting(unittest.TestCase):
    """The shared quoting policy, applied to every new title."""

    H1S = ["Notes: kickoff", "Release #2", "yes", "2026", "- dash first", 'Say "hi"',
           "Regex \\d+ cheatsheet", "Plain title"]

    def test_every_h1_reads_back(self):
        for h1 in self.H1S:
            with self.subTest(h1):
                ws = Workspace(self)
                rel = "sources/internal/ops/plan.md"
                ws.write(rel, "---\ntitle: plan\ntype: note\n---\n\n# %s\n" % h1)
                run(regen_titles.main, ["--apply"], root=ws.root)
                self.assertEqual(title_of(ws.read(rel)), h1)
                if yaml is not None:
                    self.assertEqual(yaml.safe_load(block_of(ws.read(rel)))["title"], h1)

    def test_title_replaced_in_place(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/readme-notes.md"
        ws.write(rel, "---\ntype: note\ntitle: README\ntags:\n- x\n---\n\n# Short\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), "---\ntype: note\ntitle: Short\ntags:\n- x\n---\n\n# Short\n")

    def test_missing_title_inserted_first(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/plan.md"
        ws.write(rel, "---\ntags:\n- x\ntype: note\n---\n\n# A plan\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), "---\ntitle: A plan\ntags:\n- x\ntype: note\n---\n\n# A plan\n")

    def test_second_run_changes_nothing(self):
        ws = Workspace(self)
        rel = "sources/clients/hooli/CLAUDE.md"
        ws.write(rel, "---\ntitle: CLAUDE\nclient: Hooli\n---\n\n# Hooli, Context\n")
        run(regen_titles.main, ["--apply"], root=ws.root)
        first = ws.read(rel)
        out = run(regen_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), first)
        self.assertIn("Updated: 0", out)

    def test_dry_run_writes_nothing(self):
        ws = Workspace(self)
        rel = "sources/clients/hooli/CLAUDE.md"
        text = "---\ntitle: CLAUDE\nclient: Hooli\n---\n\n# Hooli, Context\n"
        ws.write(rel, text)
        out = run(regen_titles.main, ["--dry-run"], root=ws.root)
        self.assertEqual(ws.read(rel), text)
        self.assertIn("'CLAUDE' -> 'Hooli'", out)


class NeedsRepair(unittest.TestCase):
    """A `title:` the pass did not write is replaced only when it reads as one."""

    def apply(self, rel: str, text: str) -> str:
        ws = Workspace(self)
        ws.write(rel, text)
        out = run(regen_titles.main, ["--apply"], root=ws.root)
        self.ws = ws
        return out

    def test_open_quoted_title_is_never_rewritten(self):
        # The `sq` and `dq` shapes with a generic title, so the pass wants it.
        for key in ("sq", "dq"):
            text = DAMAGED[key].replace("type: meeting", "type: note")
            quote = "'" if key == "sq" else '"'
            first = text.split("\n")[1]
            text = text.replace(first, f"title: {quote}README")
            rel = f"sources/internal/ops/2026-07-01-note-{key}.md"
            out = self.apply(rel, text)
            self.assertEqual(self.ws.read(rel), text, key)
            self.assertIn(f"{HEADER} (1):", out)
            self.assertIn(rel, out)

    def test_sane_title_below_damage_is_replaced_alone(self):
        for key in ("indented", "block"):
            text = DAMAGED[key].replace("title: Indented", "title: README").replace(
                "title: Block", "title: README")
            rel = f"sources/internal/ops/2026-07-01-note-{key}.md"
            self.apply(rel, text)
            first = DAMAGED[key].split("\n# ")[1].strip()
            self.assertEqual(self.ws.read(rel), text.replace("title: README", f"title: {first}"), key)

    def test_duplicate_title_is_not_collapsed(self):
        rel = "sources/internal/ops/2026-07-01-note-dup.md"
        text = "---\ntitle: README\ntype: note\ntitle: Kept\n---\n\n# Real title\n"
        out = self.apply(rel, text)
        self.assertEqual(self.ws.read(rel), text)
        self.assertIn(f"{HEADER} (1):", out)


if __name__ == "__main__":
    unittest.main()
