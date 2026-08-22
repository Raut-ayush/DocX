---
name: docx
description: Generates or updates a standard set of AI-development context docs for THIS project — docs/project.md, docs/PRD.md, docs/architecture.md, docs/state.md, docs/tasks.md — for either an existing codebase (by scanning it and evaluating real completion vs. what was planned) or a brand-new empty project (by asking about the idea and writing a planning-first doc set before any code exists). Use when the user tags this skill and says things like "start", "document this", "generate docs", "update docs", "status", "plan this out", or "figure out where this project is at". Works on any project regardless of language or stack, at any stage from empty to complete.
---

# DocX

Creates (or intelligently updates) seven standard context docs for this
project, so both humans and AI coding assistants have an accurate, current
picture of what it is, how it's built, and how far along it actually is.
Works whether the project has years of history or hasn't been started yet —
see the branch in step 2 below.

## Output files (always in `docs/` at the project root)

- **`docs/project.md`** — short index: one-paragraph summary, key stats, links to the other docs.
- **`docs/PRD.md`** — the *why*: original idea, problem/motivation, target users, must-have features, non-goals, any known pivots.
- **`docs/architecture.md`** — the *how*: tech stack, folder/module structure, key components, data flow, notable design decisions.
- **`docs/state.md`** — the *where things stand*: completion stage + estimate, what's actually built vs. what the PRD calls for, known gaps/discrepancies, recent activity.
- **`docs/tasks.md`** — the *what's next*: a checklist of concrete remaining work.
- **`docs/decisions.md`** — an append-only log of notable technical/architecture decisions and why they were made.
- **`docs/changes.md`** — an append-only changelog of what changed in the codebase since the last run.

Note: `DocX/rules.md` (coding rules for the AI) is a separate, project-level
file — not regenerated per run. It's synced into `CLAUDE.md`,
`.github/copilot-instructions.md`, and `.cursor/rules/` by
`scripts/sync_rules.py` (run once via `install.py`, or manually re-run
after editing `rules.md`), so those rules are already in the AI's context
every session — you don't need to re-read it here.

## Workflow

### 1. Run recon

This skill was installed by `install.py`, which copies this file plus a
`scripts/` folder into `.claude/skills/DocX/`. Run it with a path relative
to the project root (the bash tool's working directory is the project
root by default):

```bash
python3 .claude/skills/DocX/scripts/scan_project.py
```

It defaults to scanning the current working directory and automatically
skips its own files (both the installed copy and any leftover `DocX/`
clone folder at the project root) plus any previously generated `docs/`.
If the working directory isn't the project root for some reason, pass the
correct path explicitly as an argument.

This returns JSON with: tech stack signals (manifests, parsed dependencies),
git history (first/last commit, commit count, recent commit messages),
README content, other doc files found, a TODO/FIXME count with examples,
and — critically — the **contents of any docs this skill already generated
before** (`existing_ai_docs`), so you know if this is a first run or an update.

### 2. Decide: existing project, or brand-new?

Check `likely_new_project` in the scan output (a heuristic: almost no
files, no manifests, and no/minimal git history — note this stays `true`
even after planning docs exist, since `docs/` itself isn't counted as code).
**Never switch modes silently:**

- `likely_new_project` is `true` **and** `existing_ai_docs` is empty →
  confirm with the user first: "Looks like there's little or no existing
  code here — want me to help you plan this project out from scratch
  instead of documenting existing code?" If confirmed, go to **Step 2a**.
- `likely_new_project` is `true` **but** `existing_ai_docs` already has
  content → planning was already done in an earlier run and no code exists
  yet. Don't re-ask the planning questions. Just check in: ask the user
  whether they've started building or if plans have changed since; if not,
  regenerate `state.md` and `changes.md` to note "still no code written
  since last check-in" and leave `PRD.md`/`architecture.md`/`tasks.md` as
  they are.
- `likely_new_project` is `false` → continue with the normal flow at Step 3,
  no need to ask.
- User declines planning mode, or says there's actually more here → continue
  at Step 3.

#### Step 2a — Planning mode (new project)

Instead of documenting existing code, help the user plan before any exists.
Ask:

1. What do you want to build? What problem does it solve?
2. Who is it for?
3. What are the must-have features for a first version?
4. Any tech stack preference, or should I suggest one based on what you've described?
5. Anything explicitly out of scope for now?

From the answers, write the doc set with a forward-looking framing instead
of a reverse-engineered one:

- **`PRD.md`** — written directly from the user's answers (this is the
  primary source now, not inferred).
- **`architecture.md`** — a **proposed** plan: chosen/suggested tech stack
  with a one-line reason each, a planned folder/module structure, and the
  key components to be built. Clearly headed "Proposed — not yet
  implemented" so it's never mistaken for a description of real code.
- **`state.md`** — stage `idea`, `percent_estimate` near 0, confidence
  notes stating this is a planning baseline with no code written yet.
- **`tasks.md`** — an initial build roadmap derived from the PRD's
  must-have features (e.g. "Set up project skeleton", then one task per
  core feature, then testing/deployment basics) — a real starting backlog,
  not a TODO-scraped list.
- **`decisions.md`** — log the decisions actually made in this planning
  conversation (stack choice, key trade-offs), dated today, in the normal
  `## YYYY-MM-DD — <title>` / **Context** / **Decision** / **Why** format.
- **`changes.md`** — one baseline entry: "Project initialized — planning
  docs created, no code written yet."
- **`project.md`** — the usual index, last.

DocX stays docs-only here — it writes the plan, it doesn't scaffold files
or folders. Once the docs exist, the user can ask you directly to start
building against `tasks.md` in this or a later session, and `rules.md`
(already loaded into your context) governs how you code it.

