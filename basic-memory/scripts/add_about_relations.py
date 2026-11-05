#!/usr/bin/env python3
"""
Add an `- about [[Entity]]` relation to emails and meetings based on their path.

Scope: the two note types whose path names the entity they concern, an email
filed in a project's `emails/` folder and a meeting filed in its `meetings/`
folder, in every source zone:

  - sources/clients/{slug}/{project}/emails/*.md and .../meetings/*.md
  - sources/partners/{slug}/{project}/emails/*.md and .../meetings/*.md
  - sources/internal/{project}/emails/*.md and .../meetings/*.md
  - sources/personal/{project}/emails/*.md and .../meetings/*.md

Other notes are left alone: a project brief declares its entity in `client:`
or `partner:`, and the other types state their own subject. Only corpus notes
are visited, through `corpus.iter_corpus_notes`, so the pass never writes into
a folder corpus.py excludes, a `repo-files/` or `prompts/` folder among them.

The entity each path resolves to:

  - clients and partners, the `client:` or `partner:` field of
    sources/{zone}/{slug}/CLAUDE.md, `title:` as a fallback
  - internal, the `organization` of .sb-config.json. While it is null, as in a
    workspace /sb-init has not configured, internal notes are skipped rather
    than given a link to nothing
  - personal, the `title:` of the project's README.md, its folder name as a
    fallback

Inserts `- about [[Canonical Name]]` inside a `## Relations` section
(created just before `## Observations` or appended at end of body). The
frontmatter is kept byte for byte, only the body is rewritten.

Idempotent: skips files that already contain an `about [[...]]` line.

Usage:
    python3 basic-memory/scripts/add_about_relations.py --dry-run
    python3 basic-memory/scripts/add_about_relations.py --apply
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from frontmatter import read_file, split, write_file  # noqa: E402

# The project subfolders this pass annotates, see the module docstring.
TARGET_FOLDERS = ("emails", "meetings")
# Path depth of a target, counted in segments: `sources/{zone}/{slug}/{project}/{folder}/{file}`
# for an entity zone, one segment less where the zone has no entity level.
ENTITY_ZONES = {"clients": 6, "partners": 6}
PROJECT_ZONES = {"internal": 5, "personal": 5}

INTERNAL = "__INTERNAL__"
PERSONAL = "__PERSONAL__"


def scalar(fm, key: str):
    """The value of `key` when it is a non-empty string, else None."""
    value = fm.get(key) if fm is not None else None
    return value.strip() or None if isinstance(value, str) else None


def internal_entity(root: Path = WORKSPACE):
    """The internal entity name, the `organization` of .sb-config.json, or None."""
    try:
        config = json.loads((root / ".sb-config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = config.get("organization") if isinstance(config, dict) else None
    return name.strip() or None if isinstance(name, str) else None


def build_entity_map(root: Path = WORKSPACE):
    """Return {(zone, slug) -> canonical_name} from the clients' and partners' CLAUDE.md."""
    mapping = {}
    for zone, field in (("clients", "client"), ("partners", "partner")):
        for p in sorted((root / "sources" / zone).glob("*/CLAUDE.md")):
            _doc, fm = read_file(p)
            canonical = scalar(fm, field) or scalar(fm, "title")
            if canonical:
                mapping[(zone, p.parent.name)] = canonical
    return mapping


def find_target_files(root: Path = WORKSPACE):
    """Return a list of (path, rel, slug) for every email and meeting to annotate.

    `slug` is `(zone, entity)` for a client or a partner, INTERNAL for an
    internal project, and PERSONAL followed by the folder name for a personal
    project.
    """
    targets = []
    for path, rel in iter_corpus_notes(root, zones=("sources",)):
        parts = rel.split("/")
        if len(parts) < 2 or parts[-2] not in TARGET_FOLDERS:
            continue
        zone = parts[1]
        if ENTITY_ZONES.get(zone) == len(parts):
            targets.append((path, rel, (zone, parts[2])))
        elif zone == "internal" and PROJECT_ZONES[zone] == len(parts):
            targets.append((path, rel, INTERNAL))
        elif zone == "personal" and PROJECT_ZONES[zone] == len(parts):
            targets.append((path, rel, PERSONAL + parts[2]))
    return targets


def has_about_relation(body: str) -> bool:
    """Check whether the body already contains an `about [[...]]` line."""
    return bool(re.search(r"^\s*-\s+about\s+\[\[.+?\]\]", body, re.MULTILINE))


def inject_about_line(body: str, canonical: str) -> str:
    """Insert `- about [[Canonical]]` in a `## Relations` section.

    Strategy:
    - If `## Relations` exists, append the line at the end of that section
    - Else create `## Relations` section just before `## Observations` if present
    - Else append at end of body

    The caller has already ruled out a body holding an `about` line.
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


def resolve(slug, entity_map: dict, root: Path, internal):
    """The canonical name a target's slug stands for, or None."""
    if slug == INTERNAL:
        return internal
    if isinstance(slug, str) and slug.startswith(PERSONAL):
        project_slug = slug[len(PERSONAL):]
        readme = root / "sources" / "personal" / project_slug / "README.md"
        _doc, fm = read_file(readme) if readme.is_file() else (None, None)
        return scalar(fm, "title") or project_slug
    return entity_map.get(slug)


def process_file(path: Path, canonical, apply: bool, internal_skip: bool = False):
    """Return (status, message) for a single file."""
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    doc = split(text)
    body = doc.body if doc is not None else text
    if has_about_relation(body):
        return ("skip", "already has about [[...]]")
    if internal_skip:
        return ("skip", "internal entity not configured, `organization` is null in .sb-config.json")
    if not canonical:
        return ("error", "entity not resolved in entity map")
    new_body = inject_about_line(body, canonical)
    if new_body == body:
        return ("skip", "idempotent no-op")
    if apply:
        if doc is not None:
            doc.body = new_body
            write_file(path, doc)
        else:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_body)
    return ("ok", f"→ about [[{canonical}]]")


def run(root: Path = WORKSPACE, apply: bool = False):
    """Annotate every target under `root`. Return (entity_map, [(rel, status, message)])."""
    entity_map = build_entity_map(root)
    internal = internal_entity(root)
    results = []
    for path, rel, slug in find_target_files(root):
        canonical = resolve(slug, entity_map, root, internal)
        status, msg = process_file(path, canonical, apply,
                                   internal_skip=slug == INTERNAL and internal is None)
        results.append((rel, status, msg))
    return entity_map, results


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 add_about_relations.py --dry-run | --apply")
        sys.exit(1)
    apply = sys.argv[1] == "--apply"

    entity_map, results = run(WORKSPACE, apply)

    print(f"=== add_about_relations, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    print(f"Entities resolved: {len(entity_map)}")
    print(f"Target files scanned: {len(results)}")
    print()

    counts = {"ok": 0, "skip": 0, "error": 0}
    internal_skipped = 0
    for rel, status, msg in results:
        counts[status] += 1
        if status == "ok":
            print(f"  [OK]    {rel}  {msg}")
        elif status == "error":
            print(f"  [ERR]   {rel}  {msg}")
        elif msg.startswith("internal entity not configured"):
            internal_skipped += 1
        # other skips are silent

    if internal_skipped:
        print(f"  {internal_skipped} internal note(s) skipped: set `organization` in .sb-config.json (run /sb-init)")
    print()
    print(f"Summary: {counts['ok']} modified, {counts['skip']} skipped, {counts['error']} errors")


if __name__ == "__main__":
    main()
