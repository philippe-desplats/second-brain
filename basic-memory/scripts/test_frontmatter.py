#!/usr/bin/env python3
"""Tests for `frontmatter.py` and the path helpers of `corpus.py`.

The fixtures under `tests_fixtures/` were written once by real Basic Memory
(`basic_memory.file_utils.dump_frontmatter`), each `bm-*.txt` next to the
`.json` metadata it was dumped from, plus two `hand-*.txt` files for the
shapes Basic Memory never writes. They are `.txt` so no pass and no index ever
mistakes them for notes.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'

The validity tests re-read every rendered block with PyYAML when it is
importable, and skip otherwise. The scripts never need PyYAML, only this check.
"""

from __future__ import annotations

import json
import ntpath
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import corpus  # noqa: E402
import frontmatter as F  # noqa: E402
import note_types  # noqa: E402

try:
    import yaml
except ImportError:  # the stdlib-only interpreter
    yaml = None

FIXTURES = HERE / "tests_fixtures"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def bm_fixtures():
    for txt in sorted(FIXTURES.glob("bm-*.txt")):
        meta = json.loads(txt.with_suffix(".json").read_text(encoding="utf-8"))
        yield txt.stem, txt.read_text(encoding="utf-8"), meta


def as_expected(value):
    """What the reader returns for a metadata value: strings, lists of strings, None."""
    if isinstance(value, dict):
        return None
    if isinstance(value, list):
        return [str(v) for v in value]
    return None if value is None else str(value)


def fm_of(text: str) -> F.Frontmatter:
    doc = F.split(text)
    assert doc is not None
    return F.parse(doc.block)


def yaml_load(block: str):
    return yaml.safe_load(block) if block.strip() else {}


class SplitJoin(unittest.TestCase):
    def test_round_trip_every_fixture(self):
        for txt in sorted(FIXTURES.glob("*.txt")):
            text = txt.read_text(encoding="utf-8")
            doc = F.split(text)
            self.assertIsNotNone(doc, txt.name)
            self.assertEqual(F.join(doc), text, txt.name)
            self.assertEqual(F.join(doc, F.parse(doc.block)), text, txt.name)

    def test_no_frontmatter(self):
        for text in ("", "# Title\n", "--- \nx: 1\n---\n", "----\nx: 1\n---\n",
                     "---\nx: 1\n", "\n---\nx: 1\n---\n", "---"):
            self.assertIsNone(F.split(text), repr(text))

    def test_rule_in_body_is_not_part_of_block(self):
        text = "---\ntitle: A\n---\n\nIntro\n\n---\n\nmore: text\n---\n"
        doc = F.split(text)
        self.assertEqual(doc.block, "title: A\n")
        self.assertEqual(doc.body, "\nIntro\n\n---\n\nmore: text\n---\n")
        self.assertEqual(F.parse(doc.block).keys(), ["title"])

    def test_dots_closer(self):
        doc = F.split(fixture("hand-mixed.txt"))
        self.assertEqual(doc.closer, "...")
        self.assertEqual(doc.body, "Body after a dots closer.\n")

    def test_crlf_and_bom(self):
        text = "\ufeff---\r\ntitle: A\r\ntags:\r\n- x\r\n---\r\nBody\r\nline\r\n"
        doc = F.split(text)
        self.assertTrue(doc.bom)
        self.assertEqual(doc.newline, "\r\n")
        self.assertEqual(doc.block, "title: A\ntags:\n- x\n")
        self.assertEqual(F.join(doc), text)
        fm = F.parse(doc.block)
        F.set_field(fm, "title", "B")
        self.assertEqual(F.join(doc, fm),
                         "\ufeff---\r\ntitle: B\r\ntags:\r\n- x\r\n---\r\nBody\r\nline\r\n")

    def test_file_ending_on_closer(self):
        for text in ("---\ntitle: A\n---", "---\n---\n", "---\n\n---\nx"):
            self.assertEqual(F.join(F.split(text)), text)

    def test_empty_block(self):
        doc = F.split("---\n---\nBody\n")
        self.assertEqual(doc.block, "")
        self.assertEqual(F.parse(doc.block).fields, [])

    def test_read_and_write_file_keep_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            path.write_bytes(b"---\r\ntitle: A\r\n---\r\nBody\r\n")
            doc, fm = F.read_file(path)
            self.assertFalse(F.write_file(path, doc, fm))
            F.set_field(fm, "type", "note")
            self.assertTrue(F.write_file(path, doc, fm))
            self.assertEqual(path.read_bytes(), b"---\r\ntitle: A\r\ntype: note\r\n---\r\nBody\r\n")
            path.write_text("no frontmatter\n", encoding="utf-8")
            self.assertEqual(F.read_file(path), (None, None))


class ParseBasicMemory(unittest.TestCase):
    def test_values_match_dumped_metadata(self):
        for name, text, meta in bm_fixtures():
            fm = fm_of(text)
            self.assertEqual(fm.keys(), list(meta), name)
            for key, value in meta.items():
                self.assertEqual(fm.get(key), as_expected(value), "%s %s" % (name, key))

    def test_folded_title_range(self):
        fm = fm_of(fixture("bm-folded-title.txt"))
        title = fm.field("title")
        self.assertEqual((title.start, title.end, title.style), (0, 2, "plain"))
        self.assertTrue(fm.lines[1].startswith("  plan for Q3"))

    def test_folded_alias_item_range(self):
        fm = fm_of(fixture("bm-folded-alias.txt"))
        aliases = fm.field("aliases")
        self.assertEqual((aliases.start, aliases.end, aliases.style, aliases.indent),
                         (2, 5, "block", ""))
        self.assertEqual(len(aliases.value), 1)
        self.assertTrue(aliases.value[0].endswith("plan for Q3"))

    def test_nested_mapping(self):
        fm = fm_of(fixture("bm-nested.txt"))
        meta = fm.field("meta")
        self.assertEqual((meta.value, meta.style, meta.start, meta.end), (None, "nested", 1, 8))
        self.assertEqual(fm.get("type"), "note")

    def test_double_quoted_escapes(self):
        fm = fm_of(fixture("bm-double-quoted.txt"))
        self.assertTrue(fm.get("title").startswith("Tab\there"))
        self.assertIn('"q" \\ end', fm.get("aliases")[0])
        self.assertEqual(fm.get("aliases")[1], "caf\u00e9 \u2028 sep")


