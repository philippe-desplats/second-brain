#!/usr/bin/env python3
"""Tests for `propose_pruning.py`, run on a throwaway workspace.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import FOLDED_TITLE_LINES, LONG_TITLE, WorkspaceCase, note  # noqa: E402

OLD = time.time() - 400 * 86400


class Pruning(WorkspaceCase):
    def candidates(self):
        out = self.ws.run("propose_pruning.py", "--json", "--days", "30")
        self.assertEqual(out.returncode, 0, out.stderr)
        return [c["path"] for c in json.loads(out.stdout)["candidates"]]

    def old(self, rel, text):
        path = self.ws.write(rel, text)
        os.utime(path, (OLD, OLD))
        return path

    def test_unlinked_old_note_is_proposed(self):
        self.old("sources/internal/ops/2026-01-02-note-old.md", note("title: Old\ntype: note\n", "Text.\n"))
        self.assertEqual(self.candidates(), ["sources/internal/ops/2026-01-02-note-old.md"])

    def test_inbound_link_on_folded_title(self):
        self.old("sources/internal/ops/2026-01-02-note-plan.md",
                 "---\n" + FOLDED_TITLE_LINES + "type: note\n---\n\nText.\n")
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", f"See [[{LONG_TITLE}]].\n"))
        self.assertNotIn("sources/internal/ops/2026-01-02-note-plan.md", self.candidates())

    def test_inbound_link_on_alias(self):
        self.old("sources/internal/ops/2026-01-02-note-plan.md",
                 note("title: Plan\ntype: note\naliases:\n- the plan\n", "Text.\n"))
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "See [[the plan|it]].\n"))
        self.assertNotIn("sources/internal/ops/2026-01-02-note-plan.md", self.candidates())

    def test_inbound_link_escaped_for_a_table_cell(self):
        self.old("sources/internal/ops/2026-01-02-note-plan.md", note("title: Plan\ntype: note\n", "Text.\n"))
        self.ws.write("sources/internal/ops/2026-07-02-note-ref.md",
                      note("title: Ref\ntype: note\n", "| a | [[Plan\\|it]] |\n"))
        self.assertNotIn("sources/internal/ops/2026-01-02-note-plan.md", self.candidates())

    def test_only_corpus_notes_are_proposed(self):
        # A file copied into a client repository and a prompt pasted verbatim
        # are not notes, so pruning one is never proposed, however old.
        base = "sources/clients/globex/website-redesign"
        self.old(f"{base}/repo-files/NOTICE.md", "Notice.\n")
        self.old(f"{base}/prompts/p1.md", "Prompt.\n")
        self.old(f"{base}/2026-01-02-note-old.md", note("title: Old\ntype: note\n", "Text.\n"))
        self.assertEqual(self.candidates(), [f"{base}/2026-01-02-note-old.md"])

    def test_protected_subtype_in_quotes(self):
        self.old("sources/internal/ops/2026-01-02-note-map.md",
                 note("title: Map\ntype: note\nsubtype: \"moc\"\n", "Text.\n"))
        self.assertEqual(self.candidates(), [])


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class GitDates(WorkspaceCase):
    def git(self, *args, date=None):
        env = dict(os.environ, GIT_AUTHOR_DATE=date or "", GIT_COMMITTER_DATE=date or "")
        if not date:
            env.pop("GIT_AUTHOR_DATE")
            env.pop("GIT_COMMITTER_DATE")
        subprocess.run(["git", "-C", str(self.ws.root), "-c", "user.name=t",
                        "-c", "user.email=t@example.com", "-c", "core.quotepath=true",
                        "-c", "commit.gpgsign=false", *args],
                       check=True, capture_output=True, env=env)

    def test_accented_path_takes_its_commit_date(self):
        rel = "sources/internal/café/2026-01-02-note-éte.md"
        self.ws.write(rel, note("title: Ete\ntype: note\n", "Text.\n"))
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "old", date="2025-01-02T10:00:00+00:00")
        # A fresh clone: the file looks new on disk, only git knows its age.
        os.utime(self.ws.root / rel, None)
        out = self.ws.run("propose_pruning.py", "--json", "--days", "30")
        found = {c["path"]: c["last_modified"] for c in json.loads(out.stdout)["candidates"]}
        self.assertEqual(found, {rel: "2025-01-02"}, out.stdout)


if __name__ == "__main__":
    unittest.main()
