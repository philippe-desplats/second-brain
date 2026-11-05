#!/usr/bin/env python3
"""Tests for `check_frontmatter_damage.py`, run on a throwaway workspace.

Every fixture under `tests_fixtures/damage/` is real damage, not a hand-written
imitation: a note shaped the way Basic Memory writes it, then run through the
untouched 0.5.2, 0.5.3 or 0.6.0 script that broke it. The file names say which shape
each one carries, and the `.txt` suffix keeps every pass and every check from
reading a fixture as a note. Two fixtures carry the same alias bug at 2 stages, after 1
run of the 0.5.3 hook and after 4, since the damage grows with every run.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_check_helpers import WorkspaceCase, note  # noqa: E402

import check_frontmatter_damage as D  # noqa: E402

FIXTURES = HERE / "tests_fixtures" / "damage"
LONG = ("Globex Website Redesign, discovery workshop outcomes and the content "
        "inventory plan for Q3")

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# Where each fixture sits in the workspace, the path the damage was produced at.
PLACES = {
    "stray-alias-items.txt": "atlas/topics/client-onboarding.md",
    "orphan-continuation-run1.txt": "sources/clients/globex/website-redesign/2026-06-25-note-workshop-outcomes.md",
    "orphan-continuation-run4.txt": "sources/clients/globex/website-redesign/2026-06-26-note-workshop-outcomes.md",
    "broken-opener.txt": "sources/internal/ops/2026-06-26-note-plan-q3-capacity.md",
    "type-inside-list.txt": "sources/clients/globex/website-redesign/meetings/2026-06-29-meeting-review.md",
    "detached-list-items.txt": "sources/clients/globex/website-redesign/2026-06-27-note-kickoff-addendum.md",
    "concatenated-title.txt": "sources/clients/initech/CLAUDE.md",
    "observation-truncated.txt": "atlas/topics/discovery-workshop.md",
    "observation-block-indicator.txt": "atlas/people/jane-doe.md",
    "excluded-repo-files.txt": "sources/clients/globex/website-redesign/repo-files/NOTICE.md",
    "excluded-prompts.txt": "sources/clients/globex/website-redesign/prompts/content-inventory.md",
    "unquoted-title.txt": "sources/clients/initech-studio/CLAUDE.md",
    "unescaped-backslash-alias.txt": "knowledge/tech/guide-regex-cheatsheet.md",
    "unescaped-backslash-alias-3-runs.txt": "atlas/topics/regex-cheatsheet.md",
    "type-inside-folded-title.txt": "sources/clients/globex/website-redesign/meetings/2026-06-25-meeting-discovery.md",
    "type-inside-folded-title-after-hook.txt": "sources/clients/globex/website-redesign/meetings/2026-06-26-meeting-discovery.md",
    "type-inside-folded-single-quoted.txt": "sources/clients/globex/website-redesign/meetings/2026-07-01-meeting-sq.md",
    "type-inside-folded-double-quoted.txt": "sources/clients/globex/website-redesign/meetings/2026-07-07-meeting-dq.md",
    "type-inside-indented-list.txt": "sources/clients/globex/website-redesign/meetings/2026-07-05-meeting-indented.md",
    "type-inside-block-scalar.txt": "sources/clients/globex/website-redesign/meetings/2026-07-06-meeting-block.md",
    "undecoded-entity.txt": "sources/clients/globex/CLAUDE.md",
    "undecoded-brief.txt": "sources/clients/globex/website-redesign/README.md",
    "undecoded-about-link.txt": "sources/clients/globex/website-redesign/emails/2026-06-15-01-in-kickoff-questions.md",
    "undecoded-escapes.txt": "atlas/topics/catalog-search.md",
    "truncated-wikilink.txt": "sources/clients/globex/CLAUDE.md",
    "about-entity-meeting.txt": "sources/clients/globex/website-redesign/meetings/2026-06-29-meeting-wireframe-review.md",
    "about-entity-email-no-brief.txt": "sources/clients/globex/support/emails/2026-07-02-01-in-login-issue.md",
    "about-entity-brief.txt": "sources/clients/globex/website-redesign/README.md",
    "about-internal-meeting.txt": "sources/internal/pricing/meetings/2026-07-03-meeting-rate-review.md",
    "about-organization-meeting.txt": "sources/internal/pricing/meetings/2026-07-04-meeting-rate-review.md",
    "table-cell-split.txt": "sources/clients/globex/website-redesign/2026-06-30-note-search-ux.md",
}


class DamageCase(WorkspaceCase):
    def place(self, *names):
        for name in names:
            self.ws.write(PLACES[name], (FIXTURES / name).read_text(encoding="utf-8"))

    def read(self, rel):
        return (self.ws.root / rel).read_text(encoding="utf-8")

    def run_json(self, *args):
        out = self.ws.run("check_frontmatter_damage.py", "--json", *args)
        self.assertIn(out.returncode, (0, 1), out.stderr)
        return out.returncode, json.loads(out.stdout)

    def hits(self, *args, shape=None):
        _, report = self.run_json(*args)
        hits = report["hits"]
        return [h for h in hits if shape is None or h["shape"] == shape]

    def one(self, shape, *args):
        found = self.hits(*args, shape=shape)
        self.assertEqual(len(found), 1, found)
        return found[0]


class StrayAliasItems(DamageCase):
    def test_merged_alias_list_from_0_5_2_damage(self):
        self.place("stray-alias-items.txt")
        hit = self.one("stray-alias-items")
        self.assertEqual((hit["path"], hit["line"], hit["end_line"]),
                         ("atlas/topics/client-onboarding.md", 7, 10))
        self.assertEqual(hit["replacement"],
                         ["aliases: [Client Onboarding, onboarding, client kickoff]"])
        self.assertFalse(hit["needs_review"])

    def test_text_line_format(self):
        self.place("stray-alias-items.txt")
        out = self.ws.run("check_frontmatter_damage.py")
        self.assertEqual(out.returncode, 1)
        first = out.stdout.splitlines()[0]
        self.assertTrue(first.startswith("atlas/topics/client-onboarding.md:7: stray-alias-items: "), first)
        self.assertIn(" -> replace lines 7-10 with 1 line: ", first)


class OrphanContinuation(DamageCase):
    EXPECTED = ['aliases: ["%s", workshop outcomes]' % LONG]

    def test_after_one_run_of_the_0_5_3_hook(self):
        self.place("orphan-continuation-run1.txt")
        hit = self.one("orphan-continuation")
        self.assertEqual((hit["line"], hit["end_line"]), (7, 9))
        self.assertEqual(hit["replacement"], self.EXPECTED)
        self.assertFalse(hit["needs_review"])

    def test_nested_quoted_list_growth_after_four_runs(self):
        self.place("orphan-continuation-run4.txt")
        hit = self.one("orphan-continuation")
        self.assertEqual((hit["line"], hit["end_line"]), (7, 9))
        self.assertEqual(hit["replacement"], self.EXPECTED)

    def test_no_stray_alias_hit_on_the_same_lines(self):
        self.place("orphan-continuation-run1.txt")
        self.assertEqual(self.hits(shape="stray-alias-items"), [])

    def test_folded_synonym_rebuilt_from_its_continuation(self):
        # The truncated item is not the title: its continuation completes it.
        self.ws.write("atlas/topics/x.md", note(
            'title: Workshops\ntype: topic\n'
            'aliases: [Workshops, "Discovery workshop for the content inventory of the"]\n'
            '  catalog\n- workshop\n'))
        hit = self.one("orphan-continuation")
        self.assertEqual(hit["replacement"], [
            "aliases: [Workshops, Discovery workshop for the content inventory of the catalog, workshop]"])
        self.assertTrue(hit["needs_review"])

    def test_continuation_under_a_quoted_scalar(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-x.md", note(
            'title: "Q3 plan"\n  for Globex\ntype: note\n'))
        hit = self.one("orphan-continuation")
        self.assertEqual(hit["line"], 2)
        self.assertTrue(hit["needs_review"])
        self.assertIsNone(hit["replacement"])


class BrokenOpener(DamageCase):
    def test_restored_opener_from_retype_fallback_damage(self):
        self.place("broken-opener.txt")
        hit = self.one("broken-opener")
        self.assertEqual((hit["line"], hit["end_line"]), (1, 1))
        self.assertEqual(hit["replacement"], ["---", "title: Q3 capacity plan"])
        self.assertFalse(hit["needs_review"])

    def test_rest_of_the_block_still_checked(self):
        text = (FIXTURES / "type-inside-list.txt").read_text(encoding="utf-8")
        self.ws.write(PLACES["type-inside-list.txt"], "---" + text[4:])
        shapes = sorted(h["shape"] for h in self.hits())
        self.assertEqual(shapes, ["broken-opener", "type-inside-list"])


class TypeInsideList(DamageCase):
    def test_type_moved_after_the_list_from_retype_files_damage(self):
        self.place("type-inside-list.txt")
        hit = self.one("type-inside-list")
        self.assertEqual((hit["line"], hit["end_line"]), (2, 5))
        self.assertEqual(hit["replacement"], ["tags:", "- review", "- globex", "type: meeting"])
        self.assertFalse(hit["needs_review"])
        self.assertEqual(self.hits(shape="detached-list-items"), [])


class TypeInsideFoldedTitle(DamageCase):
    def test_title_rejoined_from_retype_files_damage(self):
        self.place("type-inside-folded-title.txt")
        hit = self.one("type-inside-folded-title")
        self.assertEqual((hit["line"], hit["end_line"]), (2, 4))
        self.assertEqual(hit["replacement"], [
            "title: Globex Website Redesign, discovery workshop outcomes and the content inventory",
            "  plan for Q3", "type: meeting"])
        self.assertFalse(hit["needs_review"])
        self.assertEqual([h["shape"] for h in self.hits()], ["type-inside-folded-title"])

    def test_alias_the_new_hook_took_from_the_truncated_title_is_completed(self):
        self.place("type-inside-folded-title-after-hook.txt")
        hit = self.one("type-inside-folded-title")
        self.assertEqual((hit["line"], hit["end_line"]), (2, 5))
        self.assertEqual(hit["replacement"], [
            "title: Globex Website Redesign, discovery workshop outcomes and the content inventory",
            "  plan for Q3", 'aliases: ["%s"]' % LONG, "type: meeting"])

    def test_folded_title_above_its_type_is_clean(self):
        self.ws.write("sources/internal/ops/2026-07-01-meeting-x.md", note(
            "title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
            "  plan for Q3\ntype: meeting\n"))
        self.assertEqual(self.hits(), [])


class TypeInsideAnyFirstField(DamageCase):
    """The old retype_files.py put `type:` on line 2 under any first field.

    These 4 stay valid YAML once damaged, PyYAML reads `type: 'meeting - a - b'`,
    so only the shape tells them apart, with or without PyYAML.
    """

    def check(self, name, expected, end):
        self.place(name)
        found = self.hits()
        self.assertEqual([h["shape"] for h in found], ["type-inside-folded-title"], found)
        self.assertEqual((found[0]["line"], found[0]["end_line"]), (2, end))
        self.assertEqual(found[0]["replacement"], expected)
        self.assertFalse(found[0]["needs_review"])

    def test_folded_single_quoted_title(self):
        self.check("type-inside-folded-single-quoted.txt", [
            "title: 'Atelier : l''inventaire des contenus et la feuille de route pour le trimestre",
            "  prochain, version longue'", "type: meeting"], 4)

    def test_folded_double_quoted_title(self):
        self.check("type-inside-folded-double-quoted.txt", [
            'title: "Kickoff \\\\ backslash and a long title that BM folds past the eighty column limit',
            '  for sure"', "type: meeting"], 4)

    def test_indented_list(self):
        self.check("type-inside-indented-list.txt", ["tags:", "  - a", "  - b", "type: meeting"], 5)

    def test_block_scalar(self):
        self.check("type-inside-block-scalar.txt", ["notes: |", "  one", "  two", "type: meeting"], 5)

    def test_value_on_the_next_line_is_left_alone(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-x.md", note("title: X\ntype:\n  note\n"))
        self.assertEqual(self.hits(), [])


class UndecodedQuoteInBody(DamageCase):
    def test_observation_of_a_single_quoted_value(self):
        self.place("undecoded-brief.txt")
        found = self.hits(shape="undecoded-quote-in-body")
        self.assertEqual([(h["line"], h["replacement"]) for h in found], [
            (58, ["- [title] Refonte : l'atelier du site"])])

    def test_about_link_to_an_entity_named_in_single_quotes(self):
        self.place("undecoded-entity.txt", "undecoded-about-link.txt", "undecoded-brief.txt")
        found = {(h["path"], h["line"]): h["replacement"] for h in self.hits(shape="undecoded-quote-in-body")}
        self.assertEqual(found[(PLACES["undecoded-about-link.txt"], 35)], ["- about [[Globex : l'atelier]]"])
        self.assertEqual(found[(PLACES["undecoded-brief.txt"], 68)], ["- about [[Globex : l'atelier]]"])
        self.assertEqual(found[(PLACES["undecoded-entity.txt"], 62)], ["- [client] Globex : l'atelier"])

    def test_double_quoted_escapes(self):
        self.place("undecoded-escapes.txt")
        hit = self.one("undecoded-quote-in-body")
        self.assertEqual((hit["line"], hit["replacement"]), (22, ['- [domain] C:\\d "Fast"']))
        self.assertFalse(hit["needs_review"])

    def test_found_without_pyyaml(self):
        self.place("undecoded-escapes.txt")
        out = self.ws.run("check_frontmatter_damage.py")
        self.assertEqual(out.returncode, 1, out.stdout)

    def test_decoded_observation_is_clean(self):
        self.ws.write("atlas/topics/x.md", note(
            "title: X\nname: 'L''atelier'\ntype: topic\n", "# X\n\n## Observations\n\n- [name] L'atelier\n"))
        self.assertEqual(self.hits(), [])


class UnescapedBackslashAlias(DamageCase):
    EXPECTED = ['aliases: ["Regex: \\\\d+ cheatsheet"]']

    def test_alias_re_rendered_from_the_title_after_2_runs(self):
        self.place("unescaped-backslash-alias.txt")
        hit = self.one("unescaped-backslash-alias")
        self.assertEqual((hit["line"], hit["end_line"]), (3, 3))
        self.assertEqual(hit["replacement"], self.EXPECTED)
        self.assertFalse(hit["needs_review"])

    def test_every_truncated_copy_dropped_after_3_runs(self):
        self.place("unescaped-backslash-alias-3-runs.txt")
        self.assertEqual(self.one("unescaped-backslash-alias")["replacement"], self.EXPECTED)

    def test_found_without_pyyaml(self):
        # The text output of a plain python3 run, whatever the interpreter running the suite.
        self.place("unescaped-backslash-alias.txt")
        out = self.ws.run("check_frontmatter_damage.py")
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("unescaped-backslash-alias", out.stdout)
        self.assertNotIn("invalid-yaml", out.stdout)

    def test_escaped_alias_is_clean(self):
        self.ws.write("knowledge/tech/guide-x.md", note(
            "title: 'Regex: \\d+ cheatsheet'\naliases: [\"Regex: \\\\d+ cheatsheet\"]\ntype: note\n"))
        self.assertEqual(self.hits(), [])


class DetachedListItems(DamageCase):
    def test_items_under_a_scalar_from_fix_double_damage(self):
        self.place("detached-list-items.txt")
        hit = self.one("detached-list-items")
        self.assertEqual((hit["line"], hit["end_line"]), (8, 9))
        self.assertTrue(hit["needs_review"])
        self.assertIsNone(hit["replacement"])
        self.assertIn("date", hit["what"])

    def test_items_under_an_inline_list_other_than_aliases(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-x.md", note(
            "title: X\ntype: note\ntags: [a]\n- b\n"))
        hit = self.one("detached-list-items")
        self.assertEqual(hit["line"], 5)


class ConcatenatedTitle(DamageCase):
    def test_identity_title_from_align_entity_titles_damage(self):
        self.place("concatenated-title.txt")
        hit = self.one("concatenated-title")
        self.assertEqual((hit["line"], hit["end_line"]), (2, 3))
        self.assertEqual(hit["replacement"], ["title: Initech"])
        self.assertIn("Initech 2026", hit["what"])
        self.assertFalse(hit["needs_review"])

    def test_long_folded_title_starting_with_the_identity_is_not_damage(self):
        # A person titled on purpose with a long descriptive title, folded by
        # Basic Memory. Its first line is not the identity alone, so no pass
        # replaced it, and cutting it to the name would break every link.
        self.ws.write("atlas/people/jane-doe.md", note(
            "title: Jane Doe, Head of E-commerce and Digital Partnerships for the Globex\n"
            "  International Division\n"
            "name: Jane Doe\ntype: person\n"))
        self.assertEqual(self.hits(), [])

    def test_single_line_descriptive_title_is_a_choice(self):
        self.ws.write("sources/clients/initech/CLAUDE.md", note(
            "title: Initech, Context\nclient: Initech\ntype: client-context\n"))
        self.assertEqual(self.hits(), [])

    def test_aligned_title_is_clean(self):
        self.ws.write("sources/partners/proseware/CLAUDE.md", note(
            "title: Proseware\npartner: Proseware\ntype: partner-context\n"))
        self.assertEqual(self.hits(), [])


class UnquotedTitle(DamageCase):
    def test_identity_title_quoted_from_align_entity_titles_damage(self):
        self.place("unquoted-title.txt")
        hit = self.one("unquoted-title")
        self.assertEqual((hit["line"], hit["end_line"]), (2, 2))
        self.assertEqual(hit["replacement"], ['title: "Initech: Studio"'])
        self.assertFalse(hit["needs_review"])

    def test_plain_title_and_comment_left_alone(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-x.md", note(
            'title: Q3 plan, for Globex\ntype: note\n'))
        self.ws.write("sources/internal/ops/2026-07-02-note-y.md", note(
            'title: "Already: quoted"\ntype: note\n'))
        self.assertEqual(self.hits(), [])


class Observations(DamageCase):
    def test_truncated_observation_from_add_observations_damage(self):
        self.place("observation-truncated.txt")
        hit = self.one("observation-truncated")
        self.assertEqual(hit["line"], 18)
        self.assertEqual(hit["replacement"], [
            "- [name] Discovery workshop, the half-day session that turns a signed scope into a shared map"])
        self.assertTrue(hit["needs_review"])

    def test_block_indicator_observation(self):
        self.place("observation-block-indicator.txt")
        hit = self.one("observation-block-indicator")
        self.assertEqual(hit["line"], 24)
        self.assertEqual(hit["replacement"], ["- [notes] Prefers email over calls. Never on Fridays."])
        self.assertFalse(hit["needs_review"])

    def test_longer_human_observation_is_not_truncation(self):
        self.place("observation-block-indicator.txt")
        self.assertEqual(self.hits(shape="observation-truncated"), [])

    def test_observation_outside_the_section_is_ignored(self):
        self.ws.write("atlas/topics/x.md", note(
            "title: X\nname: Long name here\ntype: topic\n", "# X\n\n- [name] Long\n"))
        self.assertEqual(self.hits(), [])


class TruncatedWikilink(DamageCase):
    FULL = "Discovery workshop, the half-day session that turns a signed scope into a shared map"

    def test_link_to_a_folded_first_line_from_auto_link_damage(self):
        self.place("truncated-wikilink.txt", "observation-truncated.txt")
        hit = self.one("truncated-wikilink")
        self.assertEqual((hit["path"], hit["line"], hit["end_line"]),
                         (PLACES["truncated-wikilink.txt"], 27, 27))
        self.assertIn("[[%s|workshop]]" % self.FULL, hit["replacement"][0])
        self.assertNotIn("shared|", hit["replacement"][0])
        self.assertFalse(hit["needs_review"])

    def test_no_folded_note_no_hit(self):
        self.place("truncated-wikilink.txt")
        self.assertEqual(self.hits(shape="truncated-wikilink"), [])

    def test_link_that_resolves_is_left(self):
        self.place("truncated-wikilink.txt", "observation-truncated.txt")
        self.ws.write("atlas/topics/shared.md", note(
            "title: Discovery workshop, the half-day session that turns a signed scope into a shared\n"
            "type: topic\n"))
        self.assertEqual(self.hits(shape="truncated-wikilink"), [])


class AboutEntityNotProject(DamageCase):
    """`- about [[Entity]]` where the schema wants the project brief.

    The fixtures are real output: about-entity-meeting, about-entity-email-no-brief
    and about-organization-meeting from the 0.6.0 add_about_relations.py,
    about-internal-meeting and about-entity-brief from the 0.5.3 one.
    """

    PROJECT = "Globex Website Redesign"

    def context(self, organization=None):
        self.ws.write("sources/clients/globex/CLAUDE.md",
                      note("title: Globex\nclient: Globex\ntype: client-context\nschema_version: 1\n", "# Globex\n"))
        self.ws.write("sources/clients/globex/website-redesign/README.md",
                      note("title: %s\naliases: [%s]\ntype: project-brief\nschema_version: 1\n"
                           % (self.PROJECT, self.PROJECT), "# Redesign\n"))
        self.ws.write("sources/internal/pricing/README.md",
                      note("title: Pricing 2026\ntype: project-brief\nschema_version: 1\n", "# Pricing\n"))
        self.ws.write(".sb-config.json", json.dumps({"organization": organization}))

    def test_meeting_link_to_the_client_becomes_the_project(self):
        self.context()
        self.place("about-entity-meeting.txt")
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["path"], hit["line"], hit["end_line"], hit["replacement"], hit["needs_review"]),
                         (PLACES["about-entity-meeting.txt"], 19, 19,
                          ["- about [[%s]]" % self.PROJECT], False))

    def test_link_dropped_when_the_pass_already_added_the_project(self):
        self.context()
        self.place("about-entity-meeting.txt")
        self.ws.write(PLACES["about-entity-meeting.txt"],
                      self.read(PLACES["about-entity-meeting.txt"]).replace(
                          "- about [[Globex]]\n", "- about [[Globex]]\n- about [[%s|the redesign]]\n" % self.PROJECT))
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["replacement"], hit["needs_review"]), (19, [], False))
        self.assertIn("replace line 19 with 0 lines", hit["repair"])

    def test_repair_then_pass_and_pass_then_repair_converge(self):
        self.context()
        rel = PLACES["about-entity-meeting.txt"]
        self.place("about-entity-meeting.txt")
        # Repair first, then the pass: the pass finds its project and writes nothing.
        self.ws.write(rel, self.read(rel).replace("- about [[Globex]]", "- about [[%s]]" % self.PROJECT))
        repaired = self.read(rel)
        self.ws.run("add_about_relations.py", "--apply")
        self.assertEqual(self.read(rel), repaired)
        # The pass first, then the repair: the pass adds the project, the repair drops the entity line.
        self.place("about-entity-meeting.txt")
        self.ws.run("add_about_relations.py", "--apply")
        hit = self.one("about-entity-not-project")
        self.assertEqual(hit["replacement"], [])
        lines = self.read(rel).split("\n")
        del lines[hit["line"] - 1]
        self.assertEqual("\n".join(lines), repaired)

    def test_internal_link_written_by_0_5_x(self):
        self.context()
        self.place("about-internal-meeting.txt")
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["replacement"], hit["needs_review"]),
                         (13, ["- about [[Pricing 2026]]"], False))

    def test_organization_link_written_by_0_6_0(self):
        self.context(organization="Acme")
        self.place("about-organization-meeting.txt")
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["replacement"]), (14, ["- about [[Pricing 2026]]"]))

    def test_organization_link_is_left_while_organization_is_null(self):
        self.context()
        self.place("about-organization-meeting.txt")
        self.assertEqual(self.hits(shape="about-entity-not-project"), [])

    def test_pass_written_line_without_a_brief_goes_with_its_block(self):
        # The 0.6.0 pass created this `## Relations` block for the line alone,
        # and an entity is no target the email schema allows, so the repair
        # removes the line, its heading and the blank line the pass added.
        self.context()
        self.place("about-entity-email-no-brief.txt")
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["end_line"], hit["replacement"], hit["needs_review"]),
                         (16, 19, [], False))
        self.assertIn("sources/clients/globex/support/README.md", hit["what"])
        self.assertIn("replace lines 16-19 with 0 lines", hit["repair"])

    def test_brief_whose_type_is_not_project_brief_counts_as_none(self):
        self.context()
        self.place("about-entity-email-no-brief.txt")
        self.ws.write("sources/clients/globex/support/README.md", note("title: Support\n", "# Support\n"))
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["replacement"], hit["needs_review"]), ([], False))
        self.assertIn("does not declare `type: project-brief`", hit["what"])

    def test_organization_line_in_an_internal_folder_without_a_brief(self):
        # The case that left `check_consistency.py` with a dead link after the 0.6.1 prompt.
        self.context(organization="Acme")
        self.place("about-organization-meeting.txt")
        rel = "sources/internal/ops/meetings/2026-07-04-meeting-rate-review.md"
        self.ws.write(rel, self.read(PLACES["about-organization-meeting.txt"]))
        (self.ws.root / PLACES["about-organization-meeting.txt"]).unlink()
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["path"], hit["line"], hit["end_line"], hit["replacement"], hit["needs_review"]),
                         (rel, 11, 14, [], False))

    def test_line_a_pass_did_not_write_needs_review(self):
        # Followed by another item: no pass wrote it there, a human may have.
        self.context()
        rel = "sources/clients/globex/support/meetings/2026-07-01-meeting-call.md"
        self.ws.write(rel, note("title: Call\ntype: meeting\n",
                                "# Call\n\n## Relations\n\n- about [[Globex]]\n- with [[Jane Doe]]\n"))
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["end_line"], hit["replacement"], hit["needs_review"]),
                         (10, 10, [], True))

    def test_other_type_whose_block_holds_the_line_alone_loses_the_block(self):
        self.context()
        rel = "sources/clients/globex/website-redesign/2026-06-30-note-ux.md"
        self.ws.write(rel, note("title: UX\ntype: note\n", "# UX\n\nText.\n\n## Relations\n\n- about [[Globex]]\n"))
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["end_line"], hit["replacement"], hit["needs_review"]),
                         (9, 12, [], True))

    def test_other_types_need_review_with_the_line_removed(self):
        self.context()
        self.place("about-entity-brief.txt")
        hit = self.one("about-entity-not-project")
        self.assertEqual((hit["line"], hit["replacement"], hit["needs_review"]), (65, [], True))

    def test_project_link_and_other_entity_relations_are_clean(self):
        self.context()
        self.ws.write("sources/clients/globex/website-redesign/meetings/2026-07-01-meeting-ok.md", note(
            "title: OK\ntype: meeting\nschema_version: 1\n",
            "# OK\n\n## Relations\n\n- with [[Globex]]\n- about [[%s]]\n" % self.PROJECT))
        self.assertEqual(self.hits(shape="about-entity-not-project"), [])


class TableCellSplit(DamageCase):
    """A link with display text in a table row. The fixture is real 0.6.0 auto_link_entities.py output.

    A bare `|` ends the cell, and Basic Memory reads the escaped `\\|` form as
    part of the target, so the repair is the bare title in both cases.
    """

    def test_alias_links_in_table_rows_become_bare_titles(self):
        self.place("table-cell-split.txt")
        found = self.hits(shape="table-cell-split-by-link")
        self.assertEqual([(h["line"], h["replacement"], h["needs_review"]) for h in found], [
            (12, ["| Results | Every [[Catalog Search]] starts from the catalog |"], False),
            (13, ["| Filters | The [[Lead Sourcing]] partner asked for a brand filter |"], False)])

    def test_escaped_alias_link_in_a_table_row_is_flagged_too(self):
        # Obsidian reads it, Basic Memory resolves its target as `X\\` and never finds it.
        self.ws.write("sources/internal/ops/2026-07-01-note-table.md", note(
            "title: T\ntype: note\n", "| a | [[X\\|y]] and [[W#h\\|v]] |\n"))
        hit = self.one("table-cell-split-by-link")
        self.assertEqual((hit["replacement"], hit["needs_review"]), (["| a | [[X]] and [[W#h]] |"], False))
        self.assertIn("Basic Memory", hit["what"])

    def test_bare_links_code_and_prose_are_clean(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-table.md", note("title: T\ntype: note\n", (
            "| a | [[X]] | [[Z#h]] |\n"
            "| b | `[[X|y]]` |\n"
            "```\n| c | [[X|y]] |\n```\n"
            "Prose keeps [[X|y]] as written.\n")))
        self.assertEqual(self.hits(shape="table-cell-split-by-link"), [])

    def test_truncated_link_in_a_table_keeps_its_escape(self):
        self.place("observation-truncated.txt")
        first = "Discovery workshop, the half-day session that turns a signed scope into a shared"
        self.ws.write("sources/internal/ops/2026-07-01-note-table.md", note(
            "title: T\ntype: note\n", "| a | [[%s\\|workshop]] |\n" % first))
        hit = self.one("truncated-wikilink")
        self.assertEqual(hit["replacement"], ["| a | [[%s\\|workshop]] |" % TruncatedWikilink.FULL])


class ExcludedFolders(DamageCase):
    def test_off_by_default(self):
        self.place("excluded-repo-files.txt", "excluded-prompts.txt")
        code, report = self.run_json()
        self.assertEqual((code, report["hits"]), (0, []))

    def test_relations_written_by_add_about_relations(self):
        self.place("excluded-repo-files.txt", "excluded-prompts.txt")
        hits = self.hits("--include-excluded", shape="pass-write-in-excluded-folder")
        self.assertEqual(sorted((h["path"], h["line"]) for h in hits), [
            (PLACES["excluded-prompts.txt"], 5), (PLACES["excluded-prompts.txt"], 7),
            (PLACES["excluded-repo-files.txt"], 5), (PLACES["excluded-repo-files.txt"], 7)])
        self.assertTrue(all(h["needs_review"] for h in hits))

    def test_wikilinks_named_as_undecidable(self):
        self.place("excluded-repo-files.txt")
        out = self.ws.run("check_frontmatter_damage.py", "--include-excluded")
        self.assertIn("cannot be told apart", out.stdout)
        self.assertIn("git log -p", out.stdout)
        self.assertIn("note:   " + PLACES["excluded-repo-files.txt"], out.stdout)

    def test_caveat_printed_without_any_excluded_folder(self):
        # The root Markdown files were linked too, a workspace with no
        # excluded folder still needs the warning.
        self.ws.write("atlas/topics/x.md", note("title: X\ntype: topic\n"))
        out = self.ws.run("check_frontmatter_damage.py", "--include-excluded")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("workspace root", out.stdout)
        self.assertIn("git log -p", out.stdout)
        _, report = self.run_json("--include-excluded")
        self.assertIn("workspace root", report["wikilink_caveat"])

    def test_tmp_folder_is_scanned_when_asked(self):
        self.ws.write("sources/clients/globex/website-redesign/tmp/scratch.md",
                      "# Scratch\n\n## Relations\n\n- about [[Globex]]\n")
        self.assertEqual(len(self.hits("--include-excluded", shape="pass-write-in-excluded-folder")), 2)


class InvalidYaml(DamageCase):
    # No old pass leaves an unknown shape, by definition, so this one is a
    # hand-written typo: a double quote never closed.
    UNKNOWN = "title: \"Globex kickoff\ntype: note\n"

    @unittest.skipUnless(HAVE_YAML, "PyYAML not importable")
    def test_unknown_shape_reported_never_repaired(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-typo.md", note(self.UNKNOWN))
        hit = self.one("invalid-yaml")
        self.assertEqual(hit["path"], "sources/internal/ops/2026-07-01-note-typo.md")
        self.assertTrue(hit["needs_review"])
        self.assertIsNone(hit["replacement"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not importable")
    def test_known_shape_not_reported_twice(self):
        self.place("stray-alias-items.txt")
        self.assertEqual([h["shape"] for h in self.hits()], ["stray-alias-items"])

    @unittest.skipIf(HAVE_YAML, "PyYAML importable")
    def test_without_pyyaml_the_report_says_so(self):
        self.ws.write("sources/internal/ops/2026-07-01-note-typo.md", note(self.UNKNOWN))
        code, report = self.run_json()
        self.assertEqual(code, 0)
        self.assertFalse(report["yaml_checked"])


class Workspace(DamageCase):
    def test_clean_basic_memory_and_hand_written_shapes_exit_0(self):
        # The clean inputs the reader is tested on: every shape Basic Memory
        # writes, and the ones humans write. None of them is damage. The notes
        # of the workspace running the suite are deliberately not read, so the
        # suite says the same on any clone.
        clean = sorted((HERE / "tests_fixtures").glob("*.txt"))
        self.assertGreater(len(clean), 5)
        for n, path in enumerate(clean):
            self.ws.write("sources/internal/shapes/2026-07-%02d-note-%s.md" % (n + 1, path.stem),
                          path.read_text(encoding="utf-8"))
        out = self.ws.run("check_frontmatter_damage.py", "--include-excluded")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_every_fixture_found_and_nothing_written(self):
        self.place(*PLACES)
        self.ws.write("sources/internal/ops/2026-07-01-note-typo.md", note(InvalidYaml.UNKNOWN))
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.ws.root.rglob("*.md")}
        shapes = {h["shape"] for h in self.hits("--include-excluded")}
        expected = {"stray-alias-items", "orphan-continuation", "broken-opener", "type-inside-list",
                    "detached-list-items", "concatenated-title", "observation-truncated",
                    "observation-block-indicator", "pass-write-in-excluded-folder",
                    "truncated-wikilink", "unquoted-title",
                    "type-inside-folded-title", "unescaped-backslash-alias",
                    "undecoded-quote-in-body", "about-entity-not-project",
                    "table-cell-split-by-link"}
        if HAVE_YAML:
            expected.add("invalid-yaml")
        self.assertEqual(shapes, expected)
        after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.ws.root.rglob("*.md")}
        self.assertEqual(before, after)


class CheckText(unittest.TestCase):
    """The pure function, without a subprocess."""

    def test_crlf_and_bom(self):
        text = "﻿---\r\naliases: [A]\r\n- B\r\ntitle: A\r\n---\r\n"
        hits = D.check_text(text, "atlas/topics/a.md")
        self.assertEqual([(h.shape, h.line, h.replacement) for h in hits],
                         [("stray-alias-items", 2, ["aliases: [A, B]"])])

    def test_no_frontmatter_no_hit(self):
        self.assertEqual(D.check_text("# Title\n\n- [name] x\n", "atlas/topics/a.md"), [])

    def test_key_line_swallowed_by_a_flow_list_needs_review(self):
        # The retyping passes refuse this note and point to this check, so the
        # check must report it even when no repair can be computed.
        text = '---\ntitle: Notes\ntags: ["a\ntype: note\n  b"]\n---\nBody\n'
        hits = D.check_text(text, "sources/internal/ops/2026-01-01-note-x.md")
        self.assertEqual([(h.shape, h.line, h.needs_review) for h in hits],
                         [("swallowed-key-line", 3, True)])
        self.assertIn("type: note", hits[0].what)

    def test_swallowed_key_reported_next_to_an_unrelated_shape(self):
        text = '---\naliases: [A]\n- B\ntitle: A\ntags: ["a\ntype: note\n  b"]\n---\nBody\n'
        shapes = [h.shape for h in D.check_text(text, "atlas/topics/a.md")]
        self.assertEqual(sorted(shapes), ["stray-alias-items", "swallowed-key-line"])

    def test_shapes_with_their_own_repair_are_not_reported_twice(self):
        text = "---\ntitle: 'Atelier : l''inventaire\ntype: meeting\n  du site'\n---\nBody\n"
        shapes = [h.shape for h in D.check_text(text, "sources/internal/ops/meetings/2026-01-01-meeting-x.md")]
        self.assertEqual(shapes, ["type-inside-folded-title"])


if __name__ == "__main__":
    unittest.main()
