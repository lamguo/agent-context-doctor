from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .templates import generated_block, tool_template
from .utils import read_text, write_text

TARGET_PATHS = {
    "claude": Path("CLAUDE.md"),
    "gemini": Path("GEMINI.md"),
    "copilot": Path(".github/copilot-instructions.md"),
    "cursor": Path(".cursor/rules/agentctx.md"),
}

BEGIN_RE = re.compile(r"<!--\s*agentctx:begin\s*-->")
END_RE = re.compile(r"<!--\s*agentctx:end\s*-->")
GENERATED_BLOCK_RE = re.compile(
    r"(?:<!--\s*agentctx:source[^\n]*-->\n)?"
    r"(?:<!--\s*agentctx:hash\s+[a-fA-F0-9]+\s*-->\n)?"
    r"<!--\s*agentctx:begin\s*-->\n"
    r".*?"
    r"<!--\s*agentctx:end\s*-->",
    re.DOTALL,
)


def sync_context(
    root: Path,
    source: str = "AGENTS.md",
    targets: Optional[Iterable[str]] = None,
    dry_run: bool = False,
    check: bool = False,
) -> Dict[str, List[str]]:
    source_path = root / source
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    source_content = read_text(source_path)
    target_names = list(targets or TARGET_PATHS.keys())
    invalid = [name for name in target_names if name not in TARGET_PATHS]
    if invalid:
        raise ValueError(f"Unknown sync target(s): {', '.join(invalid)}")

    updated: List[str] = []
    created: List[str] = []
    already_synced: List[str] = []
    out_of_sync: List[str] = []
    would_update: List[str] = []

    for target in target_names:
        relative = TARGET_PATHS[target]
        path = root / relative
        expected = _expected_content(target, source, source_content, path)
        display = relative.as_posix()

        if check:
            if path.exists() and _is_synced(read_text(path), source, source_content):
                already_synced.append(display)
            else:
                out_of_sync.append(display)
            continue

        existed = path.exists()
        current = read_text(path) if existed else ""
        if dry_run:
            if existed and _is_synced(current, source, source_content):
                already_synced.append(display)
            else:
                would_update.append(display)
            continue

        if existed and _is_synced(current, source, source_content):
            already_synced.append(display)
            continue
        write_text(path, expected)
        if existed:
            updated.append(display)
        else:
            created.append(display)

    return {
        "created": created,
        "updated": updated,
        "already_synced": already_synced,
        "out_of_sync": out_of_sync,
        "would_update": would_update,
    }


def _expected_content(target: str, source_name: str, source_content: str, path: Path) -> str:
    if not path.exists():
        return tool_template(target, source_name, source_content)
    current = read_text(path)
    replacement = generated_block(source_name, source_content).rstrip()
    if BEGIN_RE.search(current) and END_RE.search(current):
        return _replace_generated_block(current, replacement)
    if current.strip():
        return current.rstrip() + "\n\n" + replacement + "\n"
    return tool_template(target, source_name, source_content)


def _replace_generated_block(current: str, replacement_block: str) -> str:
    match = GENERATED_BLOCK_RE.search(current)
    if not match:
        return current.rstrip() + "\n\n" + replacement_block + "\n"

    before = current[: match.start()].rstrip()
    after = current[match.end() :].lstrip("\n")
    pieces = []
    if before:
        pieces.append(before)
    pieces.append(replacement_block.rstrip())
    if after:
        pieces.append(after.rstrip())
    return "\n\n".join(pieces).rstrip() + "\n"


def _current_generated_block(current: str) -> Optional[str]:
    match = GENERATED_BLOCK_RE.search(current)
    return match.group(0).strip() if match else None


def _is_synced(current: str, source_name: str, source_content: str) -> bool:
    expected = generated_block(source_name, source_content).strip()
    return _current_generated_block(current) == expected
