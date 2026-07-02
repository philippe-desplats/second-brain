#!/usr/bin/env python3
"""
Add `- about [[Entity]]` relation to emails/meetings based on their path.

Scans files under (layered structure):
  - sources/clients/{slug}/{project}/emails/*.md
  - sources/clients/{slug}/{project}/meetings/*.md
  - sources/partners/{slug}/{project}/emails/*.md
  - sources/partners/{slug}/{project}/meetings/*.md

Resolves {slug} to canonical name by reading `client:` or `partner:` frontmatter
field in sources/clients/{slug}/CLAUDE.md or sources/partners/{slug}/CLAUDE.md.

Inserts `- about [[Canonical Name]]` inside a `## Relations` section
(created just before `## Observations` or appended at end of body).

Idempotent: skips files that already contain an `about [[...]]` line.

Usage:
    python3 basic-memory/scripts/add_about_relations.py --dry-run
    python3 basic-memory/scripts/add_about_relations.py --apply
"""

import re
import sys
from pathlib import Path

# Canonical name of the internal/owner entity. Set by /sb-init.
INTERNAL_ENTITY = "Internal"

WORKSPACE = Path(__file__).resolve().parent.parent.parent
CLIENTS_DIR = WORKSPACE / "sources" / "clients"
PERSONAL_DIR = WORKSPACE / "sources" / "personal"
PARTNERS_DIR = WORKSPACE / "sources" / "partners"
INTERNAL_PROJECTS_DIR = WORKSPACE / "sources" / "internal"


def parse_frontmatter(path: Path):
    """Return (fm_dict, body_str). fm_dict only has top-level scalar keys."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content
    fm_raw = content[4:end]
    body = content[end + 4:]
    if body.startswith("\n"):
        body = body[1:]
    fm = {}
    for ln in fm_raw.split("\n"):
        if ln.startswith((" ", "\t", "-")):
            continue
        if ":" not in ln:
            continue
        k, _, v = ln.partition(":")
        v = v.strip().strip('"').strip("'")
        fm[k.strip()] = v
    return fm, body


def build_entity_map():
    """Return {slug -> canonical_name} by scanning clients and partners CLAUDE.md."""
    mapping = {}
    for p in sorted(CLIENTS_DIR.glob("*/CLAUDE.md")):
        fm, _ = parse_frontmatter(p)
        canonical = fm.get("client") or fm.get("title")
        if canonical:
            mapping[p.parent.name] = canonical
    for p in sorted(PARTNERS_DIR.glob("*/CLAUDE.md")):
        fm, _ = parse_frontmatter(p)
        canonical = fm.get("partner") or fm.get("title")
        if canonical:
            mapping[p.parent.name] = canonical
    return mapping


def find_target_files():
    """Return list of (path, canonical) for all .md files to annotate.

    Entities are resolved per source location:
    - sources/clients/{X}/** and sources/partners/{X}/** resolve to the entity's canonical name
    - sources/internal/** resolve to the literal INTERNAL_ENTITY name

    Excludes each entity's own CLAUDE.md and CONTEXT.md at the entity root.
    """
    targets = []
    for base_dir in (CLIENTS_DIR, PARTNERS_DIR):
        for entity_dir in sorted(base_dir.glob("*/")):
            if not entity_dir.is_dir():
                continue
            slug = entity_dir.name
            for md in entity_dir.rglob("*.md"):
                rel = md.relative_to(entity_dir)
                if rel.name in {"CLAUDE.md", "CONTEXT.md"} and len(rel.parts) == 1:
                    continue
                targets.append((md, slug))
    if INTERNAL_PROJECTS_DIR.is_dir():
        for md in INTERNAL_PROJECTS_DIR.rglob("*.md"):
            targets.append((md, "__INTERNAL__"))
    if PERSONAL_DIR.is_dir():
        for project_dir in sorted(PERSONAL_DIR.glob("*/")):
            if not project_dir.is_dir():
                continue
            slug = "__PERSONAL__" + project_dir.name
            for md in project_dir.rglob("*.md"):
                rel = md.relative_to(project_dir)
                if rel.name == "README.md" and len(rel.parts) == 1:
                    continue
                targets.append((md, slug))
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
            if about_line in existing_block:
                return body
            new_block = existing_block.rstrip() + f"\n{about_line}\n\n"
            return body[:section_start] + "\n" + new_block.lstrip("\n") + body[insert_at:]
        existing_tail = body[section_start:]
        if about_line in existing_tail:
            return body
        if not existing_tail.endswith("\n"):
            existing_tail = existing_tail + "\n"
        return body[:section_start] + "\n" + existing_tail.lstrip("\n").rstrip() + f"\n{about_line}\n"

    # Case 2, Observations section exists, insert Relations just before it
    obs_pattern = re.compile(r"^##\s+Observations\s*$", re.MULTILINE)
    m = obs_pattern.search(body)
    if m:
        insert_at = m.start()
        prefix = body[:insert_at].rstrip() + "\n\n"
        return prefix + f"## Relations\n\n{about_line}\n\n" + body[insert_at:]

    # Case 3, no Relations nor Observations, append at end
    tail = body.rstrip() + "\n\n## Relations\n\n" + about_line + "\n"
    return tail


def process_file(path: Path, slug: str, entity_map: dict, apply: bool):
    """Return (status, message) for a single file."""
    fm, body = parse_frontmatter(path)
    if has_about_relation(body):
        return ("skip", "already has about [[...]]")
    if slug == "__INTERNAL__":
        canonical = INTERNAL_ENTITY
    elif slug.startswith("__PERSONAL__"):
        project_slug = slug[len("__PERSONAL__"):]
        readme = PERSONAL_DIR / project_slug / "README.md"
        if readme.exists():
            fm_readme, _ = parse_frontmatter(readme)
            canonical = fm_readme.get("title") or project_slug
        else:
            canonical = project_slug
    else:
        canonical = entity_map.get(slug)
    if not canonical:
        return ("error", f"slug '{slug}' not resolved in entity map")
    new_body = inject_about_line(body, canonical)
    if new_body == body:
        return ("skip", "idempotent no-op")
    if apply:
        content = path.read_text(encoding="utf-8")
        # Rebuild: preserve exact frontmatter bytes, swap body only
        if content.startswith("---"):
            end = content.find("\n---", 4)
            if end != -1:
                head = content[:end + 4]
                # Preserve a single newline after the closing --- then the new body
                if new_body.startswith("\n"):
                    new_content = head + new_body
                else:
                    new_content = head + "\n" + new_body
                path.write_text(new_content, encoding="utf-8")
        else:
            path.write_text(new_body, encoding="utf-8")
    return ("ok", f"→ about [[{canonical}]]")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 add_about_relations.py --dry-run | --apply")
        sys.exit(1)
    apply = sys.argv[1] == "--apply"

    entity_map = build_entity_map()
    targets = find_target_files()

    print(f"=== add_about_relations, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    print(f"Entities resolved: {len(entity_map)}")
    print(f"Target files scanned: {len(targets)}")
    print()

    counts = {"ok": 0, "skip": 0, "error": 0}
    for path, slug in targets:
        status, msg = process_file(path, slug, entity_map, apply)
        counts[status] += 1
        rel = path.relative_to(WORKSPACE)
        if status == "ok":
            print(f"  [OK]    {rel}  {msg}")
        elif status == "error":
            print(f"  [ERR]   {rel}  {msg}")
        # skip is silent unless verbose

    print()
    print(f"Summary: {counts['ok']} modified, {counts['skip']} skipped, {counts['error']} errors")


if __name__ == "__main__":
    main()
