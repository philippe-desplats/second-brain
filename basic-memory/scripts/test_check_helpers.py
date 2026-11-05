#!/usr/bin/env python3
"""Tests for `check_helpers.py`, plus the throwaway workspace the check tests share.

`Workspace` builds a copy of the workspace skeleton in a temporary directory:
the scripts and the schemas, nothing else. A check under test is run as a
subprocess from that copy, so it resolves its own WORKSPACE to the copy and
never reads the real notes. The inputs are shaped like Basic Memory writes
them: titles folded at 80 columns, block lists at column 0.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_helpers as H  # noqa: E402
import frontmatter as F  # noqa: E402

REPO = HERE.parent.parent

# A title past 80 columns, which Basic Memory folds onto a second line.
LONG_TITLE = ("Globex Website Redesign, discovery workshop outcomes and the content "
              "inventory plan for Q3")
# What a reader stopping at the end of the first line gets.
TRUNCATED_TITLE = "Globex Website Redesign, discovery workshop outcomes and the content inventory"
FOLDED_TITLE_LINES = ("title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
                      "  plan for Q3\n")


def note(front: str, body: str = "") -> str:
    """A note from a frontmatter block and a body, both dedented."""
    return "---\n" + textwrap.dedent(front).lstrip("\n") + "---\n\n" + textwrap.dedent(body).lstrip("\n")


class Workspace:
    """A temporary copy of the scripts and schemas, with notes written on demand."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "ws"
        scripts = self.root / "basic-memory" / "scripts"
        scripts.mkdir(parents=True)
        for py in HERE.glob("*.py"):
            if not py.name.startswith("test_"):
                shutil.copy2(py, scripts / py.name)
        shutil.copytree(REPO / "basic-memory" / "schemas", self.root / "basic-memory" / "schemas")
        self.scripts = scripts

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(self.scripts / script), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=120)

    def close(self):
        self._tmp.cleanup()


class WorkspaceCase(unittest.TestCase):
    """A test case with a fresh Workspace in `self.ws`."""

    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.close)


class NoteNames(unittest.TestCase):
    def fm(self, text):
        return F.parse(F.split(text).block)

    def test_folded_title_read_whole(self):
        fm = self.fm("---\n" + FOLDED_TITLE_LINES + "type: note\n---\n")
        names = H.note_names(fm, "sources/x/y/a.md")
        self.assertIn(LONG_TITLE, names)
        self.assertNotIn(TRUNCATED_TITLE, names)

    def test_aliases_block_and_inline(self):
        block = self.fm("---\ntitle: Client Onboarding\naliases:\n- onboarding\n- client kickoff\n---\n")
        inline = self.fm("---\ntitle: Client Onboarding\naliases: [onboarding, client kickoff]\n---\n")
        for fm in (block, inline):
            names = H.note_names(fm, "atlas/topics/client-onboarding.md")
            self.assertTrue({"onboarding", "client kickoff", "Client Onboarding",
                             "client-onboarding", "atlas/topics/client-onboarding",
                             "atlas/topics/client-onboarding.md"} <= names)

    def test_identity_keys_accepted(self):
        fm = self.fm("---\ntitle: Globex\nclient: Globex Corp\nname: G\nsubject: Kickoff\n---\n")
        self.assertTrue({"Globex", "Globex Corp", "G", "Kickoff"} <= H.note_names(fm, "a/CLAUDE.md"))

    def test_no_frontmatter(self):
        self.assertEqual(H.note_names(None, "a/b.md"), {"b", "a/b", "a/b.md"})

    def test_link_targets(self):
        text = "[[A]] [[B|shown]] [[C#Heading]] [[D#H|shown]] [[ E ]]"
        self.assertEqual([t for t, _ in H.link_targets(text)], ["A", "B", "C", "D", "E"])

    def test_resolution_table_shared_name(self):
        table = H.resolution_table([("n1", {"x", "y"}), ("n2", {"y"})])
        self.assertEqual(sorted(table["y"]), ["n1", "n2"])


class SchemaLoader(unittest.TestCase):
    def write(self, text):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "thing.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_real_schemas_match_declared_fields(self):
        schemas = H.load_schemas(REPO / "basic-memory" / "schemas")
        self.assertEqual(len(schemas), 17)
        self.assertEqual(schemas["note"]["title"], True)
        self.assertEqual(schemas["note"]["aliases"], False)
        self.assertNotIn("moc", schemas["note"])  # an enum value, not a field

    def test_any_indent_width(self):
        for unit in ("  ", "    ", "\t"):
            text = ("---\ntitle: Thing\ntype: schema\nschema:\n%sbody?: string\nsettings:\n"
                    "%svalidation: warn\n%sfrontmatter:\n%s%sdate: string, \"d\"\n"
                    "%s%sstatus?(enum):\n%s%s- draft\n%s%stags?(array): string\n---\n") % (
                unit, unit, unit, unit, unit, unit, unit, unit, unit, unit, unit)
            fields = H.schema_fields(self.write(text))
            self.assertEqual(fields, {"date": True, "status": False, "tags": False}, repr(unit))


if __name__ == "__main__":
    unittest.main()
