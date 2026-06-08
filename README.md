<div align="center">

# 🩺 Agent Context Doctor

**One CLI to rule all your AI agent context files.**

Audit · Generate · Sync · Repair · Pack

[![PyPI Version](https://img.shields.io/pypi/v/agent-context-doctor?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/agent-context-doctor/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agent-context-doctor?logo=python&logoColor=white)](https://pypi.org/project/agent-context-doctor/)
[![License](https://img.shields.io/pypi/l/agent-context-doctor?color=green)](https://github.com/lamguo/agent-context-doctor/blob/master/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/lamguo/agent-context-doctor?style=social)](https://github.com/lamguo/agent-context-doctor)
[![Tests](https://img.shields.io/badge/tests-37%20passed-brightgreen)](https://github.com/lamguo/agent-context-doctor)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](https://pypi.org/project/agent-context-doctor/)

**Zero dependencies · Works offline · No API key needed**

</div>

---

## 📖 What is this?

Your repo has `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `HANDOFF.md`...

Keeping them in sync by hand is tedious and error-prone. **Agent Context Doctor** audits, generates, syncs, repairs, and packages all your AI coding agent context files — with one command, no dependencies, and zero network calls.

```text
$ agentctx scan
Agent Context Doctor

Repository: my-project
Score: 82/100 (Good)

Found:
  ✅ README.md
  ✅ AGENTS.md
  ✅ tests/

Missing:
  ⚠️ HANDOFF.md
  ⚠️ GEMINI.md

Problems:
  ⚠️ Missing HANDOFF.md. Long AI coding sessions are easier to resume.
  ⚠️ Missing GEMINI.md.

Suggestions:
  - Run: agentctx init --all
  - Run: agentctx handoff
```

```text
$ agentctx doctor --fix
Score: 52/100 -> 100/100
Applied:
  - created AGENTS.md
  - created HANDOFF.md
  - created CLAUDE.md
  - created GEMINI.md
  - created .github/copilot-instructions.md
  - created .cursor/rules/agentctx.md
```

---

## ✨ Why Agent Context Doctor?

### 🎯 The problem

AI coding agents (Claude Code, Gemini CLI, GitHub Copilot, Cursor, Codex) each expect their own context file format. A modern project can easily accumulate **6+ agent context files**. When you update your instructions in `AGENTS.md`, you have to manually replicate that change everywhere — or risk agents working with stale instructions.

### 💡 The solution

`agentctx` treats `AGENTS.md` as your **single source of truth** and safely propagates changes to all other tool-specific files via guarded markers (`<!-- agentctx:begin -->` ... `<!-- agentctx:end -->`). Your custom content outside the markers is preserved.

---

## 🚀 Quick start

```bash
# Install (no dependencies)
pip install agent-context-doctor

# Audit your project's AI context health
agentctx scan

# Generate missing context files (AGENTS.md, HANDOFF.md)
agentctx init

# Generate ALL tool-specific files
agentctx init --all

# Sync AGENTS.md → CLAUDE.md, GEMINI.md, Copilot, Cursor
agentctx sync --from AGENTS.md

# Generate a handoff summary for the next AI coding session
agentctx handoff

# Package everything into PROJECT_CONTEXT.md for a new agent
agentctx pack

# Auto-fix everything at once (safe — never deletes user content)
agentctx doctor --fix
```

---

## 🧰 Features at a glance

| Feature | Command | What it does |
|---|---|---|
| 🔍 **Scan** | `agentctx scan` | Scores your repo's AI context health (0–100) |
| 📋 **Init** | `agentctx init --all` | Creates starter AGENTS.md, CLAUDE.md, GEMINI.md, Copilot, Cursor, HANDOFF |
| 🔄 **Sync** | `agentctx sync` | Propagates AGENTS.md changes safely across all tool files |
| 🩺 **Doctor** | `agentctx doctor --fix` | Auto-repairs missing/outdated context in one shot |
| 📝 **Handoff** | `agentctx handoff` | Generates session handoff from local Git state |
| 📦 **Pack** | `agentctx pack` | Bundles everything into `PROJECT_CONTEXT.md` |
| ✅ **CI gate** | `agentctx scan --fail-under 80` | Fail CI builds with poor context scores |
| 🔎 **JSON mode** | `agentctx scan --json` | Machine-readable output for scripting |

### Safe by design

- `agentctx sync` only replaces content inside `<!-- agentctx:begin -->` `<!-- agentctx:end -->` markers
- Content before or after markers is **never touched**
- `agentctx doctor --fix` never deletes files — only creates missing ones
- Works **fully offline** — scans filesystem, runs `git`, no network
- **Zero runtime dependencies** — Python standard library only

---

## 📊 How it compares

| Feature | agentctx | source-agents | ai-rules-sync | ctxlint |
|---|---|---|---|---|
| Scan / health score | ✅ | ❌ | ❌ | ✅ |
| Generate starter files | ✅ | ❌ | ✅ | ❌ |
| Sync with marker safety | ✅ | ✅ | ✅ | ❌ |
| Session handoff | ✅ | ❌ | ❌ | ❌ |
| Context pack (PROJECT_CONTEXT.md) | ✅ | ❌ | ❌ | ❌ |
| Doctor auto-fix | ✅ | ❌ | ❌ | ❌ |
| CI quality gate (`--fail-under`) | ✅ | ❌ | ❌ | ✅ |
| Cursor rules support | ✅ | ❌ | ❌ | ❌ |
| Zero dependencies | ✅ | ❌ | ✅ | ❌ |
| Python (pip install) | ✅ | ❌ | ❌ | ❌ |

---

## 🛠️ CI / GitHub Actions

```yaml
- name: Check agent context quality
  run: |
    pip install agent-context-doctor
    agentctx scan --fail-under 80

- name: Ensure generated files are in sync
  run: agentctx sync --check
```

---

## 🌱 Roadmap

- [ ] Context score badge generator
- [ ] GitHub Action wrapper
- [ ] Markdown table output
- [ ] `agentctx pack --stdout`
- [ ] More stale-path detection rules

---

## 💖 Support

If Agent Context Doctor saves you time, consider supporting the project:

<p align="center">
  <a href="https://github.com/sponsors/lamguo">
    <img src="https://img.shields.io/badge/GitHub_Sponsors-EA4AAA?logo=githubsponsors&logoColor=white&style=for-the-badge" alt="GitHub Sponsors">
  </a>
  <a href="https://www.buymeacoffee.com/lamguo">
    <img src="https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?logo=buymeacoffee&logoColor=black&style=for-the-badge" alt="Buy Me a Coffee">
  </a>
</p>

<p align="center">
  <sub>微信 / Alipay 打赏码请联系作者获取</sub>
</p>

---

## 📄 License

MIT &mdash; see [LICENSE](LICENSE).

*Built with ❤️ for the AI coding agent ecosystem.*
