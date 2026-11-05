#!/usr/bin/env python3
"""
Add observations `- [field] value` to the ## Observations section of stable
files (client-context, partner-context, person, service, topic, project-brief),
based on frontmatter YAML values.

The frontmatter is preserved byte for byte, only the body is rewritten.
Observations are added only for fields whose schema is known and whose value
is present in the frontmatter. A list gives one observation per item. A value
spread over several lines, a folded scalar or a `|` or `>` block, gives one
observation with its lines joined by single spaces. Existing observations for
the same field and value are not duplicated, and an observation counts as
present once its wiki-links are read as plain text: auto_link_entities.py
turns `- [related] Client Onboarding` into `- [related] [[Client Onboarding]]`
or `[[Target|label]]`, and that link, which feeds Basic Memory relations, must
not make the next run add the plain value again. The comparison ignores case,
since a plain-text mention linked by its lowercase form becomes
`[[Canonical]]` with the canonical capitals.

Only corpus notes are visited, through `corpus.iter_corpus_notes`, so the
pass never writes into a folder corpus.py excludes.

Usage:
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --dry-run
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply
    python3 basic-memory/scripts/add_observations_from_frontmatter.py --apply --type client-context
"""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from frontmatter import Doc, Frontmatter, read_file, write_file  # noqa: E402

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


@dataclass
class Target:
    """A note the pass may annotate, read once."""

    path: Path
    rel: str
    note_type: str
    doc: Doc
    fm: Frontmatter


WIKILINK_RE = re.compile(r"\[\[([^\]|]*)(?:\|([^\]]*))?\]\]")


def one_line(value: str) -> str:
    """An observation is one line: collapse every run of whitespace to a space."""
    return " ".join(value.split())


def observation_key(field: str, value: str) -> tuple[str, str]:
    """What makes 2 observations the same: field, then text without links, any case."""
    return field.strip(), one_line(unlink(value)).casefold()


def unlink(text: str) -> str:
    """Read wiki-links as the text they show: `[[T]]` gives T, `[[T|label]]` gives label."""
    return WIKILINK_RE.sub(lambda m: m.group(2) if m.group(2) is not None else m.group(1), text)


def parse_existing_observations(body: str) -> set:
    """Return the observation_key of every observation in the ## Observations section."""
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
            existing.add(observation_key(m.group(1), m.group(2)))
    return existing


def build_observations(fm: Frontmatter, note_type: str) -> list:
    """Return list of (field, value) observations to add for this type."""
    obs = []
    for field in TYPE_FIELDS.get(note_type, []):
        value = fm.get(field)
        items = value if isinstance(value, list) else [value]
        for item in items:
            if item is None:
                continue
            text = one_line(item)
            if text:
                obs.append((field, text))
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
            # `insert_at` points at the newline that ends the section's last
            # line, so the block ends on a single newline and one blank line
            # remains before the next heading.
            insert_at = section_start + next_section.start()
            block = body[section_start:insert_at].rstrip()
            new_block = block + "\n" + addition + "\n"
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


def load(path: Path, rel: str = ""):
    """Return a Target for a note with frontmatter, or None."""
    doc, fm = read_file(path)
    if doc is None:
        return None
    note_type = fm.get("type")
    return Target(path, rel, note_type if isinstance(note_type, str) else "", doc, fm)


def find_targets(root: Path = WORKSPACE, filter_type: str = None) -> list:
    """Return a Target for every corpus note of one of the stable types."""
    targets = []
    for path, rel in iter_corpus_notes(root):
        target = load(path, rel)
        if target is None or target.note_type not in TYPE_FIELDS:
            continue
        if filter_type and target.note_type != filter_type:
            continue
        targets.append(target)
    return sorted(targets, key=lambda t: t.rel)


def process_file(path: Path, apply: bool, target: Target = None):
    """Return (status, message, new_obs). Reads the note unless `target` is given."""
    target = target or load(path)
    if target is None:
        return ("skip", "no frontmatter", [])
    planned_obs = build_observations(target.fm, target.note_type)
    if not planned_obs:
        return ("skip", "no schema fields present in frontmatter", [])
    body = target.doc.body
    existing = parse_existing_observations(body)
    new_obs = [(f, v) for f, v in planned_obs if observation_key(f, v) not in existing]
    if not new_obs:
        return ("skip", "all observations already present", [])
    new_body = insert_observations(body, new_obs)
    if new_body == body:
        return ("skip", "idempotent no-op", [])
    if apply:
        target.doc.body = new_body
        write_file(target.path, target.doc)
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

    targets = find_targets(WORKSPACE, filter_type)
    print(f"=== add_observations_from_frontmatter, mode={'APPLY' if apply else 'DRY-RUN'} ===")
    if filter_type:
        print(f"Filter: type={filter_type}")
    print(f"Target files found: {len(targets)}")
    print()

    counts = {"ok": 0, "skip": 0}
    type_counts = {}
    for target in targets:
        status, msg, new_obs = process_file(target.path, apply, target)
        counts[status] += 1
        type_counts[target.note_type] = type_counts.get(target.note_type, 0) + 1
        if status == "ok":
            print(f"  [OK] [{target.note_type}] {target.rel}  ({msg})")
            for f, v in new_obs:
                print(f"         - [{f}] {v}")
    print()
    print("By type scanned:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    print()
    print(f"Summary: {counts['ok']} modified, {counts['skip']} skipped")


if __name__ == "__main__":
    main()
