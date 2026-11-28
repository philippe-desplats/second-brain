#!/usr/bin/env python3
"""Check that the workspace stays usable from every agent harness.

The instruction file is `AGENTS.md`, the skills follow the Agent Skills spec
and live in `.claude/skills`, reached by the other harnesses through the
`.agents/skills` symlink. This check finds what silently breaks that:

    skills     a SKILL.md frontmatter key outside the Agent Skills spec, a name
               that differs from its folder or breaks the name grammar, a
               description or a compatibility longer than the spec allows
    symlink    `.agents/skills` missing, a text file left by a checkout without
               symlink support, or pointing somewhere else than `.claude/skills`
    claude-md  a `CLAUDE.md` anywhere in the tree, which makes Claude Code skip
               the `AGENTS.md` of the same folder
    agents-md  the root `AGENTS.md` missing, or larger than the 32768 bytes
               Codex reads (`project_doc_max_bytes`)
    tool-names a harness-specific tool name in a skill or a rule, other than in
               an `allowed-tools:` list and in `.claude/rules/claude-code.md`
    hooks      a hook config that is not JSON, or whose command names a `.py`
               file that does not exist

Prints one line per finding and exits 1, prints nothing and exits 0 when clean.
A line starting with `warning:` is shown but does not change the exit code.
Read-only. Standard library only.

Usage:
    python3 basic-memory/scripts/check_harness_compat.py
    python3 basic-memory/scripts/check_harness_compat.py --root path/to/workspace
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent.parent

SKILL_KEYS = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
AGENTS_MD_MAX_BYTES = 32768

# Directories a CLAUDE.md may sit in without harm, relative to the root.
CLAUDE_MD_ALLOWED = (".claude/output", ".claude/worktrees")
# Directory names skipped at any depth.
CLAUDE_MD_ANY_DEPTH = (".git", "node_modules")

CLAUDE_MD_NAMES = ("CLAUDE.md", "CLAUDE.local.md")

# Tool names that exist in one harness only.
TOOL_NAME_RE = re.compile(r"\b(?:AskUserQuestion|TaskCreate|TaskUpdate|TodoWrite)\b|\bSkill tool\b")
TOOL_NAME_EXEMPT_RULES = (".claude/rules/claude-code.md",)

HOOK_CONFIGS = (".claude/settings.json", ".codex/hooks.json", ".gemini/settings.json", ".cursor/hooks.json",
                ".qwen/settings.json")
# A placeholder without a space stands for the root while a command is split,
# since the real root may hold spaces.
ROOT_MARK = "__WORKSPACE_ROOT__"
# Innermost first: `$(git rev-parse --show-toplevel ... || pwd)`, then every
# `${VAR}` or `${VAR:-default}` and `$VAR` of a project dir, then `$PWD`.
GIT_ROOT_RE = re.compile(r"\$\(git rev-parse --show-toplevel[^)]*\)")
ROOT_VARIABLES_RE = re.compile(r"\$\{[A-Z_]+(?::-[^}]*)?\}|\$[A-Z_]*PROJECT_DIR\b|\$PWD\b")
PY_PATH_RE = re.compile(r"""[^\s"'`;|&<>()]+\.py\b""")


