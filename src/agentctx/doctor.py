from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .handoff import write_handoff
from .scanner import scan_repository
from .syncer import TARGET_PATHS, sync_context
from .templates import DEFAULT_AGENTS
from .utils import write_text


def doctor_repository(root: Path, fix: bool = False) -> Dict[str, object]:
    """Plan or apply safe context repairs.

    Safe repairs are intentionally limited:
    - create missing AGENTS.md from the starter template
    - create missing HANDOFF.md from local repository state
    - create or refresh generated tool files from AGENTS.md

    It does not delete files, overwrite user-authored content outside agentctx
    markers, or try to edit arbitrary Markdown paths.
    """
    before = scan_repository(root)
    planned = _planned_actions(root, before)
    applied: List[str] = []

    if fix:
        if not before.files.get("AGENTS.md", False):
            write_text(root / "AGENTS.md", DEFAULT_AGENTS)
            applied.append("created AGENTS.md")

        if not before.files.get("HANDOFF.md", False):
            write_handoff(root)
            applied.append("created HANDOFF.md")

        if (root / "AGENTS.md").exists():
            sync_result = sync_context(root)
            applied.extend(f"created {path}" for path in sync_result["created"])
            applied.extend(f"updated {path}" for path in sync_result["updated"])

    after = scan_repository(root) if fix else before
    return {
        "fixed": fix,
        "score_before": before.score,
        "score_after": after.score,
        "planned_actions": planned,
        "applied_actions": applied,
        "remaining_problems": [problem.to_dict() for problem in after.problems],
    }


def _planned_actions(root: Path, scan) -> List[str]:
    actions: List[str] = []
    if not scan.files.get("AGENTS.md", False):
        actions.append("create AGENTS.md")
    if not scan.files.get("HANDOFF.md", False):
        actions.append("create HANDOFF.md")

    for display in TARGET_PATHS.values():
        if not (root / display).exists():
            actions.append(f"create {display.as_posix()}")

    for problem in scan.problems:
        if problem.code == "out_of_sync" and problem.file:
            actions.append(f"refresh {problem.file}")
    return sorted(dict.fromkeys(actions))
