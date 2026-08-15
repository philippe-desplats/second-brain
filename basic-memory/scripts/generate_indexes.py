#!/usr/bin/env python3
"""
Generate agent-readable static indexes from frontmatter metadata.

Obsidian Dataview queries render dynamic indexes inside Obsidian. Outside
Obsidian (Zed, CLI, AI agents reading raw markdown), the queries look like
dead text. This script materializes the same lookups as static markdown
files so any consumer sees a real table.

Indexes generated (under atlas/maps/):
    clients-active-static.md       all type=client-context with status=active
    partners-active-static.md      all type=partner-context with status=active
    projects-active-static.md      all type=project-brief with status=active
    recent-emails-static.md        type=email modified in last 14 days
    decisions-recent-static.md     observations [decision] in last 90 days

Each generated file is overwriteable on each run. They live next to their
Dataview equivalents in atlas/maps/ and are named with the `-static` suffix.

Usage:
    python3 basic-memory/scripts/generate_indexes.py
    python3 basic-memory/scripts/generate_indexes.py --output-dir atlas/maps/
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
IGNORED_SEGMENTS = {".git", "node_modules", ".obsidian", ".claude"}
DEFAULT_OUTPUT_DIR = WORKSPACE / "atlas" / "maps"


@dataclass
class Note:
    path: Path
    frontmatter: dict = field(default_factory=dict)
    body: str = ""

    @property
    def type(self) -> str:
        return str(self.frontmatter.get("type", ""))

    @property
    def status(self) -> str:
        return str(self.frontmatter.get("status", ""))

    @property
    def title(self) -> str:
        return str(
            self.frontmatter.get("title")
            or self.frontmatter.get("client")
            or self.frontmatter.get("partner")
            or self.path.stem
        )

    @property
    def last_updated(self) -> str:
        return str(
            self.frontmatter.get("last_updated")
            or self.frontmatter.get("date")
            or ""
        )

    @property
    def rel_path(self) -> str:
        return self.path.relative_to(WORKSPACE).as_posix()


def parse_frontmatter_yaml(fm_text: str) -> dict:
    """Parse the frontmatter subset this workspace uses, standard library only.

    Handles top-level `key: value` scalars (quoted or not, colons allowed
    inside the value), inline sequences `key: [a, b]`, block sequences with
    `- item` on the following lines, blank lines and full-line comments.

    Deliberate limits, this is not a general YAML parser: scalars are always
    returned as strings (callers stringify every value they read), a nested
    mapping is consumed without being parsed and its key maps to an empty
    string, and block scalars (`|`, `>`), trailing `# comments`, anchors and
    multi-document streams are not interpreted. It never raises: a line it
    cannot read is skipped, so a malformed block yields a partial dict.

    Deliberately duplicated in auto_link_entities.py rather than extracted:
    every script in this folder stays runnable on its own. The two copies must
    remain identical, change one and change the other.
    """

    def scalar(raw: str) -> str:
        """Strip one matching pair of surrounding quotes, and empty an explicit null."""
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
            return raw[1:-1]
        if raw in ("null", "~"):
            return ""
        return raw

    result: dict = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")):
            continue  # nested or orphan line, consumed with its parent key
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not key:
            continue
        if rest.startswith("[") and rest.endswith("]"):
            result[key] = [scalar(it) for it in rest[1:-1].split(",") if it.strip()]
            continue
        if rest:
            result[key] = scalar(rest)
            continue
        # Bare key: either a block sequence or a nested mapping. Consume the
        # whole indented block, only a sequence produces a value.
        items: list = []
        is_sequence = None
        while i < len(lines):
            nxt = lines[i]
            nxt_stripped = nxt.strip()
            if not nxt_stripped or nxt_stripped.startswith("#"):
                i += 1
                continue
            if not nxt.startswith((" ", "\t", "-")):
                break
            if is_sequence is None:
                is_sequence = nxt_stripped.startswith("- ")
            if is_sequence and nxt_stripped.startswith("- "):
                items.append(scalar(nxt_stripped[2:]))
            i += 1
        result[key] = items if is_sequence else ""
    return result


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    return parse_frontmatter_yaml(fm_text), body


def iter_notes(root: Path):
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if any(p in IGNORED_SEGMENTS for p in rel.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        fm, body = parse_frontmatter(text)
        yield Note(path=path, frontmatter=fm, body=body)


def write_index(
    output_dir: Path,
    name: str,
    title: str,
    description: str,
    rows: list[dict],
    columns: list[tuple[str, str]],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{name}-static.md"

    today = dt.date.today().isoformat()
    lines = [
        "---",
        f"title: {title}",
        "type: note",
        "subtype: index",
        f"generated: {today}",
        "auto_generated: true",
        "---",
        "",
        f"# {title}",
        "",
        f"_{description}_",
        f"_Generated on {today} by `generate_indexes.py`. Do not edit by hand._",
        "",
    ]

    if not rows:
        lines.append("No entries.")
    else:
        header = "| " + " | ".join(label for _, label in columns) + " |"
        sep = "| " + " | ".join("---" for _ in columns) + " |"
        lines.append(header)
        lines.append(sep)
        for row in rows:
            cells = []
            for key, _ in columns:
                value = row.get(key, "")
                cells.append(str(value).replace("|", "\\|"))
            lines.append("| " + " | ".join(cells) + " |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def build_clients_active(notes: list[Note]) -> list[dict]:
    rows = []
    for n in notes:
        if n.type == "client-context" and n.status == "active":
            rows.append(
                {
                    "name": f"[[{n.title}]]",
                    "path": n.rel_path,
                    "last_updated": n.last_updated,
                }
            )
    rows.sort(key=lambda r: r["last_updated"], reverse=True)
    return rows


def build_partners_active(notes: list[Note]) -> list[dict]:
    rows = []
    for n in notes:
        if n.type == "partner-context" and n.status == "active":
            rows.append(
                {
                    "name": f"[[{n.title}]]",
                    "path": n.rel_path,
                    "last_updated": n.last_updated,
                }
            )
    rows.sort(key=lambda r: r["last_updated"], reverse=True)
    return rows


def build_projects_active(notes: list[Note]) -> list[dict]:
    rows = []
    for n in notes:
        if n.type == "project-brief" and n.status == "active":
            rows.append(
                {
                    "name": f"[[{n.title}]]",
                    "category": n.frontmatter.get("category", ""),
                    "path": n.rel_path,
                    "last_updated": n.last_updated,
                }
            )
    rows.sort(key=lambda r: r["last_updated"], reverse=True)
    return rows


def build_recent_emails(notes: list[Note], days: int = 14) -> list[dict]:
    cutoff = dt.date.today() - dt.timedelta(days=days)
    rows = []
    for n in notes:
        if n.type != "email":
            continue
        date_str = n.frontmatter.get("date") or n.frontmatter.get("last_updated")
        if not date_str:
            continue
        try:
            d = dt.date.fromisoformat(str(date_str)[:10])
        except ValueError:
            continue
        if d < cutoff:
            continue
        rows.append(
            {
                "date": d.isoformat(),
                "subject": n.title,
                "path": n.rel_path,
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def build_decisions_recent(notes: list[Note], days: int = 90) -> list[dict]:
    cutoff = dt.date.today() - dt.timedelta(days=days)
    decision_re = re.compile(r"^- \[decision\] (.+)$", re.MULTILINE)
    rows = []
    for n in notes:
        date_str = n.frontmatter.get("date") or n.frontmatter.get("last_updated")
        if not date_str:
            continue
        try:
            d = dt.date.fromisoformat(str(date_str)[:10])
        except ValueError:
            continue
        if d < cutoff:
            continue
        for match in decision_re.finditer(n.body):
            rows.append(
                {
                    "date": d.isoformat(),
                    "decision": match.group(1).strip(),
                    "source": n.rel_path,
                }
            )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR.relative_to(WORKSPACE)})",
    )
    args = parser.parse_args(argv)

    notes = list(iter_notes(WORKSPACE))
    print(f"Scanned {len(notes)} notes.")

    generated = []

    rows = build_clients_active(notes)
    generated.append(
        write_index(
            args.output_dir,
            "clients-active",
            "Active clients",
            "All clients with status: active in their CLAUDE.md.",
            rows,
            [("name", "Client"), ("path", "Path"), ("last_updated", "Last update")],
        )
    )

    # Skip the partners index when the zone was pruned by /sb-init
    if (WORKSPACE / "sources" / "partners").is_dir():
        rows = build_partners_active(notes)
        generated.append(
            write_index(
                args.output_dir,
                "partners-active",
                "Active partners",
                "All partners with status: active in their CLAUDE.md.",
                rows,
                [("name", "Partner"), ("path", "Path"), ("last_updated", "Last update")],
            )
        )

    rows = build_projects_active(notes)
    generated.append(
        write_index(
            args.output_dir,
            "projects-active",
            "Active projects",
            "All projects (type: project-brief) with status: active.",
            rows,
            [
                ("name", "Project"),
                ("category", "Category"),
                ("path", "Path"),
                ("last_updated", "Last update"),
            ],
        )
    )

    rows = build_recent_emails(notes)
    generated.append(
        write_index(
            args.output_dir,
            "recent-emails",
            "Recent emails",
            "Emails (type: email) dated within the last 14 days.",
            rows,
            [("date", "Date"), ("subject", "Subject"), ("path", "Path")],
        )
    )

    rows = build_decisions_recent(notes)
    generated.append(
        write_index(
            args.output_dir,
            "decisions-recent",
            "Recent decisions",
            "Observations [decision] captured within the last 90 days.",
            rows,
            [("date", "Date"), ("decision", "Decision"), ("source", "Source")],
        )
    )

    print("Generated:")
    for p in generated:
        try:
            display = p.relative_to(WORKSPACE).as_posix()
        except ValueError:
            display = str(p)
        print(f"  {display}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
