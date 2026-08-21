# DocX

Point this at an old, half-finished, or "I forgot what state this is in"
project, and it generates a standard set of AI-development context docs —
`docs/project.md`, `docs/PRD.md`, `docs/architecture.md`, `docs/state.md`,
`docs/tasks.md` — by scanning the codebase, reading whatever docs already
exist, and asking you a few questions about the project's original idea to
figure out real completion vs. what was planned.

Works on any language/stack. Safe to re-run — it updates rather than
blindly overwrites, and it never touches itself or its own output when
scanning your code.

**→ See [`USE.md`](./USE.md) for the two-step quick start.**

## Structure

```
DocX/
│   README.md          you are here
│   USE.md              quick-start: how to run it (start here)
│   install.py          one-time setup for Claude Code (@DocX tagging)
│
├───Instruction/
│       INSTRUCTIONS.md  plain-text workflow for Cursor/Copilot/other agents
│
├───scripts/
│       scan_project.py  shared recon script, used by both flavors
│
└───Skill/
        SKILL.md          Claude Code skill definition
```

## What it produces

| File | Contents |
|---|---|
| `docs/project.md` | One-paragraph summary, key stats, links to the rest |
| `docs/PRD.md` | Original idea, problem, target users, must-have features, non-goals |
| `docs/architecture.md` | Tech stack, structure, key components, data flow |
| `docs/state.md` | Completion stage + estimate, gaps vs. PRD, confidence notes |
| `docs/tasks.md` | Checklist of concrete remaining work |

On the first run, it asks a few quick questions about the project's
original idea (since that's not something it can recover from code alone).
If you don't remember, just say so — it'll infer what it can from the
README/commits/code and clearly mark that part as inferred rather than
confirmed.

On later runs, it reads what's already in `docs/`, tells you what it found,
and updates rather than starting over — your PRD's original intent is kept
unless you tell it things have changed.

## License

MIT — copy it, fork it, change it, whatever's useful.
