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

**2. Decide: existing project, or brand-new?** Check `likely_new_project`
in the script output (a heuristic: almost no files, no manifests, no/minimal
git history — stays `true` even after planning docs exist, since `docs/`
itself isn't counted as code). **Never switch modes silently:**

- `true` and `existing_ai_docs` empty → confirm first: "Looks like there's
  little or no existing code here — want me to help you plan this project
  out from scratch instead of documenting existing code?" If confirmed, go
  to **Step 2a**.
- `true` but `existing_ai_docs` already has content → planning was already
  done in an earlier run and no code exists yet. Don't re-ask the planning
  questions — check in instead: ask if they've started building or if plans
  changed. If not, just regenerate `state.md`/`changes.md` noting "still no
  code written since last check-in" and leave the rest as-is.
- `false` → continue at Step 3, no need to ask.
- User declines planning mode or says there's more here → continue at Step 3.

**Step 2a — Planning mode (new project).** Ask:

1. What do you want to build? What problem does it solve?
2. Who is it for?
3. What are the must-have features for a first version?
4. Any tech stack preference, or should I suggest one?
5. Anything explicitly out of scope for now?

Write the docs with a forward-looking framing instead of a reverse-engineered
one:

- `PRD.md`: written directly from the answers (primary source, not inferred).
- `architecture.md`: a **proposed** plan — tech stack with a one-line reason
  each, planned structure, key components to build. Head it "Proposed — not
  yet implemented" so it's never mistaken for real code.
- `state.md`: stage `idea`, `percent_estimate` near 0, confidence notes
  saying this is a planning baseline, no code yet.
- `tasks.md`: an initial build roadmap from the PRD's must-have features —
  a real starting backlog, not TODO-scraped.
- `decisions.md`: log decisions actually made in this planning conversation
  (stack choice, trade-offs), same dated format as below.
- `changes.md`: one baseline entry — "Project initialized — planning docs
  created, no code written yet."
- `project.md`: the usual index, last.

Stay docs-only — write the plan, don't scaffold files or folders. The user
can ask you to start building against `tasks.md` directly afterward, with
`rules.md` already governing how you code it. Then skip to step 6
(Summarize) — steps 3-5 below are for the existing-project flow.

**3. Check for prior docs.** If `existing_ai_docs` in the script output has
content, this is an update — tell the user briefly what the existing PRD
says and treat it as the last known statement of intent, rather than
ignoring it.

**4. Ask about the original idea** (skip only if a confirmed PRD already
exists). Ask:

1. What was the original idea / problem you were trying to solve?
2. Who is it for?
3. What would "done" look like — what were the must-have features?
4. Has anything changed since you started?

If the user doesn't remember or says to figure it out yourself, infer the
idea from the README, commit messages, and code — but clearly mark that
part of the PRD as **inferred, not confirmed**, so they know to double-check
it later.

**5. Read a little more code if needed** — entry points, routing/config
files, main modules — only enough to describe the architecture and evaluate
completion accurately. Don't try to read the whole codebase.

**6. Write the docs**, following the same logic each time:

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

**7. Summarize what changed** in the chat, and flag anything surprising
(claims vs. reality mismatches, big PRD-vs-state gaps). If the scan output
has `"secrets_redacted": true`, tell the user directly — something
resembling a secret was found (e.g. in a README or code comment) and
redacted from the scan output, which may mean a real secret is sitting in
tracked code worth their attention.

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
- Files matching common secret patterns (`.env`, `*.pem`, `id_rsa`, etc.)
  are never read by the scan, and secret-shaped text found elsewhere is
  redacted before it reaches you. This is a best-effort safety net, not a
  guarantee — don't paste secrets into chat, and don't assume a missing
  redaction flag means none exist.
- The scan respects a project's `.gitignore` (best-effort — top-level
  patterns, not full gitignore semantics) so generated/vendored folders
  don't skew the tech-stack and completion analysis.
