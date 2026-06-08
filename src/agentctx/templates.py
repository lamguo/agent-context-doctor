from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from .utils import sha256_text


DEFAULT_AGENTS = """# AGENTS.md

## Project Overview

Describe what this repository does and who it is for.

## Setup Commands

```bash
# Install dependencies here
```

## Development Commands

```bash
# Run tests here
# Run linting here
# Run build here
```

## Project Structure

Describe the real source, test, and documentation paths for this repository.

## Coding Guidelines

- Keep changes small and focused.
- Update tests when behavior changes.
- Do not introduce unnecessary dependencies.
- Prefer clear names and simple control flow.

## Testing Instructions

Run the test suite before completing changes.

## Security Notes

- Do not commit secrets, API keys, credentials, or private generated files.
- Avoid uploading repository contents to external services unless explicitly approved.

## Handoff Notes

Before ending a long session, update `HANDOFF.md`.
"""

DEFAULT_HANDOFF = """# HANDOFF.md

## Current Goal

What are we trying to complete?

## Completed

- 

## In Progress

- 

## Known Issues

- 

## Important Decisions

- 

## Files Changed Recently

- 

## Next Recommended Step

- 

## Do Not Repeat

- 
"""

CURSOR_RULE = """# Cursor Rules

Use the repository instructions in `AGENTS.md` as the source of truth.

## General Rules

- Keep changes small and focused.
- Follow the existing project style.
- Run the documented tests before completing changes.
- Do not commit secrets or generated private files.
"""


def generated_block(source_name: str, source_content: str) -> str:
    digest = sha256_text(source_content)
    return (
        f"<!-- agentctx:source {source_name} -->\n"
        f"<!-- agentctx:hash {digest} -->\n"
        "<!-- agentctx:begin -->\n"
        f"{source_content.rstrip()}\n"
        "<!-- agentctx:end -->\n"
    )


def tool_template(tool: str, source_name: str, source_content: str) -> str:
    titles = {
        "claude": "# CLAUDE.md",
        "gemini": "# GEMINI.md",
        "copilot": "# GitHub Copilot Instructions",
        "cursor": "# Cursor Rules",
    }
    notes = {
        "claude": "This file contains project context for Claude Code.",
        "gemini": "This file contains project context for Gemini CLI.",
        "copilot": "This file contains repository-wide custom instructions for GitHub Copilot.",
        "cursor": "This file contains Cursor project rules generated from the shared agent context.",
    }
    title = titles[tool]
    note = notes[tool]
    return f"{title}\n\n{note}\n\nGenerated sections are managed by agent-context-doctor.\n\n{generated_block(source_name, source_content)}"


def init_templates(include_all: bool = False, source_content: Optional[str] = None) -> Dict[Path, str]:
    agents_content = source_content or DEFAULT_AGENTS
    templates: Dict[Path, str] = {
        Path("AGENTS.md"): agents_content,
        Path("HANDOFF.md"): DEFAULT_HANDOFF,
    }
    if include_all:
        templates.update(
            {
                Path("CLAUDE.md"): tool_template("claude", "AGENTS.md", agents_content),
                Path("GEMINI.md"): tool_template("gemini", "AGENTS.md", agents_content),
                Path(".github/copilot-instructions.md"): tool_template("copilot", "AGENTS.md", agents_content),
                Path(".cursor/rules/agentctx.md"): tool_template("cursor", "AGENTS.md", agents_content),
            }
        )
    return templates
