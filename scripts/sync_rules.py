#!/usr/bin/env python3
"""
sync_rules.py — propagate DocX/rules.md into the files each AI IDE tool
auto-loads into context every session, so the rules apply automatically
without the AI needing to re-read a separate file (saving tokens/credits).

Sync targets, relative to the project root:
    CLAUDE.md                          (Claude Code project memory)
    .github/copilot-instructions.md    (GitHub Copilot Chat)
    .cursor/rules/docx-rules.mdc       (Cursor project rules)

For CLAUDE.md and copilot-instructions.md — files that may already contain
other project-specific content — this inserts/replaces a clearly marked
block rather than overwriting the whole file, so re-running is always safe.
For the dedicated Cursor rules file, it just writes the whole file, since
that file belongs entirely to DocX.

Usage (run from the project root, or pass a path):
    python3 sync_rules.py [project_root]

These tools' conventions can change over time — if a sync target seems
outdated, check that tool's current docs before assuming DocX is wrong.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TOOL_ROOT = SCRIPT_DIR.parent
RULES_SRC = TOOL_ROOT / "rules.md"

MARKER_START = "<!-- DocX:rules:start -->"
MARKER_END = "<!-- DocX:rules:end -->"


def build_block(rules_text: str) -> str:
    return f"{MARKER_START}\n{rules_text.strip()}\n{MARKER_END}"


def upsert_marked_block(target: Path, block: str, header_if_new: str = ""):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        content = target.read_text(errors="ignore")
        if MARKER_START in content and MARKER_END in content:
            pre = content.split(MARKER_START)[0]
            post = content.split(MARKER_END)[1]
            new_content = pre + block + post
        else:
            sep = "\n\n" if content and not content.endswith("\n\n") else ""
            new_content = content + sep + block + "\n"
    else:
        new_content = (header_if_new + "\n\n" if header_if_new else "") + block + "\n"
    target.write_text(new_content)


def sync_claude_md(root: Path, rules_text: str):
    target = root / "CLAUDE.md"
    upsert_marked_block(target, build_block(rules_text))
    return target


def sync_copilot_instructions(root: Path, rules_text: str):
    target = root / ".github" / "copilot-instructions.md"
    upsert_marked_block(target, build_block(rules_text))
    return target


def sync_cursor_rules(root: Path, rules_text: str):
    target = root / ".cursor" / "rules" / "docx-rules.mdc"
    target.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = "---\nalwaysApply: true\n---\n\n"
    target.write_text(frontmatter + rules_text.strip() + "\n")
    return target


def main():
    if not RULES_SRC.exists():
        print(f"Could not find {RULES_SRC} — is this script still inside DocX/scripts/?")
        sys.exit(1)

    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()
    rules_text = RULES_SRC.read_text(errors="ignore")

    written = [
        sync_claude_md(root, rules_text),
        sync_copilot_instructions(root, rules_text),
        sync_cursor_rules(root, rules_text),
    ]

    print(f"Synced {RULES_SRC} into:")
    for w in written:
        print(f"  - {w.relative_to(root)}")
    print("\nRe-run this any time you edit DocX/rules.md to keep these in sync.")


if __name__ == "__main__":
    main()