class ParseHandWritten(unittest.TestCase):
    def test_block_scalars(self):
        fm = fm_of(fixture("hand-block-scalars.txt"))
        self.assertEqual(fm.get("literal"), "First line\n  indented line\n\nafter blank\n")
        self.assertEqual(fm.get("strip"), "no trailing newline")
        self.assertEqual(fm.get("keep"), "kept trailing\n\n")
        self.assertEqual(fm.get("folded"),
                         "folded one folded two\nnew paragraph\n  more indented\nback\n")
        self.assertEqual(fm.get("folded_strip"), "a b")
        self.assertEqual(fm.get("explicit"), "  two extra spaces\n")
        self.assertEqual(fm.field("keep").end, fm.field("folded").start)
        self.assertEqual([f.style for f in fm.fields][:3], ["plain", "literal", "literal"])

    def test_mixed_shapes(self):
        fm = fm_of(fixture("hand-mixed.txt"))
        self.assertEqual(fm.get("title"), "Mixed shapes")
        self.assertEqual(fm.get("aliases"),
                         ["four space item", 'double "quoted" item', "single 'quoted' item"])
        self.assertEqual(fm.field("aliases").indent, "    ")
        self.assertEqual(fm.get("tags"), ["l'onboarding", "kickoff", "b, c", "d'e", "plain item"])
        self.assertEqual(fm.get("topics"), ["alpha", "beta folded over two lines"])
        for key in ("empty", "nothing", "tilde"):
            self.assertIsNone(fm.get(key, "absent"), key)
        self.assertEqual(fm.get("status"), "active")
        self.assertIn("# T3", fm.lines[fm.field("status").start])
        self.assertEqual(fm.get("folded_plain"), "first part second part\nafter blank")
        self.assertEqual(fm.get("quoted_folded"), "single quoted over two lines")
        self.assertEqual(fm.get("next_line_value"), "a value on the next line")
        self.assertEqual(fm.get("url"), "https://example.com/a#b")
        self.assertEqual(fm.field("flow_map").style, "nested")
        self.assertEqual(fm.field("title").start, 1)

    def test_matches_pyyaml_on_hand_fixtures(self):
        if yaml is None:
            self.skipTest("PyYAML not installed")
        for name in ("hand-block-scalars.txt", "hand-mixed.txt"):
            doc = F.split(fixture(name))
            expected = yaml.safe_load(doc.block)
            fm = F.parse(doc.block)
            for key, value in expected.items():
                self.assertEqual(fm.get(key), as_expected(value), "%s %s" % (name, key))

    def test_tab_and_two_space_indented_lists(self):
        fm = F.parse("a:\n\t- one\n\t- two\nb:\n  - three\n  - four\n    folded\nc: x\n")
        self.assertEqual(fm.get("a"), ["one", "two"])
        self.assertEqual(fm.field("a").indent, "\t")
        self.assertEqual(fm.get("b"), ["three", "four folded"])
        self.assertEqual((fm.field("b").start, fm.field("b").end), (3, 7))
        self.assertEqual(fm.get("c"), "x")

    def test_flow_list_edge_cases(self):
        fm = F.parse("a: [l'onboarding, kickoff]\nb: []\nc: [\"x\\\"y\", 'it''s']\n"
                     "d: [one,\n  two]\ne: [[nested], x]\nf: [x] # note\n")
        self.assertEqual(fm.get("a"), ["l'onboarding", "kickoff"])
        self.assertEqual(fm.get("b"), [])
        self.assertEqual(fm.get("c"), ['x"y', "it's"])
        self.assertEqual(fm.get("d"), ["one", "two"])
        self.assertEqual(fm.field("e").style, "nested")
        self.assertEqual(fm.get("f"), ["x"])

    def test_quoted_scalars(self):
        fm = F.parse("a: 'it''s'\nb: \"q \\\" \\\\ \\n \\t \\/ \\u00e9\"\n"
                     "c: \"line one\\\n  \\ two\"\nd: 'x' # c\ne: \"a\n\n  b\"\n")
        self.assertEqual(fm.get("a"), "it's")
        self.assertEqual(fm.get("b"), 'q " \\ \n \t / \u00e9')
        self.assertEqual(fm.get("c"), "line one two")
        self.assertEqual(fm.get("d"), "x")
        self.assertEqual(fm.get("e"), "a\nb")

    def test_comments_and_null(self):
        fm = F.parse("# top\na: x # c\n# between\nb: ~\nc: null\nd:\n# end\n")
        self.assertEqual(fm.keys(), ["a", "b", "c", "d"])
        self.assertEqual(fm.get("a"), "x")
        self.assertEqual((fm.get("b"), fm.get("c"), fm.get("d")), (None, None, None))
        self.assertEqual(fm.get("missing", "dflt"), "dflt")
        self.assertEqual((fm.field("a").start, fm.field("a").end), (1, 2))

    def test_duplicates(self):
        fm = F.parse("a: 1\nb: 2\na: 3\n")
        self.assertEqual(fm.duplicates(), ["a"])
        self.assertEqual(fm.get("a"), "1")
        F.set_field(fm, "a", "x")
        self.assertEqual(F.render(fm), "a: x\nb: 2\n")


