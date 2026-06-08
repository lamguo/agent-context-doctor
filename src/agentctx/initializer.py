from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .templates import DEFAULT_AGENTS, init_templates
from .utils import read_text, write_text


def init_context_files(root: Path, include_all: bool = False, force: bool = False, dry_run: bool = False) -> Dict[str, List[str]]:
    created: List[str] = []
    skipped: List[str] = []
    would_create: List[str] = []
    overwritten: List[str] = []

    agents_path = root / "AGENTS.md"
    source_content = DEFAULT_AGENTS if force or not agents_path.exists() else read_text(agents_path)

    for relative_path, content in init_templates(include_all, source_content=source_content).items():
        path = root / relative_path
        display = relative_path.as_posix()
        existed_before = path.exists()
        if dry_run:
            if existed_before and not force:
                skipped.append(display)
            else:
                would_create.append(display)
            continue
        if existed_before and not force:
            skipped.append(display)
            continue
        write_text(path, content)
        if existed_before and force:
            overwritten.append(display)
        else:
            created.append(display)

    return {
        "created": created,
        "skipped": skipped,
        "would_create": would_create,
        "overwritten": overwritten,
    }
