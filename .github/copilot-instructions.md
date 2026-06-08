# GitHub Copilot Instructions

This file contains repository-wide custom instructions for GitHub Copilot.

Generated sections are managed by agent-context-doctor.

<!-- agentctx:source AGENTS.md -->
<!-- agentctx:hash dd115a2f0876 -->
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
agentctx scan --json
agentctx scan --fail-under 80
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
- Keep `agentctx doctor --fix` safe: no deletion and no overwriting user-authored content outside markers.
- Avoid network calls in runtime code.

## Testing Instructions

Run the full test suite before completing changes:

```bash
pytest
```

Also run a CLI smoke test:

```bash
agentctx scan --json
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
