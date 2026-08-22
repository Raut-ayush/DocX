# DocX — Instructions

This file is a workflow for an AI coding assistant (Cursor, GitHub Copilot
Chat, or any other agentic IDE chat) to follow when asked to generate or
update this project's context docs. It does the same job as `Skill/SKILL.md`
(the Claude Code version), written as plain instructions instead of a
Claude-specific skill file.

**How to use:** tell your AI assistant something like *"Read
DocX/Instruction/INSTRUCTIONS.md and follow it to document this project"* —
or paste this file's contents into your assistant's custom
instructions/rules for this repo. If your assistant can run terminal
commands (most agentic IDE chats can), it can run the bundled recon script
itself as part of the workflow below.

---

## Your task

Generate or update seven standard context docs for this project, always in a
`docs/` folder at the project root (the folder that `DocX/` was cloned into,
i.e. one level up from this file):

- **`docs/project.md`** — short index: one-paragraph summary, key stats, links to the other docs.
- **`docs/PRD.md`** — the *why*: original idea, problem/motivation, target users, must-have features, non-goals, known pivots.
- **`docs/architecture.md`** — the *how*: tech stack, folder/module structure, key components, data flow, design decisions.
- **`docs/state.md`** — the *where things stand*: completion stage + estimate, what's built vs. what the PRD calls for, gaps, recent activity.
- **`docs/tasks.md`** — the *what's next*: a checklist of concrete remaining work.
- **`docs/decisions.md`** — an append-only log of notable technical/architecture decisions and why they were made.
- **`docs/changes.md`** — an append-only changelog of what changed in the codebase since the last run.

`DocX/rules.md` is a separate file (not regenerated here) that sets coding
rules for the AI — see the "Rules sync" note at the end of this file.

## Steps

**1. Run recon on the codebase.** From the project root:

```bash
python3 DocX/scripts/scan_project.py
```

No path argument needed when run from the project root — it defaults to
scanning the current working directory, while automatically skipping its
own `DocX/` folder (and any previously generated `docs/`) so it never
treats itself as part of the project being documented.

This gives you tech stack signals (manifests + parsed dependencies), git
history, README content, other doc files, TODO/FIXME markers, and the
contents of any docs this workflow previously generated (so you know if
you're updating rather than starting fresh).

**2. Check for prior docs.** If `existing_ai_docs` in the script output has
content, this is an update — tell the user briefly what the existing PRD
says and treat it as the last known statement of intent, rather than
ignoring it.

**3. Ask about the original idea** (skip only if a confirmed PRD already
exists). Ask:

1. What was the original idea / problem you were trying to solve?
2. Who is it for?
3. What would "done" look like — what were the must-have features?
4. Has anything changed since you started?

If the user doesn't remember or says to figure it out yourself, infer the
idea from the README, commit messages, and code — but clearly mark that
part of the PRD as **inferred, not confirmed**, so they know to double-check
it later.

**4. Read a little more code if needed** — entry points, routing/config
files, main modules — only enough to describe the architecture and evaluate
completion accurately. Don't try to read the whole codebase.

**5. Write the docs**, following the same logic each time:

- `PRD.md`: write fresh from the user's answers (or inferred + labeled) on
  first run. On updates, keep prior intent unless the user's new answers
  contradict it — note the change, don't silently erase old intent.
- `architecture.md`: regenerate from current code each run (this reflects
  present reality). Preserve any hand-written rationale notes that aren't
  derivable from the scan.
- `state.md`: always regenerate — completion stage, a rough percent
  estimate, and confidence notes explaining the basis. Explicitly flag any
  gap between what the PRD calls for and what the code actually has.
- `decisions.md`: **append-only**, never rewrite past entries. On first
  run, seed it with any decisions you can reasonably infer (framework
  choice, DB choice, etc.), dated today and marked "_reconstructed
  retroactively_". On later runs, compare the scan's `recent_commits`
  against what's already logged (by commit hash) and add entries only for
  new decisions — not every commit, just ones reflecting a real technical
  choice. Format: `## YYYY-MM-DD — <title>` with **Context**, **Decision**,
  **Why**.
- `tasks.md`: regenerate as a `- [ ]` checklist from TODOs/FIXMEs, PRD gaps,
  and anything the user flags. Keep prior completed items checked only if
  the code still supports that.
- `changes.md`: **append-only**, never rewrite past entries. First run:
  one entry as a baseline snapshot. Later runs: compare against the
  previous `state.md` and `recent_commits` to summarize what actually
  changed — dated, short bullet entries. If there's no git history, base
  it on the diff between old and new `state.md` instead.
- `project.md`: regenerate last, once every other doc is final — one
  paragraph summary, key stats, links to all six other docs.

Be specific and honest about completion — don't just restate PRD/README
claims without checking them against the actual code.

**6. Summarize what changed** in the chat, and flag anything surprising
(claims vs. reality mismatches, big PRD-vs-state gaps).

## Rules sync (recommended, one-time)

`DocX/rules.md` holds coding rules for the AI (style, scope, safety). Run
this once so those rules load automatically every session instead of
needing to be re-read each time:

```bash
python3 DocX/scripts/sync_rules.py .
```

This writes/updates a marked block in `CLAUDE.md`,
`.github/copilot-instructions.md`, and `.cursor/rules/docx-rules.mdc` —
whichever your tool uses — without touching any other content already in
those files. Re-run it any time you edit `DocX/rules.md`.

## Notes

- Works on any tech stack — the recon script detects common manifest files
  (package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, etc.)
  but degrades gracefully if none are found.
- Re-running should always leave the project better documented than before —
  never silently destroy prior human-written content.
