<div align="center">

# 📄 DocX

### Your project, documented — and your AI, disciplined.

*Drop it in. Ask it to start. Get seven docs that actually reflect reality —*
*and coding rules your AI assistant actually follows, every session.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Cursor%20%7C%20Copilot-6f42c1)](#-compatibility)
[![Stack](https://img.shields.io/badge/stack-any%20language-informational)](#-how-it-works)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)

</div>

---

## 😵‍💫 The problem

You've got a folder of projects. Some are ideas that never left the runway.
Some are half-built and paused mid-thought. One or two might actually be
done — you're not sure anymore. You open one in your AI-powered IDE, ask it
to "add the export feature," and it confidently invents an architecture
that doesn't match what's actually there.

**DocX fixes the context problem at the source.**

## ✨ What it does

Tag it once, and DocX scans the codebase, reads whatever docs already
exist, asks you a few sharp questions about the *original idea* — the part
no scanner can recover from code alone — and writes seven structured docs
that stay accurate as the project evolves:

| File | Answers |
|---|---|
| 📋 `docs/project.md` | *"What is this, in one paragraph?"* |
| 🎯 `docs/PRD.md` | *"What were we actually trying to build?"* |
| 🏗️ `docs/architecture.md` | *"How is it actually built, right now?"* |
| 📊 `docs/state.md` | *"How far along is it, really — and where's the gap?"* |
| ✅ `docs/tasks.md` | *"What's left?"* |
| 🧭 `docs/decisions.md` | *"Why did we choose this over the alternative?"* |
| 📝 `docs/changes.md` | *"What actually changed since last time?"* |

Plus one more file that isn't about documentation at all:

| File | Answers |
|---|---|
| ⚖️ `DocX/rules.md` | *"How should the AI behave while coding here?"* |

`rules.md` gets synced straight into whatever your AI IDE auto-loads every
session — so it's not a doc you hope the AI reads, it's baked into its
context from turn one. Balanced defaults out of the box (match existing
style, don't over-engineer, ask before big changes, no silent new
dependencies), plus a clearly marked spot for your own house rules.

## 🚀 Quick start

<table>
<tr><th>Claude Code</th><th>Cursor / Copilot / any agentic IDE chat</th></tr>
<tr valign="top">
<td>

```bash
git clone <this-repo-url> DocX
python3 DocX/install.py
```

Then, in chat:

```
@DocX start
```

</td>
<td>

```bash
git clone <this-repo-url> DocX
python3 DocX/scripts/sync_rules.py .
```

Then, in chat:

```
Read DocX/Instruction/INSTRUCTIONS.md
and follow it to document this project.
```

</td>
</tr>
</table>

First run asks a few quick questions about the project's original intent.
Don't remember? Say so — DocX infers what it can from the code and README,
and clearly labels that part as inferred, not confirmed.

Every run after that **updates rather than starts over**: your PRD's
intent is preserved unless you say it's changed, `decisions.md` and
`changes.md` grow as an append-only log, and `tasks.md` reflects what's
actually still left.

Full walkthrough → [`USE.md`](./USE.md)

## 🧠 How it works

```
                    ┌─────────────────────┐
                    │   scan_project.py   │   deterministic recon:
                    │   (the facts)       │   manifests, git log,
                    └──────────┬───────────┘   TODOs, existing docs
                               │
                               ▼
                    ┌─────────────────────┐
                    │  the AI assistant   │   reasoning + writing:
                    │   (the judgment)     │   what's really done,
                    └──────────┬───────────┘   what's a real gap
                               │
                               ▼
              seven docs, always in sync with what's real
```

The script never guesses at meaning — it just gathers facts fast and
cheaply. The AI never has to manually `ls` and `cat` its way around your
repo — it reasons over structured data instead. That split is why this
works on any stack: the recon script speaks JSON, not framework opinions.

## 📦 Structure

```
DocX/
│   README.md            you are here
│   USE.md                quick-start walkthrough
│   LICENSE               MIT
│   install.py            one-time Claude Code setup (@DocX tagging + rules sync)
│   rules.md              canonical AI coding rules — edit this to customize
│
├───Instruction/
│       INSTRUCTIONS.md   plain-text workflow for Cursor / Copilot / other agents
│
├───scripts/
│       scan_project.py   shared recon script
│       sync_rules.py     propagates rules.md into each tool's auto-loaded context
│
└───Skill/
        SKILL.md          Claude Code skill definition
```

## 🔌 Compatibility

| Tool | How it's triggered | Rules auto-load into |
|---|---|---|
| **Claude Code** | `@DocX start` | `CLAUDE.md` |
| **GitHub Copilot Chat** | tell it to read `INSTRUCTIONS.md` | `.github/copilot-instructions.md` |
| **Cursor** | tell it to read `INSTRUCTIONS.md` | `.cursor/rules/docx-rules.mdc` |
| **Anything else with terminal + chat** | tell it to read `INSTRUCTIONS.md` | manual, via `rules.md` |

Works on any language or stack — `scan_project.py` detects common manifest
files (`package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`,
`go.mod`, `pom.xml`, and more) and degrades gracefully when none are found.

## 🙋 Who this is for

Built with early-in-their-journey AI-assisted developers in mind — people
who are still figuring out what guardrails to even ask an AI for. DocX
ships opinionated, balanced defaults so you don't have to know that up
front, and stays out of the way once you do.

Just as useful, though, if you simply have too many side projects and not
enough memory of what state they're in.

## 🤝 Contributing

Issues and PRs welcome — especially around new manifest-file detection,
additional sync targets for other IDEs, or sharper default rules.

## 📄 License

[MIT](./LICENSE) — copy it, fork it, change it, ship it.

