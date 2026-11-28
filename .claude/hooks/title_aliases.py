#!/usr/bin/env python3
"""Post-edit hook: keep Obsidian resolving the wikilinks Basic Memory resolves.

Basic Memory resolves a wikilink on `title:`, Obsidian on the basename only.
`basic-memory/scripts/add_title_aliases.py` bridges the two by adding each
cited note's own title to its aliases, which the Alias Linker community plugin
then resolves. Obsidian alone ignores aliases for resolution. Run once, the pass
decays: every note that becomes the target of a new wikilink starts without the
alias. This hook reruns the pass after every Write or Edit of a note-zone markdown
file, so the graph stays resolved without anyone remembering to.

Bound to Edit as well as Write: an Edit that adds a wikilink creates exactly the
need this pass answers, on the target note rather than on the edited one.

The pass itself decides what it may write, through `corpus.is_corpus_note`.
This hook only decides when to run it: a markdown file under a note zone, asked
of `corpus.in_note_zone` so the list of zones is defined once.

Harness-agnostic. The workspace root is two levels above this script, and only
when that folder holds no `basic-memory/scripts` does the hook fall back on
`$CLAUDE_PROJECT_DIR`. It acts on write or edit events only: a `tool_name` in
`WRITE_TOOLS` (case-insensitive), or no `tool_name` and a file path (Cursor
`afterFileEdit`). Any other tool, a Read or a Bash, exits at once. The edited
path is the first found of `tool_input.file_path`, `path`, `absolute_path`,
`filePath`, then a top-level `file_path`, `path` or `filePath`. For an
`apply_patch`, the first `*** Update File:` or `*** Add File:` line of the patch.
A write event carrying no path runs the full pass with no exclusion.

On any event but an Edit or a `replace`, the written note itself is excluded
from the pass, so a hook of your own running in parallel on the same event
cannot race it on that file. The note is picked up by the next pass, on the next
edit anywhere in the note zones. A non-blocking lock keeps 2 passes from running
at once, the second one exits.

It rewrites files after the tool ran, so a note the session holds in mind may be
one line behind disk. An Edit refused as stale right afterwards needs a re-read,
nothing more.

Fails open on any error or timeout: a metadata pass must never break a write.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import fcntl
except ImportError:  # no POSIX locking here, the pass runs unlocked
    fcntl = None

TIMEOUT = 30
WRITE_TOOLS = frozenset({"write", "edit", "multiedit", "notebookedit", "write_file", "replace",
                         "apply_patch", "edit_file", "create_file", "str_replace_based_edit_tool"})
EDIT_TOOLS = frozenset({"edit", "replace"})
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Update|Add) File: (.+?)\s*$", re.MULTILINE)
LOCK = Path(".claude") / "output" / ".alias-pass.lock"


def workspace_root() -> Path:
    """The repository this script lives in, `$CLAUDE_PROJECT_DIR` only as a fallback."""
    here = Path(__file__).resolve().parents[2]
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and not (here / "basic-memory" / "scripts").is_dir():
        return Path(env)
    return here


WORKSPACE = workspace_root()
SCRIPTS = WORKSPACE / "basic-memory" / "scripts"
PASS = SCRIPTS / "add_title_aliases.py"

sys.path.insert(0, str(SCRIPTS))
try:
    from corpus import in_note_zone
except Exception:  # no corpus.py means no pass to run either, fail open
    in_note_zone = None


def patch_path(tool_input) -> str | None:
    """The first file an `apply_patch` names, None when it names none."""
    if isinstance(tool_input, dict):
        text = tool_input.get("command") or tool_input.get("input") or ""
    else:
        text = tool_input
    if isinstance(text, list):
        text = "\n".join(str(part) for part in text)
    match = PATCH_FILE_RE.search(text) if isinstance(text, str) else None
    return match.group(1) if match else None


def event_path(data: dict) -> str | None:
    """The edited file path of an event, whatever the harness, None when it has none."""
    tool_input = data.get("tool_input")
    fields = tool_input if isinstance(tool_input, dict) else {}
    candidates = (fields.get("file_path"), fields.get("path"), fields.get("absolute_path"),
                  fields.get("filePath"), data.get("file_path"), data.get("path"), data.get("filePath"))
    for value in candidates:
        if isinstance(value, str) and value:
            return value
    if str(data.get("tool_name", "")).lower() == "apply_patch":
        return patch_path(tool_input)
    return None


def note_zone_markdown(raw: str) -> str | None:
    """The workspace-relative path when it is a note-zone markdown file."""
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = WORKSPACE / path
    try:
        rel = path.resolve().relative_to(WORKSPACE.resolve())
    except (OSError, ValueError):
        return None
    if in_note_zone is None or path.suffix != ".md" or not in_note_zone(rel.as_posix()):
        return None
    return rel.as_posix()


def run_pass(cmd: list[str]) -> None:
    """Run the pass unless another one holds the lock."""
    if fcntl is None:
        subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, timeout=TIMEOUT)
        return
    lock = WORKSPACE / LOCK
    lock.parent.mkdir(parents=True, exist_ok=True)
    with open(lock, "w") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
        subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, timeout=TIMEOUT)


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input) if raw_input.strip() else {}
        if not isinstance(data, dict):
            return
        tool = data.get("tool_name")
        tool = tool.lower() if isinstance(tool, str) else None
        raw = event_path(data)
        if tool is None:
            if raw is None:
                return
        elif tool not in WRITE_TOOLS:
            return
        cmd = [sys.executable, str(PASS), "--apply", "--quiet", "--root", str(WORKSPACE)]
        if raw is not None:
            rel = note_zone_markdown(raw)
            if rel is None:
                return
            if tool not in EDIT_TOOLS:
                cmd += ["--exclude", rel]
        run_pass(cmd)
    except Exception:
        return


if __name__ == "__main__":
    main()
