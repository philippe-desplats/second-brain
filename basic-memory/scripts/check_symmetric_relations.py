#!/usr/bin/env python3
"""
Check symmetric relations on client-context and partner-context CLAUDE.md files.

Required pairs:
    managed_by (client) ↔ manages (partner)
    owned_by (client) ↔ owns (partner)
    referred_by (client) ↔ brings_lead (partner)
    co_delivered_with (auto-symmetric)

Usage:
    python3 basic-memory/scripts/check_symmetric_relations.py --check
    python3 basic-memory/scripts/check_symmetric_relations.py --suggest
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
CLIENTS = WORKSPACE / "sources" / "clients"
PARTNERS = WORKSPACE / "sources" / "partners"

PAIR_CLIENT_TO_PARTNER = {
    "managed_by": "manages",
    "owned_by": "owns",
    "referred_by": "brings_lead",
    "co_delivered_with": "co_delivered_with",
}


def parse_fm_and_relations(path: Path):
    """Return (frontmatter_dict, relations_list_from_body). relations_list is list of (type, target)."""
    content = path.read_text(encoding="utf-8")
    fm = {}
    body = content
    if content.startswith("---"):
        end = content.find("\n---", 4)
        if end != -1:
            fm_raw = content[4:end]
            body = content[end + 4:]
            for ln in fm_raw.split("\n"):
                if ln.startswith((" ", "\t")):
                    continue
                if ":" not in ln:
                    continue
                k, _, v = ln.partition(":")
                v = v.strip().strip('"').strip("'")
                fm[k.strip()] = v
    # Parse ## Relations section in body
    relations = []
    in_rel = False
    for ln in body.split("\n"):
        if re.match(r"^##\s+Relations\s*$", ln):
            in_rel = True
            continue
        if in_rel and ln.startswith("## "):
            break
        if in_rel:
            m = re.match(r"^-\s+(\w+)\s+\[\[([^\]]+)\]\]", ln)
            if m:
                relations.append((m.group(1), m.group(2)))
    return fm, relations


def load_all():
    """Load all client and partner CLAUDE.md with their relations."""
    clients = {}  # slug -> (path, fm, relations)
    partners = {}
    for p in sorted(CLIENTS.glob("*/CLAUDE.md")):
        slug = p.parent.name
        fm, rels = parse_fm_and_relations(p)
        clients[slug] = (p, fm, rels)
    for p in sorted(PARTNERS.glob("*/CLAUDE.md")):
        slug = p.parent.name
        fm, rels = parse_fm_and_relations(p)
        partners[slug] = (p, fm, rels)
    return clients, partners


def resolve_entity_name(fm: dict) -> str:
    """Return the canonical entity name for wikilink resolution."""
    return fm.get("client") or fm.get("partner") or fm.get("title", "")


def build_name_to_slug_maps(clients: dict, partners: dict):
    """Build name -> slug lookup for clients and partners."""
    c_map = {resolve_entity_name(fm): slug for slug, (_, fm, _) in clients.items()}
    p_map = {resolve_entity_name(fm): slug for slug, (_, fm, _) in partners.items()}
    return c_map, p_map


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"--check", "--suggest"}:
        print("Usage: python3 check_symmetric_relations.py --check | --suggest")
        sys.exit(1)

    mode = sys.argv[1]

    clients, partners = load_all()
    c_name_map, p_name_map = build_name_to_slug_maps(clients, partners)

    asymmetries = []

    # For each client-side relation, check the inverse exists on partner side
    for c_slug, (c_path, c_fm, c_rels) in clients.items():
        c_name = resolve_entity_name(c_fm)
        for rel_type, target in c_rels:
            if rel_type not in PAIR_CLIENT_TO_PARTNER:
                continue
            expected_inverse = PAIR_CLIENT_TO_PARTNER[rel_type]
            # target should be a partner (or auto-symmetric a client for co_delivered_with)
            if rel_type == "co_delivered_with":
                # target can be partner or another client, check both maps
                if target in p_name_map:
                    p_slug = p_name_map[target]
                    _, _, p_rels = partners[p_slug]
                    if not any(rt == expected_inverse and t == c_name for rt, t in p_rels):
                        asymmetries.append({
                            "side": "client",
                            "source": str(c_path.relative_to(WORKSPACE)),
                            "source_name": c_name,
                            "relation": rel_type,
                            "target": target,
                            "expected_on": str(partners[p_slug][0].relative_to(WORKSPACE)),
                            "expected_line": f"- {expected_inverse} [[{c_name}]]",
                        })
                continue
            # Otherwise target is expected partner
            if target not in p_name_map:
                asymmetries.append({
                    "side": "client",
                    "source": str(c_path.relative_to(WORKSPACE)),
                    "source_name": c_name,
                    "relation": rel_type,
                    "target": target,
                    "expected_on": "ORPHAN (no matching partner)",
                    "expected_line": f"- {expected_inverse} [[{c_name}]]",
                })
                continue
            p_slug = p_name_map[target]
            _, _, p_rels = partners[p_slug]
            if not any(rt == expected_inverse and t == c_name for rt, t in p_rels):
                asymmetries.append({
                    "side": "client",
                    "source": str(c_path.relative_to(WORKSPACE)),
                    "source_name": c_name,
                    "relation": rel_type,
                    "target": target,
                    "expected_on": str(partners[p_slug][0].relative_to(WORKSPACE)),
                    "expected_line": f"- {expected_inverse} [[{c_name}]]",
                })

    # For each partner-side relation, check the inverse exists on client side
    PAIR_PARTNER_TO_CLIENT = {v: k for k, v in PAIR_CLIENT_TO_PARTNER.items() if k != v}
    for p_slug, (p_path, p_fm, p_rels) in partners.items():
        p_name = resolve_entity_name(p_fm)
        for rel_type, target in p_rels:
            if rel_type not in PAIR_PARTNER_TO_CLIENT:
                continue
            expected_inverse = PAIR_PARTNER_TO_CLIENT[rel_type]
            if target not in c_name_map:
                asymmetries.append({
                    "side": "partner",
                    "source": str(p_path.relative_to(WORKSPACE)),
                    "source_name": p_name,
                    "relation": rel_type,
                    "target": target,
                    "expected_on": "ORPHAN (no matching client)",
                    "expected_line": f"- {expected_inverse} [[{p_name}]]",
                })
                continue
            c_slug = c_name_map[target]
            _, _, c_rels = clients[c_slug]
            if not any(rt == expected_inverse and t == p_name for rt, t in c_rels):
                asymmetries.append({
                    "side": "partner",
                    "source": str(p_path.relative_to(WORKSPACE)),
                    "source_name": p_name,
                    "relation": rel_type,
                    "target": target,
                    "expected_on": str(clients[c_slug][0].relative_to(WORKSPACE)),
                    "expected_line": f"- {expected_inverse} [[{p_name}]]",
                })

    # Report
    print(f"=== Symmetric relations check ===")
    print(f"Clients scanned: {len(clients)}")
    print(f"Partners scanned: {len(partners)}")
    print(f"Asymmetries found: {len(asymmetries)}")
    print()

    if not asymmetries:
        print("✓ All symmetric relations are mirrored correctly.")
        return

    print("Asymmetries:")
    for a in asymmetries:
        print(f"  {a['source']}")
        print(f"    declares:  {a['relation']} [[{a['target']}]]")
        print(f"    missing on: {a['expected_on']}")
        if mode == "--suggest":
            print(f"    add line:   {a['expected_line']}")
        print()


if __name__ == "__main__":
    main()
