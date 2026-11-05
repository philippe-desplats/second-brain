#!/usr/bin/env python3
"""
Check symmetric relations on client-context and partner-context CLAUDE.md files.

Required pairs:
    managed_by (client) ↔ manages (partner)
    owned_by (client) ↔ owns (partner)
    referred_by (client) ↔ brings_lead (partner)
    co_delivered_with (auto-symmetric, between any 2 clients or partners)

Every declared relation is checked from the side that declares it, so a pair
broken on either side is reported. A target is matched by its display-free
name, `[[Proseware|our partner]]` reads as `Proseware`, against the entity's
`client:` or `partner:` field and its `title:`, both read whole when folded.

Exits 1 when any asymmetry is found, 0 otherwise. `--check` is the default.

Usage:
    python3 basic-memory/scripts/check_symmetric_relations.py
    python3 basic-memory/scripts/check_symmetric_relations.py --check
    python3 basic-memory/scripts/check_symmetric_relations.py --suggest
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import frontmatter as F  # noqa: E402
from check_helpers import WIKILINK_PATTERN, scalar  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent.parent
CLIENTS = WORKSPACE / "sources" / "clients"
PARTNERS = WORKSPACE / "sources" / "partners"

# side -> {relation: (inverse relation, sides the target may live on)}
PAIRS = {
    "client": {
        "managed_by": ("manages", ("partner",)),
        "owned_by": ("owns", ("partner",)),
        "referred_by": ("brings_lead", ("partner",)),
        "co_delivered_with": ("co_delivered_with", ("client", "partner")),
    },
    "partner": {
        "manages": ("managed_by", ("client",)),
        "owns": ("owned_by", ("client",)),
        "brings_lead": ("referred_by", ("client",)),
        "co_delivered_with": ("co_delivered_with", ("client", "partner")),
    },
}

RELATION_RE = re.compile(r"^-\s+(\w+)\s+" + WIKILINK_PATTERN)
USAGE = "Usage: python3 check_symmetric_relations.py [--check | --suggest]"


class Entity:
    """One client or partner context file: its names and declared relations."""

    def __init__(self, side: str, path: Path):
        self.side = side
        self.path = path
        doc, fm = F.read_file(path)
        body = doc.body if doc is not None else path.read_text(encoding="utf-8")
        self.name = scalar(fm, side) or scalar(fm, "title") or path.parent.name
        self.names = {self.name, scalar(fm, "title")} - {""}
        self.relations = parse_relations(body)

    @property
    def rel(self) -> str:
        return self.path.relative_to(WORKSPACE).as_posix()

    def declares(self, relation: str, names: set[str]) -> bool:
        return any(rt == relation and t in names for rt, t in self.relations)


def parse_relations(body: str) -> list[tuple[str, str]]:
    """(relation, target) pairs listed under the body's `## Relations` heading."""
    relations = []
    in_rel = False
    for ln in body.split("\n"):
        if re.match(r"^##\s+Relations\s*$", ln):
            in_rel = True
            continue
        if in_rel and ln.startswith("## "):
            break
        if in_rel:
            m = RELATION_RE.match(ln)
            if m:
                relations.append((m.group(1), m.group(2).strip()))
    return relations


def load_all() -> list[Entity]:
    """Every client and partner context file, clients first."""
    entities = [Entity("client", p) for p in sorted(CLIENTS.glob("*/CLAUDE.md"))]
    entities += [Entity("partner", p) for p in sorted(PARTNERS.glob("*/CLAUDE.md"))]
    return entities


def find_asymmetries(entities: list[Entity]) -> list[dict]:
    by_name: dict[tuple[str, str], Entity] = {}
    for e in entities:
        for name in e.names:
            by_name.setdefault((e.side, name), e)

    asymmetries = []
    for source in entities:
        for rel_type, target in source.relations:
            if rel_type not in PAIRS[source.side]:
                continue
            inverse, target_sides = PAIRS[source.side][rel_type]
            match = next((by_name[(side, target)] for side in target_sides
                          if (side, target) in by_name), None)
            if match is not None and match.declares(inverse, source.names):
                continue
            if match is None:
                expected_on = "ORPHAN (no matching " + " or ".join(target_sides) + ")"
            else:
                expected_on = match.rel
            asymmetries.append({
                "side": source.side,
                "source": source.rel,
                "source_name": source.name,
                "relation": rel_type,
                "target": target,
                "expected_on": expected_on,
                "expected_line": f"- {inverse} [[{source.name}]]",
            })
    return asymmetries


def main(argv: list[str]) -> int:
    if len(argv) > 1 or (argv and argv[0] not in {"--check", "--suggest"}):
        print(USAGE)
        return 1
    mode = argv[0] if argv else "--check"

    entities = load_all()
    asymmetries = find_asymmetries(entities)

    print("=== Symmetric relations check ===")
    print(f"Clients scanned: {sum(e.side == 'client' for e in entities)}")
    print(f"Partners scanned: {sum(e.side == 'partner' for e in entities)}")
    print(f"Asymmetries found: {len(asymmetries)}")
    print()

    if not asymmetries:
        print("✓ All symmetric relations are mirrored correctly.")
        return 0

    print("Asymmetries:")
    for a in asymmetries:
        print(f"  {a['source']}")
        print(f"    declares:  {a['relation']} [[{a['target']}]]")
        print(f"    missing on: {a['expected_on']}")
        if mode == "--suggest":
            print(f"    add line:   {a['expected_line']}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