class Edit(unittest.TestCase):
    def check_yaml(self, fm):
        if yaml is not None:
            yaml_load(F.render(fm))

    def test_set_folded_title_replaces_every_line(self):
        fm = fm_of(fixture("bm-folded-title.txt"))
        F.set_field(fm, "title", "Short: title")
        self.assertEqual(fm.lines[:2], ['title: "Short: title"', "type: meeting"])
        self.check_yaml(fm)

    def test_set_folded_alias_list_keeps_block_style(self):
        fm = fm_of(fixture("bm-folded-alias.txt"))
        title = fm.get("title")
        F.set_field(fm, "aliases", ["Short", title])
        aliases = fm.field("aliases")
        self.assertEqual(fm.lines[aliases.start:aliases.end],
                         ["aliases:", "- Short", "- " + title])
        self.assertEqual(fm.get("type"), "note")
        self.check_yaml(fm)

    def test_set_keeps_indent_of_block_list(self):
        fm = fm_of(fixture("hand-mixed.txt"))
        F.set_field(fm, "aliases", ["x", "y, z"])
        self.assertEqual(fm.lines[2:5], ["aliases:", "    - x", "    - y, z"])
        F.set_field(fm, "tags", ["a", "b, c"])
        self.assertEqual(fm.lines[fm.field("tags").start], 'tags: [a, "b, c"]')
        self.assertEqual(fm.get("topics"), ["alpha", "beta folded over two lines"])

    def test_set_explicit_style(self):
        fm = F.parse("tags: [a, b]\n")
        F.set_field(fm, "tags", ["a", "b"], style="block")
        self.assertEqual(F.render(fm), "tags:\n- a\n- b\n")
        F.set_field(fm, "tags", ["a", "b"], style="flow")
        self.assertEqual(F.render(fm), "tags: [a, b]\n")

    def test_set_on_each_shape(self):
        for txt in sorted(FIXTURES.glob("*.txt")):
            doc = F.split(txt.read_text(encoding="utf-8"))
            for key in F.parse(doc.block).keys():
                for value in ("new: value", ["one", "two, three"], None):
                    fm = F.parse(doc.block)
                    others = {k: fm.get(k) for k in fm.keys() if k != key}
                    F.set_field(fm, key, value)
                    self.assertEqual(fm.get(key), value, "%s %s" % (txt.name, key))
                    self.assertEqual({k: fm.get(k) for k in fm.keys() if k != key}, others,
                                     "%s %s" % (txt.name, key))
                    self.assertEqual(fm.keys(), F.parse(doc.block).keys())
                    self.check_yaml(fm)

    def test_set_nested_replaces_whole_mapping(self):
        fm = fm_of(fixture("bm-nested.txt"))
        F.set_field(fm, "meta", "flat")
        self.assertEqual(F.render(fm),
                         "title: Nested mapping\nmeta: flat\ntype: note\nstatus: active\n")

    def test_nested_untouched_by_other_edits(self):
        text = fixture("bm-nested.txt")
        doc = F.split(text)
        fm = F.parse(doc.block)
        F.set_field(fm, "status", "done")
        F.set_field(fm, "aliases", ["Nested mapping"], after="title")
        meta = fm.field("meta")
        original = F.parse(doc.block).field("meta")
        self.assertEqual(fm.lines[meta.start:meta.end],
                         F.parse(doc.block).lines[original.start:original.end])

    def test_insert_after_and_at_end(self):
        fm = fm_of(fixture("bm-folded-title.txt"))
        F.set_field(fm, "aliases", [fm.get("title")], after="title")
        self.assertEqual(fm.keys(), ["title", "aliases", "type", "schema_version", "date"])
        self.assertEqual(fm.field("aliases").start, 2)
        F.set_field(fm, "status", "active")
        self.assertEqual(fm.keys()[-1], "status")
        F.set_field(fm, "zz", "x", after="missing")
        self.assertEqual(fm.keys()[-1], "zz")
        self.check_yaml(fm)

    def test_insert_after_column0_list(self):
        fm = fm_of(fixture("bm-column0-aliases.txt"))
        F.set_field(fm, "status", "active", after="aliases")
        self.assertEqual(fm.lines[1:5], ["aliases:", "- Jane Doe", "- J. Doe", "status: active"])

    def test_insert_into_trailing_blank_block(self):
        fm = F.parse("a: 1\n\n")
        F.set_field(fm, "b", "x")
        self.assertEqual(F.render(fm), "a: 1\nb: x\n\n")

    def test_drop_field(self):
        fm = fm_of(fixture("bm-folded-alias.txt"))
        F.drop_field(fm, "aliases")
        F.drop_field(fm, "missing")
        self.assertEqual(fm.keys(), ["title", "type"])
        self.assertEqual(len(fm.lines), 3)
        fm = fm_of(fixture("hand-block-scalars.txt"))
        F.drop_field(fm, "keep")
        self.assertEqual(fm.get("folded"),
                         "folded one folded two\nnew paragraph\n  more indented\nback\n")
        fm = F.parse("a: 1\nb: 2\na: 3\n")
        F.drop_field(fm, "a")
        self.assertEqual(F.render(fm), "b: 2\n")

    def test_idempotent(self):
        for txt in sorted(FIXTURES.glob("*.txt")):
            doc = F.split(txt.read_text(encoding="utf-8"))
            for value in ("Regex: \\d+ cheatsheet", ["a", "b, c", "yes"], None, "plain"):
                fm = F.parse(doc.block)
                F.set_field(fm, "aliases", value, after="title")
                once = F.render(fm)
                F.set_field(fm, "aliases", value, after="title")
                self.assertEqual(F.render(fm), once, txt.name)
                F.set_field(F.parse(once), "aliases", value)
                self.assertEqual(F.render(F.set_field(F.parse(once), "aliases", value)), once)

    def test_same_value_leaves_lines_untouched(self):
        doc = F.split(fixture("bm-folded-alias.txt"))
        fm = F.parse(doc.block)
        F.set_field(fm, "aliases", fm.get("aliases"))
        F.set_field(fm, "title", fm.get("title"))
        self.assertEqual(F.render(fm), doc.block)

    def test_render_is_block(self):
        doc = F.split(fixture("bm-unicode.txt"))
        self.assertEqual(F.render(F.parse(doc.block)), doc.block)


