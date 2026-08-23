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

## Starting a brand-new project

Same clone, same command — DocX just behaves differently once it notices
there's basically no code yet. It never assumes; it always asks first:

```
You: @DocX start

DocX: Looks like there's little or no existing code here — want me to
      help you plan this project out from scratch instead of documenting
      existing code?

You: yes

DocX: What do you want to build? What problem does it solve?
You: A minimal habit tracker — just mark habits done, see a streak.
     Existing ones are too bloated with social features I don't want.

DocX: Who's it for?
You: Just me, for now.

DocX: What are the must-have features for a first version?
You: Add/remove habits, mark done for today, streak counter,
     it needs to remember data between runs.

DocX: Any tech stack preference?
You: Python, keep it simple — CLI is fine, no need for a web UI yet.
```

From that short back-and-forth, DocX writes:

- **`PRD.md`** — the idea, problem, and must-have features, straight from
  your answers.
- **`architecture.md`** — a *proposed* plan (e.g. Python + SQLite, a small
  CLI structure), clearly marked "not yet implemented" so it's never
  mistaken for real code.
- **`state.md`** — an honest `idea` stage, ~0% — nothing built yet, and
  it says so.
- **`tasks.md`** — a real starting backlog: set up the repo, implement
  storage, implement the core commands, add tests — not a scraped TODO
  list, an actual roadmap.
- **`decisions.md`** — why Python/SQLite over the alternatives, logged
  the moment you decided it, not reconstructed later from guesswork.
- **`changes.md`** — one baseline entry marking day one.

**Why bother planning before writing code?** Because that plan is exactly
what you hand the AI next. Ask it to start building against `tasks.md` in
the same session, and it's working from a real spec instead of improvising
architecture on the fly — with `rules.md` (already loaded, no extra
prompting needed) keeping the output disciplined as it goes. As you finish
real chunks of work, the AI will nudge you to re-run `@DocX` so `state.md`
and `tasks.md` catch up to reality instead of going stale the way most
"planning docs" do the moment coding actually starts.

It always confirms before switching into planning mode — if you say no,
or if there's actually more here than it thought, it just falls back to
the normal documentation flow.

Want to tune the coding rules? Edit `DocX/rules.md` directly — there's a
"Your Custom Rules" section at the bottom just for that — then re-run the
sync step above.
