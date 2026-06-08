from __future__ import annotations

from pathlib import Path
from typing import List

from .models import HandoffData
from .scanner import detect_commands
from .utils import git_branch, git_recent_commits, git_status_files, write_text


def collect_handoff_data(root: Path) -> HandoffData:
    modified, untracked = git_status_files(root)
    commands = detect_commands(root)
    next_steps = _next_steps(root, modified, untracked, commands)
    return HandoffData(
        repository=root.name or str(root),
        branch=git_branch(root),
        recent_commits=git_recent_commits(root),
        modified_files=modified,
        untracked_files=untracked,
        detected_commands=commands,
        next_steps=next_steps,
    )


def _next_steps(root: Path, modified: List[str], untracked: List[str], commands: dict) -> List[str]:
    steps: List[str] = []
    if modified or untracked:
        steps.append("Review the modified and untracked files before handing work to another agent.")
    if commands.get("test"):
        steps.append(f"Run the documented test command: {commands['test'][0]}")
    else:
        steps.append("Document a test command in AGENTS.md.")
    if not (root / "AGENTS.md").exists():
        steps.append("Create AGENTS.md with `agentctx init`.")
    if not (root / "HANDOFF.md").exists():
        steps.append("Create HANDOFF.md with `agentctx handoff`.")
    steps.append("Run `agentctx scan` and fix high-severity context issues first.")
    return steps


def render_handoff(data: HandoffData) -> str:
    lines: List[str] = []
    lines.append("# HANDOFF.md")
    lines.append("")
    lines.append("## Current Repository State")
    lines.append("")
    lines.append(f"- Repository: `{data.repository}`")
    lines.append(f"- Branch: `{data.branch}`")
    lines.append("")
    lines.append("## Recent Commits")
    lines.append("")
    if data.recent_commits:
        for commit in data.recent_commits:
            lines.append(f"- {commit}")
    else:
        lines.append("- No recent commits detected, or this is not a Git repository.")
    lines.append("")
    lines.append("## Modified Files")
    lines.append("")
    if data.modified_files:
        for file in data.modified_files:
            lines.append(f"- `{file}`")
    else:
        lines.append("- None detected.")
    lines.append("")
    lines.append("## Untracked Files")
    lines.append("")
    if data.untracked_files:
        for file in data.untracked_files:
            lines.append(f"- `{file}`")
    else:
        lines.append("- None detected.")
    lines.append("")
    lines.append("## Detected Project Commands")
    lines.append("")
    for kind in ["install", "test", "build"]:
        values = data.detected_commands.get(kind, [])
        lines.append(f"- {kind.title()}: {', '.join(values) if values else 'not detected'}")
    lines.append("")
    lines.append("## Next Recommended Steps")
    lines.append("")
    for step in data.next_steps:
        lines.append(f"- {step}")
    lines.append("")
    lines.append("## Notes For The Next Agent")
    lines.append("")
    lines.append("- Read `AGENTS.md` first if it exists.")
    lines.append("- Avoid repeating completed work unless the handoff says it needs verification.")
    lines.append("- Keep changes small and verify with the documented test command.")
    lines.append("")
    return "\n".join(lines)


def write_handoff(root: Path, output: str = "HANDOFF.md") -> HandoffData:
    data = collect_handoff_data(root)
    write_text(root / output, render_handoff(data))
    return data
