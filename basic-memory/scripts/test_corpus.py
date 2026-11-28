#!/usr/bin/env python3
"""Tests for the corpus walk and the agent instruction file names, on a temporary tree."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from corpus import iter_corpus_notes  # noqa: E402


class AgentsFiles(unittest.TestCase):
    def test_root_agents_md_is_not_a_note_but_entity_and_project_ones_are(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rels = ["AGENTS.md", "sources/clients/globex/AGENTS.md",
                    "sources/clients/globex/web/AGENTS.md", "sources/internal/pricing/CLAUDE.md"]
            for rel in rels:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# x\n", encoding="utf-8")
            found = sorted(rel for _, rel in iter_corpus_notes(root))
            self.assertEqual(found, sorted(rels[1:]))


if __name__ == "__main__":
    unittest.main()
