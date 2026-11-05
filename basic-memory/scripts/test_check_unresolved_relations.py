#!/usr/bin/env python3
"""Tests for `check_unresolved_relations.py`, on a synthetic Basic Memory index.

The index is a small SQLite file holding the 3 tables the script reads, with
the columns Basic Memory declares for them, so no real index is ever opened.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import sqlite3
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import WorkspaceCase  # noqa: E402

SCHEMA = """
CREATE TABLE project (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE,
                      permalink VARCHAR NOT NULL UNIQUE, path VARCHAR NOT NULL);
CREATE TABLE entity (id INTEGER PRIMARY KEY, title VARCHAR NOT NULL, file_path VARCHAR NOT NULL,
                     project_id INTEGER NOT NULL);
CREATE TABLE relation (id INTEGER PRIMARY KEY, from_id INTEGER NOT NULL, to_id INTEGER,
                       to_name VARCHAR NOT NULL, relation_type VARCHAR NOT NULL,
                       project_id INTEGER NOT NULL);
"""


class Unresolved(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.db = self.ws.root / "memory.db"
        conn = sqlite3.connect(self.db)
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO project VALUES (?, ?, ?, ?)",
                         [(1, "Demo Brain", "demo-brain", "/p/demo"), (2, "other", "other", "/p/other")])
        conn.executemany("INSERT INTO entity VALUES (?, ?, ?, ?)", [
            (1, "Globex", "sources/clients/globex/CLAUDE.md", 1),
            (2, "Client Context", "basic-memory/schemas/client-context.md", 1),
            (3, "Elsewhere", "notes/elsewhere.md", 2),
        ])
        conn.executemany("INSERT INTO relation VALUES (?, ?, ?, ?, ?, ?)", [
            (1, 1, None, "Client", "links_to", 1),          # a real note, a capitalised name
            (2, 2, None, "Other entity", "competes_with", 1),  # written in a schema
            (3, 1, 1, "Globex", "links_to", 1),             # resolved
            (4, 3, None, "Missing Thing", "links_to", 2),    # another project
            (5, 3, None, "Another Gap", "links_to", 2),
        ])
        conn.commit()
        conn.close()

    def config(self, project):
        self.ws.write(".sb-config.json", json.dumps({"schema": "sb-config/v1",
                                                     "basic_memory_project": project}))

    def run_check(self):
        return self.ws.run("check_unresolved_relations.py", "--db", str(self.db))

    def test_filters_on_the_configured_project(self):
        for value in ("Demo Brain", "demo-brain"):
            self.config(value)
            out = self.run_check()
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("Unresolved relations: 2 / 3", out.stdout)
            self.assertNotIn("Missing Thing", out.stdout)

    def test_null_project_counts_every_project(self):
        self.config(None)
        out = self.run_check()
        self.assertIn("Unresolved relations: 4 / 5", out.stdout)
        self.assertIn("every Basic Memory project", out.stdout)

    def test_missing_config_counts_every_project(self):
        out = self.run_check()
        self.assertIn("Unresolved relations: 4 / 5", out.stdout)

    def test_unknown_project_fails(self):
        self.config("nope")
        out = self.run_check()
        self.assertEqual(out.returncode, 1)
        self.assertIn("nope", out.stderr)

    def test_schema_example_derived_from_source_path(self):
        self.config("demo-brain")
        out = self.run_check().stdout
        example = out.split("Example syntax from the schemas")[1]
        self.assertIn("[[Other entity]]", example)
        self.assertNotIn("[[Client]]", example)
        self.assertIn("[[Client]]", out.split("Probable entity with no note")[1].split("\n\n")[0])


if __name__ == "__main__":
    unittest.main()
