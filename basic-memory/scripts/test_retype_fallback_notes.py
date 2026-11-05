#!/usr/bin/env python3
"""Tests for `retype_fallback_notes.py`.

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
import retype_fallback_notes  # noqa: E402
from test_retype_files import DAMAGED, Workspace, block_of, run, yaml  # noqa: E402

# As Basic Memory writes it: column-0 list, blank line before the body.
RESEARCH = "---\ntitle: Vendors\ntype: note\ntags:\n- a\n- b\n---\n\n# Vendors\n"


class Fallback(unittest.TestCase):
    def test_opening_delimiter_kept(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-02-research-vendors.md"
        ws.write(rel, RESEARCH)
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), RESEARCH.replace("type: note", "type: research"))
        if yaml is not None:
            self.assertEqual(yaml.safe_load(block_of(ws.read(rel)))["type"], "research")

    def test_second_run_changes_nothing(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-02-research-vendors.md"
        ws.write(rel, RESEARCH)
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        first = ws.read(rel)
        out = run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), first)
        self.assertIn("Files with type: note found: 0", out)

    def test_knowledge_note_with_subtype_is_kept(self):
        ws = Workspace(self)
        rel = "knowledge/business/guide-pricing-plan-landing.md"
        text = "---\ntitle: Pricing plan guide\ntype: note\nsubtype: guide\n---\n\n# Guide\n"
        ws.write(rel, text)
        out = run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), text)
        self.assertIn("[       note] " + rel, out)

    def test_word_after_date_wins(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-04-note-plan-q3.md"
        text = "---\ntitle: Plan Q3\ntype: note\n---\n"
        ws.write(rel, text)
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), text)

    def test_agrees_with_retype_files(self):
        ws = Workspace(self)
        rel = "sources/clients/globex/web/meetings/2026-01-01-research-audit.md"
        ws.write(rel, "---\ntitle: Audit\ntype: note\n---\n")
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(F.parse(block_of(ws.read(rel))).get("type"), "meeting")

    def test_dry_run_writes_nothing(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-02-research-vendors.md"
        ws.write(rel, RESEARCH)
        out = run(retype_fallback_notes.main, ["--dry-run"], root=ws.root)
        self.assertEqual(ws.read(rel), RESEARCH)
        self.assertIn("[   research] " + rel, out)

    def test_crlf_note_keeps_its_line_endings(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-02-research-vendors.md"
        path = ws.root / rel
        path.parent.mkdir(parents=True)
        path.write_bytes(RESEARCH.replace("\n", "\r\n").encode())
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(path.read_bytes(),
                         RESEARCH.replace("type: note", "type: research").replace("\n", "\r\n").encode())


class NeedsRepair(unittest.TestCase):
    HEADER = "Needs repair, run check_frontmatter_damage.py"

    def test_damaged_shapes_are_never_rewritten(self):
        ws = Workspace(self)
        notes = {f"sources/internal/ops/2026-07-01-research-{k}.md": v.replace("type: meeting", "type: note")
                 for k, v in DAMAGED.items()}
        for rel, text in notes.items():
            ws.write(rel, text)
        run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        for rel, text in notes.items():
            self.assertEqual(ws.read(rel), text, rel)

    def test_duplicate_type_is_not_collapsed(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-07-01-research-dup.md"
        text = "---\ntype: note\ntitle: Dup\ntype: strategy\n---\nBody\n"
        ws.write(rel, text)
        out = run(retype_fallback_notes.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), text)
        self.assertIn(f"{self.HEADER} (1):", out)
        self.assertIn(rel, out)


if __name__ == "__main__":
    unittest.main()