Then skip to Step 7 (Report back) — steps 3-6 below are for the existing-
project flow.

### 3. Check for existing docs

If `existing_ai_docs` in the scan output has content (i.e. this isn't the
first run):
- Treat the existing `PRD.md` as the last known statement of intent.
- Briefly tell the user what you found (e.g. "Found an existing PRD saying
  this is a recipe-sharing app for home cooks — still accurate?") rather
  than silently discarding it.
- Plan to **update, not blindly overwrite** — see step 5.

If there are no existing docs, this is a first run — proceed to ask about
the original idea before writing anything.

### 4. Ask the user about the original idea

Skip this step only if a solid, still-confirmed `PRD.md` already exists.
Otherwise, ask a short set of guided questions (don't dump all at once if
the chat UI supports incremental turns — but a single grouped message is
fine too):

1. What was the original idea / problem you were trying to solve with this project?
2. Who is it for?
3. What would "done" look like — what were the must-have features?
4. Has anything changed since you started (pivots, dropped features, new direction)?

**If the user says they don't remember / says to figure it out yourself:**
fall back to inferring the idea from the README, commit messages, and code
structure — but clearly label that section of the PRD as **inferred, not
confirmed** (e.g. "_Inferred from code and commit history — please correct
if this is wrong._"), so the user knows to sanity-check it later.

### 5. Read further if needed

Use the README content, doc files, and TODO examples from the scan first.
If that's not enough to describe the architecture or evaluate completion
confidently, read a handful of key source files yourself (entry points,
routing/config files, main modules) — don't read the whole codebase, just
enough to be accurate.

### 6. Write or update the docs

For each file, reason about what changed and write the updated version:

- **`PRD.md`** — write fresh on first run from the user's answers (or
  inferred + labeled). On updates, keep the existing PRD unless the user's
  answers this time contradict it — then note the change rather than
  silently erasing the old intent.
- **`architecture.md`** — regenerate from current code each time; architecture
  reflects present reality, not history. If the existing file has a
  hand-written section that's not something you could have derived from
  the scan (e.g. a rationale note), preserve it rather than deleting it.
- **`state.md`** — always regenerate. This is a point-in-time snapshot:
  completion `stage` (idea / scaffolded / in-progress / near-complete /
  complete / abandoned), a rough `percent_estimate`, and — importantly —
  **confidence notes** explaining the basis for that estimate. Explicitly
  call out any gap between what the PRD says should exist and what the
  code actually shows (e.g. "PRD lists user auth as a must-have; no auth
  code found in the scan").
- **`decisions.md`** — **append-only**, never rewrite past entries. On first
  run, seed it with any decisions you can reasonably infer (e.g. framework
  choice, DB choice) dated as of today and clearly marked
  "_reconstructed retroactively — not logged in real time_". On later runs,
  compare the scan's `recent_commits` against what's already logged (match
  by commit hash) and add new entries only for decisions not yet recorded —
  don't log every commit, only ones that reflect a real technical/architecture
  choice (a new dependency, a structural change, a chosen pattern). Format
  each entry as:
  ```
  ## YYYY-MM-DD — <short title>
  **Context:** why this came up
  **Decision:** what was chosen
  **Why:** the reasoning / trade-off
  ```
- **`tasks.md`** — regenerate as a checklist (`- [ ] ...`), pulling from
  TODO/FIXME markers, PRD requirements not yet met, and anything the user
  flagged. If the previous `tasks.md` had items checked off as done, only
  keep them checked if the code still reflects that (don't silently
  un-check completed work, but do add newly-discovered gaps).
- **`changes.md`** — **append-only**, never rewrite past entries. On first
  run, add one entry summarizing the current state as a baseline snapshot.
  On later runs, compare the current scan against the previous `state.md`
  (from `existing_ai_docs`) and the `recent_commits` list to summarize what
  actually changed since the last run — new features, resolved gaps, new
  dependencies. Keep entries dated and short:
  ```
  ## YYYY-MM-DD
  - Added task CRUD endpoints
  - Added Jest test coverage for src/app.js
  ```
  If the project has no git history to diff against, base this on what's
  different between the old and new `state.md` content instead.
- **`project.md`** — always regenerate last, once every other doc is final:
  one paragraph summary + current stats + links to all six other docs.

Be honest and specific in `percent_estimate` and gap analysis — never
present a guess as more precise than it is, and don't just restate PRD/README
claims without checking them against the actual code.

### 7. Report back

Summarize in the chat what was created/changed — don't just say "done."
Call out anything surprising (claims vs. reality mismatches, big gaps
between PRD and current state). If the scan output has
`"secrets_redacted": true`, tell the user directly that something
resembling a secret was found and redacted from the scan (e.g. in a README
or code comment) — this is a signal worth their attention even outside of
DocX's own docs, since it may mean a real secret is sitting in tracked code.

## Notes

- Files matching common secret patterns (`.env`, `*.pem`, `id_rsa`, etc.)
  are never read or listed by the scan script, and any secret-shaped text
  found elsewhere is redacted before it reaches you — but this is a
  best-effort safety net, not a guarantee. Don't paste secrets into chat
  yourself, and don't assume the absence of a redaction flag means none
  exist.
- The scan respects a project's `.gitignore` (best-effort — top-level
  patterns, not full gitignore semantics) so generated/vendored folders
  don't pollute the tech-stack and completion analysis.
- This skill is designed to be dropped into any project and used standalone —
  it makes no assumptions about tech stack.
- Re-running is meant to be safe and additive: it should leave the user in a
  better-documented state than before, never silently destroy prior human input.