class RenderScalar(unittest.TestCase):
    PLAIN = ["Globex", "Jane Doe", "it's done", "The \"Fast\" Track", "a:b", "a#b",
             "Réunion à Noël", "C:\\path", "100%", "plan for Q3", "2026 plan",
             "yes please", "v1.2.3-beta"]
    QUOTED = ["", " lead", "trail ", "- item", "-x", "?", ":x", "#tag", "[x]", "{x}",
              "&a", "*a", "!tag", "|", ">", "'q'", '"q"', "%x", "@x", "`x",
              "Acme: Studio", "Foo #2", "ends:", "yes", "No", "TRUE", "false", "on",
              "OFF", "y", "N", "null", "Null", "~", "2026", "-3", "+1", "1.5", ".5",
              "1e3", "0x1F", "0o17", "1_000", ".inf", ".NaN", "2026-07-02",
              "2026-07-02T10:00:00", "1:20", "<<", "=", "tab\there", "line\nbreak",
              "bell\x07", "sep\u2028x", "Regex: \\d+", "back\\slash: x", "x\ufeffy"]

    def test_plain(self):
        for value in self.PLAIN:
            self.assertEqual(F.render_scalar(value), value, repr(value))

    def test_quoted(self):
        for value in self.QUOTED:
            out = F.render_scalar(value)
            self.assertTrue(out.startswith('"') and out.endswith('"'), repr(value))

    def test_flow_context(self):
        for value in ("a, b", "x[1]", "a]", "y{z}", "a}b"):
            self.assertEqual(F.render_scalar(value), value)
            self.assertTrue(F.render_scalar(value, flow=True).startswith('"'))
        self.assertEqual(F.render_list(["a", "b, c", "d'e"]), '[a, "b, c", d\'e]')
        self.assertEqual(F.render_list([]), "[]")
        self.assertEqual(F.render_list(["a", "b: c"], "block", "  "), '  - a\n  - "b: c"')

    def test_escapes(self):
        self.assertEqual(F.render_scalar('a: "b" \\ c'), '"a: \\"b\\" \\\\ c"')
        self.assertEqual(F.render_scalar(None), "null")
        self.assertEqual(F.render_scalar("line\nbreak"), '"line\\nbreak"')

    def test_reader_reads_back_rendered(self):
        for value in self.PLAIN + self.QUOTED:
            fm = F.parse("k: %s\nl: %s\n" % (F.render_scalar(value), F.render_list([value, "z"])))
            self.assertEqual(fm.get("k"), value, repr(value))
            self.assertEqual(fm.get("l"), [value, "z"], repr(value))

    def test_valid_yaml(self):
        if yaml is None:
            self.skipTest("PyYAML not installed")
        for value in self.PLAIN + self.QUOTED:
            block = "k: %s\nl: %s\nm:\n%s\n" % (F.render_scalar(value),
                                                F.render_list([value, "z"]),
                                                F.render_list([value], "block"))
            data = yaml.safe_load(block)
            self.assertEqual(data, {"k": value, "l": [value, "z"], "m": [value]}, repr(value))

    def test_every_rendered_fixture_edit_is_valid_yaml(self):
        if yaml is None:
            self.skipTest("PyYAML not installed")
        for name, text, meta in bm_fixtures():
            fm = fm_of(text)
            for key, value in meta.items():
                if isinstance(value, dict):
                    continue
                if not isinstance(value, list):
                    value = str(value)
                F.set_field(fm, key, value, style="flow" if isinstance(value, list) else None)
                F.set_field(fm, "copy_" + key, value)
            data = yaml_load(F.render(fm))
            for key in fm.keys():
                self.assertEqual(as_expected(data[key]), fm.get(key), "%s %s" % (name, key))


