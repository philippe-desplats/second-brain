#!/usr/bin/env python3
"""
Add observations `- [field] value` to the ## Observations section of stable
files (client-context, partner-context, person, service, topic, project-brief),
based on frontmatter YAML values.

The frontmatter is preserved as-is. Observations are added only for fields
whose schema is known and whose value is present in the frontmatter. Existing
observations for the same field are not duplicated.

Usage:
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --dry-run
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply --type client-context
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Schema-defined fields per type (required + optional scalars/arrays likely to have values)
TYPE_FIELDS = {
    "person": [
        "name", "role", "email", "phone", "linkedin", "notes",
    ],
    "service": [
        "name", "service_type", "status", "price_model", "price", "currency", "launch_date",
    ],
    "topic": [
        "name", "domain", "aliases", "status", "related",
    ],
    "client-context": [
        "client", "status", "last_updated", "legal_form", "company_id", "vat_id",
        "industry", "day_rate", "tone", "addressing", "primary_channel",
        "email_format", "language", "constraints",
    ],
    "partner-context": [
        "partner", "status", "partnership_type", "last_updated", "active_tracks",
        "business_referral", "contract", "client_facets", "vendor_facets",
        "legal_form", "company_id", "vat_id", "tone", "addressing",
        "primary_channel", "language", "constraints",
    ],
    "project-brief": [
        "title", "category", "created", "status",
    ],
}

# Fields that are arrays (one observation per item)
ARRAY_FIELDS = {
    "aliases", "related", "constraints", "active_tracks",
    "client_facets", "vendor_facets",
}


def parse_frontmatter_yaml(fm_raw: str) -> dict:
    """Parse frontmatter YAML. Returns dict with string values or list of strings for arrays.

    Handles:
    - key: value (scalar)
    - key: [a, b, c] (inline array, split on commas outside quotes)
    - key:\n  - item1\n  - item2 (block array)
    """
    result = {}
    lines = fm_raw.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln or ln.startswith("#"):
            i += 1
            continue
        if ln.startswith((" ", "\t", "-")):
            i += 1
            continue
        if ":" not in ln:
            i += 1
            continue
        key, _, rest = ln.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest.startswith("[") and rest.endswith("]"):
            items_str = rest[1:-1].strip()
            items = [it.strip().strip('"').strip("'") for it in items_str.split(",") if it.strip()]
            result[key] = items
        elif rest == "":
            items = []
            j = i + 1
            while j < len(lines):
                next_ln = lines[j]
                if next_ln.startswith(("  - ", "\t- ")) or re.match(r"^\s+-\s+", next_ln):
                    item = re.sub(r"^\s+-\s+", "", next_ln).strip().strip('"').strip("'")
                    items.append(item)
                    j += 1
                elif next_ln.startswith((" ", "\t")):
                    j += 1
                else:
                    break
            if items:
                result[key] = items
            i = j
            continue
        else:
            value = rest.strip('"').strip("'")
            result[key] = value
        i += 1
    return result


def format_value(value) -> str:
    """Format a scalar value for observation output."""
    if isinstance(value, str):
        return value
    return str(value)


def parse_existing_observations(body: str) -> set:
    """Return set of (field, value) tuples already present in ## Observations section."""
    existing = set()
    obs_match = re.search(r"##\s+Observations\s*\n", body)
    if not obs_match:
        return existing
    start = obs_match.end()
    end_match = re.search(r"\n##\s+\S", body[start:])
    section = body[start:start + end_match.start()] if end_match else body[start:]
    for ln in section.split("\n"):
        m = re.match(r"^\s*-\s+\[([^\]]+)\]\s+(.+)$", ln)
        if m:
            existing.add((m.group(1).strip(), m.group(2).strip()))
    return existing


def build_observations(fm: dict, note_type: str) -> list:
    """Return list of (field, value) observations to add for this type."""
    fields = TYPE_FIELDS.get(note_type, [])
    obs = []
    for field in fields:
        if field not in fm:
            continue
        value = fm[field]
        if value is None or value == "":
            continue
        if field in ARRAY_FIELDS and isinstance(value, list):
            for item in value:
                if item:
                    obs.append((field, format_value(item)))
        elif isinstance(value, list):
            for item in value:
                if item:
                    obs.append((field, format_value(item)))
        else:
            obs.append((field, format_value(value)))
    return obs


