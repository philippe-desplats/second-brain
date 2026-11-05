#!/usr/bin/env python3
"""Tests for `check_consistency.py`, run on a throwaway workspace.

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

from test_check_helpers import (FOLDED_TITLE_LINES, LONG_TITLE, TRUNCATED_TITLE,  # noqa: E402
                                WorkspaceCase, note)

import check_consistency  # noqa: E402

TOPIC = note("""
    title: Client Onboarding
    name: Client Onboarding
    type: topic
    schema_version: 1
    aliases:
    - onboarding
    """, "# Client Onboarding\n")


class Links(WorkspaceCase):
    def findings(self, only):
        out = self.ws.run("check_consistency.py", "--only", only, "--json")
        return out, json.loads(out.stdout)["findings"]

    def write_long(self):
        self.ws.write("sources/internal/redesign/2026-07-01-note-plan.md",
                      "---\n" + FOLDED_TITLE_LINES + "type: note\nschema_version: 1\n---\n\n# Plan\n")

    def test_link_to_a_folded_title_resolves(self):
        self.write_long()
        self.ws.write("sources/internal/redesign/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", f"See [[{LONG_TITLE}]].\n"))
        out, findings = self.findings("links")
        self.assertEqual(findings, [], out.stdout)
        self.assertEqual(out.returncode, 0)

    def test_link_to_a_truncated_title_is_dead(self):
        self.write_long()
        self.ws.write("sources/internal/redesign/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", f"See [[{TRUNCATED_TITLE}]].\n"))
        out, findings = self.findings("links")
        self.assertEqual(len(findings), 1, out.stdout)
        self.assertEqual(out.returncode, 1)

    def test_link_escaped_for_a_table_cell_resolves(self):
        self.write_long()
        self.ws.write("sources/internal/redesign/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", f"| plan | [[{LONG_TITLE}\\|the plan]] |\n"))
        out, findings = self.findings("links")
        self.assertEqual(findings, [], out.stdout)

    def test_alias_in_block_list_resolves(self):
        self.ws.write("atlas/topics/client-onboarding.md", TOPIC)
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "About [[onboarding|the onboarding]].\n"))
        _, findings = self.findings("links")
        self.assertEqual(findings, [])

    def test_identity_key_still_accepted(self):
        # Documented permissiveness: `client:` resolves in this check.
        self.ws.write("sources/clients/globex/CLAUDE.md",
                      note("title: Globex\nclient: Globex Corporation\ntype: client-context\n"))
        self.ws.write("sources/clients/globex/web/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "For [[Globex Corporation]].\n"))
        _, findings = self.findings("links")
        self.assertEqual(findings, [])


class Topics(WorkspaceCase):
    def findings(self):
        out = self.ws.run("check_consistency.py", "--only", "topics", "--json")
        return out, json.loads(out.stdout)["findings"]

    def setUp(self):
        super().setUp()
        self.ws.write("atlas/topics/client-onboarding.md", TOPIC)

    def test_bogus_slug_in_block_list_warns(self):
        self.ws.write("sources/internal/ops/README.md",
                      note("title: Ops\ntype: project-brief\ntopics:\n- client-onboarding\n- bogus-slug\n"))
        out, findings = self.findings()
        self.assertEqual([f["issue"].split("`")[3] for f in findings], ["bogus-slug"], out.stdout)
        self.assertEqual(findings[0]["severity"], "warning")
        self.assertEqual(out.returncode, 0)

    def test_bogus_slug_inline_warns_the_same(self):
        self.ws.write("sources/internal/ops/README.md",
                      note("title: Ops\ntype: project-brief\ntopics: [client-onboarding, bogus-slug]\n"))
        _, inline = self.findings()
        self.ws.write("sources/internal/ops/README.md",
                      note("title: Ops\ntype: project-brief\ntopics:\n  - client-onboarding\n  - bogus-slug\n"))
        _, block = self.findings()
        self.assertEqual(inline, block)
        self.assertEqual(len(inline), 1)

    def test_known_slugs_are_silent(self):
        self.ws.write("sources/internal/ops/README.md",
                      note("title: Ops\ntype: project-brief\ntopics:\n- client-onboarding\n"))
        _, findings = self.findings()
        self.assertEqual(findings, [])


class Templates(WorkspaceCase):
    def findings(self):
        out = self.ws.run("check_consistency.py", "--only", "templates", "--json")
        return json.loads(out.stdout)["findings"]

    def skill(self, front):
        self.ws.write(".claude/skills/demo/SKILL.md",
                      "# Demo\n\n```markdown\n---\n" + front + "---\n\n# Body\n```\n")

    def test_placeholder_type_is_skipped(self):
        self.skill("title: {Name}\ntype: {note|meeting}\nschema_version: 1\n")
        self.assertEqual(self.findings(), [])

    def test_missing_schema_version_reported(self):
        self.skill("title: {Name}\ntype: note\ndate: 2026-07-02\n")
        issues = [f["issue"] for f in self.findings()]
        self.assertEqual(issues, ["`type: note` example omits `schema_version`"])

    def test_untyped_identity_example_reported(self):
        self.skill("title: {Name}\ndate: 2026-07-02\n")
        self.assertEqual(len(self.findings()), 1)

    def test_unknown_field_reported(self):
        self.skill("title: {Name}\ntype: note\nschema_version: 1\nbogus_field: x\n")
        issues = [f["issue"] for f in self.findings()]
        self.assertEqual(len(issues), 1)
        self.assertIn("bogus_field", issues[0])


class Docstring(unittest.TestCase):
    def test_counts_its_classes(self):
        doc = check_consistency.__doc__
        self.assertIn("Four defect classes", doc)
        self.assertIn("    4. ", doc)
        self.assertNotIn("    5. ", doc)


if __name__ == "__main__":
    unittest.main()