# (value, rendered in block context, rendered as a flow list item). Exact
# strings, so a regression in the quoting policy fails under plain python3,
# with no PyYAML to catch it.
GOLDEN = [
    ("What changed in Q3?", "What changed in Q3?", '"What changed in Q3?"'),
    ("Quoi de neuf ?", "Quoi de neuf ?", '"Quoi de neuf ?"'),
    ("- x", '"- x"', '"- x"'),
    ("-x", '"-x"', '"-x"'),
    ("? x", '"? x"', '"? x"'),
    ("?x", '"?x"', '"?x"'),
    (": x", '": x"', '": x"'),
    ("x:", '"x:"', '"x:"'),
    ("a:b", "a:b", '"a:b"'),
    ("a: b", '"a: b"', '"a: b"'),
    ("a #b", '"a #b"', '"a #b"'),
    ("a#b", "a#b", "a#b"),
    ("!x", '"!x"', '"!x"'),
    ("&x", '"&x"', '"&x"'),
    ("*x", '"*x"', '"*x"'),
    ("%x", '"%x"', '"%x"'),
    ("@x", '"@x"', '"@x"'),
    ("`x", '"`x"', '"`x"'),
    ("|x", '"|x"', '"|x"'),
    (">x", '">x"', '">x"'),
    ("'x", '"\'x"', '"\'x"'),
    ('"x', '"\\"x"', '"\\"x"'),
    ("...x", '"...x"', '"...x"'),
    ("---", '"---"', '"---"'),
    ("l'onboarding", "l'onboarding", "l'onboarding"),
    ('The "Fast" Track', 'The "Fast" Track', 'The "Fast" Track'),
    ("x [1]", "x [1]", '"x [1]"'),
    ("{y}", '"{y}"', '"{y}"'),
    ("a,b", "a,b", '"a,b"'),
    ("Acme: Studio", '"Acme: Studio"', '"Acme: Studio"'),
    ("yes", '"yes"', '"yes"'),
    ("Off", '"Off"', '"Off"'),
    ("2026", '"2026"', '"2026"'),
    ("1.5", '"1.5"', '"1.5"'),
    ("2026-07-02", '"2026-07-02"', '"2026-07-02"'),
    ("~", '"~"', '"~"'),
    ("", '""', '""'),
    ("  x", '"  x"', '"  x"'),
    ("x\t", '"x\\t"', '"x\\t"'),
    ("café", "café", "café"),
    ("https://example.com/a#b", "https://example.com/a#b", '"https://example.com/a#b"'),
    ("C:\\path\\d+", "C:\\path\\d+", '"C:\\\\path\\\\d+"'),
]

FUZZ_ALPHABET = list("abc XYZ éà'\"\\:#,-?[]{}|>&*!%@`.~\t") + [
    "  ", ": ", " #", " ?", "- ", "? ", "\n", "l'", "yes", "null", "2026-01-01", "1.5",
    "---", "...", "\u2028", "\x85", "\ufeff", "\x00", "\x7f", "😀"]


def fuzz_values(seed: int, count: int):
    rng = random.Random(seed)
    for _ in range(count):
        text = "".join(rng.choice(FUZZ_ALPHABET) for _ in range(rng.randint(0, 12)))
        if rng.random() < 0.1:
            text = "word " * rng.randint(10, 20) + text
        yield text


class RenderPolicy(unittest.TestCase):
    def test_golden(self):
        for value, block, flow in GOLDEN:
            self.assertEqual(F.render_scalar(value), block, repr(value))
            self.assertEqual(F.render_scalar(value, flow=True), flow, repr(value))
        self.assertEqual(F.render_list(["What changed in Q3?", "Quoi de neuf ?"]),
                         '["What changed in Q3?", "Quoi de neuf ?"]')

    def test_fuzz_render_reads_back(self):
        values = list(fuzz_values(20261105, 3000))
        for n in range(0, len(values), 3):
            chunk = values[n:n + 3]
            scalar = chunk[0]
            block = "k: %s\nl: %s\nm:\n%s\n" % (F.render_scalar(scalar), F.render_list(chunk),
                                                F.render_list(chunk, "block"))
            fm = F.parse(block)
            self.assertEqual((fm.get("k"), fm.get("l"), fm.get("m")), (scalar, chunk, chunk),
                             repr(block))
            if yaml is not None:
                self.assertEqual(yaml.safe_load(block), {"k": scalar, "l": chunk, "m": chunk},
                                 repr(block))
        if yaml is None:
            self.skipTest("PyYAML not installed, the own-reader half ran")


class Defects(unittest.TestCase):
    def test_hash_continuation_inside_single_quotes(self):
        fm = F.parse("title: 'Globex website redesign weekly sync: decisions on the catalog search open\n"
                     "  #42'\ntype: meeting\n")
        title = fm.field("title")
        self.assertEqual((title.start, title.end), (0, 2))
        self.assertTrue(fm.get("title").endswith("open #42"))
        F.set_field(fm, "aliases", [fm.get("title")], after="title")
        self.assertEqual(fm.lines[1], "  #42'")
        self.assertTrue(fm.lines[2].startswith("aliases: "))
        self.assertEqual(fm.get("aliases"), [fm.get("title")])

    def test_hash_continuation_inside_double_quotes_and_items(self):
        fm = F.parse('a: "one\n  #two"\nb:\n- "x\n  #y"\n- \'z\n  #w\'\nc: 1\n')
        self.assertEqual(fm.get("a"), "one #two")
        self.assertEqual(fm.get("b"), ["x #y", "z #w"])
        self.assertEqual((fm.field("b").start, fm.field("b").end), (2, 7))
        F.set_field(fm, "d", "x", after="a")
        self.assertEqual(fm.lines[:3], ['a: "one', '  #two"', "d: x"])

    def test_hash_continuation_of_plain_scalar_is_a_comment(self):
        # PyYAML reads {'a': 'plain'}: after a space, `#` opens a comment.
        fm = F.parse("a: plain\n  #42\nb: 1\n")
        self.assertEqual(fm.get("a"), "plain")
        self.assertEqual((fm.field("a").start, fm.field("a").end), (0, 2))
        F.set_field(fm, "c", "x", after="a")
        self.assertEqual(F.render(fm), "a: plain\n  #42\nc: x\nb: 1\n")

    def test_flow_scanner_honours_escapes(self):
        fm = F.parse('a: ["Le \\"Fast\\" [\'x", b, \'it\'\'s ]\']\nb: [x?, "y]"]\n')
        self.assertEqual(fm.get("a"), ['Le "Fast" [\'x', "b", "it's ]"])
        self.assertEqual(fm.field("a").style, "flow")
        self.assertEqual(fm.get("b"), ["x?", "y]"])

    def test_flow_mapping_item_is_nested(self):
        for text in ("a: [x: y]\n", "a: [? x]\n", "a: [{b: 1}]\n", "a: [\"k\": v]\n"):
            self.assertEqual(F.parse(text).field("a").style, "nested", text)

    def test_same_value_repairs_invalid_plain(self):
        fm = F.parse("aliases: [What changed in Q3?]\ntitle: Acme: Studio\n")
        F.set_field(fm, "aliases", ["What changed in Q3?"])
        F.set_field(fm, "title", "Acme: Studio")
        self.assertEqual(F.render(fm), 'aliases: ["What changed in Q3?"]\ntitle: "Acme: Studio"\n')
        once = F.render(fm)
        F.set_field(fm, "aliases", ["What changed in Q3?"])
        self.assertEqual(F.render(fm), once)

    def test_rewrite_keeps_quoting_of_kept_items(self):
        fm = F.parse("aliases: ['Globex', \"it's\", plain]\ntags:\n  - 'a'\n  - b\n")
        F.set_field(fm, "aliases", ["New", "Globex", "it's", "plain"])
        self.assertEqual(fm.lines[0], "aliases: [New, 'Globex', \"it's\", plain]")
        F.set_field(fm, "tags", ["a", "b", "c"])
        self.assertEqual(fm.lines[1:], ["tags:", "  - 'a'", "  - b", "  - c"])
        fm = F.parse('a: ["\\q bad", ok]\n')
        F.set_field(fm, "a", ["\\q bad", "ok", "new"])
        # `\\q` is no YAML escape, so that source is not written back.
        self.assertEqual(fm.lines[0], 'a: [\\q bad, ok, new]')


