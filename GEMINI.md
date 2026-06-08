# GEMINI.md

This file contains project context for Gemini CLI.

Generated sections are managed by agent-context-doctor.

<!-- agentctx:source AGENTS.md -->
<!-- agentctx:hash 0b090331881e -->
<!-- agentctx:begin -->
# AGENTS.md

## Project Overview

Agent Context Doctor is a Python CLI that audits, generates, syncs, repairs, and packages repository context files for AI coding agents.

## Setup Commands

```bash
python -m pip install -e .[dev]
```

## Development Commands

```bash
pytest
agentctx scan
agentctx verify --min-score 90
agentctx sync --check
agentctx pack --stdout
agentctx badge
agentctx doctor
```

## Project Structure

- `src/agentctx/` - source code for the CLI package.
- `tests/` - pytest test suite.
- `docs/` - additional documentation.
- `.github/workflows/ci.yml` - GitHub Actions workflow.

## Coding Guidelines

- Keep the package zero-runtime-dependency unless there is a strong reason to add one.
- Prefer small, focused functions over large command handlers.
- Keep CLI output stable and readable.
- Keep JSON output stable and script-friendly.
- Keep `scan` human-oriented and `verify` CI-oriented.
- Keep `agentctx doctor --fix` safe: no deletion and no overwriting user-authored content outside markers.
- Avoid network calls in runtime code.

## Testing Instructions

Run the full test suite before completing changes:

```bash
pytest
```

Also run a CLI smoke test:

```bash
agentctx verify --min-score 90
agentctx sync --check
```

## Security Notes

- Do not collect or upload repository contents.
- Do not commit secrets, API keys, credentials, or private generated files.
- Treat all scanned file contents as local-only data.

## Handoff Notes

Before ending a long session, update `HANDOFF.md` or run:

```bash
agentctx handoff
```
<!-- agentctx:end -->
