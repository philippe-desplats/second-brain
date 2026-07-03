#!/usr/bin/env python3
"""Weekly curation reminder: drops a note in inbox/ and fires a best-effort OS notification.

Schedule this script (launchd on macOS, cron on Linux, Task Scheduler on Windows);
it never runs the assistant itself. The owner opens Claude Code and runs
/curate -w 7 when they see the reminder. Idempotent: one reminder per day maximum.
"""

import datetime
import platform
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
INBOX = WORKSPACE / "inbox"

MESSAGE = "Curation time: open Claude Code and run /curate -w 7"


def write_reminder(today):
    if not INBOX.is_dir():
        return None
    path = INBOX / f"{today}-note-curation-reminder.md"
    if path.exists():
        return None
    lines = [
        "---",
        f"title: Curation reminder {today}",
        "type: note",
        f"date: {today}",
        "---",
        "",
        "# Curation reminder",
        "",
        f"{MESSAGE}.",
        "Delete this file once the review is done.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def notify():
    system = platform.system()
    try:
        if system == "Darwin":
            script = f'display notification "{MESSAGE}" with title "Second brain"'
            subprocess.run(["osascript", "-e", script],
                           check=False, capture_output=True, timeout=10)
        elif system == "Linux":
            subprocess.run(["notify-send", "Second brain", MESSAGE],
                           check=False, capture_output=True, timeout=10)
        elif system == "Windows":
            popup = f"(New-Object -ComObject Wscript.Shell).Popup('{MESSAGE}', 10, 'Second brain')"
            subprocess.run(["powershell", "-NoProfile", "-Command", popup],
                           check=False, capture_output=True, timeout=15)
    except Exception:
        pass  # notification is best-effort; the inbox note is the reliable channel


def main():
    today = datetime.date.today().isoformat()
    created = write_reminder(today)
    notify()
    if created:
        print(f"Reminder written: {created}")
    else:
        print("Reminder already present or inbox/ missing; nothing written.")


if __name__ == "__main__":
    main()
