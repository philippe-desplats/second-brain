#!/usr/bin/env python3
"""
Add an `- about [[Project]]` relation to emails and meetings based on their path.

Scope: the two note types whose path names the project they concern, an email
filed in a project's `emails/` folder and a meeting filed in its `meetings/`
folder, in every source zone:

  - sources/clients/{slug}/{project}/emails/*.md and .../meetings/*.md
  - sources/partners/{slug}/{project}/emails/*.md and .../meetings/*.md
  - sources/internal/{project}/emails/*.md and .../meetings/*.md
  - sources/personal/{project}/emails/*.md and .../meetings/*.md

Other notes are left alone. Only corpus notes are visited, through
`corpus.iter_corpus_notes`, so the pass never writes into a folder corpus.py
excludes, a `repo-files/` or `prompts/` folder among them.

The target is the project brief, as `basic-memory/schemas/email.md` and
`meeting.md` type `about`: the `title:` of the `README.md` of the note's
project folder, or of its `CLAUDE.md`, declaring `type: project-brief`. The
entity is never the target, `client:` or `partner:` carries it. A note whose
project has no such brief, or a brief without a title, gets nothing and is
listed in the report with the reason. Which folder is the project and which
file is its brief is decided by `note_types.project_brief`, the rule the
damage check also reads.

Inserts `- about [[Project title]]` inside a `## Relations` section
(created just before `## Observations` or appended at end of body). The
frontmatter is kept byte for byte, only the body is rewritten.

Idempotent: a note whose `about` already links its project, by the brief's
title or one of its aliases, is skipped. A note whose `about` links something
else, the entity an older version wrote included, gets the project added next
to it. `check_frontmatter_damage.py` reports the entity line as
about-entity-not-project.

Usage:
    python3 basic-memory/scripts/add_about_relations.py --dry-run
    python3 basic-memory/scripts/add_about_relations.py --apply
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_helpers import WIKILINK_RE  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from frontmatter import read_file, split, write_file  # noqa: E402
from note_types import project_brief, project_folder  # noqa: E402

# The project subfolders this pass annotates, see the module docstring.
TARGET_FOLDERS = ("emails", "meetings")
# Path depth of a target, counted in segments: `sources/{zone}/{slug}/{project}/{folder}/{file}`
# for an entity zone, one segment less where the zone has no entity level.
TARGET_DEPTH = {"clients": 6, "partners": 6, "internal": 5, "personal": 5}

ABOUT_PREFIX_RE = re.compile(r"^\s*-\s+about\s+(?=\[\[)", re.MULTILINE)


def find_target_files(root: Path = WORKSPACE):
    """Return a list of (path, rel, project folder) for every email and meeting to annotate."""
    targets = []
    for path, rel in iter_corpus_notes(root, zones=("sources",)):
        parts = rel.split("/")
        if len(parts) < 2 or parts[-2] not in TARGET_FOLDERS:
            continue
        if TARGET_DEPTH.get(parts[1]) == len(parts):
            targets.append((path, rel, project_folder(rel)))
    return targets


def about_targets(body: str):
    """The target of every `- about [[...]]` line of the body."""
    targets = []
    for m in ABOUT_PREFIX_RE.finditer(body):
        link = WIKILINK_RE.match(body, m.end())
        if link is not None:
            targets.append(link.group(1).strip())
    return targets


def inject_about_line(body: str, canonical: str) -> str:
    """Insert `- about [[Canonical]]` in a `## Relations` section.

    Strategy:
    - If `## Relations` exists, append the line at the end of that section
    - Else create `## Relations` section just before `## Observations` if present
    - Else append at end of body

    The caller has already ruled out a body linking the project.
    """
    about_line = f"- about [[{canonical}]]"

    # Case 1, Relations section exists
    rel_pattern = re.compile(r"^##\s+Relations\s*$", re.MULTILINE)
    m = rel_pattern.search(body)
    if m:
        section_start = m.end()
        next_section = re.search(r"\n##\s+\S", body[section_start:])
        if next_section:
            insert_at = section_start + next_section.start()
            existing_block = body[section_start:insert_at]
            new_block = existing_block.rstrip() + f"\n{about_line}\n"
            return body[:section_start] + "\n" + new_block.lstrip("\n") + body[insert_at:]
        existing_tail = body[section_start:]
        return body[:section_start] + "\n" + existing_tail.lstrip("\n").rstrip() + f"\n{about_line}\n"

    # Case 2, Observations section exists, insert Relations just before it
    obs_pattern = re.compile(r"^##\s+Observations\s*$", re.MULTILINE)
    m = obs_pattern.search(body)
    if m:
        insert_at = m.start()
        prefix = body[:insert_at].rstrip() + "\n\n"
        return prefix + f"## Relations\n\n{about_line}\n\n" + body[insert_at:]

    # Case 3, no Relations nor Observations, append at end
    return body.rstrip() + "\n\n## Relations\n\n" + about_line + "\n"


def frontmatter_reader(root: Path):
    """`frontmatter_of(rel)` for `note_types.project_brief`, reading the disk under `root`."""
    def frontmatter_of(rel):
        path = root / rel
        if not path.is_file():
            return None
        try:
            return read_file(path)[1]
        except (OSError, UnicodeDecodeError):
            return None
    return frontmatter_of


def process_file(path: Path, brief, why, apply: bool):
    """Return (status, message) for a single file."""
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    doc = split(text)
    body = doc.body if doc is not None else text
    if brief is None:
        return ("no-brief", why)
    if brief.names & set(about_targets(body)):
        return ("skip", "already links its project")
    new_body = inject_about_line(body, brief.title)
    if new_body == body:
        return ("skip", "idempotent no-op")
    if apply:
        if doc is not None:
            doc.body = new_body
            write_file(path, doc)
        else:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_body)
    return ("ok", f"→ about [[{brief.title}]]")


def run(root: Path = WORKSPACE, apply: bool = False):
    """Annotate every target under `root`. Return ({folder: brief or None}, [(rel, status, message)])."""
    frontmatter_of = frontmatter_reader(root)
    briefs, results = {}, []
    for path, rel, folder in find_target_files(root):
        if folder not in briefs:
            briefs[folder] = project_brief(folder, frontmatter_of)
        brief, why = briefs[folder]
        status, msg = process_file(path, brief, why, apply)
        results.append((rel, status, msg))
    return {folder: brief for folder, (brief, _why) in briefs.items()}, results


def report(briefs: dict, results: list, apply: bool) -> None:
    """Print what `run` did or would do: every write and every note left without a brief."""
    print(f"=== add_about_relations, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    print(f"Project briefs resolved: {sum(1 for b in briefs.values() if b is not None)} of {len(briefs)}")
    print(f"Target files scanned: {len(results)}")
    print()
    counts = {"ok": 0, "skip": 0, "no-brief": 0}
    for rel, status, msg in results:
        counts[status] += 1
        if status == "ok":
            print(f"  [OK]    {rel}  {msg}")
        elif status == "no-brief":
            print(f"  [NO BRIEF] {rel}  {msg}")
        # skips are silent
    print()
    print(f"Summary: {counts['ok']} modified, {counts['skip']} skipped, "
          f"{counts['no-brief']} without a project brief")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 add_about_relations.py --dry-run | --apply")
        sys.exit(1)
    apply = sys.argv[1] == "--apply"
    briefs, results = run(WORKSPACE, apply)
    report(briefs, results, apply)


if __name__ == "__main__":
    main()
