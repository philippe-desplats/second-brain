#!/usr/bin/env python3
"""Tests for `curation_reminder.py`. The OS notification is replaced by a counter.

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

import check_helpers as H  # noqa: E402
import curation_reminder as R  # noqa: E402
import frontmatter as F  # noqa: E402

try:
    import yaml
except ImportError:  # the stdlib-only interpreter
    yaml = None


class Reminder(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.inbox = Path(tmp.name) / "inbox"
        self.inbox.mkdir()
        self.calls = 0

        def fake_notify():
            self.calls += 1

        for name, value in (("INBOX", self.inbox), ("notify", fake_notify)):
            original = getattr(R, name)
            setattr(R, name, value)
            self.addCleanup(setattr, R, name, original)

    def run_main(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            R.main()
        return out.getvalue()

    def test_notifies_once_per_day(self):
        self.run_main()
        second = self.run_main()
        self.assertEqual(self.calls, 1)
        self.assertEqual(len(list(self.inbox.glob("*.md"))), 1)
        self.assertIn("nothing written", second)

    def test_no_inbox_no_notification(self):
        self.inbox.rmdir()
        self.run_main()
        self.assertEqual(self.calls, 0)

    def test_note_validates_against_the_note_schema(self):
        self.run_main()
        path = next(self.inbox.glob("*.md"))
        _, fm = F.read_file(path)
        self.assertEqual(fm.get("type"), "note")
        self.assertEqual(fm.get("schema_version"), "1")
        declared = H.load_schemas(HERE.parent / "schemas")["note"]
        required = {k for k, req in declared.items() if req}
        self.assertLessEqual(required, set(fm.keys()))
        self.assertLessEqual(set(fm.keys()) - {"type", "schema_version"}, set(declared))
        self.assertEqual(fm.get("note_type"), "reminder")
        if yaml is not None:
            data = yaml.safe_load(F.split(path.read_text(encoding="utf-8")).block)
            self.assertEqual(data["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