def check_skills(root: Path) -> list[str]:
    """The Agent Skills spec, applied to every `.claude/skills/*/SKILL.md`."""
    out: list[str] = []
    skills = root / ".claude" / "skills"
    if not skills.is_dir():
        return out
    for skill_md in sorted(skills.glob("*/SKILL.md")):
        rel = skill_md.relative_to(root).as_posix()
        folder = skill_md.parent.name
        doc = F.split(skill_md.read_text(encoding="utf-8", errors="replace"))
        if doc is None:
            out.append("skills: %s: no frontmatter" % rel)
            continue
        fm = F.parse(doc.block)
        for key in fm.keys():
            if key not in SKILL_KEYS:
                out.append("skills: %s: key `%s` is not in the Agent Skills spec" % (rel, key))
        name = fm.get("name")
        if not isinstance(name, str) or not name:
            out.append("skills: %s: `name` is missing" % rel)
        else:
            if name != folder:
                out.append("skills: %s: name `%s` differs from its folder `%s`" % (rel, name, folder))
            if not NAME_RE.match(name) or len(name) > NAME_MAX:
                out.append("skills: %s: name `%s` must match %s and hold 1 to %d characters"
                           % (rel, name, NAME_RE.pattern, NAME_MAX))
        tools = fm.field("allowed-tools")
        if tools is not None and (isinstance(tools.value, list) or tools.style in ("flow", "block", "nested")):
            out.append("skills: %s: `allowed-tools` must be one space-separated string, not a YAML list" % rel)
        description = fm.get("description")
        if not isinstance(description, str) or not description.strip():
            out.append("skills: %s: `description` is missing or empty" % rel)
        elif len(description) > DESCRIPTION_MAX:
            out.append("skills: %s: description holds %d characters, the limit is %d"
                       % (rel, len(description), DESCRIPTION_MAX))
        if "compatibility" in fm:
            compatibility = fm.get("compatibility")
            if not isinstance(compatibility, str):
                out.append("skills: %s: `compatibility` must be a string" % rel)
            elif len(compatibility) > COMPATIBILITY_MAX:
                out.append("skills: %s: compatibility holds %d characters, the limit is %d"
                           % (rel, len(compatibility), COMPATIBILITY_MAX))
    return out


def same_skills(copy: Path, original: Path) -> bool:
    """Same skill folders, same SKILL.md bytes."""
    def skills(base: Path) -> dict:
        return {d.name: (d / "SKILL.md").read_bytes() if (d / "SKILL.md").is_file() else None
                for d in base.iterdir() if d.is_dir()}
    return skills(copy) == skills(original)


SKILL_LINKS = (".agents", ".kiro")


def check_one_link(root: Path, parent: str) -> list[str]:
    """`<parent>/skills` must resolve to `.claude/skills`."""
    name = "%s/skills" % parent
    link = root / parent / "skills"
    target = root / ".claude" / "skills"
    repair = "repair: ln -s ../.claude/skills %s" % name
    if not os.path.lexists(link):
        return ["symlink: %s is missing, %s" % (name, repair)]
    if link.is_file() and not link.is_symlink():
        return ["symlink: %s is a text file, a checkout without symlink support, %s" % (name, repair)]
    if not link.is_dir():
        return ["symlink: %s is a broken link, %s" % (name, repair)]
    if link.resolve() != target.resolve():
        if not link.is_symlink() and same_skills(link, target):
            return ["warning: symlink: %s is a real copy of .claude/skills, identical today, "
                    "it will drift, %s" % (name, repair)]
        return ["symlink: %s resolves to %s, not to .claude/skills, %s"
                % (name, link.resolve(), repair)]
    return []


def check_symlink(root: Path) -> list[str]:
    """`.agents/skills` and `.kiro/skills` must resolve to `.claude/skills`."""
    findings: list[str] = []
    for parent in SKILL_LINKS:
        findings += check_one_link(root, parent)
    return findings


def check_claude_md(root: Path) -> list[str]:
    """No CLAUDE.md or CLAUDE.local.md outside the folders where it is harmless.

    A directory below the root that holds its own `.git` is a third-party
    repository: the walk stops there and reports it, since its own instruction
    files may be loaded by a harness.
    """
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath).relative_to(root).as_posix()
        here = "" if here == "." else here
        kept = []
        for d in sorted(dirnames):
            rel = here + "/" + d if here else d
            if d in CLAUDE_MD_ANY_DEPTH or rel in CLAUDE_MD_ALLOWED:
                continue
            if (Path(dirpath) / d / ".git").exists():
                out.append("warning: claude-md: %s is a third-party repository, a harness may load its "
                           "AGENTS.md or CLAUDE.md as instructions, do not rename its files, move it "
                           "outside the workspace or keep an archive" % rel)
                continue
            kept.append(d)
        dirnames[:] = kept
        for name in CLAUDE_MD_NAMES:
            if name not in filenames:
                continue
            rel = (here + "/" + name) if here else name
            if name == "CLAUDE.local.md":
                fix = "move its content into a local rule or delete it, never rename it to AGENTS.md (it would be committed)"
            elif here == ".claude":
                fix = "move its content into .claude/rules/claude-code.md and delete it"
            else:
                fix = "rename it to AGENTS.md or merge it into the existing AGENTS.md"
            out.append("claude-md: %s: a %s makes Claude Code skip the AGENTS.md of its folder and every "
                       "folder below, %s" % (rel, name, fix))
    return out