# Shapes the 0.5.3 retype_files pass left behind: `type: meeting` inserted
# after the first line of the block, inside whatever field opened there.
DAMAGED = [
    ("title: 'Atelier : l''inventaire et la feuille de route pour le trimestre\n"
     "type: meeting\n  prochain, version longue'\ndate: 2026-07-01\n",
     {"title": ("Atelier : l'inventaire et la feuille de route pour le trimestre"
                " type: meeting prochain, version longue", 0, 3),
      "date": ("2026-07-01", 3, 4)}),
    ('title: "Kickoff \\\\ backslash and a long title folded past the limit\n'
     'type: meeting\n  for sure"\n',
     {"title": ("Kickoff \\ backslash and a long title folded past the limit"
                " type: meeting for sure", 0, 3)}),
    ("tags:\ntype: meeting\n  - a\n  - b\ntitle: Indented\n",
     {"tags": (None, 0, 1), "type": ("meeting - a - b", 1, 4), "title": ("Indented", 4, 5)}),
    ("notes: |\ntype: meeting\n  one\n  two\ntitle: Block\n",
     {"notes": ("", 0, 1), "type": ("meeting one two", 1, 4), "title": ("Block", 4, 5)}),
    ("tags: [a,\ntype: b,\n  c]\nz: 1\n", {"tags": ("nested", 0, 3), "z": ("1", 3, 4)}),
    ("aliases:\n- 'one\ntype: meeting\n  two'\n- three\nz: 1\n",
     {"aliases": (["one type: meeting two", "three"], 0, 5), "z": ("1", 5, 6)}),
]

# Characters `str.splitlines` breaks on and Basic Memory writes raw. The
# expected value is what PyYAML reads from the single-quoted dump.
EXOTIC = [(" ", "Plan B"), (" ", "Plan B"), ("\x85", "Plan B"),
          ("\x0b", None), ("\x0c", None), ("\x1c", None), ("\x1d", None), ("\x1e", None)]


