#!/usr/bin/env python3
"""Tests for `retype_files.py` and the shared table of `note_types.py`.

Inputs are shaped the way Basic Memory writes them (`yaml.dump`, column-0
lists) plus the indented lists humans and Obsidian write. Every written block
is re-read with PyYAML when it is importable.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import frontmatter as F  # noqa: E402
import retype_files  # noqa: E402
from note_types import NOTE_TYPES, classify  # noqa: E402

try:
    import yaml
except ImportError:  # the stdlib-only interpreter
    yaml = None


def run(main, *args, **kwargs) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main(*args, **kwargs)
    return out.getvalue()


class Workspace:
    """A throwaway workspace root holding the notes a test writes."""

    def __init__(self, test: unittest.TestCase):
        self._tmp = tempfile.TemporaryDirectory()
        test.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")


# The 4 shapes the 0.5.3 `retype_files.py` left behind: it inserted `type:`
# after the first line of the first field, inside a folded quoted title, a
# list or a block scalar. A parser then reads the indented lines that follow
# as part of `type:`, so replacing that field deletes them.
DAMAGED = {
    "sq": ("---\ntitle: 'Atelier : l''inventaire des contenus et la feuille de route pour le trimestre\n"
           "type: meeting\n  prochain, version longue'\ndate: 2026-07-01\n---\n\n# A\n"),
    "dq": ('---\ntitle: "Kickoff \\\\ backslash and a long title that BM folds past the eighty column limit\n'
           'type: meeting\n  for sure"\n---\n\n# D\n'),
    "indented": "---\ntags:\ntype: meeting\n  - a\n  - b\ntitle: Indented\n---\n\n# I\n",
    "block": "---\nnotes: |\ntype: meeting\n  one\n  two\ntitle: Block\n---\n\n# B\n",
}


def block_of(text: str) -> str:
    doc = F.split(text)
    assert doc is not None, text
    return doc.block


class Classify(unittest.TestCase):
    def test_word_after_date_wins_over_keywords(self):
        self.assertEqual(classify("sources/internal/ops/2026-01-04-note-plan-q3.md"), "note")
        self.assertEqual(classify("sources/internal/ops/2026-01-04-research-audit.md"), "research")
        self.assertEqual(classify("sources/internal/ops/2026-01-04-kickoff-plan.md"), "strategy")

    def test_folder_forces_its_type(self):
        self.assertEqual(classify("sources/clients/globex/web/meetings/2026-01-01-research-audit.md"),
                         "meeting")
        self.assertEqual(classify("sources/clients/globex/web/clippings/page.md"), "clipping")
        self.assertEqual(classify("sources/clients/globex/web/sessions/2026-01-01-note-x.md"), "session")
        self.assertEqual(classify("sources/clients/globex/web/proposals/offer.md"), "deliverable")

    def test_context_files(self):
        self.assertEqual(classify("sources/clients/globex/CLAUDE.md"), "client-context")
        self.assertEqual(classify("sources/partners/proseware/CLAUDE.md"), "partner-context")
        self.assertEqual(classify("sources/clients/globex/web/README.md"), "project-brief")
        self.assertIsNone(classify("sources/internal/CONTEXT.md"))

    def test_knowledge_subtype_is_never_retyped(self):
        rel = "knowledge/business/guide-pricing-plan-landing.md"
        self.assertIsNone(classify(rel, "guide"))
        self.assertEqual(classify(rel), "strategy")

    def test_email_sequence_outside_folder(self):
        self.assertEqual(classify("sources/clients/globex/web/2026-01-01-02-out-kickoff.md"), "email")


class InsertType(unittest.TestCase):
    """M1: a missing `type:` lands after a complete field, never inside a list."""

    CASES = {
        "column-0 list": "---\ntags:\n- x\n- y\ntitle: Kickoff\n---\n\n# Kickoff\n",
        "indented list": "---\ntags:\n  - x\n  - y\ntitle: Kickoff\n---\n\n# Kickoff\n",
        "no title": "---\ntags:\n- x\n- y\nstatus: active\naliases:\n- a\n---\n\n# Kickoff\n",
        "folded title": ("---\ntitle: Globex Website Redesign, discovery workshop outcomes and the"
                         " content inventory\n  plan for Q3\ntags:\n- x\n---\n\n# K\n"),
    }

    def test_every_shape(self):
        for label, text in self.CASES.items():
            with self.subTest(label):
                ws = Workspace(self)
                rel = "sources/internal/ops/2026-01-03-meeting-kickoff.md"
                ws.write(rel, text)
                run(retype_files.main, ["--apply"], root=ws.root)
                written = ws.read(rel)
                fm = F.parse(block_of(written))
                self.assertEqual(fm.get("type"), "meeting")
                original = F.parse(block_of(text))
                for key in original.keys():
                    self.assertEqual(fm.get(key), original.get(key), key)
                if "title" in original:
                    self.assertEqual(fm.fields[fm.keys().index("title") + 1].key, "type")
                if yaml is not None:
                    data = yaml.safe_load(block_of(written))
                    self.assertEqual(data["type"], "meeting")
                    self.assertEqual(data["tags"], original.get("tags"))
                self.assertTrue(written.endswith("\n# Kickoff\n") or written.endswith("\n# K\n"))

    def test_second_run_changes_nothing(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-03-meeting-kickoff.md"
        ws.write(rel, self.CASES["column-0 list"])
        run(retype_files.main, ["--apply"], root=ws.root)
        first = ws.read(rel)
        out = run(retype_files.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), first)
        self.assertIn("Updated: 0", out)
        self.assertIn("Already correct: 1", out)

    def test_existing_type_replaced_in_place(self):
        ws = Workspace(self)
        rel = "sources/clients/globex/web/meetings/notes.md"
        ws.write(rel, "---\ntitle: Notes\ntype: research\ntags:\n- x\n---\nBody\n")
        run(retype_files.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), "---\ntitle: Notes\ntype: meeting\ntags:\n- x\n---\nBody\n")

    def test_clippings_and_sessions_force_their_type(self):
        ws = Workspace(self)
        ws.write("sources/internal/ops/clippings/page.md", "---\ntitle: Page\ntype: research\n---\n")
        ws.write("sources/internal/ops/sessions/2026-01-01-session-x.md",
                 "---\ntitle: S\ntype: strategy\n---\n")
        run(retype_files.main, ["--apply"], root=ws.root)
        self.assertIn("type: clipping", ws.read("sources/internal/ops/clippings/page.md"))
        self.assertIn("type: session", ws.read("sources/internal/ops/sessions/2026-01-01-session-x.md"))

    def test_dry_run_writes_nothing(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/2026-01-03-meeting-kickoff.md"
        ws.write(rel, self.CASES["column-0 list"])
        out = run(retype_files.main, ["--dry-run"], root=ws.root)
        self.assertEqual(ws.read(rel), self.CASES["column-0 list"])
        self.assertIn("Would update: 1", out)

    def test_excluded_folders_are_never_written(self):
        ws = Workspace(self)
        rel = "sources/internal/ops/prompts/2026-01-03-meeting-kickoff.md"
        ws.write(rel, self.CASES["column-0 list"])
        run(retype_files.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), self.CASES["column-0 list"])


class NeedsRepair(unittest.TestCase):
    """A `type:` the pass did not write is replaced only when it reads as one."""

    HEADER = "Needs repair, run check_frontmatter_damage.py"

    def apply(self, notes: dict) -> str:
        ws = Workspace(self)
        for rel, text in notes.items():
            ws.write(rel, text)
        out = run(retype_files.main, ["--apply"], root=ws.root)
        for rel, text in notes.items():
            self.assertEqual(ws.read(rel), text, rel)
        return out

    def test_damaged_shapes_are_never_rewritten(self):
        notes = {f"sources/clients/globex/web/meetings/2026-07-01-meeting-{k}.md": v
                 for k, v in DAMAGED.items()}
        out = self.apply(notes)
        self.assertIn(f"{self.HEADER} (4):", out)
        for rel in notes:
            self.assertIn(rel, out)
        self.assertIn("Updated: 0", out)

    def test_damaged_shapes_outside_a_container_are_reported(self):
        notes = {f"sources/internal/ops/2026-07-01-meeting-{k}.md": v for k, v in DAMAGED.items()}
        out = self.apply(notes)
        self.assertIn(f"{self.HEADER} (4):", out)

    def test_unknown_type_is_not_replaced(self):
        out = self.apply({"sources/clients/globex/web/meetings/notes.md":
                          "---\ntitle: Notes\ntype: memo\n---\nBody\n"})
        self.assertIn(f"{self.HEADER} (1):", out)
        self.assertIn("memo", out)

    def test_duplicate_type_is_not_collapsed(self):
        out = self.apply({"sources/clients/globex/web/meetings/notes.md":
                          "---\ntype: note\ntitle: Notes\ntype: research\n---\nBody\n"})
        self.assertIn(f"{self.HEADER} (1):", out)

    def test_type_is_not_inserted_into_an_open_title(self):
        out = self.apply({"sources/clients/globex/web/meetings/notes.md":
                          "---\ntitle: 'Open quote, never closed\ndate: 2026-07-01\n---\nBody\n"})
        self.assertIn(f"{self.HEADER} (1):", out)

    def test_flow_list_swallowing_a_key_line_blocks_the_note(self):
        out = self.apply({"sources/clients/globex/web/meetings/notes.md":
                          '---\ntitle: Notes\ntags: ["a\ntype: note\n  b"]\n---\nBody\n'})
        self.assertIn(f"{self.HEADER} (1):", out)
        self.assertIn("swallows the key line `type: note`", out)

    def test_key_line_inside_an_indented_block_is_content(self):
        ws = Workspace(self)
        rel = "sources/clients/globex/web/meetings/notes.md"
        ws.write(rel, "---\ntitle: Notes\nnotes: |\n  type: x\n  key: v\n---\nBody\n")
        out = run(retype_files.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel),
                         "---\ntitle: Notes\ntype: meeting\nnotes: |\n  type: x\n  key: v\n---\nBody\n")
        self.assertNotIn(self.HEADER, out)

    def test_healthy_notes_are_still_updated(self):
        ws = Workspace(self)
        rel = "sources/clients/globex/web/meetings/notes.md"
        ws.write(rel, "---\ntitle: 'Notes: kickoff'\ntype: 'note'\n---\nBody\n")
        out = run(retype_files.main, ["--apply"], root=ws.root)
        self.assertEqual(ws.read(rel), "---\ntitle: 'Notes: kickoff'\ntype: meeting\n---\nBody\n")
        self.assertNotIn(self.HEADER, out)


class NoteTypes(unittest.TestCase):
    def test_known_types_are_the_schemas(self):
        schemas = HERE.parent / "schemas"
        names = {p.stem for p in schemas.glob("*.md") if p.stem != "README"}
        self.assertEqual(set(NOTE_TYPES), names)


if __name__ == "__main__":
    unittest.main()
