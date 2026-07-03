#!/usr/bin/env python3
"""Condensed replay of a /sb-init session inside Claude Code, used to record docs/demo.gif.

Regenerate the GIF with `vhs docs/demo.tape` (https://github.com/charmbracelet/vhs).
The exchanges below are a shortened replay of a real guided setup session; the
rendering mimics the Claude Code terminal UI (welcome banner, input box, tool calls).
"""

import sys
import time

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
ORANGE = "\033[38;2;215;119;87m"

BOX_W = 62


def out(text: str, delay: float = 0.006, end: str = "\n") -> None:
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


def say(text: str = "", delay: float = 0.002) -> None:
    out(text, delay=delay)


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def bline(text: str = "") -> None:
    pad = BOX_W - 1 - len(text)
    rendered = text.replace("✻", f"{ORANGE}✻{RESET}")
    print("│ " + rendered + " " * pad + "│")


def banner() -> None:
    print("╭" + "─" * BOX_W + "╮")
    bline("✻ Welcome to Claude Code!")
    bline()
    bline("  /help for help, /status for your current setup")
    bline()
    bline("  cwd: ~/my-second-brain")
    print("╰" + "─" * BOX_W + "╯")


def input_box(text: str) -> None:
    time.sleep(0.7)
    print("╭" + "─" * BOX_W + "╮")
    print("│ >" + " " * (BOX_W - 2) + "│")
    print("╰" + "─" * BOX_W + "╯")
    print(f"{DIM}  ? for shortcuts{RESET}")
    sys.stdout.write("\033[3A\033[5G")
    sys.stdout.flush()
    time.sleep(0.5)
    out(text, delay=0.04, end="")
    time.sleep(0.6)
    sys.stdout.write("\033[1A\r\033[0J")
    sys.stdout.flush()
    print(f"{DIM}> {text}{RESET}")
    print()


def think(label: str, fake_secs: int) -> None:
    for i in range(8):
        dots = "·" * (i % 4)
        sys.stdout.write(f"\r\033[K{ORANGE}✻{RESET} {DIM}Thinking{dots}{RESET}")
        sys.stdout.flush()
        time.sleep(0.16)
    sys.stdout.write(f"\r\033[K{DIM}✻ {label} for {fake_secs}s{RESET}\n\n")
    sys.stdout.flush()


def claude(*lines: str) -> None:
    for i, line in enumerate(lines):
        prefix = "⏺ " if i == 0 else "  "
        out(prefix + line, delay=0.007)
    print()


def tool(call: str, result: str) -> None:
    out(f"{GREEN}⏺{RESET} {BOLD}{call}{RESET}", delay=0.003)
    out(f"  {DIM}⎿  {result}{RESET}", delay=0.002)


def answered(question: str, answer: str) -> None:
    out(f"⏺ {BOLD}User answered Claude's questions:{RESET}", delay=0.004)
    out(f"  {DIM}· {question} → {GREEN}{answer}{RESET}", delay=0.004)
    print()


def ask_select(header: str, question: str, options: list, pick_index: int) -> None:
    time.sleep(0.6)

    def draw(pointer: int) -> list:
        title = f"─ {header} "
        lines = ["╭" + title + "─" * (BOX_W - len(title)) + "╮"]
        lines.append("│ " + question + " " * (BOX_W - 1 - len(question)) + "│")
        lines.append("│" + " " * BOX_W + "│")
        for i, (name, desc) in enumerate(options):
            if i == pointer:
                text = f" ❯ {name:<13}{desc}"
                lines.append("│" + f"{GREEN}{BOLD}{text}{RESET}" + " " * (BOX_W - len(text)) + "│")
            else:
                text = f"   {name:<13}{desc}"
                lines.append("│" + DIM + text + RESET + " " * (BOX_W - len(text)) + "│")
        lines.append("╰" + "─" * BOX_W + "╯")
        return lines

    block = draw(0)
    for line in block:
        print(line)
    height = len(block)
    for pointer in range(1, pick_index + 1):
        time.sleep(0.8)
        sys.stdout.write(f"\033[{height}A")
        for line in draw(pointer):
            sys.stdout.write("\r\033[K" + line + "\n")
        sys.stdout.flush()
    time.sleep(1.0)
    sys.stdout.write(f"\033[{height}A\r\033[0J")
    sys.stdout.flush()


def main() -> None:
    clear()
    say(f"{DIM}~/my-second-brain{RESET}")
    sys.stdout.write(BOLD + "$ " + RESET)
    sys.stdout.flush()
    time.sleep(0.5)
    out("claude", delay=0.09)
    time.sleep(0.9)

    clear()
    banner()
    print()

    input_box("/sb-init")
    think("Cogitated", 3)
    claude(
        f"{BOLD}Welcome to your second brain.{RESET} Six steps, about 15",
        "minutes: why, profile, identity, personalization, memory,",
        "launch. Nothing is written before you approve a recap.",
    )
    time.sleep(0.5)
    claude(
        f"{BOLD}Question 1 of 5, the trigger.{RESET} What happened recently",
        "that made you decide you needed this?",
    )

    input_box("Last week I forgot a commitment made in a client meeting")
    think("Worked", 5)
    claude(
        "Ouch, the spoken commitment that slips away. That is exactly",
        "the kind of leak this system plugs. Noted as your trigger.",
        f"{DIM}(four more: status quo, success in 90 days, priority flow,{RESET}",
        f"{DIM}retrieval pain){RESET}",
    )

    ask_select(
        "Profile",
        "Which profile is closest to how you work?",
        [
            ("Agency", "A team serving multiple clients"),
            ("Freelance", "You deliver work to clients on your own"),
            ("Solopreneur", "Your own products, few client folders"),
            ("Personal", "Knowledge and life projects"),
        ],
        1,
    )
    answered("Which profile is closest to how you work?", "Freelance")
    claude(
        "Freelance keeps three zones: clients, internal, personal.",
        "Here is the full recap, nothing written yet:",
    )
    say("  ┌────────────────┬──────────────────────────────────────────┐")
    say("  │ Trigger        │ Forgotten commitment, client meeting     │")
    say("  │ Priority flow  │ Client context before every call         │")
    say("  │ Profile        │ freelance (clients, internal, personal)  │")
    say("  │ Language       │ English                                  │")
    say("  │ Tone defaults  │ warm professional, sign-off: Alex, Acme  │")
    say("  └────────────────┴──────────────────────────────────────────┘")
    print()

    input_box("Approved.")
    think("Brewed", 4)
    tool("Write(sources/internal/second-brain-charter.md)", "Wrote 24 lines")
    tool("Write(sources/internal/CONTEXT.md)", "Wrote 18 lines")
    tool("Update(CLAUDE.md)", "Profile block filled, zones pruned")
    tool("Update(.sb-config.json)", "initialized: true")
    print()

    claude(f"{GREEN}{BOLD}✓ Your second brain is ready.{RESET}")
    say("  ┌────────────────┬──────────────────────────────────────────┐")
    say("  │ First note     │ sources/clients/acme/consulting/emails/  │")
    say("  │ Semantic search│ Basic Memory wired, project: my-brain    │")
    say("  │ Weekly ritual  │ friday, /curate -w 7                     │")
    say("  └────────────────┴──────────────────────────────────────────┘")
    print()
    claude(
        "Feed the priority flow first: client context before every",
        "call. That is where the system earns your trust.",
    )
    time.sleep(3.0)


if __name__ == "__main__":
    main()
