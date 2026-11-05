#!/usr/bin/env python3
"""Tests for add_observations_from_frontmatter.py, standard library only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'

The demo blocks below are the demo notes as Basic Memory rewrites them with
`dump_frontmatter`: block lists at column 0, long values folded at 80 columns.
The expected observations are the ones the pass produced on the same notes
before the rewrite, so a rewrite by Basic Memory must not lose any of them.
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import add_observations_from_frontmatter as obs  # noqa: E402
import auto_link_entities as autolink  # noqa: E402

BODY = "\n# Heading\n\n## Observations\n\n## Relations\n\n- relates_to [[Something]]\n"

CATALOG_SEARCH = """\
title: Catalog Search
name: Catalog Search
type: topic
schema_version: 1
domain: tech
aliases:
- Catalog Search
- product search
- part search
- faceted search
status: active
related:
- Progressive disclosure
- Information architecture
"""

CLIENT_ONBOARDING = """\
title: Client Onboarding
name: Client Onboarding
type: topic
schema_version: 1
domain: ops
aliases:
- Client Onboarding
- onboarding
- client kickoff
status: active
related:
- Project kickoff
- Discovery workshop
"""

GLOBEX = """\
title: Globex
aliases:
- Globex
client: Globex
type: client-context
schema_version: 1
status: active
last_updated: 2026-06-22
legal_form: company
company_id: REG-77120453
industry: Industrial e-commerce
tone: professional
addressing: informal
primary_channel: email
email_format: standard-professional
language: en
constraints:
- No meetings on Fridays
"""

PROSEWARE = """\
title: Proseware
aliases:
- Proseware
partner: Proseware
type: partner-context
schema_version: 1
status: active
partnership_type: mixed
last_updated: 2026-06-24
active_tracks:
- Lead referral, Proseware sends front-end and e-commerce work, we send ERP and order-flow
  work back
- Technical coordination on shared accounts, where their order backend meets our front
  end
business_referral: Proseware refers web work and takes 10% of the first engagement,
  leads we send back carry no fee
