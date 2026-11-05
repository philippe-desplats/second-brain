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
    - Entity context file (sources/clients/{X}/CLAUDE.md,
      sources/partners/{X}/CLAUDE.md) → title is the identity field, `client:`
      or `partner:`, never the H1, since Basic Memory resolves `[[Acme]]` on
      `title:` only (see .claude/rules/frontmatter.md). No identity → skip, log
    - H1 absent → skip, log edge case
    - H1 too long (>100 chars) → skip, log edge case
    - H1 identical to the current title → skip (no improvement)
    - Title declared twice, holding a list or a block, opening a quote its
      range never closes, or absorbing a list item or another field, or any
      field of the note swallowing a column-0 `key:` line → skip, listed
      under "Needs repair", since a range may hold another field
    - Otherwise → replace title with H1 content
    - The new value is quoted through the shared policy of `frontmatter.py`
      when YAML would misread it plain

Only corpus notes are visited, through `corpus.iter_corpus_notes`, so the
pass never writes into the folders `corpus.py` excludes.

Usage:
    python3 basic-memory/scripts/regen_titles.py --dry-run
    python3 basic-memory/scripts/regen_titles.py --apply
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from note_types import REPAIR_HINT, classify, field_damage  # noqa: E402

UNUSABLE_GENERIC_TITLES = {"README", "CLAUDE", "CONTEXT", "MIGRATION", "PLAN", "SUMMARY", "NOTES", "TODO"}

# Entity context type -> the identity field its title must equal.
IDENTITY_FIELDS = {"client-context": "client", "partner-context": "partner"}


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


def set_title(fm: F.Frontmatter, new_title: str) -> F.Frontmatter:
    """Set `title:`, its whole line range when present, as the first field otherwise."""
    if "title" in fm:
        return F.set_field(fm, "title", new_title)
    line = F.render_field("title", new_title)
    return F.parse("".join(ln + "\n" for ln in line + fm.lines))


def as_text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def main(argv=None, root=WORKSPACE):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in {"--dry-run", "--apply"}:
        print("Usage: python3 regen_titles.py --dry-run | --apply")
        sys.exit(1)

    dry_run = argv[0] == "--dry-run"

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
    edge_cases_no_identity = []
    needs_repair = []
    updates = []

    for path, rel in iter_corpus_notes(root):
        stats["scanned"] += 1

        try:
            doc, fm = F.read_file(path)
        except (OSError, UnicodeDecodeError) as e:
            print(f"SKIP {path}: {e}", file=sys.stderr)
            continue
        if doc is None:
            continue

        damage = field_damage(fm, "title")
        if damage:
            needs_repair.append((rel, damage))
            continue

        title = as_text(fm.get("title"))
        slug = path.stem

        if not needs_regen(title, slug):
            stats["already_good"] += 1
            continue

        identity_field = IDENTITY_FIELDS.get(classify(rel))
        if identity_field:
            new = as_text(fm.get(identity_field))
            if not new:
                edge_cases_no_identity.append(rel)
                continue
        else:
            new = extract_h1(doc.body)
            if new is None:
                stats["no_h1"] += 1
                edge_cases_no_h1.append(rel)
                continue

            if len(new) > 100:
                stats["h1_too_long"] += 1
                edge_cases_long.append((rel, new))
                continue

        # Sometimes the new value is identical to the current title (bad case), skip
        if new == title:
            edge_cases_identical.append(rel)
            continue

        stats["would_update"] += 1
        updates.append({"path": rel, "old": title, "new": new})

        if not dry_run:
            if F.write_file(path, doc, set_title(fm, new)):
                stats["updated"] += 1

    # Report
    print(f"=== Regen titles report ({'DRY RUN' if dry_run else 'APPLIED'}) ===")
    print(f"Scanned: {stats['scanned']}")
    print(f"Already good: {stats['already_good']}")
    print(f"No H1 (skip): {stats['no_h1']}")
    print(f"H1 too long (skip): {stats['h1_too_long']}")
    print(f"Same as title (skip): {len(edge_cases_identical)}")
    print(f"No identity field (skip): {len(edge_cases_no_identity)}")
    print(f"Needs repair (skip): {len(needs_repair)}")
    print(f"Would update: {stats['would_update']}" if dry_run else f"Updated: {stats['updated']}")

    if dry_run and updates:
        print("\nSample updates (first 15):")
        for u in updates[:15]:
            print(f"  {u['path']}")
            print(f"    {u['old']!r} -> {u['new']!r}")

    if edge_cases_no_h1:
        print("\nEdge cases NO H1 (need manual review):")
        for p in edge_cases_no_h1[:10]:
            print(f"  {p}")
        if len(edge_cases_no_h1) > 10:
            print(f"  ... and {len(edge_cases_no_h1) - 10} more")

    if edge_cases_long:
        print("\nEdge cases H1 too long (need manual review):")
        for p, h in edge_cases_long[:5]:
            print(f"  {p}")
            print(f"    ({len(h)} chars) {h[:80]}...")

    if edge_cases_no_identity:
        print("\nEdge cases entity context without its identity field (need manual review):")
        for p in edge_cases_no_identity[:10]:
            print(f"  {p}")

    if needs_repair:
        print(f"\n{REPAIR_HINT} ({len(needs_repair)}):")
        for p, damage in needs_repair:
            print(f"  {p}: {damage}, left untouched")


if __name__ == "__main__":
    main()
