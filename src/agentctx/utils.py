from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".tox",
}

EXCLUDED_FILES = {
    "PROJECT_CONTEXT.md",
}


def resolve_root(path: Optional[str] = None) -> Path:
    return Path(path or os.getcwd()).resolve()


def read_text(path: Path, limit: Optional[int] = None) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    if limit is not None and len(text) > limit:
        return text[:limit]
    return text


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def run_git(root: Path, args: Sequence[str]) -> Tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return 127, ""
    return completed.returncode, completed.stdout.strip()


def git_branch(root: Path) -> str:
    code, out = run_git(root, ["branch", "--show-current"])
    if code == 0 and out:
        return out
    code, out = run_git(root, ["rev-parse", "--short", "HEAD"])
    if code == 0 and out:
        return f"detached@{out}"
    return "not a Git repository"


def git_recent_commits(root: Path, limit: int = 5) -> List[str]:
    code, out = run_git(root, ["log", f"-{limit}", "--pretty=format:%h %s"])
    if code != 0 or not out:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def git_status_files(root: Path) -> Tuple[List[str], List[str]]:
    code, out = run_git(root, ["status", "--porcelain"])
    if code != 0 or not out:
        return [], []
    modified: List[str] = []
    untracked: List[str] = []
    for line in out.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        if status == "??":
            untracked.append(path)
        else:
            modified.append(path)
    return modified, untracked


def safe_tree(root: Path, max_files: int = 180, max_depth: int = 4) -> List[str]:
    lines: List[str] = []
    count = 0

    def walk(directory: Path, prefix: str = "", depth: int = 0) -> None:
        nonlocal count
        if count >= max_files or depth > max_depth:
            return
        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            return
        entries = [
            entry
            for entry in entries
            if entry.name not in EXCLUDED_DIRS
            and entry.name not in EXCLUDED_FILES
            and not entry.name.endswith(".egg-info")
        ]
        for index, entry in enumerate(entries):
            if count >= max_files:
                return
            connector = "└── " if index == len(entries) - 1 else "├── "
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{prefix}{connector}{entry.name}{suffix}")
            count += 1
            if entry.is_dir() and not entry.is_symlink():
                extension = "    " if index == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, depth + 1)

    walk(root)
    if count >= max_files:
        lines.append("... truncated ...")
    return lines


def iter_existing(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.exists():
            yield path
