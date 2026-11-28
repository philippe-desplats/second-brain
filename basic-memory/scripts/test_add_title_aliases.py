#!/usr/bin/env python3
"""Tests for `add_title_aliases.py` and its hook `.claude/hooks/title_aliases.py`.

Each test builds a throwaway workspace in a temporary directory, copies the
pass, its sibling modules and the hook into it, and runs them as the CLI and
the hook run, in a subprocess. No test reads or writes the real workspace.

The note shapes are the ones real Basic Memory writes with
`basic_memory.file_utils.dump_frontmatter`, checked against it when the Basic
Memory interpreter runs the suite, plus the hand-written shapes Obsidian and
humans produce.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'

PyYAML, when importable, re-reads every written block. The pass never needs it.
"""

from __future__ import annotations

import importlib.util
import json
import ntpath
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

import add_title_aliases as A  # noqa: E402
import corpus  # noqa: E402
import frontmatter as F  # noqa: E402

try:
    import yaml
except ImportError:  # the stdlib-only interpreter
    yaml = None

SIBLINGS = ("add_title_aliases.py", "check_helpers.py", "corpus.py", "frontmatter.py")
HOOK = REPO / ".claude" / "hooks" / "title_aliases.py"

LONG_TITLE = ("Globex Website Redesign, discovery workshop outcomes and the content "
              "inventory plan for Q3")
LONG_ALIAS = ("Globex discovery workshop, the long alias that Basic Memory folds once "
              "it runs past eighty columns")

# Verbatim output of dump_frontmatter, see test_inputs_match_basic_memory.
BM_FOLDED_TITLE_IN_ALIASES = (
    "---\n"
    "title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan for Q3\n"
    "aliases:\n"
    "- Globex Website Redesign, discovery workshop outcomes and the content inventory plan\n"
    "  for Q3\n"
    "type: note\n"
    "---\n\n# H"
)
BM_FOLDED_OTHER_ALIAS = (
    "---\n"
    "title: Globex Website Redesign, discovery workshop outcomes and the content inventory\n"
    "  plan for Q3\n"
    "aliases:\n"
    "- Globex discovery workshop, the long alias that Basic Memory folds once it runs past\n"
    "  eighty columns\n"
    "type: note\n"
    "---\n\n# H"
)
BM_BACKSLASH = "---\ntitle: 'Regex: \\d+ cheatsheet'\ntype: note\n---\n\n# H"

SUMMARY_RE = re.compile(r"Candidate notes: (\d+) cited titles, (\d+) to modify, "
                        r"(\d+) already compliant, (\d+) ambiguous")


def bm_dump(metadata: dict, content: str) -> str | None:
    """dump_frontmatter of real Basic Memory, or None when it is not importable.

    Runs isolated in a subprocess: Basic Memory imports the python-frontmatter
    package, which the sibling `frontmatter.py` on this path would shadow.
    """
    code = (
        "import json, sys\n"
        "from types import SimpleNamespace\n"
        "from basic_memory.file_utils import dump_frontmatter\n"
        "meta, content = json.loads(sys.stdin.read())\n"
        "sys.stdout.write(dump_frontmatter(SimpleNamespace(metadata=meta, content=content)))\n"
    )
    proc = subprocess.run([sys.executable, "-I", "-c", code], input=json.dumps([metadata, content]),
                          capture_output=True, text=True, cwd=tempfile.gettempdir())
    if proc.returncode != 0:
        return None
    return proc.stdout


class Workspace:
    """A temporary workspace holding the pass, its siblings and the hook."""

    def __init__(self, case: unittest.TestCase):
        self.root = Path(tempfile.mkdtemp(prefix="aliases-"))
        case.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        scripts = self.root / "basic-memory" / "scripts"
        scripts.mkdir(parents=True)
        for name in SIBLINGS:
            shutil.copy(HERE / name, scripts / name)
        hooks = self.root / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        shutil.copy(HOOK, hooks / HOOK.name)
        self.pass_path = scripts / "add_title_aliases.py"
        self.hook_path = hooks / HOOK.name

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(self.pass_path), "--root", str(self.root), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=60)

    def hook(self, event: dict, env: dict | None = None) -> subprocess.CompletedProcess:
        environ = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        environ.update(env or {})
        return subprocess.run([sys.executable, "-I", str(self.hook_path)], input=json.dumps(event),
                              cwd=self.root, capture_output=True, text=True, timeout=60, env=environ)


