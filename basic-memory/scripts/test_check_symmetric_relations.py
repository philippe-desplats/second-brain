#!/usr/bin/env python3
"""Tests for `check_symmetric_relations.py`, run on a throwaway workspace.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import WorkspaceCase, note  # noqa: E402


def client(name, *relations):
    return note(f"title: {name}\nclient: {name}\ntype: client-context\nschema_version: 1\n",
                f"# {name}\n\n## Relations\n\n" + "".join(f"- {r}\n" for r in relations))


def partner(name, *relations):
    return note(f"title: {name}\npartner: {name}\ntype: partner-context\nschema_version: 1\n",
                f"# {name}\n\n## Relations\n\n" + "".join(f"- {r}\n" for r in relations))


class Symmetric(WorkspaceCase):
    def write(self, kind, slug, text):
        self.ws.write(f"sources/{kind}/{slug}/CLAUDE.md", text)

    def run_check(self, *args):
        out = self.ws.run("check_symmetric_relations.py", *args)
        count = int(next(ln for ln in out.stdout.splitlines()
                         if ln.startswith("Asymmetries found:")).split(":")[1])
        return out, count

    def test_no_argument_runs_the_check(self):
        self.write("clients", "globex", client("Globex", "managed_by [[Proseware]]"))
        self.write("partners", "proseware", partner("Proseware", "manages [[Globex]]"))
        out, count = self.run_check()
        self.assertEqual((out.returncode, count), (0, 0), out.stdout)

    def test_asymmetry_exits_non_zero(self):
        self.write("clients", "globex", client("Globex", "managed_by [[Proseware]]"))
        self.write("partners", "proseware", partner("Proseware"))
        for args in ((), ("--check",), ("--suggest",)):
            out, count = self.run_check(*args)
            self.assertEqual((out.returncode, count), (1, 1), (args, out.stdout))
        self.assertIn("add line:   - manages [[Globex]]", self.ws.run(
            "check_symmetric_relations.py", "--suggest").stdout)

    def test_bad_argument_prints_usage(self):
        out = self.ws.run("check_symmetric_relations.py", "--bogus")
        self.assertEqual(out.returncode, 1)
        self.assertIn("Usage", out.stdout)

    def test_partner_side_co_delivery_checked(self):
        self.write("clients", "globex", client("Globex"))
        self.write("partners", "proseware", partner("Proseware", "co_delivered_with [[Globex]]"))
        out, count = self.run_check()
        self.assertEqual(count, 1, out.stdout)
        self.assertIn("sources/clients/globex/CLAUDE.md", out.stdout)

    def test_client_to_client_co_delivery_checked(self):
        self.write("clients", "globex", client("Globex", "co_delivered_with [[Initech]]"))
        self.write("clients", "initech", client("Initech"))
        out, count = self.run_check()
        self.assertEqual(count, 1, out.stdout)
        self.write("clients", "initech", client("Initech", "co_delivered_with [[Globex]]"))
        self.assertEqual(self.run_check()[1], 0)

    def test_partner_to_partner_co_delivery_symmetric(self):
        self.write("partners", "proseware", partner("Proseware", "co_delivered_with [[Contoso]]"))
        self.write("partners", "contoso", partner("Contoso", "co_delivered_with [[Proseware]]"))
        self.assertEqual(self.run_check()[1], 0)

    def test_display_alias_resolved(self):
        self.write("clients", "globex", client("Globex", "managed_by [[Proseware|our partner]]"))
        self.write("partners", "proseware", partner("Proseware", "manages [[Globex|the client]]"))
        out, count = self.run_check()
        self.assertEqual(count, 0, out.stdout)
        self.assertNotIn("ORPHAN", out.stdout)

    def test_unknown_target_is_an_orphan(self):
        self.write("clients", "globex", client("Globex", "owned_by [[Nobody]]"))
        out, count = self.run_check()
        self.assertEqual(count, 1)
        self.assertIn("ORPHAN (no matching partner)", out.stdout)

    def test_folded_identity_name(self):
        long = "Proseware Digital Studio and Partners, white label web delivery for the Benelux"
        folded = ("title: Proseware Digital Studio and Partners, white label web delivery for the\n"
                  "  Benelux\npartner: Proseware Digital Studio and Partners, white label web delivery for the\n"
                  "  Benelux\ntype: partner-context\n")
        self.write("clients", "globex", client("Globex", f"managed_by [[{long}]]"))
        self.write("partners", "proseware", "---\n" + folded + "---\n\n## Relations\n\n- manages [[Globex]]\n")
        out, count = self.run_check()
        self.assertEqual(count, 0, out.stdout)


if __name__ == "__main__":
    unittest.main()
