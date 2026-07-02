#!/usr/bin/env python3
"""
Retype files: update frontmatter `type:` based on path/filename patterns.

Usage:
    python3 basic-memory/scripts/retype_files.py --dry-run
    python3 basic-memory/scripts/retype_files.py --apply

Pattern mapping (most specific first), post layered migration:
    {entity}/emails/YYYY-MM-DD-{seq}-{direction}-*.md → email
    {entity}/emails/YYYY-MM-DD-writing-*.md           → email (legacy)
    {entity}/emails/YYYY-MM-DD-reply-*.md             → email (variant)
    {entity}/emails/*.md                              → email (catchall)
    {entity}/meetings/*.md                            → meeting
    {entity}/deliverables/*.md                        → deliverable
    {entity}/transcripts/*.md                         → transcript
    YYYY-MM-DD-meeting-*.md   (anywhere)              → meeting
    YYYY-MM-DD-research-*.md  (anywhere)              → research
    YYYY-MM-DD-brainstorm-*.md (anywhere)             → brainstorm
    YYYY-MM-DD-strategy-*.md  (anywhere)              → strategy
    YYYY-MM-DD-writing-*.md   (outside emails/)       → writing
    YYYY-MM-DD-note-*.md      (anywhere)              → note
    sources/clients/{X}/CLAUDE.md                     → client-context
    sources/partners/{X}/CLAUDE.md                    → partner-context
    sources/{any}/{project}/README.md                 → project-brief

Exclusions: .claude/, templates/, basic-memory/, .git/, CONTEXT.md (legacy)
Excluded from retyping if already has correct non-note type (idempotent).
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EXCLUDED_DIRS = {".claude", "templates", "basic-memory", ".git", ".obsidian", "node_modules"}
DATED_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def is_excluded(path: Path) -> bool:
    for part in path.relative_to(WORKSPACE).parts:
        if part in EXCLUDED_DIRS:
            return True
    if path.name == "CONTEXT.md":
        return True
    if path.name == ".DS_Store":
        return True
    return False


def detect_target_type(path: Path) -> str | None:
    """Return target type or None if no pattern matches."""
    rel = path.relative_to(WORKSPACE)
    parts = rel.parts
    name = path.name
    stem = path.stem

    # Special: CLAUDE.md
    if name == "CLAUDE.md":
        # Layered structure: sources/{clients|partners}/{slug}/CLAUDE.md
        if (
            len(parts) == 4
            and parts[0] == "sources"
            and parts[1] == "clients"
        ):
            return "client-context"
        if (
            len(parts) == 4
            and parts[0] == "sources"
            and parts[1] == "partners"
        ):
            return "partner-context"
        # Project CLAUDE.md inside any sources/{type}/{project}/ scope (4+ parts)
        if len(parts) >= 4 and parts[0] == "sources":
            return "project-brief"
        # Root CLAUDE.md or other → leave as note
        return None

    # Special: README.md inside a project folder under sources/
    if name == "README.md":
        # Projects live in sources/{clients|partners|internal|personal}/{...}/README.md
        if (
            len(parts) >= 3
            and parts[0] == "sources"
            and parts[1] in {"clients", "partners", "internal", "personal"}
        ):
            return "project-brief"
        return None

    # Ancestor-directory based (handles emails/subfolder/file.md cases)
    ancestors = set(parts[:-1])
    if "emails" in ancestors or "mails" in ancestors:
        return "email"
    if "meetings" in ancestors:
        return "meeting"
    if "deliverables" in ancestors:
        return "deliverable"
    if "transcripts" in ancestors:
        return "transcript"

    # Dated prefix patterns
    if DATED_PREFIX.match(stem):
        after = stem[11:]  # drop "YYYY-MM-DD-"
        # Email patterns in `/emails/` or `/mails/` already handled above
        if after.startswith("meeting-") or after == "meeting":
            return "meeting"
        if after.startswith("research-") or after == "research":
            return "research"
        if after.startswith("brainstorm-") or after == "brainstorm":
            return "brainstorm"
        if after.startswith("strategy-") or after == "strategy":
            return "strategy"
        if after.startswith("writing-") or after == "writing":
            return "writing"
        if after.startswith("note-") or after == "note":
            return "note"
        # Email legacy patterns outside emails/ folder still get caught above
        # Sequential email pattern `01-out-*` etc.
        m = re.match(r"^\d{2}-(out|in|reply)-", after)
        if m:
            return "email"

    return None


def parse_frontmatter(content: str) -> tuple[dict, str, str] | None:
    """Return (frontmatter_dict, frontmatter_raw, body) or None if no frontmatter."""
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

    # Naive YAML parsing, only top-level scalar keys needed for our use
    fm = {}
    for ln in fm_lines:
        if ln.startswith(" ") or ln.startswith("\t"):
            continue  # skip nested lines
        if ":" not in ln:
            continue
        key, _, val = ln.partition(":")
        fm[key.strip()] = val.strip().strip('"').strip("'")

    return fm, "\n".join(fm_lines), body


def update_type_in_frontmatter(fm_raw: str, new_type: str) -> str:
    """Update or insert `type:` line in frontmatter raw string."""
    lines = fm_raw.split("\n")
    updated = False
    for i, ln in enumerate(lines):
        if ln.startswith("type:") or ln.startswith("type :"):
            lines[i] = f"type: {new_type}"
            updated = True
            break
    if not updated:
        # Insert after first line (usually title: or the first key)
        lines.insert(1 if lines else 0, f"type: {new_type}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--dry-run", "--apply"}:
        print("Usage: python3 retype_files.py --dry-run | --apply")
        sys.exit(1)

    dry_run = sys.argv[1] == "--dry-run"

    stats = {
        "total_scanned": 0,
        "already_correct": 0,
        "no_frontmatter": 0,
        "no_pattern": 0,
        "would_update": 0,
        "updated": 0,
        "by_target": {},
    }
    changes = []

    for path in WORKSPACE.rglob("*.md"):
        if is_excluded(path):
            continue
        stats["total_scanned"] += 1

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"SKIP {path}: {e}", file=sys.stderr)
            continue

        parsed = parse_frontmatter(content)
        if parsed is None:
            stats["no_frontmatter"] += 1
            continue
        fm, fm_raw, body = parsed

        target = detect_target_type(path)
        if target is None:
            stats["no_pattern"] += 1
            continue

        current = fm.get("type", "")

        if current == target:
            stats["already_correct"] += 1
            continue

        # Folder-based override: if any ancestor folder is explicit container, always use that type
        rel_parts = set(path.relative_to(WORKSPACE).parts[:-1])
        folder_override = bool(rel_parts & {"emails", "mails", "meetings", "deliverables", "transcripts"})

        # Skip only if current has specific type AND we are not in a folder-override case
        if current and current not in {"note", ""} and not folder_override:
            changes.append({
                "path": str(path.relative_to(WORKSPACE)),
                "current": current,
                "target": target,
                "action": "SKIP_CONFLICT",
            })
            continue

        stats["would_update"] += 1
        stats["by_target"][target] = stats["by_target"].get(target, 0) + 1
        changes.append({
            "path": str(path.relative_to(WORKSPACE)),
            "current": current or "(none)",
            "target": target,
            "action": "UPDATE",
        })

        if not dry_run:
            new_fm = update_type_in_frontmatter(fm_raw, target)
            new_content = f"---\n{new_fm}\n---\n{body}"
            path.write_text(new_content, encoding="utf-8")
            stats["updated"] += 1

    # Report
    print(f"=== Retype report ({'DRY RUN' if dry_run else 'APPLIED'}) ===")
    print(f"Total scanned: {stats['total_scanned']}")
    print(f"Already correct: {stats['already_correct']}")
    print(f"No frontmatter: {stats['no_frontmatter']}")
    print(f"No pattern: {stats['no_pattern']}")
    print(f"Would update: {stats['would_update']}" if dry_run else f"Updated: {stats['updated']}")
    print("")
    print("By target type:")
    for t, n in sorted(stats["by_target"].items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")
    print("")
    conflicts = [c for c in changes if c["action"] == "SKIP_CONFLICT"]
    if conflicts:
        print(f"Skipped {len(conflicts)} conflicts (non-note → other):")
        for c in conflicts[:10]:
            print(f"  {c['path']}: {c['current']} -> {c['target']}")
    if dry_run and stats["would_update"] > 0:
        print(f"\nSample updates (first 10):")
        for c in [c for c in changes if c["action"] == "UPDATE"][:10]:
            print(f"  {c['path']}: {c['current']} -> {c['target']}")


if __name__ == "__main__":
    main()