def insert_observations(body: str, new_obs: list) -> str:
    """Insert new observations into ## Observations section (create if absent)."""
    if not new_obs:
        return body
    obs_match = re.search(r"^##\s+Observations\s*$", body, re.MULTILINE)
    new_lines = [f"- [{field}] {value}" for field, value in new_obs]
    addition = "\n".join(new_lines)
    if obs_match:
        section_start = obs_match.end()
        next_section = re.search(r"\n##\s+\S", body[section_start:])
        if next_section:
            insert_at = section_start + next_section.start()
            block = body[section_start:insert_at].rstrip()
            new_block = block + "\n" + addition + "\n\n"
            return body[:section_start] + "\n" + new_block.lstrip("\n") + body[insert_at:]
        tail = body[section_start:].rstrip()
        return body[:section_start] + "\n" + tail.lstrip("\n") + "\n" + addition + "\n"

    # No Observations section: create one before ## Relations if present, else append
    rel_match = re.search(r"^##\s+Relations\s*$", body, re.MULTILINE)
    if rel_match:
        insert_at = rel_match.start()
        prefix = body[:insert_at].rstrip() + "\n\n"
        return prefix + "## Observations\n\n" + addition + "\n\n" + body[insert_at:]
    return body.rstrip() + "\n\n## Observations\n\n" + addition + "\n"


def parse_file(path: Path):
    """Return (fm_raw, fm_parsed, body, note_type) or (None, None, None, None) if skip."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None, None, None, None
    end = content.find("\n---", 4)
    if end == -1:
        return None, None, None, None
    fm_raw = content[4:end]
    body = content[end + 4:]
    if body.startswith("\n"):
        body = body[1:]
    fm = parse_frontmatter_yaml(fm_raw)
    note_type = fm.get("type", "")
    return fm_raw, fm, body, note_type


def find_targets(filter_type: str = None):
    """Return list of Path for files matching one of the 6 stable types."""
    targets = []
    for md in WORKSPACE.rglob("*.md"):
        parts = md.relative_to(WORKSPACE).parts
        if any(p.startswith(".") for p in parts):
            continue
        if "node_modules" in parts or "basic-memory" in parts:
            continue
        if "templates" in parts or "schemas" in parts:
            continue
        _, fm, _, note_type = parse_file(md)
        if note_type not in TYPE_FIELDS:
            continue
        if filter_type and note_type != filter_type:
            continue
        targets.append(md)
    return sorted(targets)


def process_file(path: Path, apply: bool):
    fm_raw, fm, body, note_type = parse_file(path)
    if not fm_raw:
        return ("skip", "no frontmatter", [])
    planned_obs = build_observations(fm, note_type)
    if not planned_obs:
        return ("skip", "no schema fields present in frontmatter", [])
    existing = parse_existing_observations(body)
    new_obs = [(f, v) for f, v in planned_obs if (f, v) not in existing]
    if not new_obs:
        return ("skip", "all observations already present", [])
    new_body = insert_observations(body, new_obs)
    if new_body == body:
        return ("skip", "idempotent no-op", [])
    if apply:
        content = path.read_text(encoding="utf-8")
        end = content.find("\n---", 4)
        head = content[:end + 4]
        suffix = "\n" + new_body if not new_body.startswith("\n") else new_body
        path.write_text(head + suffix, encoding="utf-8")
    return ("ok", f"{len(new_obs)} observations", new_obs)


def main():
    args = sys.argv[1:]
    if not args or args[0] not in {"--dry-run", "--apply"}:
        print("Usage: python3 add_observations_from_frontmatter.py --dry-run|--apply [--type TYPE]")
        sys.exit(1)
    apply = args[0] == "--apply"
    filter_type = None
    if "--type" in args:
        idx = args.index("--type")
        if idx + 1 < len(args):
            filter_type = args[idx + 1]

    targets = find_targets(filter_type)
    print(f"=== add_observations_from_frontmatter, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    if filter_type:
        print(f"Filter: type={filter_type}")
    print(f"Target files found: {len(targets)}")
    print()

    counts = {"ok": 0, "skip": 0, "error": 0}
    type_counts = {}
    for path in targets:
        status, msg, new_obs = process_file(path, apply)
        counts[status] += 1
        rel = path.relative_to(WORKSPACE)
        _, _, _, note_type = parse_file(path)
        type_counts[note_type] = type_counts.get(note_type, 0) + 1
        if status == "ok":
            print(f"  [OK] [{note_type}] {rel}  ({msg})")
            for f, v in new_obs:
                print(f"         - [{f}] {v}")
    print()
    print("By type scanned:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    print()
    print(f"Summary: {counts['ok']} modified, {counts['skip']} skipped, {counts['error']} errors")


if __name__ == "__main__":
    main()