def summary(proc: subprocess.CompletedProcess) -> tuple[int, int, int, int]:
    m = SUMMARY_RE.search(proc.stdout)
    if not m:
        raise AssertionError("no summary line in:\n%s\n%s" % (proc.stdout, proc.stderr))
    return tuple(int(x) for x in m.groups())


def aliases_of(text: str):
    doc = F.split(text)
    return F.parse(doc.block).get("aliases")


class Base(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace(self)

    def cite(self, *titles: str, rel: str = "sources/internal/links/2026-01-01-note-links.md") -> None:
        body = "\n".join("- see [[%s]]" % t for t in titles)
        self.ws.write(rel, "---\ntitle: Links\ntype: note\n---\n\n%s\n" % body)

    def assert_valid_yaml(self, text: str) -> dict | None:
        """The block parses as YAML when PyYAML is here, and as frontmatter always."""
        doc = F.split(text)
        self.assertIsNotNone(doc)
        F.parse(doc.block)
        if yaml is None:
            return None
        data = yaml.safe_load(doc.block)
        self.assertIsInstance(data, dict)
        return data

    def apply_ok(self, *args: str) -> tuple[int, int, int, int]:
        proc = self.ws.run("--apply", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return summary(proc)


class InputShapes(unittest.TestCase):
    def test_inputs_match_basic_memory(self):
        cases = [
            ({"title": LONG_TITLE, "aliases": [LONG_TITLE], "type": "note"}, BM_FOLDED_TITLE_IN_ALIASES),
            ({"title": LONG_TITLE, "aliases": [LONG_ALIAS], "type": "note"}, BM_FOLDED_OTHER_ALIAS),
            ({"title": "Regex: \\d+ cheatsheet", "type": "note"}, BM_BACKSLASH),
        ]
        for meta, expected in cases:
            dumped = bm_dump(meta, "# H")
            if dumped is None:
                self.skipTest("Basic Memory is not importable from this interpreter")
            self.assertEqual(dumped, expected)


class FoldedAliases(Base):
    """H1: a list item folded over 2 lines is one item, and a rewrite keeps it whole."""

    NOTE = "sources/clients/globex/website/2026-01-02-note-discovery.md"

    def test_folded_title_already_in_aliases_is_compliant(self):
        self.ws.write(self.NOTE, BM_FOLDED_TITLE_IN_ALIASES)
        self.cite(LONG_TITLE)
        self.assertEqual(self.apply_ok()[1:3], (0, 1))
        self.assertEqual(self.ws.read(self.NOTE), BM_FOLDED_TITLE_IN_ALIASES)

    def test_apply_dump_apply_chain(self):
        self.ws.write(self.NOTE, BM_FOLDED_OTHER_ALIAS)
        self.cite(LONG_TITLE)
        self.assertEqual(self.apply_ok()[1], 1)
        written = self.ws.read(self.NOTE)
        expected = [LONG_TITLE, LONG_ALIAS]
        self.assertEqual(aliases_of(written), expected)
        data = self.assert_valid_yaml(written)
        if data is not None:
            self.assertEqual(data["aliases"], expected)
            self.assertEqual(data["title"], LONG_TITLE)
            dumped = bm_dump(data, F.split(written).body.lstrip("\n"))
            if dumped is not None:
                self.ws.write(self.NOTE, dumped)
                self.assertEqual(aliases_of(dumped), expected)
        before = self.ws.read(self.NOTE)
        self.assertEqual(self.apply_ok()[1:3], (0, 1))
        self.assertEqual(self.ws.read(self.NOTE), before)


class Exclusion(Base):
    """M4: --exclude stops the write on that note, never the ambiguity guard."""

    A_NOTE = "sources/internal/alpha/2026-01-03-note-shared.md"
    B_NOTE = "sources/internal/beta/2026-01-03-note-shared.md"

    def test_write_event_keeps_shared_title_ambiguous(self):
        self.ws.write(self.A_NOTE, "---\ntitle: Shared Title\ntype: note\n---\n\n# A\n")
        self.ws.write(self.B_NOTE, "---\ntitle: Shared Title\ntype: note\n---\n\n# B\n")
        self.cite("Shared Title")
        before_b = self.ws.read(self.B_NOTE)
        proc = self.ws.hook({"tool_name": "Write",
                             "tool_input": {"file_path": str(self.ws.root / self.A_NOTE)}})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertEqual(self.ws.read(self.B_NOTE), before_b)
        self.assertIsNone(aliases_of(self.ws.read(self.A_NOTE)))
        self.assertEqual(summary(self.ws.run())[3], 1)

    def test_excluded_note_is_not_written(self):
        self.ws.write(self.A_NOTE, "---\ntitle: Alone\ntype: note\n---\n\n# A\n")
        self.cite("Alone")
        self.apply_ok("--exclude", self.A_NOTE)
        self.assertIsNone(aliases_of(self.ws.read(self.A_NOTE)))

    def test_backslash_exclude_matches(self):
        """B7: a Windows relative path names the same note."""
        self.ws.write(self.A_NOTE, "---\ntitle: Alone\ntype: note\n---\n\n# A\n")
        self.cite("Alone")
        self.apply_ok("--exclude", self.A_NOTE.replace("/", "\\"))
        self.assertIsNone(aliases_of(self.ws.read(self.A_NOTE)))


class WindowsPaths(unittest.TestCase):
    """B7: relative paths reach the zone and exclusion checks with forward slashes."""

    def test_relpath_normalised(self):
        rel = ntpath.join("sources", "internal", "alpha", "note.md")
        self.assertIn("\\", rel)
        self.assertEqual(A.to_posix(rel), "sources/internal/alpha/note.md")
        self.assertTrue(A.writable(rel, ".", set()))
        self.assertFalse(A.writable(rel, ".", {A.to_posix(rel)}))
        self.assertFalse(A.writable(ntpath.join("docs", "x.md"), ".", set()))

    def test_exclude_normalised(self):
        self.assertEqual(A.normalise_excludes([".\\sources\\a.md", "sources/b.md"]),
                         {"sources/a.md", "sources/b.md"})


class Quoting(Base):
    NOTE = "knowledge/tech/pattern-regex.md"

    def test_backslash_title_round_trips(self):
        """M5: a backslash is escaped on write, read back equal, and written once."""
        title = "Regex: \\d+ cheatsheet"
        self.ws.write(self.NOTE, BM_BACKSLASH)
        self.cite(title)
        self.assertEqual(self.apply_ok()[1], 1)
        written = self.ws.read(self.NOTE)
        self.assertEqual(aliases_of(written), [title])
        data = self.assert_valid_yaml(written)
        if data is not None:
            self.assertEqual(data["aliases"], [title])
        self.assertEqual(self.apply_ok()[1:3], (0, 1))
        self.assertEqual(self.ws.read(self.NOTE), written)

    def test_double_quoted_title_with_escapes_resolves(self):
        """B8: the escapes of a double-quoted title are decoded before matching."""
        self.ws.write(self.NOTE, '---\ntitle: "The \\"Fast\\" Track"\ntype: note\n---\n\n# H\n')
        self.cite('The "Fast" Track')
        self.assertEqual(self.apply_ok()[1], 1)
        written = self.ws.read(self.NOTE)
        self.assertEqual(aliases_of(written), ['The "Fast" Track'])
        self.assert_valid_yaml(written)
        self.assertEqual(self.apply_ok()[1:3], (0, 1))

    def test_link_escaped_for_a_table_cell_cites_its_target(self):
        """`[[X\\|y]]`, the form a table row needs, cites X."""
        self.ws.write(self.NOTE, "---\ntitle: Onboarding\ntype: note\n---\n\n# H\n")
        self.cite("Onboarding\\|the onboarding")
        self.assertEqual(self.apply_ok()[1], 1)
        self.assertEqual(aliases_of(self.ws.read(self.NOTE)), ["Onboarding"])

    def test_apostrophe_mid_word_stays_one_item(self):
        self.ws.write(self.NOTE, "---\ntitle: Onboarding\naliases: [l'onboarding, kickoff]\ntype: note\n---\n\n# H\n")
        self.cite("Onboarding")
        self.assertEqual(self.apply_ok()[1], 1)
        written = self.ws.read(self.NOTE)
        self.assertEqual(aliases_of(written), ["Onboarding", "l'onboarding", "kickoff"])
        data = self.assert_valid_yaml(written)
        if data is not None:
            self.assertEqual(data["aliases"], ["Onboarding", "l'onboarding", "kickoff"])
        self.assertEqual(self.apply_ok()[1:3], (0, 1))

    def test_retyped_words_are_quoted(self):
        """Yes, null and 2026 would read back as a boolean, a null and a number."""
        notes = {"Yes": "knowledge/tech/pattern-yes.md",
                 "null": "knowledge/tech/pattern-null.md",
                 "2026": "knowledge/tech/pattern-year.md"}
        for title, rel in notes.items():
            self.ws.write(rel, "---\ntitle: '%s'\ntype: note\n---\n\n# H\n" % title)
        self.cite(*notes)
        self.assertEqual(self.apply_ok()[1], 3)
        for title, rel in notes.items():
            written = self.ws.read(rel)
            self.assertIn('aliases: ["%s"]' % title, written)
            data = self.assert_valid_yaml(written)
            if data is not None:
                self.assertEqual(data["aliases"], [title])


class Hook(Base):
    def load_hook(self):
        spec = importlib.util.spec_from_file_location("title_aliases_hook", HOOK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_zone_predicate_comes_from_corpus(self):
        hook = self.load_hook()
        self.assertFalse(hasattr(hook, "NOTE_ZONES"))
        self.assertIs(hook.in_note_zone, corpus.in_note_zone)
        self.assertEqual(hook.TIMEOUT, 30)

    def test_edit_outside_note_zones_does_not_run_the_pass(self):
        note = "atlas/topics/onboarding.md"
        self.ws.write(note, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        self.ws.write("docs/guide.md", "See [[Onboarding]].\n")
        proc = self.ws.hook({"tool_name": "Edit", "tool_input": {"file_path": str(self.ws.root / "docs/guide.md")}})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertIsNone(aliases_of(self.ws.read(note)))

    def test_edit_in_note_zone_runs_the_pass_silently(self):
        note = "atlas/topics/onboarding.md"
        self.ws.write(note, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        self.cite("Onboarding")
        proc = self.ws.hook({"tool_name": "Edit", "tool_input": {
            "file_path": str(self.ws.root / "sources/internal/links/2026-01-01-note-links.md")}})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertEqual(aliases_of(self.ws.read(note)), ["Onboarding"])

    def test_bad_input_fails_open(self):
        proc = subprocess.run([sys.executable, "-I", str(self.ws.hook_path)], input="not json",
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))


class HookHarnesses(Base):
    """The hook reads the event of any harness and finds its workspace by itself."""

    NOTE = "atlas/topics/onboarding.md"

    def setUp(self):
        super().setUp()
        self.ws.write(self.NOTE, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        self.cite("Onboarding")

    def assert_aliased(self, event, env=None):
        proc = self.ws.hook(event, env)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertEqual(aliases_of(self.ws.read(self.NOTE)), ["Onboarding"])

    def assert_untouched(self, event, env=None):
        proc = self.ws.hook(event, env)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertIsNone(aliases_of(self.ws.read(self.NOTE)))

    def path(self, rel="sources/internal/links/2026-01-01-note-links.md"):
        return str(self.ws.root / rel)

    def test_tool_input_path(self):
        self.assert_aliased({"tool_input": {"path": self.path()}})

    def test_tool_input_absolute_path(self):
        self.assert_aliased({"tool_name": "write_file", "tool_input": {"absolute_path": self.path()}})

    def test_top_level_file_path_cursor(self):
        self.assert_aliased({"hook_event_name": "afterFileEdit", "file_path": self.path()})

    def test_camel_case_file_path(self):
        self.assert_aliased({"tool_input": {"filePath": self.path()}})
        self.ws.write(self.NOTE, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        self.assert_aliased({"filePath": self.path()})

    def test_top_level_path(self):
        self.assert_aliased({"path": self.path()})

    def test_found_path_outside_note_zones_does_nothing(self):
        self.assert_untouched({"tool_input": {"path": self.path("docs/guide.md")}})

    def test_non_markdown_path_does_nothing(self):
        self.assert_untouched({"file_path": self.path("sources/internal/x/data.json")})

    def test_no_path_runs_the_full_pass(self):
        self.assert_aliased({"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch"}})

    def test_empty_object_does_nothing(self):
        self.assert_untouched({})

    def test_read_and_search_tools_exit_at_once(self):
        for tool in ("Read", "Grep", "read_file", "Bash", "glob"):
            with self.subTest(tool):
                self.assert_untouched({"tool_name": tool, "tool_input": {"file_path": self.path()}})

    def test_tool_names_are_case_insensitive(self):
        self.assert_aliased({"tool_name": "WRITE_FILE", "tool_input": {"path": self.path()}})

    def test_replace_is_an_edit_and_not_excluded(self):
        self.assert_aliased({"tool_name": "replace", "tool_input": {"file_path": self.path(self.NOTE)}})

    def test_apply_patch_path_is_extracted(self):
        patch = "*** Begin Patch\n*** Update File: %s\n@@\n-a\n+b\n*** End Patch" % self.NOTE
        self.assert_untouched({"tool_name": "apply_patch", "tool_input": {"command": patch}})
        patch = "*** Begin Patch\n*** Add File: docs/x.md\n+a\n*** End Patch"
        self.assert_untouched({"tool_name": "apply_patch", "tool_input": {"input": patch}})
        patch = "*** Begin Patch\n*** Add File: sources/internal/links/2026-01-01-note-links.md\n+a\n*** End Patch"
        self.assert_aliased({"tool_name": "apply_patch", "tool_input": {"command": patch}})

    def test_a_held_lock_makes_the_second_pass_exit(self):
        import fcntl
        lock = self.ws.root / ".claude" / "output" / ".alias-pass.lock"
        lock.parent.mkdir(parents=True)
        with open(lock, "w") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            self.assert_untouched({"tool_name": "Write", "tool_input": {"file_path": self.path()}})
        self.assert_aliased({"tool_name": "Write", "tool_input": {"file_path": self.path()}})

    def test_write_of_the_target_excludes_it(self):
        self.assert_untouched({"tool_name": "Write", "tool_input": {"file_path": self.path(self.NOTE)}})

    def test_empty_stdin_fails_open(self):
        proc = subprocess.run([sys.executable, "-I", str(self.ws.hook_path)], input="",
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))

    def test_non_object_json_fails_open(self):
        proc = subprocess.run([sys.executable, "-I", str(self.ws.hook_path)], input="[1, 2]",
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))

    def test_script_location_wins_over_claude_project_dir(self):
        other = Workspace(self)
        other.write(self.NOTE, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        link = "sources/internal/links/2026-01-01-note-links.md"
        other.write(link, "---\ntitle: Links\ntype: note\n---\n\n- see [[Onboarding]]\n")
        proc = self.ws.hook({"file_path": self.path()}, {"CLAUDE_PROJECT_DIR": str(other.root)})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertEqual(aliases_of(self.ws.read(self.NOTE)), ["Onboarding"])
        self.assertIsNone(aliases_of(other.read(self.NOTE)))

    def test_claude_project_dir_is_only_a_fallback(self):
        other = Workspace(self)
        other.write(self.NOTE, "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        link = "sources/internal/links/2026-01-01-note-links.md"
        other.write(link, "---\ntitle: Links\ntype: note\n---\n\n- see [[Onboarding]]\n")
        shutil.rmtree(self.ws.root / "basic-memory")
        proc = self.ws.hook({"file_path": str(other.root / link)}, {"CLAUDE_PROJECT_DIR": str(other.root)})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))

    def test_script_location_is_the_default_root(self):
        self.assert_aliased({"file_path": self.path()})


class Check(Base):
    """`--check` reports through the exit code and writes nothing."""

    NOTE = "atlas/topics/onboarding.md"
    TEXT = "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n"

    def test_exit_1_when_a_note_would_change_and_nothing_is_written(self):
        self.ws.write(self.NOTE, self.TEXT)
        self.cite("Onboarding")
        proc = self.ws.run("--check")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.ws.read(self.NOTE), self.TEXT)

    def test_exit_0_when_nothing_to_do(self):
        self.ws.write(self.NOTE, self.TEXT)
        self.assertEqual(self.ws.run("--check").returncode, 0)

    def test_exit_0_when_already_compliant(self):
        self.ws.write(self.NOTE, self.TEXT)
        self.cite("Onboarding")
        self.apply_ok()
        self.assertEqual(self.ws.run("--check").returncode, 0)

    def test_quiet_check_prints_nothing(self):
        self.ws.write(self.NOTE, self.TEXT)
        self.cite("Onboarding")
        proc = self.ws.run("--check", "--quiet")
        self.assertEqual((proc.returncode, proc.stdout), (1, ""))

    def test_check_ignores_apply(self):
        self.ws.write(self.NOTE, self.TEXT)
        self.cite("Onboarding")
        proc = self.ws.run("--check", "--apply")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.ws.read(self.NOTE), self.TEXT)


class Report(Base):
    def test_dry_run_writes_nothing_and_keeps_the_report(self):
        note = "atlas/topics/onboarding.md"
        original = "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n"
        self.ws.write(note, original)
        self.cite("Onboarding")
        proc = self.ws.run()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(summary(proc), (1, 1, 0, 0))
        self.assertIn("aliases: [Onboarding]", proc.stdout)
        self.assertIn("DRY-RUN, nothing written. Add --apply to write.", proc.stdout)
        self.assertEqual(self.ws.read(note), original)

    def test_quiet_prints_nothing(self):
        self.ws.write("atlas/topics/onboarding.md", "---\ntitle: Onboarding\ntype: topic\n---\n\n# H\n")
        self.cite("Onboarding")
        proc = self.ws.run("--apply", "--quiet")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_crlf_and_insertion_after_title(self):
        note = "atlas/topics/onboarding.md"
        self.ws.write(note, "---\r\ntitle: Onboarding\r\ntype: topic\r\n---\r\n\r\n# H\r\n")
        self.cite("Onboarding")
        self.apply_ok()
        raw = (self.ws.root / note).read_bytes().decode("utf-8")
        self.assertEqual(raw, "---\r\ntitle: Onboarding\r\naliases: [Onboarding]\r\ntype: topic\r\n---\r\n\r\n# H\r\n")

    def test_note_outside_corpus_never_written(self):
        note = "sources/internal/kit/prompts/onboarding.md"
        original = "---\ntitle: Onboarding\ntype: note\n---\n\n# H\n"
        self.ws.write(note, original)
        self.cite("Onboarding")
        self.assertEqual(self.apply_ok()[0], 0)
        self.assertEqual(self.ws.read(note), original)


if __name__ == "__main__":
    unittest.main()
