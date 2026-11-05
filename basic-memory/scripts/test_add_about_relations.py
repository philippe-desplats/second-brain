#!/usr/bin/env python3
"""Tests for add_about_relations.py, standard library only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import add_about_relations as about  # noqa: E402

MEETING = "---\ntitle: Kickoff\ntype: meeting\n---\n\n# Kickoff\n\nNotes.\n"


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.write("sources/clients/acme/CLAUDE.md",
                   "---\ntitle: Acme\nclient: Acme\ntype: client-context\n---\n\n# Acme\n")
        self.write("sources/partners/initech/CLAUDE.md",
                   "---\ntitle: Initech\npartner: Initech\ntype: partner-context\n---\n\n# Initech\n")

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def config(self, organization):
        self.write(".sb-config.json", json.dumps({"schema": "sb-config/v1",
                                                  "organization": organization}))

    def results(self, apply=False):
        _entities, results = about.run(self.root, apply)
        return {rel: (status, msg) for rel, status, msg in results}


class Scope(Workspace):
    def test_emails_and_meetings_of_every_zone_are_targets(self):
        wanted = [
            "sources/clients/acme/site/emails/2026-01-01-01-in-hello.md",
            "sources/clients/acme/site/meetings/2026-01-01-meeting-kickoff.md",
            "sources/internal/pricing/meetings/2026-01-01-meeting-review.md",
            "sources/partners/initech/resale/emails/2026-01-01-01-out-offer.md",
            "sources/personal/learning/meetings/2026-01-01-meeting-mentor.md",
        ]
        for rel in wanted:
            self.write(rel, MEETING)
        targets = [rel for _path, rel, _slug in about.find_target_files(self.root)]
        self.assertEqual(sorted(targets), sorted(wanted))

    def test_other_note_types_are_left_alone(self):
        for rel in ("sources/clients/acme/site/README.md",
                    "sources/clients/acme/site/2026-01-01-research-audit.md",
                    "sources/clients/acme/site/deliverables/2026-01-01-contract.md",
                    "sources/clients/acme/site/sessions/2026-01-01-session-a.md",
                    "sources/personal/learning/README.md"):
            self.write(rel, MEETING)
        self.assertEqual(about.find_target_files(self.root), [])

    def test_folders_corpus_excludes_are_never_written(self):
        for rel in ("sources/clients/acme/captures/emails/2026-01-01-01-in-page.md",
                    "sources/clients/acme/repo-files/meetings/2026-01-01-meeting-x.md",
                    "sources/internal/prompts/meetings/2026-01-01-meeting-p.md",
                    "sources/internal/tmp/meetings/2026-01-01-meeting-t.md",
                    "sources/partners/initech/skills/emails/2026-01-01-01-in-s.md"):
            self.write(rel, MEETING)
        self.config("Studio")
        self.assertEqual(about.find_target_files(self.root), [])
        self.assertEqual(self.results(apply=True), {})


class Resolution(Workspace):
    def test_client_meeting_gets_the_client(self):
        path = self.write("sources/clients/acme/site/meetings/2026-01-01-meeting-k.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("## Relations\n\n- about [[Acme]]\n", path.read_text(encoding="utf-8"))

    def test_internal_notes_are_skipped_while_organization_is_null(self):
        self.config(None)
        path = self.write("sources/internal/pricing/meetings/2026-01-01-meeting-r.md", MEETING)
        results = self.results(apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"), MEETING)
        status, _msg = results["sources/internal/pricing/meetings/2026-01-01-meeting-r.md"]
        self.assertEqual(status, "skip")

    def test_internal_notes_are_skipped_without_a_config_file(self):
        path = self.write("sources/internal/pricing/meetings/2026-01-01-meeting-r.md", MEETING)
        about.run(self.root, apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"), MEETING)

    def test_internal_notes_get_the_organization(self):
        self.config("Studio Nord")
        path = self.write("sources/internal/pricing/meetings/2026-01-01-meeting-r.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Studio Nord]]\n", path.read_text(encoding="utf-8"))

    def test_folded_personal_project_title_is_read_whole(self):
        self.write("sources/personal/learning/README.md",
                   "---\ntitle: Learning Rust the slow way, a personal project about systems"
                   " programming and patience\n  for real\ntype: project-brief\n---\n\n# L\n")
        path = self.write("sources/personal/learning/meetings/2026-01-01-meeting-m.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Learning Rust the slow way, a personal project about systems"
                      " programming and patience for real]]\n",
                      path.read_text(encoding="utf-8"))

    def test_quoted_entity_name_is_decoded(self):
        self.write("sources/clients/globex/CLAUDE.md",
                   "---\ntitle: 'Globex: Industrial'\nclient: 'Globex: Industrial'\n"
                   "type: client-context\n---\n")
        path = self.write("sources/clients/globex/site/emails/2026-01-01-01-in-a.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Globex: Industrial]]\n", path.read_text(encoding="utf-8"))

    def test_unknown_entity_is_an_error(self):
        self.write("sources/clients/ghost/site/emails/2026-01-01-01-in-a.md", MEETING)
        status, _msg = self.results()["sources/clients/ghost/site/emails/2026-01-01-01-in-a.md"]
        self.assertEqual(status, "error")


class Writing(Workspace):
    def test_frontmatter_and_blank_line_are_kept_and_second_run_is_a_no_op(self):
        rel = "sources/clients/acme/site/meetings/2026-01-01-meeting-k.md"
        path = self.write(rel, MEETING)
        about.run(self.root, apply=True)
        once = path.read_text(encoding="utf-8")
        self.assertEqual(once, MEETING + "\n## Relations\n\n- about [[Acme]]\n")
        self.assertEqual(self.results(apply=True)[rel][0], "skip")
        self.assertEqual(path.read_text(encoding="utf-8"), once)

    def test_dry_run_writes_nothing(self):
        path = self.write("sources/clients/acme/site/meetings/2026-01-01-meeting-k.md", MEETING)
        self.assertEqual(self.results(apply=False)[
            "sources/clients/acme/site/meetings/2026-01-01-meeting-k.md"][0], "ok")
        self.assertEqual(path.read_text(encoding="utf-8"), MEETING)

    def test_relation_goes_before_observations(self):
        text = MEETING + "\n## Observations\n\n- [decision] Go\n"
        path = self.write("sources/clients/acme/site/meetings/2026-01-01-meeting-k.md", text)
        about.run(self.root, apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         MEETING + "\n## Relations\n\n- about [[Acme]]\n\n"
                                   "## Observations\n\n- [decision] Go\n")

    def test_note_without_frontmatter_keeps_its_text(self):
        path = self.write("sources/clients/acme/site/emails/2026-01-01-01-in-a.md", "# Hello\n")
        about.run(self.root, apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         "# Hello\n\n## Relations\n\n- about [[Acme]]\n")


if __name__ == "__main__":
    unittest.main()
