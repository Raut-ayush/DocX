#!/usr/bin/env python3
"""
install.py — one-time setup for Claude Code.

Claude Code only auto-discovers skills sitting in .claude/skills/<name>/.
Since DocX is meant to be cloned directly into a project's root folder,
this copies what Claude Code needs (SKILL.md + scripts/) into
.claude/skills/DocX/, so you can tag it with @DocX in Claude Code chat.

Not needed if you're just using the generic Instruction/INSTRUCTIONS.md
flow with Cursor, Copilot, etc.

Usage (run once, from anywhere):
    python3 install.py
"""

import shutil
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOL_ROOT.parent

SKILL_SRC = TOOL_ROOT / "Skill" / "SKILL.md"
SCRIPTS_SRC = TOOL_ROOT / "scripts"

DEST_DIR = PROJECT_ROOT / ".claude" / "skills" / "DocX"


def main():
    if not SKILL_SRC.exists():
        print(f"Could not find {SKILL_SRC} — is this script still inside DocX/?")
        sys.exit(1)

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILL_SRC, DEST_DIR / "SKILL.md")

    dest_scripts = DEST_DIR / "scripts"
    if dest_scripts.exists():
        shutil.rmtree(dest_scripts)
    shutil.copytree(SCRIPTS_SRC, dest_scripts)

    print(f"Installed DocX into: {DEST_DIR}")
    print("In Claude Code, inside this project, you can now run:")
    print("    @DocX start")
    print()
    print("Note: if you edit DocX/Skill/SKILL.md later, re-run this script")
    print("to sync the change into .claude/skills/DocX/.")


if __name__ == "__main__":
    main()
