#!/usr/bin/env python3
"""Tests for `fix_double_frontmatter.py` and `check_double_frontmatter.py`.

Both scripts share one detection, `find_extra_blocks`, so they are tested
together on the same inputs.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_double_frontmatter  # noqa: E402
import fix_double_frontmatter as fix  # noqa: E402
from test_retype_files import Workspace, block_of, run, yaml  # noqa: E402

DOUBLE = ("---\ntitle: A\ntags:\n- x\n---\n\n"
          "---\ntitle: A\ntags:\n- y\n- z\nnotes: |\n  kept line\nstatus: active\n---\n\n# A\n")
MERGED = "---\ntitle: A\ntags:\n- x\nstatus: active\n---\n\n# A\n"
RULES = "---\ntitle: R\ntype: note\n---\n---\n\nIntro after a rule.\n\n---\n\nMore text.\n"
PROSE_KEY = "---\ntitle: R\n---\n\n---\nKey takeaways: none\n---\n"
# A body opening on a rule, then a one-word label, then a rule: prose, not
# frontmatter, although `Summary` is a valid key name.
LABEL = ("---\ntitle: Rule body\ntype: note\ndate: 2026-07-01\n---\n"
         "---\n\nSummary: the client agreed to the scope.\n\n---\n\nMore prose.\n")
# Written by python-frontmatter, the library Basic Memory dumps with, when the
# whole file is taken as content: the new block lands on top of the old one.
# The body keeps a rule, a `Summary:` label and a rule, which stay body.
BM_DOUBLE = ("---\npermalink: sources/clients/acme/web/kickoff\ntitle: Kickoff\ntype: meeting\n---\n\n"
             "---\ntitle: Kickoff\ntype: meeting\ndate: '2026-07-02'\ntags:\n- kickoff\n---\n\n"
             "# Kickoff\n\n---\n\nSummary: scope agreed.\n\n---\n")
# No known schema key, but a key the first block also has.
SHARED_KEY = "---\ndate: 2026-07-01\nstatus: draft\n---\n---\ndate: 2026-07-02\nowner: me\n---\n"


class Detection(unittest.TestCase):
    def test_double_detected(self):
        self.assertIsNotNone(fix.find_extra_blocks(DOUBLE))

    def test_body_rules_are_not_frontmatter(self):
        self.assertIsNone(fix.find_extra_blocks(RULES))
        self.assertIsNone(fix.find_extra_blocks(PROSE_KEY))

    def test_one_word_label_between_rules_is_prose(self):
        self.assertIsNone(fix.find_extra_blocks(LABEL))
        for label in ("Note: x", "Status: x", "Outcome: signed", "owner: me"):
            text = "---\ntitle: R\ntype: note\n---\n---\n" + label + "\n---\n\nEnd.\n"
            self.assertIsNone(fix.find_extra_blocks(text), label)

    def test_mixed_block_with_a_prose_line_is_prose(self):
        text = "---\ntitle: R\n---\n---\ntitle: R\nA sentence of prose.\n---\n"
        self.assertIsNone(fix.find_extra_blocks(text))

    def test_basic_memory_double_block_still_detected(self):
        found = fix.find_extra_blocks(BM_DOUBLE)
        self.assertIsNotNone(found)
        self.assertEqual(len(found[1]), 1)
        fixed, blocks, dropped = fix.fix_text(BM_DOUBLE)
        self.assertEqual((blocks, dropped), (2, ["title", "type"]))
        self.assertEqual(fixed, "---\npermalink: sources/clients/acme/web/kickoff\ntitle: Kickoff\n"
                                "type: meeting\ndate: '2026-07-02'\ntags:\n- kickoff\n---\n\n"
                                "# Kickoff\n\n---\n\nSummary: scope agreed.\n\n---\n")
        self.assertIsNone(fix.find_extra_blocks(fixed))

    def test_block_sharing_a_key_with_the_first_is_detected(self):
        self.assertIsNotNone(fix.find_extra_blocks(SHARED_KEY))

    def test_single_block_and_no_block(self):
        self.assertIsNone(fix.find_extra_blocks(MERGED))
        self.assertIsNone(fix.find_extra_blocks("# No frontmatter\n\n---\ntitle: x\n---\n"))

    def test_check_uses_the_same_function(self):
        self.assertIs(check_double_frontmatter.find_extra_blocks, fix.find_extra_blocks)


class Merge(unittest.TestCase):
    def test_duplicate_key_dropped_with_items_and_continuations(self):
        text, blocks, dropped = fix.fix_text(DOUBLE.replace("notes: |\n  kept line\n", ""))
        self.assertEqual(text, MERGED)
        self.assertEqual((blocks, dropped), (2, ["title", "tags"]))

    def test_block_scalar_of_a_new_key_kept_whole(self):
        text, _, _ = fix.fix_text(DOUBLE)
        self.assertEqual(text, "---\ntitle: A\ntags:\n- x\nnotes: |\n  kept line\nstatus: active\n---\n\n# A\n")
        if yaml is not None:
            self.assertEqual(yaml.safe_load(block_of(text)),
                             {"title": "A", "tags": ["x"], "notes": "kept line\n", "status": "active"})

    def test_three_stacked_blocks(self):
        text, blocks, _ = fix.fix_text("---\ntitle: A\n---\n---\ntype: note\n---\n\n"
                                       "---\ntitle: B\npermalink: a\n---\nBody\n")
        self.assertEqual(text, "---\ntitle: A\ntype: note\npermalink: a\n---\nBody\n")
        self.assertEqual(blocks, 3)

    def test_third_block_may_share_a_key_with_the_second_only(self):
        text, blocks, _ = fix.fix_text("---\ntitle: A\n---\n---\ntype: note\nowner: me\n---\n"
                                       "---\nowner: you\n---\nBody\n")
        self.assertEqual(text, "---\ntitle: A\ntype: note\nowner: me\n---\nBody\n")
        self.assertEqual(blocks, 3)

    def test_crlf_kept(self):
        text, _, _ = fix.fix_text(DOUBLE.replace("notes: |\n  kept line\n", "").replace("\n", "\r\n"))
        self.assertEqual(text, MERGED.replace("\n", "\r\n"))


class Cli(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace(self)
        self.ws.write("sources/internal/ops/double.md", DOUBLE)
        self.ws.write("sources/internal/ops/rules.md", RULES)

    def test_dry_run_is_the_default_and_reports(self):
        out = run(fix.main, [], root=self.ws.root)
        self.assertEqual(self.ws.read("sources/internal/ops/double.md"), DOUBLE)
        self.assertIn("Would fix 1 files", out)
        self.assertIn("sources/internal/ops/double.md: merge 2 blocks, drop duplicate keys: title, tags", out)
        self.assertNotIn("rules.md", out)

    def test_apply_writes_and_is_idempotent(self):
        run(fix.main, ["--apply"], root=self.ws.root)
        first = self.ws.read("sources/internal/ops/double.md")
        self.assertIsNone(fix.find_extra_blocks(first))
        self.assertEqual(self.ws.read("sources/internal/ops/rules.md"), RULES)
        out = run(fix.main, ["--apply"], root=self.ws.root)
        self.assertEqual(self.ws.read("sources/internal/ops/double.md"), first)
        self.assertIn("Fixed 0 files", out)

    def test_explicit_dry_run_writes_nothing(self):
        out = run(fix.main, ["--dry-run"], root=self.ws.root)
        self.assertEqual(self.ws.read("sources/internal/ops/double.md"), DOUBLE)
        self.assertIn("Would fix 1 files", out)

    def test_unknown_argument_is_refused(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            run(fix.main, ["--force"], root=self.ws.root)
        self.assertEqual(self.ws.read("sources/internal/ops/double.md"), DOUBLE)

    def test_never_writes_outside_the_corpus(self):
        rel = "sources/internal/ops/prompts/double.md"
        self.ws.write(rel, DOUBLE)
        run(fix.main, ["--apply"], root=self.ws.root)
        self.assertEqual(self.ws.read(rel), DOUBLE)

    def test_check_reports_what_fix_would_merge(self):
        self.ws.write("templates/double.md", DOUBLE)
        out = run(check_double_frontmatter.main, root=self.ws.root)
        self.assertIn("Total files with DOUBLE frontmatter: 2", out)
        self.assertIn("  sources/internal/ops/double.md\n", out)
        self.assertIn("  templates/double.md  (outside the corpus, repair by hand)", out)
        self.assertNotIn("rules.md", out)


if __name__ == "__main__":
    unittest.main()
