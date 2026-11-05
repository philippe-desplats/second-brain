#!/usr/bin/env python3
"""PostToolUse: keep Obsidian resolving the wikilinks Basic Memory resolves.

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

On a Write, the written note itself is excluded from the pass, so a hook of your
own running in parallel on the same event cannot race it on that file. The note
is picked up by the next pass, on the next Write or Edit anywhere in the note
zones.

It rewrites files after the tool ran, so a note the session holds in mind may be
one line behind disk. An Edit refused as stale right afterwards needs a re-read,
nothing more.

Fails open on any error or timeout: a metadata pass must never break a write.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SCRIPTS = WORKSPACE / "basic-memory" / "scripts"
PASS = SCRIPTS / "add_title_aliases.py"
TIMEOUT = 30

sys.path.insert(0, str(SCRIPTS))
try:
    from corpus import in_note_zone
except Exception:  # no corpus.py means no pass to run either, fail open
    in_note_zone = None


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


def main() -> None:
    try:
        data = json.load(sys.stdin)
        tool = data.get("tool_name")
        if tool not in ("Write", "Edit"):
            return
        raw = (data.get("tool_input") or {}).get("file_path")
        rel = note_zone_markdown(raw) if isinstance(raw, str) else None
        if rel is None:
            return
        cmd = [sys.executable, str(PASS), "--apply", "--quiet", "--root", str(WORKSPACE)]
        if tool == "Write":
            cmd += ["--exclude", rel]
        subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, timeout=TIMEOUT)
    except Exception:
        return


if __name__ == "__main__":
    main()
