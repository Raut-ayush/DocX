# Using DocX

Two ways to use it, pick one:

## Claude Code

```bash
git clone <this-repo-url> DocX
python3 DocX/install.py
```

Then in Claude Code chat, inside this project:

```
@DocX start
```

(`install.py` copies what Claude Code needs into `.claude/skills/DocX/` so
the tag works. Re-run it if you ever edit `Skill/SKILL.md`.)

## Cursor / Copilot Chat / any other agentic IDE chat

```bash
git clone <this-repo-url> DocX
```

Then in your AI chat, inside this project, say:

```
Read DocX/Instruction/INSTRUCTIONS.md and follow it to document this project.
```

---

Either way, on first run it'll ask you a few quick questions about the
project's original idea (what it does that code alone can't tell it), then
generate `docs/project.md`, `docs/PRD.md`, `docs/architecture.md`,
`docs/state.md`, and `docs/tasks.md` at your project root. Run it again
any time to refresh — it updates rather than starting over.
