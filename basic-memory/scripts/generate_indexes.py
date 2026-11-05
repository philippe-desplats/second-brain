#!/usr/bin/env python3
"""
Generate agent-readable static indexes from frontmatter metadata.

Obsidian Bases views render dynamic indexes inside Obsidian. Outside
Obsidian (Zed, CLI, agents reading raw markdown), a `.base` file is inert
configuration rather than a readable table. This script materializes the equivalent lookups as static markdown files so
any consumer sees a real table. Equivalent, not identical: `recent-emails`
cuts at fourteen days here while its `.base` twin caps at fourteen rows.

Indexes generated (under atlas/maps/):
    clients-active-static.md       all type=client-context with status=active
    partners-active-static.md      all type=partner-context with status=active
    projects-active-static.md      all type=project-brief with status=active
    recent-emails-static.md        type=email whose `date` is in the last 14 days
    decisions-recent-static.md     observations [decision] in last 90 days

Only corpus notes are indexed, through `corpus.iter_corpus_notes`: a row
pointing into `prompts/`, `captures/`, `repo-files/`, `templates/` or `docs/`
would list a file that is not a note.

Each generated file is overwriteable on each run. They live next to the
`.base` views in atlas/maps/ and are named with the `-static` suffix. The
`decisions-recent` index has no `.base` twin: it reads observations from note
bodies, which Bases cannot filter on.

Usage:
    python3 basic-memory/scripts/generate_indexes.py
    python3 basic-memory/scripts/generate_indexes.py --output-dir atlas/maps/
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import WORKSPACE, iter_corpus_notes  # noqa: E402
from frontmatter import parse, split  # noqa: E402

DEFAULT_OUTPUT_DIR = WORKSPACE / "atlas" / "maps"


@dataclass
class Note:
    path: Path
    rel_path: str
    frontmatter: dict = field(default_factory=dict)
    body: str = ""

    def text(self, *keys: str) -> str:
        """The first of `keys` holding a non-empty value, as text, else ""."""
        for key in keys:
            value = self.frontmatter.get(key)
            if value not in (None, "", []):
                return str(value)
        return ""

    @property
    def type(self) -> str:
        return self.text("type")

    @property
    def status(self) -> str:
        return self.text("status")

    @property
    def title(self) -> str:
        return self.text("title", "client", "partner") or self.path.stem

    @property
    def last_updated(self) -> str:
        return self.text("last_updated", "date")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    doc = split(text)
    if doc is None:
        return {}, text
    return parse(doc.block).to_dict(), doc.body


def iter_notes(root: Path):
    for path, rel in iter_corpus_notes(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        fm, body = parse_frontmatter(text)
        yield Note(path=path, rel_path=rel, frontmatter=fm, body=body)


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
        "schema_version: 1",
        "subtype: index",
        f"date: {today}",
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
                cells.append(" ".join(str(value).split()).replace("|", "\\|"))
            lines.append("| " + " | ".join(cells) + " |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def build_active(notes: list[Note], note_type: str, extra: tuple[str, ...] = ()) -> list[dict]:
    """Rows for every note of `note_type` with status active, newest update first.

    `extra` names frontmatter fields copied into the row as they are.
    """
    rows = []
    for n in notes:
        if n.type == note_type and n.status == "active":
            row = {
                "name": f"[[{n.title}]]",
                "path": n.rel_path,
                "last_updated": n.last_updated,
            }
            for key in extra:
                row[key] = n.text(key)
            rows.append(row)
    rows.sort(key=lambda r: r["last_updated"], reverse=True)
    return rows


def build_recent_emails(notes: list[Note], days: int = 14) -> list[dict]:
    cutoff = dt.date.today() - dt.timedelta(days=days)
    rows = []
    for n in notes:
        if n.type != "email":
            continue
        date_str = n.text("date", "last_updated")
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
        date_str = n.text("date", "last_updated")
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


def main(argv: list[str], root: Path = WORKSPACE) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR.relative_to(WORKSPACE)})",
    )
    args = parser.parse_args(argv)

    notes = list(iter_notes(root))
    print(f"Scanned {len(notes)} notes.")

    generated = []

    rows = build_active(notes, "client-context")
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
    if (root / "sources" / "partners").is_dir():
        rows = build_active(notes, "partner-context")
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

    rows = build_active(notes, "project-brief", extra=("category",))
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
            display = p.relative_to(root).as_posix()
        except ValueError:
            display = str(p)
        print(f"  {display}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
