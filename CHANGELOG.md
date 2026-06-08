# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-08

### Added

- Added Cursor as a first-class sync target with `agentctx sync --to cursor`.
- Added `agentctx scan --fail-under SCORE` for CI quality gates.
- Added `agentctx doctor` and `agentctx doctor --fix` for safe automatic context repairs.

### Fixed

- `agentctx init --all` now uses an existing `AGENTS.md` as the source for generated tool files instead of the default template.
- `agentctx pack` no longer includes an existing `PROJECT_CONTEXT.md` in the generated project tree.

## [0.1.1] - 2026-06-08

### Fixed

- Made sync checks compare the generated block content, not only the stored hash.
- Ignored fenced Markdown code blocks while extracting local path references.
- Avoided duplicate command detection for `python -m pytest` and `python -m pip install`.
- Removed unused imports from source modules.
- Updated the default AGENTS.md template to avoid self-referencing placeholder paths.

## [0.1.0] - 2026-06-08

### Added

- `agentctx scan` with human-readable and JSON output.
- `agentctx init` for generating AGENTS.md and HANDOFF.md templates.
- `agentctx init --all` for Claude, Gemini, Copilot, and Cursor context files.
- `agentctx sync` with marker-based safe updates and CI-friendly `--check` mode.
- `agentctx handoff` for local Git state summaries.
- `agentctx pack` for PROJECT_CONTEXT.md generation.
- Zero runtime dependencies.
- Pytest coverage for core workflows.
