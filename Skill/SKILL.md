---
name: DocX
description: Generates or updates a standard set of AI-development context docs for THIS project — docs/project.md, docs/PRD.md, docs/architecture.md, docs/state.md, docs/tasks.md — by scanning the codebase, reading any existing docs/README, and asking the user about the project's original idea/intent to evaluate real completion vs. what was planned. Use when the user tags this skill and says things like "start", "document this", "generate docs", "update docs", "status", or "figure out where this project is at". Works on any project regardless of language or stack.
---

# DocX

Creates (or intelligently updates) five standard context docs for this
project, so both humans and AI coding assistants have an accurate, current
picture of what it is, how it's built, and how far along it actually is —
useful for projects that were set aside and picked back up later.

## Output files (always in `docs/` at the project root)

- **`docs/project.md`** — short index: one-paragraph summary, key stats, links to the other four docs.
- **`docs/PRD.md`** — the *why*: original idea, problem/motivation, target users, must-have features, non-goals, any known pivots.
- **`docs/architecture.md`** — the *how*: tech stack, folder/module structure, key components, data flow, notable design decisions.
- **`docs/state.md`** — the *where things stand*: completion stage + estimate, what's actually built vs. what the PRD calls for, known gaps/discrepancies, recent activity.
- **`docs/tasks.md`** — the *what's next*: a checklist of concrete remaining work.

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

### 2. Check for existing docs

If `existing_ai_docs` in the scan output has content (i.e. this isn't the
first run):
- Treat the existing `PRD.md` as the last known statement of intent.
- Briefly tell the user what you found (e.g. "Found an existing PRD saying
  this is a recipe-sharing app for home cooks — still accurate?") rather
  than silently discarding it.
- Plan to **update, not blindly overwrite** — see step 5.

If there are no existing docs, this is a first run — proceed to ask about
the original idea before writing anything.

### 3. Ask the user about the original idea

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

### 4. Read further if needed

Use the README content, doc files, and TODO examples from the scan first.
If that's not enough to describe the architecture or evaluate completion
confidently, read a handful of key source files yourself (entry points,
routing/config files, main modules) — don't read the whole codebase, just
enough to be accurate.

### 5. Write or update the five docs

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
- **`tasks.md`** — regenerate as a checklist (`- [ ] ...`), pulling from
  TODO/FIXME markers, PRD requirements not yet met, and anything the user
  flagged. If the previous `tasks.md` had items checked off as done, only
  keep them checked if the code still reflects that (don't silently
  un-check completed work, but do add newly-discovered gaps).
- **`project.md`** — always regenerate last, once the other four are final:
  one paragraph summary + current stats + links.

Be honest and specific in `percent_estimate` and gap analysis — never
present a guess as more precise than it is, and don't just restate PRD/README
claims without checking them against the actual code.

### 6. Report back

Summarize in the chat what was created/changed — don't just say "done."
Call out anything surprising (claims vs. reality mismatches, big gaps
between PRD and current state).

## Notes

- This skill is designed to be dropped into any project and used standalone —
  it makes no assumptions about tech stack.
- Re-running is meant to be safe and additive: it should leave the user in a
  better-documented state than before, never silently destroy prior human input.
