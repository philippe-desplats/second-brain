#!/usr/bin/env python3
"""Tests for `check_orphans.py`, run on a throwaway workspace.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import FOLDED_TITLE_LINES, LONG_TITLE, WorkspaceCase, note  # noqa: E402


class Orphans(WorkspaceCase):
    def orphans(self):
        out = self.ws.run("check_orphans.py")
        self.assertEqual(out.returncode, 0, out.stderr)
        return [ln for ln in out.stdout.splitlines()[2:] if ln]

    def test_topic_reached_through_alias(self):
        self.ws.write("atlas/topics/client-onboarding.md", note(
            "title: Client Onboarding\ntype: topic\naliases:\n- onboarding\n", "# Client Onboarding\n"))
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "About [[onboarding]].\n"))
        self.assertEqual(self.orphans(), [])

    def test_folded_title_read_whole(self):
        self.ws.write("sources/internal/redesign/2026-07-01-note-plan.md",
                      "---\n" + FOLDED_TITLE_LINES + "type: note\n---\n\n# Plan\n")
        self.ws.write("sources/internal/redesign/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", f"See [[{LONG_TITLE}]].\n"))
        self.assertEqual(self.orphans(), [])

    def test_link_escaped_for_a_table_cell_reaches_its_target(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-plan.md",
                      note("title: Plan\ntype: note\n", "# Plan\n"))
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "| a | [[Plan\\|the plan]] |\n"))
        self.assertEqual(self.orphans(), [])

    def test_unlinked_note_is_an_orphan(self):
        self.ws.write("sources/internal/ops/2026-07-02-note-lonely.md",
                      note("title: Lonely\ntype: note\n", "Nothing here.\n"))
        self.assertEqual(self.orphans(), ["sources/internal/ops/2026-07-02-note-lonely.md"])

    def test_root_structural_files_are_never_orphans(self):
        for name in ("AGENTS.md", "CLAUDE.md", "README.md"):
            self.ws.write(name, "# Root\n")
        self.assertEqual(self.orphans(), [])

    def test_zone_readme_stays_exempt_while_entity_agents_md_is_a_note(self):
        for zone in ("atlas", "sources", "knowledge", "inbox"):
            self.ws.write(zone + "/README.md", "# Zone\n")
        self.ws.write("sources/clients/x/AGENTS.md",
                      note("title: X\nclient: X\ntype: client-context\n", "# X\n"))
        self.assertEqual(self.orphans(), ["sources/clients/x/AGENTS.md"])

    def test_entity_and_project_agents_md_are_checked(self):
        self.ws.write("sources/clients/globex/AGENTS.md",
                      note("title: Globex\nclient: Globex\ntype: client-context\n", "# Globex\n"))
        self.ws.write("sources/clients/globex/web/AGENTS.md",
                      note("title: Globex Web\ntype: project-brief\n", "# Web\n"))
        self.ws.write("sources/internal/pricing/CLAUDE.md",
                      note("title: Pricing\ntype: project-brief\n", "# Pricing\n"))
        self.assertEqual(self.orphans(), ["sources/clients/globex/AGENTS.md",
                                          "sources/clients/globex/web/AGENTS.md",
                                          "sources/internal/pricing/CLAUDE.md"])

    def test_agents_segment_copy_of_the_skills_is_ignored(self):
        self.ws.write(".agents/skills/demo/notes.md", "# Copy\n")
        self.assertEqual(self.orphans(), [])

    def test_journal_skipped_in_block_form(self):
        self.ws.write("sources/personal/journal/2026-07-02-note-journal.md",
                      note("title: Journal\ntype: note\nnote_type: 'journal'\n", "Today.\n"))
        self.assertEqual(self.orphans(), [])


if __name__ == "__main__":
    unittest.main()
