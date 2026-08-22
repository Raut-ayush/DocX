# Using DocX

> **Windows note:** if `python3` isn't recognized in your terminal, use
> `python` instead in every command below (some Windows Python installs
> only register the `python` command).

Two ways to use it, pick one:

## Claude Code

```bash
git clone https://github.com/Raut-ayush/DocX.git DocX
python3 DocX/install.py
```

Then in Claude Code chat, inside this project:

```
@DocX start
```

`install.py` does two things in one go: copies what Claude Code needs into
`.claude/skills/DocX/` so the tag works, and syncs `DocX/rules.md` into
`CLAUDE.md` so your coding rules apply automatically every session.
Re-run it if you ever edit `Skill/SKILL.md` or `rules.md`.

## Cursor / Copilot Chat / any other agentic IDE chat

```bash
git clone https://github.com/Raut-ayush/DocX.git DocX
python3 DocX/scripts/sync_rules.py .
```

The sync step is optional but recommended — it loads `DocX/rules.md` into
whichever file your tool auto-reads every session (`.github/copilot-instructions.md`,
`.cursor/rules/`), so the AI follows your rules without you repeating them.

Then in your AI chat, inside this project, say:

```
Read DocX/Instruction/INSTRUCTIONS.md and follow it to document this project.
```

---

Either way, on first run it'll ask you a few quick questions about the
project's original idea (what it does that code alone can't tell it), then
generate `docs/project.md`, `docs/PRD.md`, `docs/architecture.md`,
`docs/state.md`, `docs/tasks.md`, `docs/decisions.md`, and `docs/changes.md`
at your project root. Run it again any time to refresh — it updates rather
than starting over, and `decisions.md`/`changes.md` grow as a running log
instead of being rewritten.

Want to tune the coding rules? Edit `DocX/rules.md` directly — there's a
"Your Custom Rules" section at the bottom just for that — then re-run the
sync step above.
