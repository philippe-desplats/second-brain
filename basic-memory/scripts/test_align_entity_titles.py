#!/usr/bin/env python3
"""Tests for `align_entity_titles.py`.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import align_entity_titles  # noqa: E402
import frontmatter as F  # noqa: E402
from test_retype_files import DAMAGED, Workspace, block_of, run, yaml  # noqa: E402

HEADER = "Needs repair, run check_frontmatter_damage.py"

# As Basic Memory writes a title longer than its 80 columns.
FOLDED = ("---\ntitle: Initech, Context and a long description of the whole relationship history"
          " and\n  co-delivery\nclient: Initech\ntype: client-context\n---\n\n# Initech, Context\n")


class Align(unittest.TestCase):
    def test_folded_title_replaced_whole(self):
        ws = Workspace(self)
        rel = "sources/clients/initech/CLAUDE.md"
        ws.write(rel, FOLDED)
        run(align_entity_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel),
                         "---\ntitle: Initech\nclient: Initech\ntype: client-context\n---\n\n"
                         "# Initech, Context\n")

    def test_second_run_is_compliant_and_writes_nothing(self):
        ws = Workspace(self)
        rel = "sources/clients/initech/CLAUDE.md"
        ws.write(rel, FOLDED)
        run(align_entity_titles.main, ["--apply"], root=ws.root)
        first = ws.read(rel)
        out = run(align_entity_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), first)
        self.assertIn("1 already compliant, 0 to fix", out)

    def test_quoting_goes_through_shared_policy(self):
        cases = {
            "sources/clients/acme-studio/CLAUDE.md": ("client", "'Acme: Studio'", "Acme: Studio"),
            "atlas/topics/foo-2.md": ("name", "'Foo #2'", "Foo #2"),
            "sources/partners/yes/CLAUDE.md": ("partner", "'yes'", "yes"),
        }
        ws = Workspace(self)
        for rel, (key, raw, _) in cases.items():
            ws.write(rel, "---\ntitle: x\n%s: %s\n---\n\n# H\n" % (key, raw))
        run(align_entity_titles.main, ["--apply"], root=ws.root)
        for rel, (_, _, value) in cases.items():
            with self.subTest(rel):
                text = ws.read(rel)
                self.assertEqual(F.parse(block_of(text)).get("title"), value)
                if yaml is not None:
                    self.assertEqual(yaml.safe_load(block_of(text))["title"], value)

    def test_missing_title_inserted_first(self):
        ws = Workspace(self)
        rel = "atlas/people/jane-doe.md"
        ws.write(rel, "---\nname: Jane Doe\naliases:\n- J. Doe\n---\n\n# Jane Doe\n")
        run(align_entity_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel),
                         "---\ntitle: Jane Doe\nname: Jane Doe\naliases:\n- J. Doe\n---\n\n# Jane Doe\n")

    def test_folded_identity_is_read_whole(self):
        ws = Workspace(self)
        rel = "atlas/topics/long.md"
        ws.write(rel, "---\ntitle: Long\nname: A very long topic name that Basic Memory folded over\n"
                      "  two lines\n---\n")
        run(align_entity_titles.main, ["--apply"], root=ws.root)
        self.assertEqual(F.parse(block_of(ws.read(rel))).get("title"),
                         "A very long topic name that Basic Memory folded over two lines")

    def test_dry_run_writes_nothing(self):
        ws = Workspace(self)
        rel = "sources/clients/initech/CLAUDE.md"
        ws.write(rel, FOLDED)
        out = run(align_entity_titles.main, [], root=ws.root)
        self.assertEqual(ws.read(rel), FOLDED)
        self.assertIn("1 to fix", out)


class NeedsRepair(unittest.TestCase):
    """A `title:` is replaced only when its range reads as one title."""

    def apply(self, text: str) -> str:
        self.ws = Workspace(self)
        self.rel = "sources/clients/globex/CLAUDE.md"
        self.ws.write(self.rel, text)
        return run(align_entity_titles.main, ["--apply"], root=self.ws.root)

    def test_open_quoted_title_is_never_rewritten(self):
        for key in ("sq", "dq"):
            text = DAMAGED[key].replace("type: meeting", "type: client-context").replace(
                "\n---\n\n#", "\nclient: Globex\n---\n\n#")
            out = self.apply(text)
            self.assertEqual(self.ws.read(self.rel), text, key)
            self.assertIn(f"{HEADER} (1):", out)
            self.assertIn(self.rel, out)
            self.assertIn("0 to fix", out)

    def test_sane_title_below_damage_is_replaced_alone(self):
        for key, title in (("indented", "Indented"), ("block", "Block")):
            text = DAMAGED[key].replace("\n---\n\n#", "\nclient: Globex\n---\n\n#")
            self.apply(text)
            self.assertEqual(self.ws.read(self.rel), text.replace(f"title: {title}", "title: Globex"), key)

    def test_duplicate_title_is_not_collapsed(self):
        text = "---\ntitle: Old\nclient: Globex\ntitle: Kept\n---\n\n# Globex\n"
        out = self.apply(text)
        self.assertEqual(self.ws.read(self.rel), text)
        self.assertIn(f"{HEADER} (1):", out)


if __name__ == "__main__":
    unittest.main()