class Cycle3(unittest.TestCase):
    def test_damaged_shapes_golden(self):
        for block, expected in DAMAGED:
            fm = F.parse(block)
            got = {}
            for f in fm.fields:
                got[f.key] = ("nested" if f.style == "nested" else f.value, f.start, f.end)
            self.assertEqual(got, expected, block)
            if yaml is not None:
                data = yaml.safe_load(block)
                self.assertEqual(sorted(data), sorted(expected), block)

    def test_damaged_title_then_set_type(self):
        for block, _ in DAMAGED[:2]:
            fm = F.parse(block)
            title = fm.get("title")
            F.set_field(fm, "type", "meeting", after="title")
            self.assertEqual(fm.get("title"), title)
            self.assertEqual(fm.field("type").start, 3)
            if yaml is not None:
                self.assertEqual(yaml.safe_load(F.render(fm))["title"], title)

    def test_exotic_line_breaks_round_trip(self):
        for ch, expected in EXOTIC:
            title_line = "title: 'Plan%s  B'" % ch if expected else "title: \"Plan%sB\"" % ch
            text = "---\n%s\naliases:\n- x\ntype: note\n---\n\nbody %s line\n" % (title_line, ch)
            doc = F.split(text)
            self.assertEqual(F.join(doc), text, repr(ch))
            self.assertEqual(doc.body, "\nbody %s line\n" % ch)
            fm = F.parse(doc.block)
            self.assertEqual(fm.keys(), ["title", "aliases", "type"], repr(ch))
            if expected:
                self.assertEqual(fm.get("title"), expected, repr(ch))
            F.set_field(fm, "aliases", ["x", "y"])
            F.set_field(fm, "status", "active")
            out = F.join(doc, fm)
            self.assertEqual(out.split("\n")[1], title_line, repr(ch))

    def test_yaml_whitespace_only(self):
        fm = F.parse("a: \xa0x\xa0\nb: x　\nc:\n-  y \nd: '\xa0q'\n")
        self.assertEqual(fm.get("a"), "\xa0x\xa0")
        self.assertEqual(fm.get("b"), "x　")
        self.assertEqual(fm.get("c"), [" y "])
        self.assertEqual(fm.get("d"), "\xa0q")
        fm = F.parse("a: x\n\xa0\nb: 1\n")
        self.assertEqual(fm.keys(), ["a", "b"])
        self.assertFalse(F._is_blank("\xa0"))
        if yaml is not None:
            self.assertEqual(yaml.safe_load("a: \xa0x\xa0\nb: x　\n"), {"a": "\xa0x\xa0", "b": "x　"})

    def test_drop_after_keep_block(self):
        cases = [
            ("keep: |+\n  keep\ntitle: x\n\nother: y\n", "title", "keep: |+\n  keep\nother: y\n"),
            ("keep: |+\n  keep\ntitle: x\n\n", "title", "keep: |+\n  keep\n"),
            ("keep: >+\n  k\n\ntitle: x\n\n\nz: 1\n", "title", "keep: >+\n  k\n\nz: 1\n"),
            ("a: |\n  k\ntitle: x\n\nz: 1\n", "title", "a: |\n  k\n\nz: 1\n"),
        ]
        for block, key, expected in cases:
            before = F.parse(block).get("keep", F.parse(block).get("a"))
            fm = F.drop_field(F.parse(block), key)
            self.assertEqual(F.render(fm), expected, block)
            self.assertEqual(fm.get("keep", fm.get("a")), before, block)

    def test_insert_at_end_after_keep_block(self):
        fm = F.parse("a: 1\nkeep: |+\n  k\n\n")
        F.set_field(fm, "zz", "v")
        self.assertEqual(F.render(fm), "a: 1\nkeep: |+\n  k\n\nzz: v\n")
        self.assertEqual(fm.get("keep"), "k\n\n")

    def test_escaped_quote_before_colon_is_no_key(self):
        # `"a\": [x"` is one scalar, the escaped quote followed by `:` opens no key.
        block = 'aliases:\n- "a\\": [x"\ntype:\n- b\n'
        fm = F.parse(block)
        self.assertEqual(fm.keys(), ["aliases", "type"])
        self.assertEqual(fm.get("aliases"), ['a": [x'])
        _check_yaml(self, block, fm)

    def test_anchor_and_tag_properties(self):
        fm = F.parse("a: &x 1\nb: !!str 2026\nc: *x\nd: &y |\n  t\n")
        self.assertEqual((fm.get("a"), fm.get("b"), fm.get("d")), ("1", "2026", "t\n"))
        self.assertEqual(fm.field("c").style, "nested")


def _check_yaml(test, block, fm):
    """Compare every non-nested field of `fm` with what PyYAML reads, when it can."""
    if yaml is None:
        return
    data = yaml.safe_load(block) or {}
    test.assertEqual(sorted(data), sorted(fm.keys()), block)
    for f in fm.fields:
        if f.style != "nested":
            test.assertEqual(as_expected(data[f.key]), f.value, block)


class Cycle3Fuzz(unittest.TestCase):
    """One generated case per defect of the third review, PyYAML-checked when present."""

    WORDS = ["alpha", "l''inventaire", "Q3?", "x: y", "#42", "a,b", "café", "\\\\", "yes", "2026"]
    INSERTS = ["type: meeting", "- item", "# hash", "key: value", "  indented", "[x, y]"]

    def test_fuzz_quoted_spans(self):
        rng = random.Random(31)
        for _ in range(400):
            quote = rng.choice("'\"")
            words = [rng.choice(self.WORDS) for _ in range(rng.randint(2, 6))]
            if quote == '"':
                words = [w.replace("''", "'").replace("\\\\", "\\\\\\\\") for w in words]
            inserted = rng.choice(self.INSERTS)
            block = "title: %s%s\n%s\n  %s%s\nz: 1\n" % (quote, " ".join(words[:1]), inserted,
                                                      " ".join(words[1:]), quote)
            fm = F.parse(block)
            title = fm.field("title")
            self.assertEqual((title.start, title.end), (0, 3), block)
            self.assertEqual(fm.keys(), ["title", "z"], block)
            self.assertIn(inserted.strip(" "), title.value, block)
            _check_yaml(self, block, fm)
            F.set_field(fm, "type", "note", after="title")
            self.assertEqual(fm.field("type").start, 3, block)

    def test_fuzz_exotic_characters(self):
        rng = random.Random(32)
        alphabet = ["a", "b", " ", "é", " ", " ", "\x85", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\xa0"]
        for _ in range(400):
            inner = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))
            title_line = "title: '%s'" % inner.replace("'", "''")
            text = "---\n%s\ntype: note\n---\nbody%s\n" % (title_line, inner)
            doc = F.split(text)
            self.assertEqual(F.join(doc), text, repr(text))
            fm = F.parse(doc.block)
            self.assertEqual(fm.keys(), ["title", "type"], repr(text))
            F.set_field(fm, "type", "meeting")
            self.assertEqual(F.join(doc, fm).split("\n")[1], title_line, repr(text))
            if yaml is not None and not any(c in inner for c in "\x0b\x0c\x1c\x1d\x1e"):
                self.assertEqual(yaml.safe_load(doc.block)["title"], fm.get("title"), repr(text))

    def test_fuzz_non_yaml_whitespace_edges(self):
        rng = random.Random(33)
        edges = ["\xa0", " ", "　", " ", " ", ""]
        for _ in range(400):
            value = rng.choice(edges) + rng.choice(["x", "plan B", "l'x"]) + rng.choice(edges)
            block = "a: %s\nb:\n- %s\nc: [%s]\n" % (value, value, value)
            fm = F.parse(block)
            self.assertEqual((fm.get("a"), fm.get("b"), fm.get("c")), (value, [value], [value]),
                             repr(block))
            _check_yaml(self, block, fm)
            self.assertEqual(F.parse("k: %s\n" % F.render_scalar(value)).get("k"), value)

    def test_fuzz_keep_blocks(self):
        rng = random.Random(34)
        for _ in range(400):
            parts = ["keep: |%s\n  text\n%s" % (rng.choice(["+", "", "-"]), "\n" * rng.randint(0, 2))]
            for key in rng.sample(["a", "b", "c"], rng.randint(1, 3)):
                parts.append("%s: v%s\n%s" % (key, key, "\n" * rng.randint(0, 2)))
            block = "".join(parts)
            fm = F.parse(block)
            keep = fm.get("keep")
            others = [k for k in fm.keys() if k != "keep"]
            op = rng.choice(["drop", "set", "new"])
            target = rng.choice(others)
            if op == "drop":
                F.drop_field(fm, target)
            elif op == "set":
                F.set_field(fm, target, "changed")
            else:
                F.set_field(fm, "zz", "new", after=rng.choice([None, target, "keep"]))
            out = F.render(fm)
            self.assertEqual(F.parse(out).get("keep"), keep, repr((block, op, target, out)))
            if yaml is not None:
                self.assertEqual(yaml.safe_load(out)["keep"], keep, repr((block, op, out)))


