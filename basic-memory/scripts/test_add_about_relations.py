#!/usr/bin/env python3
"""Tests for add_about_relations.py, standard library only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import io
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


def brief(title: str, type_line: str = "type: project-brief\n") -> str:
    return f"---\ntitle: {title}\n{type_line}schema_version: 1\n---\n\n# Brief\n"


class Resolution(Workspace):
    """The link names the project brief of the note's folder, never the entity."""

    def test_client_meeting_gets_its_project(self):
        self.write("sources/clients/acme/site/README.md", brief("Acme Site Redesign"))
        path = self.write("sources/clients/acme/site/meetings/2026-01-01-meeting-k.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("## Relations\n\n- about [[Acme Site Redesign]]\n", path.read_text(encoding="utf-8"))

    def test_partner_email_gets_its_project(self):
        self.write("sources/partners/initech/resale/README.md", brief("Initech Resale"))
        path = self.write("sources/partners/initech/resale/emails/2026-01-01-01-out-offer.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Initech Resale]]\n", path.read_text(encoding="utf-8"))

    def test_internal_meeting_gets_its_project_whatever_the_organization(self):
        self.config("Studio Nord")
        self.write("sources/internal/pricing/README.md", brief("Pricing 2026"))
        path = self.write("sources/internal/pricing/meetings/2026-01-01-meeting-r.md", MEETING)
        about.run(self.root, apply=True)
        text = path.read_text(encoding="utf-8")
        self.assertIn("- about [[Pricing 2026]]\n", text)
        self.assertNotIn("Studio Nord", text)

    def test_folded_project_title_is_read_whole(self):
        self.write("sources/personal/learning/README.md",
                   "---\ntitle: Learning Rust the slow way, a personal project about systems"
                   " programming and patience\n  for real\ntype: project-brief\n---\n\n# L\n")
        path = self.write("sources/personal/learning/meetings/2026-01-01-meeting-m.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Learning Rust the slow way, a personal project about systems"
                      " programming and patience for real]]\n",
                      path.read_text(encoding="utf-8"))

    def test_quoted_project_title_is_decoded(self):
        self.write("sources/clients/acme/site/README.md", brief("'Site: l''atelier'"))
        path = self.write("sources/clients/acme/site/emails/2026-01-01-01-in-a.md", MEETING)
        about.run(self.root, apply=True)
        self.assertIn("- about [[Site: l'atelier]]\n", path.read_text(encoding="utf-8"))


class MissingBrief(Workspace):
    """A note whose project has no usable brief gets nothing and is reported."""

    REL = "sources/clients/acme/site/meetings/2026-01-01-meeting-k.md"

    def outcome(self):
        path = self.write(self.REL, MEETING)
        status, msg = self.results(apply=True)[self.REL]
        self.assertEqual(path.read_text(encoding="utf-8"), MEETING)
        return status, msg

    def test_folder_without_a_readme(self):
        self.assertEqual(self.outcome(), ("no-brief", "no project brief at `sources/clients/acme/site/README.md`"))

    def test_readme_that_is_not_a_project_brief(self):
        self.write("sources/clients/acme/site/README.md", brief("Site", type_line=""))
        status, msg = self.outcome()
        self.assertEqual(status, "no-brief")
        self.assertIn("does not declare `type: project-brief`", msg)

    def test_brief_without_a_title(self):
        self.write("sources/clients/acme/site/README.md", "---\ntype: project-brief\n---\n\n# Site\n")
        status, msg = self.outcome()
        self.assertEqual(status, "no-brief")
        self.assertIn("no usable `title:`", msg)

    def test_main_prints_every_note_without_a_brief(self):
        self.write(self.REL, MEETING)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            about.report(*about.run(self.root, apply=False), apply=False)
        self.assertIn("[NO BRIEF] %s  no project brief at" % self.REL, buf.getvalue())
        self.assertIn("1 without a project brief", buf.getvalue())


class Writing(Workspace):
    def setUp(self):
        super().setUp()
        self.write("sources/clients/acme/site/README.md",
                   "---\ntitle: Acme Site\naliases: [Acme Site, the site]\ntype: project-brief\n---\n\n# S\n")

    def test_frontmatter_and_blank_line_are_kept_and_second_run_is_a_no_op(self):
        rel = "sources/clients/acme/site/meetings/2026-01-01-meeting-k.md"
        path = self.write(rel, MEETING)
        about.run(self.root, apply=True)
        once = path.read_text(encoding="utf-8")
        self.assertEqual(once, MEETING + "\n## Relations\n\n- about [[Acme Site]]\n")
        self.assertEqual(self.results(apply=True)[rel][0], "skip")
        self.assertEqual(path.read_text(encoding="utf-8"), once)

    def test_note_linking_its_project_by_alias_or_label_is_left_alone(self):
        for n, link in enumerate(("[[the site]]", "[[Acme Site|our site]]", "[[Acme Site\\|our site]]")):
            text = MEETING + "\n## Relations\n\n- about %s\n" % link
            rel = "sources/clients/acme/site/meetings/2026-01-0%d-meeting-k.md" % (n + 1)
            path = self.write(rel, text)
            self.assertEqual(self.results(apply=True)[rel][0], "skip", link)
            self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_note_linking_another_subject_still_gets_its_project(self):
        rel = "sources/clients/acme/site/meetings/2026-01-01-meeting-k.md"
        path = self.write(rel, MEETING + "\n## Relations\n\n- about [[Acme]]\n")
        about.run(self.root, apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         MEETING + "\n## Relations\n\n- about [[Acme]]\n- about [[Acme Site]]\n")

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
                         MEETING + "\n## Relations\n\n- about [[Acme Site]]\n\n"
                                   "## Observations\n\n- [decision] Go\n")

    def test_note_without_frontmatter_keeps_its_text(self):
        path = self.write("sources/clients/acme/site/emails/2026-01-01-01-in-a.md", "# Hello\n")
        about.run(self.root, apply=True)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         "# Hello\n\n## Relations\n\n- about [[Acme Site]]\n")


if __name__ == "__main__":
    unittest.main()
