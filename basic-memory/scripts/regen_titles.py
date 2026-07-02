#!/usr/bin/env python3
"""
Regenerate titles in frontmatter from H1 content when title is unusable.

Unusable patterns:
    title: {slug of filename}
    title: README
    title: CLAUDE (already fixed manually, but catch any leftover)
    title: CONTEXT
    title: MIGRATION
    title: PLAN
    title: nodes, plan, services, network, etc (generic slug)

Rules:
    - H1 absent → skip, log edge case
    - H1 too long (>100 chars) → skip, log edge case
    - H1 contains YAML special chars (:, #, &, *, [, ]) → quote value with "..."
    - H1 identical to slug → skip (already bad, no improvement)
    - Otherwise → replace title with H1 content

Usage:
    python3 basic-memory/scripts/regen_titles.py --dry-run
    python3 basic-memory/scripts/regen_titles.py --apply
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EXCLUDED_DIRS = {".claude", "templates", "basic-memory", ".git", ".obsidian", "node_modules"}

UNUSABLE_GENERIC_TITLES = {"README", "CLAUDE", "CONTEXT", "MIGRATION", "PLAN", "SUMMARY", "NOTES", "TODO"}


def is_excluded(path: Path) -> bool:
    for part in path.relative_to(WORKSPACE).parts:
        if part in EXCLUDED_DIRS:
            return True
    if path.name == ".DS_Store":
        return True
    return False


def parse_frontmatter(content: str):
    """Return (fm_dict, fm_raw, body, fm_end_line) or None."""
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end = i
            break
    if end is None:
        return None
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])

    fm = {}
    for ln in fm_lines:
        if ln.startswith(" ") or ln.startswith("\t"):
            continue
        if ":" not in ln:
            continue
        key, _, val = ln.partition(":")
        # Strip optional quotes
        v = val.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        elif v.startswith("'") and v.endswith("'"):
            v = v[1:-1]
        fm[key.strip()] = v

    return fm, "\n".join(fm_lines), body, end


def extract_h1(body: str) -> str | None:
    """Return first H1 line text or None."""
    for ln in body.split("\n"):
        stripped = ln.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped[2:].strip()
            if title:
                return title
    return None


def needs_regen(title: str, slug: str) -> bool:
    """True if title is unusable and should be regenerated."""
    if not title:
        return True
    if title == slug:
        return True
    if title in UNUSABLE_GENERIC_TITLES:
        return True
    # Also catch cases like "nodes", "plan", "services" that match simple lowercase generics
    # (these are file slugs that ended up as titles)
    if title.islower() and len(title) < 20 and title == slug.lower():
        return True
    return False


def yaml_safe(value: str) -> str:
    """Return YAML-safe representation of a string value."""
    # Remove trailing punctuation that looks bad
    value = value.rstrip()
    # Always quote if contains YAML special chars
    special = [":", "#", "&", "*", "[", "]", "{", "}", "|", ">", "%", "@", "`", "!", "?", "'", '"']
    if any(c in value for c in special):
        # Escape internal double-quotes
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    # If starts with special chars or is empty, quote
    if not value or value[0] in "-?:,[]{}#&*!>|'\"":
        return f'"{value}"'
    return value


def update_title_in_frontmatter(fm_raw: str, new_title: str) -> str:
    """Replace the title: line in frontmatter raw block."""
    lines = fm_raw.split("\n")
    safe = yaml_safe(new_title)
    for i, ln in enumerate(lines):
        if ln.startswith("title:") or ln.startswith("title :"):
            lines[i] = f"title: {safe}"
            return "\n".join(lines)
    # No title, insert at top
    lines.insert(0, f"title: {safe}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 regen_titles.py --dry-run | --apply")
        sys.exit(1)

    dry_run = sys.argv[1] == "--dry-run"

    stats = {
        "scanned": 0,
        "already_good": 0,
        "no_h1": 0,
        "h1_too_long": 0,
        "would_update": 0,
        "updated": 0,
    }
    edge_cases_no_h1 = []
    edge_cases_long = []
    edge_cases_identical = []
    updates = []

    for path in WORKSPACE.rglob("*.md"):
        if is_excluded(path):
            continue
        stats["scanned"] += 1

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"SKIP {path}: {e}", file=sys.stderr)
            continue

        parsed = parse_frontmatter(content)
        if parsed is None:
            continue
        fm, fm_raw, body, _ = parsed

        title = fm.get("title", "")
        slug = path.stem

        if not needs_regen(title, slug):
            stats["already_good"] += 1
            continue

        h1 = extract_h1(body)
        if h1 is None:
            stats["no_h1"] += 1
            edge_cases_no_h1.append(str(path.relative_to(WORKSPACE)))
            continue

        if len(h1) > 100:
            stats["h1_too_long"] += 1
            edge_cases_long.append((str(path.relative_to(WORKSPACE)), h1))
            continue

        # Sometimes H1 is identical to current title (bad case), skip
        if h1 == title:
            edge_cases_identical.append(str(path.relative_to(WORKSPACE)))
            continue

        stats["would_update"] += 1
        updates.append({
            "path": str(path.relative_to(WORKSPACE)),
            "old": title,
            "new": h1,
        })

        if not dry_run:
            new_fm = update_title_in_frontmatter(fm_raw, h1)
            new_content = f"---\n{new_fm}\n---\n{body}"
            path.write_text(new_content, encoding="utf-8")
            stats["updated"] += 1

    # Report
    print(f"=== Regen titles report ({'DRY RUN' if dry_run else 'APPLIED'}) ===")
    print(f"Scanned: {stats['scanned']}")
    print(f"Already good: {stats['already_good']}")
    print(f"No H1 (skip): {stats['no_h1']}")
    print(f"H1 too long (skip): {stats['h1_too_long']}")
    print(f"Same as title (skip): {len(edge_cases_identical)}")
    print(f"Would update: {stats['would_update']}" if dry_run else f"Updated: {stats['updated']}")

    if dry_run and updates:
        print(f"\nSample updates (first 15):")
        for u in updates[:15]:
            print(f"  {u['path']}")
            print(f"    {u['old']!r} -> {u['new']!r}")

    if edge_cases_no_h1:
        print(f"\nEdge cases NO H1 (need manual review):")
        for p in edge_cases_no_h1[:10]:
            print(f"  {p}")
        if len(edge_cases_no_h1) > 10:
            print(f"  ... and {len(edge_cases_no_h1) - 10} more")

    if edge_cases_long:
        print(f"\nEdge cases H1 too long (need manual review):")
        for p, h in edge_cases_long[:5]:
            print(f"  {p}")
            print(f"    ({len(h)} chars) {h[:80]}...")


if __name__ == "__main__":
    main()
