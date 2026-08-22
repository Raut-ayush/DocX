# AI Coding Rules

These rules apply to any AI assistant helping code in this project. They're
synced into whichever file your tool auto-loads every session (see
`Sync targets` below), so they're already part of the AI's context —
no need to ask it to re-read this file each time.

If you're new to AI-assisted development: these exist to keep the AI's
output predictable, reviewable, and cheap to run — not to slow it down.

## Code style
- Match this repo's existing conventions (naming, formatting, patterns) —
  don't introduce a different style in new code.
- Prefer the smallest correct change. Don't refactor unrelated code as a
  side effect of an unrelated task.
- Don't add abstractions, config options, or "future-proofing" that
  wasn't asked for. Build for what's needed now.

## Efficiency (write less, save credits)
- Be concise. Don't restate the task back at length before doing it.
- Don't re-read entire files when a targeted look (a function, a diff)
  answers the question.
- Don't generate boilerplate comments that just restate what the code
  already says.
- Batch a clearly-scoped set of changes into one pass instead of many
  tiny incremental edits.

## Scope & permission
- Don't add a new dependency without asking first.
- Don't delete or rewrite large working sections of code without being
  asked to.
- If a request is ambiguous or could be done multiple reasonable ways,
  ask a short clarifying question rather than guessing broadly.

## Quality & safety
- Write tests for new non-trivial logic. Don't over-test trivial code
  (simple getters, one-line wrappers, etc.).
- Never hardcode secrets, API keys, or credentials — use environment
  variables or existing config patterns in this repo.
- Validate external input (user input, API responses, file contents) and
  handle errors explicitly — don't silently swallow exceptions.

---

## Your Custom Rules

<!-- Add your own project-specific rules below this line.
     This section is preserved when DocX re-syncs this file. -->

