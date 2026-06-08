# Contributing

Thanks for considering a contribution to Agent Context Doctor.

## Development setup

```bash
python -m pip install -e .[dev]
pytest
agentctx scan
agentctx verify --min-score 90
```

## Contribution guidelines

- Keep runtime dependencies at zero unless there is a strong reason to add one.
- Keep CLI output stable and readable.
- Keep JSON output script-friendly.
- Add or update tests for behavior changes.
- Do not make `doctor --fix` destructive. It must not delete files or overwrite user-authored content outside `agentctx` markers.
- Avoid network calls in runtime code.

## Before opening a pull request

Run:

```bash
pytest
agentctx verify --min-score 90
agentctx sync --check
agentctx pack --stdout > /tmp/PROJECT_CONTEXT.md
```

## Good first issues

- Add a new command detection pattern.
- Improve a false-positive path detection case.
- Improve docs for a specific AI coding tool.
- Add tests for a new repository fixture.
