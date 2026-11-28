#!/usr/bin/env python3
"""Tests for `check_harness_compat.py`, on temporary fixture trees only.

Run from the workspace root:

    python3 -I -m unittest discover -s basic-memory/scripts -p 'test_*.py'
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_harness_compat as C  # noqa: E402


def skill(name="demo", description="Does a thing.", extra="", body="Body.\n"):
    return "---\nname: %s\ndescription: %s\n%s---\n\n%s" % (name, description, extra, body)


class Tree(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="compat-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.write("AGENTS.md", "# Rules\n")
        self.write(".claude/skills/demo/SKILL.md", skill())
        (self.root / ".agents").mkdir()
        os.symlink("../.claude/skills", self.root / ".agents" / "skills")
        (self.root / ".kiro").mkdir()
        os.symlink("../.claude/skills", self.root / ".kiro" / "skills")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def found(self, prefix=None):
        lines = C.findings(self.root)
        return [ln for ln in lines if prefix is None or ln.startswith(prefix)]


class Clean(Tree):
    def test_clean_tree_has_no_finding(self):
        self.assertEqual(self.found(), [])

    def test_cli_exit_codes(self):
        cmd = [sys.executable, "-I", str(HERE / "check_harness_compat.py"), "--root", str(self.root)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.write("CLAUDE.md", "x")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(len(proc.stdout.splitlines()), 1)


class Skills(Tree):
    def test_unknown_key(self):
        self.write(".claude/skills/demo/SKILL.md", skill(extra="model: opus\n"))
        self.assertEqual(len(self.found("skills")), 1)
        self.assertIn("`model`", self.found("skills")[0])

    def test_spec_keys_are_accepted(self):
        extra = "license: MIT\ncompatibility: any\nmetadata:\n  a: b\nallowed-tools: Bash\n"
        self.write(".claude/skills/demo/SKILL.md", skill(extra=extra))
        self.assertEqual(self.found(), [])

    def test_name_must_equal_folder(self):
        self.write(".claude/skills/demo/SKILL.md", skill(name="other"))
        self.assertIn("differs from its folder", self.found("skills")[0])

    def test_name_grammar(self):
        for bad in ("Demo", "demo-", "-demo", "de--mo", "de_mo"):
            with self.subTest(bad):
                self.write(".claude/skills/%s/SKILL.md" % bad, skill(name=bad))
                self.assertTrue(any("must match" in ln for ln in self.found("skills")), bad)

    def test_name_length(self):
        name = "a" * 65
        self.write(".claude/skills/%s/SKILL.md" % name, skill(name=name))
        self.assertTrue(any("must match" in ln for ln in self.found("skills")))

    def test_description_limits(self):
        self.write(".claude/skills/demo/SKILL.md", skill(description="a" * 1024))
        self.assertEqual(self.found(), [])
        self.write(".claude/skills/demo/SKILL.md", skill(description="a" * 1025))
        self.assertIn("1025", self.found("skills")[0])
        self.write(".claude/skills/demo/SKILL.md", "---\nname: demo\n---\n\nBody\n")
        self.assertIn("`description`", self.found("skills")[0])

    def test_compatibility_limit(self):
        self.write(".claude/skills/demo/SKILL.md", skill(extra="compatibility: %s\n" % ("a" * 501)))
        self.assertIn("501", self.found("skills")[0])

    def test_no_frontmatter(self):
        self.write(".claude/skills/demo/SKILL.md", "Body only.\n")
        self.assertIn("no frontmatter", self.found("skills")[0])


class Symlink(Tree):
    def test_missing(self):
        os.remove(self.root / ".agents" / "skills")
        self.assertIn("ln -s ../.claude/skills .agents/skills", self.found("symlink")[0])

    def test_text_file_left_by_a_checkout(self):
        os.remove(self.root / ".agents" / "skills")
        self.write(".agents/skills", "../.claude/skills")
        line = self.found("symlink")[0]
        self.assertIn("text file", line)
        self.assertIn("ln -s ../.claude/skills .agents/skills", line)

    def test_points_elsewhere(self):
        os.remove(self.root / ".agents" / "skills")
        (self.root / "other").mkdir()
        os.symlink("../other", self.root / ".agents" / "skills")
        self.assertIn("not to .claude/skills", self.found("symlink")[0])


class ClaudeMd(Tree):
    def test_found_anywhere(self):
        self.write("sources/clients/globex/CLAUDE.md", "x")
        self.write("CLAUDE.md", "x")
        lines = self.found("claude-md")
        self.assertEqual(len(lines), 2)

    def test_allowed_places(self):
        for rel in (".git/CLAUDE.md", "node_modules/pkg/CLAUDE.md", ".claude/output/CLAUDE.md",
                    ".claude/worktrees/a/CLAUDE.md"):
            self.write(rel, "x")
        self.assertEqual(self.found(), [])


class ClaudeLocal(Tree):
    def test_local_file_and_messages_by_location(self):
        self.write("CLAUDE.local.md", "x")
        self.write("sources/clients/globex/CLAUDE.md", "x")
        self.write(".claude/CLAUDE.md", "x")
        lines = {ln.split(":")[1].strip(): ln for ln in self.found("claude-md")}
        self.assertEqual(len(lines), 3)
        self.assertIn("never rename it to AGENTS.md (it would be committed)", lines["CLAUDE.local.md"])
        self.assertIn("skip the AGENTS.md of its folder and every folder below", lines["CLAUDE.local.md"])
        self.assertIn("merge it into the existing AGENTS.md", lines["sources/clients/globex/CLAUDE.md"])
        self.assertIn("move its content into .claude/rules/claude-code.md and delete it",
                      lines[".claude/CLAUDE.md"])


class ThirdPartyRepos(Tree):
    def test_nested_git_repository_is_a_warning_and_not_descended(self):
        self.write("vendor/lib/.git/HEAD", "ref")
        self.write("vendor/lib/CLAUDE.md", "x")
        lines = self.found("warning")
        self.assertEqual(len(lines), 1)
        self.assertIn("vendor/lib", lines[0])
        self.assertIn("do not rename its files", lines[0])
        self.assertEqual(self.found("claude-md"), [])

    def test_node_modules_at_any_depth_is_skipped(self):
        self.write("sources/x/node_modules/pkg/CLAUDE.md", "x")
        self.assertEqual(self.found(), [])

    def test_root_git_directory_is_not_a_warning(self):
        self.write(".git/HEAD", "ref")
        self.assertEqual(self.found(), [])


class AllowedToolsShape(Tree):
    def test_list_is_a_finding_and_string_is_not(self):
        self.write(".claude/skills/demo/SKILL.md", skill(extra="allowed-tools:\n  - Bash\n  - Read\n"))
        self.assertIn("space-separated string", self.found("skills")[0])
        self.write(".claude/skills/demo/SKILL.md", skill(extra="allowed-tools: [Bash, Read]\n"))
        self.assertIn("space-separated string", self.found("skills")[0])
        self.write(".claude/skills/demo/SKILL.md", skill(extra="allowed-tools: Bash Read\n"))
        self.assertEqual(self.found(), [])


class CopiedSkills(Tree):
    def make_copy(self):
        os.remove(self.root / ".agents" / "skills")
        shutil.copytree(self.root / ".claude" / "skills", self.root / ".agents" / "skills")

    def test_identical_real_directory_is_a_warning_with_exit_0(self):
        self.make_copy()
        lines = self.found()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("warning:"), lines[0])
        cmd = [sys.executable, "-I", str(HERE / "check_harness_compat.py"), "--root", str(self.root)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("warning:", proc.stdout)

    def test_drifted_copy_is_a_finding(self):
        self.make_copy()
        self.write(".agents/skills/demo/SKILL.md", skill(description="Changed."))
        line = self.found("symlink")[0]
        self.assertIn("ln -s ../.claude/skills .agents/skills", line)

    def test_copy_with_an_extra_skill_is_a_finding(self):
        self.make_copy()
        self.write(".agents/skills/extra/SKILL.md", skill(name="extra"))
        self.assertEqual(len(self.found("symlink")), 1)


class AgentsMd(Tree):
    def test_missing(self):
        os.remove(self.root / "AGENTS.md")
        self.assertIn("missing", self.found("agents-md")[0])

    def test_size_limit(self):
        self.write("AGENTS.md", "a" * 32768)
        self.assertEqual(self.found(), [])
        self.write("AGENTS.md", "a" * 32769)
        self.assertIn("32769", self.found("agents-md")[0])


class ToolNames(Tree):
    def test_found_in_skill_and_rule(self):
        self.write(".claude/skills/demo/SKILL.md", skill(body="Use AskUserQuestion here.\nAnd the Skill tool.\n"))
        self.write(".claude/rules/x.md", "Call TodoWrite, TaskCreate and TaskUpdate.\n")
        self.assertEqual(len(self.found("tool-names")), 5)

    def test_allowed_tools_frontmatter_is_exempt(self):
        self.write(".claude/skills/demo/SKILL.md",
                   skill(extra="allowed-tools: AskUserQuestion TodoWrite\n"))
        self.assertEqual(self.found(), [])

    def test_inline_allowed_tools_is_exempt_but_body_is_not(self):
        self.write(".claude/skills/demo/SKILL.md",
                   skill(extra="allowed-tools: AskUserQuestion\n", body="TodoWrite\n"))
        lines = self.found("tool-names")
        self.assertEqual(len(lines), 1)
        self.assertIn("TodoWrite", lines[0])

    def test_claude_code_rule_is_exempt(self):
        self.write(".claude/rules/claude-code.md", "AskUserQuestion and the Skill tool.\n")
        self.assertEqual(self.found(), [])

    def test_nested_skill_markdown_is_scanned(self):
        self.write(".claude/skills/demo/steps/one.md", "TaskCreate\n")
        self.assertEqual(len(self.found("tool-names")), 1)


class Hooks(Tree):
    def config(self, rel, command, wrap=None):
        self.write(rel, json.dumps({"hooks": {"X": [{"hooks": [{"type": "command", "command": command}]}]}}))

    def test_existing_script_passes(self):
        self.write(".claude/hooks/t.py", "")
        self.config(".codex/hooks.json", 'python3 "$(git rev-parse --show-toplevel)/.claude/hooks/t.py"')
        self.config(".claude/settings.json", 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/t.py"')
        self.config(".cursor/hooks.json", "python3 .claude/hooks/t.py")
        self.assertEqual(self.found(), [])

    def test_missing_script(self):
        self.config(".gemini/settings.json", 'python3 "$(git rev-parse --show-toplevel)/.claude/hooks/gone.py"')
        lines = self.found("hooks")
        self.assertEqual(len(lines), 1)
        self.assertIn("gone.py", lines[0])

    def test_invalid_json(self):
        self.write(".codex/hooks.json", "{nope")
        self.assertIn("not valid JSON", self.found("hooks")[0])

    def test_root_with_a_space(self):
        spaced = Path(tempfile.mkdtemp(prefix="compat ")) / "Mobile Documents" / "ws"
        self.addCleanup(shutil.rmtree, spaced.parent.parent, ignore_errors=True)
        spaced.mkdir(parents=True)
        (spaced / ".claude" / "hooks").mkdir(parents=True)
        (spaced / ".claude" / "hooks" / "t.py").write_text("")
        for rel, cmd in ((".codex/hooks.json", 'python3 "$(git rev-parse --show-toplevel)/.claude/hooks/t.py"'),
                         (".claude/settings.json", 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/t.py"'),
                         (".gemini/settings.json", 'python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/t.py"')):
            (spaced / rel).parent.mkdir(parents=True, exist_ok=True)
            (spaced / rel).write_text(json.dumps({"hooks": [{"command": cmd}]}))
        self.assertEqual(C.check_hooks(spaced), [])
        (spaced / ".claude" / "hooks" / "t.py").unlink()
        self.assertEqual(len(C.check_hooks(spaced)), 3)

    def test_fallback_forms_resolve_to_the_root(self):
        self.write(".claude/hooks/t.py", "")
        git = '$(git rev-parse --show-toplevel 2>/dev/null || pwd)'
        self.config(".gemini/settings.json", 'python3 -I "${GEMINI_PROJECT_DIR:-%s}/.claude/hooks/t.py"' % git)
        self.config(".claude/settings.json", 'python3 -I "${CLAUDE_PROJECT_DIR:-%s}/.claude/hooks/t.py"' % git)
        self.config(".qwen/settings.json", 'python3 -I "${QWEN_PROJECT_DIR:-%s}/.claude/hooks/t.py"' % git)
        self.assertEqual(self.found(), [])
        self.config(".qwen/settings.json", 'python3 -I "${QWEN_PROJECT_DIR:-%s}/.claude/hooks/gone.py"' % git)
        self.assertIn("gone.py", self.found("hooks")[0])

    def test_command_without_py_is_ignored(self):
        self.config(".codex/hooks.json", "echo hello")
        self.assertEqual(self.found(), [])

    def test_absent_configs_are_ignored(self):
        self.assertEqual(self.found("hooks"), [])


if __name__ == "__main__":
    unittest.main()


class KiroLinkTest(unittest.TestCase):
    """The `.kiro/skills` link is checked exactly like `.agents/skills`."""

    def test_missing_kiro_link_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude" / "skills").mkdir(parents=True)
            (root / ".agents").mkdir()
            os.symlink("../.claude/skills", root / ".agents" / "skills")
            findings = C.check_symlink(root)
            self.assertEqual(len(findings), 1)
            self.assertIn(".kiro/skills is missing", findings[0])

    def test_both_links_resolving_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude" / "skills").mkdir(parents=True)
            for parent in (".agents", ".kiro"):
                (root / parent).mkdir()
                os.symlink("../.claude/skills", root / parent / "skills")
            self.assertEqual(C.check_symlink(root), [])
