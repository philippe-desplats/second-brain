#!/usr/bin/env python3
"""Tests for `audit_field_usage.py`, run on a throwaway workspace.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import FOLDED_TITLE_LINES, WorkspaceCase  # noqa: E402


class Lists(WorkspaceCase):
    def tags_filled(self):
        out = self.ws.run("audit_field_usage.py", "--type", "note", "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)["report"]["note"]
        return report["note_count"], report["fields"]["tags"]["filled"]

    def write(self, tags_block):
        self.ws.write("sources/internal/ops/2026-07-02-note-a.md",
                      "---\ntitle: A\ntype: note\nschema_version: 1\ndate: 2026-07-02\ntags:\n"
                      + tags_block + "---\n\nBody\n")

    def test_every_indent_width_counts(self):
        for block in ("- a\n", "  - a\n", "    - a\n", "\t- a\n", "  -   a\n"):
            self.write(block)
            self.assertEqual(self.tags_filled(), (1, 1), repr(block))

    def test_empty_list_is_not_filled(self):
        self.ws.write("sources/internal/ops/2026-07-02-note-a.md",
                      "---\ntitle: A\ntype: note\ntags: []\n---\n")
        self.assertEqual(self.tags_filled(), (1, 0))

    def test_crlf_and_folded_title(self):
        text = ("---\n" + FOLDED_TITLE_LINES + "type: note\ntags:\n    - a\n---\n").replace("\n", "\r\n")
        self.ws.write("sources/internal/ops/2026-07-02-note-a.md", text)
        self.assertEqual(self.tags_filled(), (1, 1))

    def test_continuation_line_is_not_a_key(self):
        # A folded title's second line must never surface as an undeclared field.
        self.ws.write("sources/internal/ops/2026-07-02-note-a.md",
                      "---\ntitle: A long title that goes on\n  plan: for Q3\ntype: note\n---\n")
        out = self.ws.run("audit_field_usage.py", "--type", "note", "--json")
        self.assertEqual(json.loads(out.stdout)["undeclared"], [])


class Corpus(WorkspaceCase):
    """The audit walks the corpus `corpus.py` defines, like every other pass."""

    def untyped(self):
        out = self.ws.run("audit_field_usage.py", "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)["notes_without_type"]

    def test_machine_consumed_folders_are_not_notes(self):
        base = "sources/clients/acme/website/"
        for folder in ("prompts", "captures", "repo-files"):
            self.ws.write(base + folder + "/file.md", "---\nsource: verbatim\n---\n\nText\n")
        self.ws.write(base + "2026-07-02-note-real.md", "---\ntitle: Real\n---\n\nBody\n")
        self.assertEqual(self.untyped(), [base + "2026-07-02-note-real.md"])

    def test_skill_state_file_is_not_a_note(self):
        self.ws.write("sources/internal/ops/session.md", "---\ntask_id: 3\n---\n")
        self.ws.write("sources/internal/ops/skills/step.md", "---\nstep: 1\n---\n")
        self.assertEqual(self.untyped(), [])


if __name__ == "__main__":
    unittest.main()