class DamageFacts(unittest.TestCase):
    """Grammar-level facts about a parsed block, shared by every damage guard."""

    def test_swallowed_key_line_inside_a_quoted_title(self):
        fm = F.parse('title: "Globex plan\ntype: meeting\n  for Q3"\ndate: 2026-01-02\n')
        self.assertEqual(F.swallowed_key_line(fm), "`title:` swallows the key line `type: meeting`")
        self.assertIsNone(F.swallowed_key_line(F.parse("title: Plan\n  for Q3\ntype: note\n")))

    def test_quote_closed(self):
        closed = F.parse("title: 'it''s' # kept\n")
        self.assertTrue(F.quote_closed(closed, closed.field("title")))
        escaped = F.parse('title: "C:\\\\"\n')
        self.assertTrue(F.quote_closed(escaped, escaped.field("title")))
        open_ = F.parse('title: "never closed\ntype: note\n')
        self.assertFalse(F.quote_closed(open_, open_.field("title")))
        junk = F.parse('title: "closed" then text\n')
        self.assertFalse(F.quote_closed(junk, junk.field("title")))

    def test_written_key_is_the_identifier_subset(self):
        self.assertTrue(F.WRITTEN_KEY_RE.fullmatch("project_brief-2"))
        self.assertIsNone(F.WRITTEN_KEY_RE.fullmatch("Key takeaways"))
        self.assertTrue(F.KEY_LINE_RE.match("type: note"))
        self.assertTrue(F.KEY_LINE_RE.match("aliases:"))
        self.assertIsNone(F.KEY_LINE_RE.match("Key takeaways: x"))

    def test_note_types_reuses_the_grammar_facts(self):
        self.assertIs(note_types.swallowed_key_line, F.swallowed_key_line)


class CorpusPaths(unittest.TestCase):
    def test_rel_posix(self):
        root = corpus.WORKSPACE
        self.assertEqual(corpus.rel_posix(root / "sources" / "a.md"), "sources/a.md")
        self.assertEqual(corpus.rel_posix(str(root / "atlas" / "x y.md"), str(root)), "atlas/x y.md")
        self.assertEqual(corpus.rel_posix("sources/a.md", "."),
                         os.path.relpath(os.path.abspath("sources/a.md"), os.path.abspath(".")))

    def test_windows_separators(self):
        rel = ntpath.relpath(r"C:\vault\sources\globex\prompts\p.md", r"C:\vault")
        self.assertIn("\\", rel)
        self.assertTrue(corpus.in_note_zone(rel))
        self.assertFalse(corpus.is_corpus_note(rel))
        self.assertTrue(corpus.is_corpus_note(r"sources\globex\website\note.md"))
        self.assertFalse(corpus.in_note_zone(r"templates\note.md"))

    def test_iter_corpus_notes_yields_posix_rel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("sources/a/n.md", "sources/a/prompts/p.md", "atlas/é.md",
                        "sources/a/tmp/t.md", "templates/x.md"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("x\n", encoding="utf-8")
            (root / "inbox" / "dir.md").mkdir(parents=True)
            rels = [rel for _, rel in corpus.iter_corpus_notes(root)]
            self.assertEqual(rels, ["sources/a/n.md", "atlas/é.md"])

    def test_excluded_walk_is_the_complement_of_the_corpus_walk(self):
        # Every Markdown file under a note zone is either a corpus note or an
        # excluded one, never both. Only folders that hold no notes at all,
        # `.git` and the like, are seen by neither walk.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seen = ("sources/a/n.md", "sources/a/prompts/p.md", "sources/a/repo-files/N.md",
                    "sources/a/captures/c.md", "sources/a/skills/s/SKILL.md", "sources/a/session.md",
                    "sources/a/tmp/t.md", "atlas/é.md", "inbox/i.md")
            unseen = ("sources/a/.git/g.md", "sources/a/node_modules/m.md", "templates/x.md")
            for rel in seen + unseen:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("x\n", encoding="utf-8")
            notes = [rel for _, rel in corpus.iter_corpus_notes(root)]
            excluded = [rel for _, rel in corpus.iter_excluded_notes(root)]
            self.assertEqual(sorted(notes), ["atlas/é.md", "inbox/i.md", "sources/a/n.md"])
            self.assertEqual(set(notes) & set(excluded), set())
            self.assertEqual(sorted(notes + excluded), sorted(seen))

    def test_git_ignored_is_relative_and_unquoted(self):
        for name in corpus.git_ignored():
            self.assertFalse(name.startswith('"'), name)
            self.assertTrue(corpus.in_note_zone(name), name)


if __name__ == "__main__":
    unittest.main()