contract: affiliation
legal_form: company
company_id: REG-20884517
tone: direct
addressing: informal
primary_channel: email
language: en
constraints:
- Never write to a shared account's ERP owner without telling Proseware first
brings_lead:
- Globex
"""

LEAD_SOURCING = """\
title: Lead Sourcing
name: Lead Sourcing
type: topic
schema_version: 1
domain: business
aliases:
- referral
- lead generation
- apport d'affaires
status: active
related:
- Client Onboarding
"""

EXPECTED = {
    "catalog-search": [
        ("name", "Catalog Search"), ("domain", "tech"),
        ("aliases", "Catalog Search"), ("aliases", "product search"),
        ("aliases", "part search"), ("aliases", "faceted search"),
        ("status", "active"),
        ("related", "Progressive disclosure"), ("related", "Information architecture"),
    ],
    "client-onboarding": [
        ("name", "Client Onboarding"), ("domain", "ops"),
        ("aliases", "Client Onboarding"), ("aliases", "onboarding"),
        ("aliases", "client kickoff"), ("status", "active"),
        ("related", "Project kickoff"), ("related", "Discovery workshop"),
    ],
    "globex": [
        ("client", "Globex"), ("status", "active"), ("last_updated", "2026-06-22"),
        ("legal_form", "company"), ("company_id", "REG-77120453"),
        ("industry", "Industrial e-commerce"), ("tone", "professional"),
        ("addressing", "informal"), ("primary_channel", "email"),
        ("email_format", "standard-professional"), ("language", "en"),
        ("constraints", "No meetings on Fridays"),
    ],
    "proseware": [
        ("partner", "Proseware"), ("status", "active"), ("partnership_type", "mixed"),
        ("last_updated", "2026-06-24"),
        ("active_tracks", "Lead referral, Proseware sends front-end and e-commerce work, "
                          "we send ERP and order-flow work back"),
        ("active_tracks", "Technical coordination on shared accounts, where their order "
                          "backend meets our front end"),
        ("business_referral", "Proseware refers web work and takes 10% of the first "
                              "engagement, leads we send back carry no fee"),
        ("contract", "affiliation"), ("legal_form", "company"),
        ("company_id", "REG-20884517"), ("tone", "direct"), ("addressing", "informal"),
        ("primary_channel", "email"), ("language", "en"),
        ("constraints", "Never write to a shared account's ERP owner without telling "
                        "Proseware first"),
    ],
}


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def note(self, rel: str, block: str, body: str = BODY) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + block + "---\n" + body, encoding="utf-8")
        return path

    def planned(self, path: Path):
        status, _msg, new_obs = obs.process_file(path, apply=False)
        self.assertEqual(status, "ok")
        return new_obs


class BasicMemoryShapes(Workspace):
    def test_demo_notes_keep_every_observation_after_a_basic_memory_rewrite(self):
        cases = {
            "catalog-search": ("atlas/topics/catalog-search.md", CATALOG_SEARCH),
            "client-onboarding": ("atlas/topics/client-onboarding.md", CLIENT_ONBOARDING),
            "globex": ("sources/clients/globex/CLAUDE.md", GLOBEX),
            "proseware": ("sources/partners/proseware/CLAUDE.md", PROSEWARE),
        }
        for name, (rel, block) in cases.items():
            with self.subTest(note=name):
                self.assertEqual(self.planned(self.note(rel, block)), EXPECTED[name])

    def test_literal_block_gives_one_complete_observation(self):
        path = self.note("atlas/people/ann.md",
                         "name: Ann\ntype: person\nnotes: |\n  First line.\n  Second line.\n")
        self.assertEqual(self.planned(path),
                         [("name", "Ann"), ("notes", "First line. Second line.")])

    def test_folded_block_gives_one_complete_observation(self):
        path = self.note("atlas/people/ann.md",
                         "name: Ann\ntype: person\nnotes: >-\n  Met at the\n  kickoff.\n")
        self.assertEqual(self.planned(path),
                         [("name", "Ann"), ("notes", "Met at the kickoff.")])

    def test_flow_list_splits_on_commas_outside_quotes_only(self):
        path = self.note("atlas/topics/t.md",
                         "name: Topic\ntype: topic\n"
                         "related: [\"Search, faceted\", l'onboarding, kickoff]\n")
        self.assertEqual(self.planned(path), [
            ("name", "Topic"), ("related", "Search, faceted"),
            ("related", "l'onboarding"), ("related", "kickoff"),
        ])

    def test_null_values_give_no_observation(self):
        path = self.note("atlas/people/ann.md", "name: Ann\ntype: person\nrole: null\nemail: ~\n")
        self.assertEqual(self.planned(path), [("name", "Ann")])


class Writing(Workspace):
    def test_apply_keeps_the_block_and_the_blank_line_before_the_heading(self):
        path = self.note("sources/clients/globex/CLAUDE.md", GLOBEX)
        obs.process_file(path, apply=True)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n" + GLOBEX + "---\n\n# Heading\n"))
        self.assertIn("- [constraints] No meetings on Fridays\n\n## Relations\n", text)
        self.assertNotIn("\n\n\n", text)

    def test_second_apply_changes_nothing(self):
        path = self.note("sources/partners/proseware/CLAUDE.md", PROSEWARE)
        obs.process_file(path, apply=True)
        once = path.read_text(encoding="utf-8")
        status, _msg, _new = obs.process_file(path, apply=True)
        self.assertEqual(status, "skip")
        self.assertEqual(path.read_text(encoding="utf-8"), once)


class Scope(Workspace):
    def test_only_corpus_notes_are_targets(self):
        block = "name: Ann\ntype: person\n"
        kept = self.note("atlas/people/ann.md", block)
        for rel in ("sources/clients/x/site/prompts/p.md",
                    "sources/clients/x/site/captures/c.md",
                    "sources/clients/x/site/repo-files/LICENSE.md",
                    "sources/clients/x/site/tmp/t.md",
                    "docs/ann.md", "templates/person.md"):
            self.note(rel, block)
        targets = [t.path for t in obs.find_targets(self.root)]
        self.assertEqual(targets, [kept])

    def test_type_filter(self):
        self.note("atlas/people/ann.md", "name: Ann\ntype: person\n")
        topic = self.note("atlas/topics/t.md", "name: Topic\ntype: topic\n")
        self.assertEqual([t.path for t in obs.find_targets(self.root, "topic")], [topic])


class WithAutoLink(Workspace):
    """add_observations, then auto_link_entities, then add_observations again."""

    def observe(self):
        for target in obs.find_targets(self.root):
            obs.process_file(target.path, True, target)

    def autolink(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            autolink.main(["--apply"], root=self.root)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_text(encoding="utf-8")
                for p in sorted(self.root.rglob("*.md"))}

    def setUp(self):
        super().setUp()
        self.note("atlas/topics/catalog-search.md", CATALOG_SEARCH)
        self.note("atlas/topics/client-onboarding.md", CLIENT_ONBOARDING)
        self.note("atlas/topics/lead-sourcing.md", LEAD_SOURCING)
        self.note("sources/clients/globex/CLAUDE.md", GLOBEX)
        self.note("sources/partners/proseware/CLAUDE.md", PROSEWARE)

    def test_third_run_changes_nothing_and_the_cycle_adds_no_duplicate(self):
        self.observe()
        self.autolink()
        linked = self.snapshot()
        # The link pass did write inside observations, which is what feeds
        # Basic Memory relations.
        self.assertIn("- [active_tracks] Lead [[Lead Sourcing|referral]], Proseware",
                      linked["sources/partners/proseware/CLAUDE.md"])
        self.assertIn("- [related] [[Client Onboarding]]\n", linked["atlas/topics/lead-sourcing.md"])
        self.observe()
        self.assertEqual(self.snapshot(), linked)
        self.autolink()
        self.observe()
        self.assertEqual(self.snapshot(), linked)
        for rel, text in linked.items():
            lines = re.findall(r"^- \[[^\]]+\] .+$", text, re.MULTILINE)
            with self.subTest(note=rel):
                self.assertEqual(len(lines), len(set(lines)))

    def test_linked_observation_counts_as_present(self):
        block = "name: Topic\ntype: topic\nrelated: [client onboarding, Search box, Lead referral]\n"
        body = ("\n# T\n\n## Observations\n\n- [name] Topic\n"
                "- [related] [[Client Onboarding]]\n"
                "- [related] [[Catalog Search|Search]] box\n"
                "- [related] Lead [[Lead Sourcing|referral]]\n")
        status, _msg, new_obs = obs.process_file(self.note("atlas/topics/t.md", block, body), apply=False)
        self.assertEqual((status, new_obs), ("skip", []))

    def test_an_observation_with_other_text_is_still_added(self):
        block = "name: Topic\ntype: topic\nrelated: [Client Onboarding plan]\n"
        body = "\n# T\n\n## Observations\n\n- [name] Topic\n- [related] [[Client Onboarding]]\n"
        path = self.note("atlas/topics/t.md", block, body)
        self.assertEqual(self.planned(path), [("related", "Client Onboarding plan")])


if __name__ == "__main__":
    unittest.main()