def check_agents_md(root: Path) -> list[str]:
    path = root / "AGENTS.md"
    if not path.is_file():
        return ["agents-md: AGENTS.md is missing at the workspace root"]
    size = path.stat().st_size
    if size > AGENTS_MD_MAX_BYTES:
        return ["agents-md: AGENTS.md holds %d bytes, Codex reads %d at most" % (size, AGENTS_MD_MAX_BYTES)]
    return []


def exempt_lines(text: str) -> set[int]:
    """1-based numbers of the lines of an `allowed-tools:` frontmatter field."""
    doc = F.split(text)
    if doc is None:
        return set()
    field = F.parse(doc.block).field("allowed-tools")
    if field is None:
        return set()
    # Block line i sits on file line i + 2, the opening delimiter being line 1.
    return {i + 2 for i in range(field.start, field.end)}


def check_tool_names(root: Path) -> list[str]:
    out: list[str] = []
    files = sorted((root / ".claude" / "skills").rglob("*.md")) if (root / ".claude" / "skills").is_dir() else []
    rules = root / ".claude" / "rules"
    if rules.is_dir():
        files += sorted(rules.glob("*.md"))
    for path in files:
        rel = path.relative_to(root).as_posix()
        if rel in TOOL_NAME_EXEMPT_RULES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        skip = exempt_lines(text)
        for number, line in enumerate(text.splitlines(), 1):
            if number in skip:
                continue
            for match in TOOL_NAME_RE.finditer(line):
                out.append("tool-names: %s:%d: `%s` is specific to one harness" % (rel, number, match.group(0)))
    return out


def commands_in(value) -> list[str]:
    """Every string held by a `command` key, at any depth of a parsed JSON value."""
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "command" and isinstance(item, str):
                found.append(item)
            else:
                found += commands_in(item)
    elif isinstance(value, list):
        for item in value:
            found += commands_in(item)
    return found


def check_hooks(root: Path) -> list[str]:
    out: list[str] = []
    for rel in HOOK_CONFIGS:
        path = root / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            out.append("hooks: %s: not valid JSON (%s)" % (rel, exc))
            continue
        for command in commands_in(data):
            command = ROOT_VARIABLES_RE.sub(ROOT_MARK, GIT_ROOT_RE.sub(ROOT_MARK, command))
            for token in PY_PATH_RE.findall(command):
                if "$" in token:
                    continue  # an unknown variable, nothing to verify
                if token.startswith(ROOT_MARK):
                    target = root / token[len(ROOT_MARK):].lstrip("/")
                else:
                    target = Path(token)
                    if not target.is_absolute():
                        target = root / target
                if not target.is_file():
                    out.append("hooks: %s: command names %s, which does not exist" % (rel, token))
    return out


def findings(root: Path) -> list[str]:
    root = Path(root)
    return (check_skills(root) + check_symlink(root) + check_claude_md(root) + check_agents_md(root)
            + check_tool_names(root) + check_hooks(root))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(WORKSPACE), help="workspace root (default: this workspace)")
    args = parser.parse_args(argv)
    lines = findings(Path(args.root))
    for line in lines:
        print(line)
    return 1 if any(not line.startswith("warning:") for line in lines) else 0


if __name__ == "__main__":
    sys.exit(main())
