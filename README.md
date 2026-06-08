# Agent Context Doctor

Audit, generate, sync, and package repository context files for AI coding agents.

`agentctx` helps you keep project instructions accurate across tools such as Codex, Claude Code, Gemini CLI, Cursor, and GitHub Copilot. It works locally, uses no LLM API, and has zero runtime dependencies.

## Why?

AI coding agents work better when your repository has clear, current, and tool-readable instructions. Many projects now carry several context files:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`
- `.cursor/rules/`
- `HANDOFF.md`

Keeping those files synchronized by hand is easy to forget. Agent Context Doctor scans your repository, reports missing or stale context, generates starter files, safely syncs generated sections, and creates handoff/context packs for the next AI coding session.

## Features

- **Scan repository context** with a readable score and machine-readable JSON.
- **Generate starter files** for AGENTS.md, Claude, Gemini, Copilot, Cursor, and handoff notes.
- **Safely sync generated sections** without deleting user-written content outside markers, including Cursor rules.
- **Create handoff summaries** from local Git state.
- **Package AI-ready context** into `PROJECT_CONTEXT.md`.
- **Run safe repairs** with `agentctx doctor --fix`.
- **Zero runtime dependencies**; Python standard library only.

## Installation

From PyPI, once published:

```bash
pip install agent-context-doctor
```

From source:

```bash
git clone https://github.com/lamguo/agent-context-doctor.git
cd agent-context-doctor
python -m pip install -e .
```

## Quick start

```bash
# Audit the current repository
agentctx scan

# JSON output for scripts or CI
agentctx scan --json
agentctx scan --fail-under 80

# Generate AGENTS.md and HANDOFF.md if missing
agentctx init

# Generate all supported context files
agentctx init --all

# Sync AGENTS.md into Claude, Gemini, Copilot, and Cursor instruction files
agentctx sync --from AGENTS.md

# Check whether generated files are in sync
agentctx sync --check

# Generate a handoff file from local Git state
agentctx handoff

# Generate PROJECT_CONTEXT.md for a new AI coding session
agentctx pack

# Plan safe context repairs
agentctx doctor

# Apply safe context repairs
agentctx doctor --fix
```

## Example scan output

```text
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
  ⚠️ Missing HANDOFF.md. Long AI coding sessions are easier to resume with a handoff file.
  ⚠️ Missing GEMINI.md.

Suggestions:
  - Run: agentctx init --all
  - Run: agentctx handoff
```

## Commands

### `agentctx scan`

Checks common AI context files, project files, referenced local paths, common test commands, and sync markers.

```bash
agentctx scan
agentctx scan --json
agentctx scan --fail-under 80
agentctx scan --root /path/to/repo
```

### `agentctx init`

Creates starter templates. Existing files are skipped by default.

```bash
agentctx init
agentctx init --all
agentctx init --dry-run
agentctx init --force
```

### `agentctx sync`

Copies `AGENTS.md` into generated sections in tool-specific files. It only replaces content between `agentctx` markers.

```bash
agentctx sync --from AGENTS.md
agentctx sync --to claude --to gemini
agentctx sync --to cursor
agentctx sync --dry-run
agentctx sync --check
```

### `agentctx handoff`

Creates a handoff file using local Git metadata.

```bash
agentctx handoff
agentctx handoff --json
agentctx handoff --output HANDOFF.md
```

### `agentctx pack`

Creates an AI-ready context package.

```bash
agentctx pack
agentctx pack --output PROJECT_CONTEXT.md
```

### `agentctx doctor`

Plans or applies safe automatic repairs. Safe repairs can create missing starter files, generate `HANDOFF.md`, and create or refresh generated tool files from `AGENTS.md`. It does not delete files or overwrite user-authored content outside `agentctx` markers.

```bash
agentctx doctor
agentctx doctor --fix
agentctx doctor --json
```

## Generated file safety

`agentctx sync` uses markers like this:

```md
<!-- agentctx:source AGENTS.md -->
<!-- agentctx:hash abc123 -->
<!-- agentctx:begin -->
Generated content here.
<!-- agentctx:end -->
```

On later syncs, only the generated block is replaced. Content before or after the markers is preserved.

## CI usage

```yaml
- name: Check agent context
  run: agentctx scan --json

- name: Ensure generated agent files are synced
  run: agentctx sync --check
```

## Development

```bash
python -m pip install -e .[dev]
pytest
agentctx scan
```

## Roadmap

- More stale-path detection rules.
- Markdown table output option.
- Context score badge helper.
- Optional GitHub Action wrapper.
- Optional `--stdout` mode for `agentctx pack`.

## License

MIT
