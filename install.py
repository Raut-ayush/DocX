#!/usr/bin/env python3
"""
install.py — one-time setup for Claude Code.

Claude Code only auto-discovers skills sitting in .claude/skills/<name>/.
Since DocX is meant to be cloned directly into a project's root folder,
this copies what Claude Code needs (SKILL.md + scripts/) into
.claude/skills/DocX/, so you can tag it with @DocX in Claude Code chat.

It also syncs DocX/rules.md into CLAUDE.md, .github/copilot-instructions.md,
and .cursor/rules/, so your coding rules load into the AI's context every
session automatically, without needing to be re-read each time.

Not needed for the generic flow (Cursor, Copilot, etc. without Claude Code) —
use scripts/sync_rules.py directly for the rules sync in that case.

Usage (run once, from anywhere):
    python3 install.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOL_ROOT.parent

SKILL_SRC = TOOL_ROOT / "Skill" / "SKILL.md"
SCRIPTS_SRC = TOOL_ROOT / "scripts"
SYNC_SCRIPT = TOOL_ROOT / "scripts" / "sync_rules.py"

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

    print("\nSyncing DocX/rules.md into your AI tools' auto-loaded context...")
    subprocess.run([sys.executable, str(SYNC_SCRIPT), str(PROJECT_ROOT)], check=False)

    print("\nIn Claude Code, inside this project, you can now run:")
    print("    @DocX start")
    print()
    print("Note: if you edit DocX/Skill/SKILL.md or DocX/rules.md later,")
    print("re-run this script to sync the changes.")


if __name__ == "__main__":
    main()
