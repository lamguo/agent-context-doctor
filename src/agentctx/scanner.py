from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .markers import find_agentctx_marker_conflicts, current_generated_block
from .models import Problem, ScanResult
from .templates import generated_block
from .utils import read_text, resolve_root

CONTEXT_FILES = {
    "README.md": Path("README.md"),
    "AGENTS.md": Path("AGENTS.md"),
    "CLAUDE.md": Path("CLAUDE.md"),
    "GEMINI.md": Path("GEMINI.md"),
    "HANDOFF.md": Path("HANDOFF.md"),
    ".github/copilot-instructions.md": Path(".github/copilot-instructions.md"),
    ".cursor/rules/": Path(".cursor/rules"),
}

PROJECT_FILES = {
    "pyproject.toml": Path("pyproject.toml"),
    "package.json": Path("package.json"),
    "Makefile": Path("Makefile"),
    "tests/": Path("tests"),
    "docs/": Path("docs"),
}

MARKDOWN_CONTEXT_PATHS = [
    Path("README.md"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("GEMINI.md"),
    Path("HANDOFF.md"),
    Path(".github/copilot-instructions.md"),
    Path(".cursor/rules/agentctx.md"),
]

TEST_COMMAND_PATTERNS = [
    ("python -m pytest", re.compile(r"\bpython\s+-m\s+pytest\b")),
    ("pytest", re.compile(r"\bpytest\b")),
    ("make test", re.compile(r"\bmake\s+test\b")),
    ("npm test", re.compile(r"\bnpm\s+test\b")),
    ("pnpm test", re.compile(r"\bpnpm\s+test\b")),
    ("yarn test", re.compile(r"\byarn\s+test\b")),
    ("go test", re.compile(r"\bgo\s+test\b")),
    ("cargo test", re.compile(r"\bcargo\s+test\b")),
]

BUILD_COMMAND_PATTERNS = [
    ("python -m build", re.compile(r"\bpython\s+-m\s+build\b")),
    ("make build", re.compile(r"\bmake\s+build\b")),
    ("npm run build", re.compile(r"\bnpm\s+run\s+build\b")),
    ("pnpm build", re.compile(r"\bpnpm\s+build\b")),
    ("yarn build", re.compile(r"\byarn\s+build\b")),
    ("cargo build", re.compile(r"\bcargo\s+build\b")),
    ("go build", re.compile(r"\bgo\s+build\b")),
]

INSTALL_COMMAND_PATTERNS = [
    ("python -m pip install", re.compile(r"\bpython\s+-m\s+pip\s+install\b")),
    ("pip install", re.compile(r"\bpip\s+install\b")),
    ("npm install", re.compile(r"\bnpm\s+install\b")),
    ("pnpm install", re.compile(r"\bpnpm\s+install\b")),
    ("yarn install", re.compile(r"\byarn\s+install\b")),
    ("poetry install", re.compile(r"\bpoetry\s+install\b")),
]

PATHLIKE_EXTENSIONS = (
    ".py",
    ".md",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".ini",
    ".cfg",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
)

KNOWN_FILENAMES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "HANDOFF.md",
    "CHANGELOG.md",
    "LICENSE",
    "pyproject.toml",
    "package.json",
    "Makefile",
}

GENERATED_OR_OUTPUT_REFS = {
    "PROJECT_CONTEXT.md",
}


def scan_repository(root: Optional[Path] = None) -> ScanResult:
    root = root or resolve_root()
    files = _detect_files(root)
    problems: List[Problem] = []
    suggestions: List[str] = []

    _add_missing_context_problems(files, problems, suggestions)
    commands = detect_commands(root)
    _add_command_problems(root, commands, problems, suggestions)
    _add_path_reference_problems(root, problems)
    _add_sync_problems(root, problems, suggestions)
    _add_marker_conflict_problems(root, problems)

    score = _score(files, problems, commands)
    rating = score_rating(score)
    repository = root.name or str(root)
    if not suggestions and score < 100:
        suggestions.append("Run: agentctx scan --json")

    return ScanResult(
        root=str(root),
        repository=repository,
        score=score,
        rating=rating,
        files=files,
        commands=commands,
        problems=problems,
        suggestions=sorted(dict.fromkeys(suggestions)),
    )


def _detect_files(root: Path) -> Dict[str, bool]:
    files: Dict[str, bool] = {}
    for name, relative_path in {**CONTEXT_FILES, **PROJECT_FILES}.items():
        path = root / relative_path
        if name.endswith("/"):
            files[name] = path.is_dir()
        else:
            files[name] = path.is_file()
    return files


def _add_missing_context_problems(files: Dict[str, bool], problems: List[Problem], suggestions: List[str]) -> None:
    if not files.get("AGENTS.md", False):
        problems.append(
            Problem(
                level="error",
                code="missing_agents_md",
                file="AGENTS.md",
                message="Missing AGENTS.md. AI coding agents need a predictable project instruction file.",
                suggestion="Run: agentctx init",
            )
        )
        suggestions.append("Run: agentctx init")
    if not files.get("README.md", False):
        problems.append(
            Problem(
                level="warning",
                code="missing_readme",
                file="README.md",
                message="Missing README.md. Repository context is harder to summarize without it.",
            )
        )
    if not files.get("HANDOFF.md", False):
        problems.append(
            Problem(
                level="warning",
                code="missing_handoff_md",
                file="HANDOFF.md",
                message="Missing HANDOFF.md. Long AI coding sessions are easier to resume with a handoff file.",
                suggestion="Run: agentctx handoff",
            )
        )
        suggestions.append("Run: agentctx handoff")
    for file_name in ["CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursor/rules/"]:
        if not files.get(file_name, False):
            problems.append(
                Problem(
                    level="info",
                    code="missing_tool_context",
                    file=file_name,
                    message=f"Missing {file_name}.",
                    suggestion="Run: agentctx init --all",
                )
            )
            suggestions.append("Run: agentctx init --all")


def detect_commands(root: Path) -> Dict[str, List[str]]:
    texts: List[str] = []
    for relative in MARKDOWN_CONTEXT_PATHS:
        path = root / relative
        if path.exists() and path.is_file():
            texts.append(read_text(path, limit=200_000))
    texts.extend(_project_config_texts(root))
    combined = "\n".join(texts)
    return {
        "test": _match_commands(combined, TEST_COMMAND_PATTERNS),
        "build": _match_commands(combined, BUILD_COMMAND_PATTERNS),
        "install": _match_commands(combined, INSTALL_COMMAND_PATTERNS),
    }


def _project_config_texts(root: Path) -> List[str]:
    texts: List[str] = []
    makefile = root / "Makefile"
    if makefile.exists():
        text = read_text(makefile, limit=200_000)
        texts.append(text)
        if re.search(r"(?m)^test\s*:", text):
            texts.append("make test")
        if re.search(r"(?m)^build\s*:", text):
            texts.append("make build")
    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(read_text(package_json, limit=200_000))
        except json.JSONDecodeError:
            data = {}
        scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
        if isinstance(scripts, dict):
            if "test" in scripts:
                texts.append("npm test")
            if "build" in scripts:
                texts.append("npm run build")
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = read_text(pyproject, limit=200_000)
        texts.append(text)
        if "tool.pytest" in text or "pytest" in text:
            texts.append("pytest")
    return texts


def _match_commands(text: str, patterns: Sequence[Tuple[str, re.Pattern[str]]]) -> List[str]:
    candidates: List[Tuple[int, int, str]] = []
    for command, pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            candidates.append((start, end, command))

    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))

    found: List[str] = []
    seen_commands: Set[str] = set()
    covered_spans: List[Tuple[int, int]] = []
    for start, end, command in candidates:
        if any(_spans_overlap(start, end, existing_start, existing_end) for existing_start, existing_end in covered_spans):
            continue
        covered_spans.append((start, end))
        if command not in seen_commands:
            found.append(command)
            seen_commands.add(command)
    return found


def _spans_overlap(start: int, end: int, other_start: int, other_end: int) -> bool:
    return start < other_end and other_start < end


def _add_command_problems(root: Path, commands: Dict[str, List[str]], problems: List[Problem], suggestions: List[str]) -> None:
    if not commands.get("test"):
        problems.append(
            Problem(
                level="warning",
                code="missing_test_command",
                message="No common test command was found in README, context files, or common project configs.",
            )
        )
        suggestions.append("Document a test command in AGENTS.md")
    per_file_tests: Dict[str, List[str]] = {}
    for relative in [Path("README.md"), Path("AGENTS.md"), Path("CLAUDE.md"), Path("GEMINI.md")]:
        path = root / relative
        if path.exists():
            matches = _match_commands(read_text(path, limit=200_000), TEST_COMMAND_PATTERNS)
            if matches:
                per_file_tests[relative.as_posix()] = matches
    normalized = {name: set(values) for name, values in per_file_tests.items()}
    if len(normalized) >= 2:
        values = list(normalized.values())
        first = values[0]
        if any(value != first for value in values[1:]):
            problems.append(
                Problem(
                    level="warning",
                    code="test_command_conflict",
                    message="Different context files mention different test commands.",
                    suggestion="Choose one canonical test command in AGENTS.md, then run agentctx sync.",
                )
            )
            suggestions.append("Run: agentctx sync --from AGENTS.md")


def _add_path_reference_problems(root: Path, problems: List[Problem]) -> None:
    seen: Set[Tuple[str, str]] = set()
    for relative in MARKDOWN_CONTEXT_PATHS:
        path = root / relative
        if not path.exists() or not path.is_file():
            continue
        text = read_text(path, limit=250_000)
        for ref in extract_local_path_refs(text):
            key = (relative.as_posix(), ref)
            if key in seen:
                continue
            seen.add(key)
            target = root / ref
            if not _is_inside_root(root, target):
                continue
            if not target.exists():
                problems.append(
                    Problem(
                        level="warning",
                        code="missing_path_reference",
                        file=relative.as_posix(),
                        message=f"Referenced path `{ref}` does not exist.",
                    )
                )


def _is_inside_root(root: Path, target: Path) -> bool:
    # Use lexical absolute paths instead of Path.resolve(). This keeps symlinked
    # paths inside the repository from being treated as outside merely because
    # the symlink target points elsewhere, while still rejecting ../ escapes.
    root_abs = os.path.abspath(root)
    target_abs = os.path.abspath(target)
    try:
        return os.path.commonpath([root_abs, target_abs]) == root_abs
    except ValueError:
        return False


def extract_local_path_refs(markdown_text: str) -> List[str]:
    refs: List[str] = []
    text = _remove_fenced_code_blocks(markdown_text)
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        candidate = match.group(1).strip()
        candidate = candidate.split("#", 1)[0].strip()
        if candidate:
            refs.extend(_split_path_candidates(candidate))
    for match in re.finditer(r"(?<!`)`([^`\n]+)`(?!`)", text):
        inline = match.group(1).strip()
        # Inline code often contains commands such as `pytest tests/`. Treat it
        # as a path reference only when the entire inline span is one path-like token.
        if not re.search(r"\s", inline):
            refs.extend(_split_path_candidates(inline))
    return sorted(dict.fromkeys(refs))


def _remove_fenced_code_blocks(markdown_text: str) -> str:
    text = re.sub(r"```.*?```", "", markdown_text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.DOTALL)
    return text


def _split_path_candidates(text: str) -> List[str]:
    text = text.strip().strip("'\"")
    if not text or text.startswith(("http://", "https://", "mailto:", "#", "$", "-")):
        return []
    candidates: List[str] = []
    parts = re.split(r"\s+", text)
    for raw in parts:
        candidate = raw.strip().strip("'\"").rstrip(".,:;)]}")
        candidate = candidate.lstrip("([{!")
        if not candidate or candidate.startswith(("http://", "https://", "mailto:", "#", "$", "-")):
            continue
        if candidate in GENERATED_OR_OUTPUT_REFS:
            continue
        if "*" in candidate or "?" in candidate:
            continue
        if candidate.startswith("/"):
            continue
        if _looks_like_path(candidate):
            candidates.append(candidate.rstrip("/"))
    return candidates


def _looks_like_path(candidate: str) -> bool:
    if re.fullmatch(r"\d+/\d+", candidate):
        return False
    if candidate in KNOWN_FILENAMES:
        return True
    if candidate.endswith("/"):
        return True
    if "/" in candidate and not candidate.startswith(("http:", "https:")):
        return True
    return candidate.endswith(PATHLIKE_EXTENSIONS)


def _add_sync_problems(root: Path, problems: List[Problem], suggestions: List[str]) -> None:
    source = root / "AGENTS.md"
    if not source.exists():
        return
    for relative in [Path("CLAUDE.md"), Path("GEMINI.md"), Path(".github/copilot-instructions.md"), Path(".cursor/rules/agentctx.md")]:
        path = root / relative
        if not path.exists():
            continue
        text = read_text(path, limit=250_000)
        marker_hash = _marker_hash(text)
        if marker_hash and not _generated_block_matches(text, "AGENTS.md", read_text(source)):
            problems.append(
                Problem(
                    level="warning",
                    code="out_of_sync",
                    file=relative.as_posix(),
                    message=f"{relative.as_posix()} appears to be out of sync with AGENTS.md.",
                    suggestion="Run: agentctx sync --from AGENTS.md",
                )
            )
            suggestions.append("Run: agentctx sync --from AGENTS.md")


def _marker_hash(text: str) -> Optional[str]:
    match = re.search(r"<!--\s*agentctx:hash\s+([a-fA-F0-9]+)\s*-->", text)
    return match.group(1) if match else None


def _generated_block_matches(text: str, source_name: str, source_content: str) -> bool:
    expected = generated_block(source_name, source_content).strip()
    block = current_generated_block(text)
    return block == expected


def _add_marker_conflict_problems(root: Path, problems: List[Problem]) -> None:
    for relative in MARKDOWN_CONTEXT_PATHS:
        path = root / relative
        if not path.exists() or not path.is_file():
            continue
        conflicts = find_agentctx_marker_conflicts(read_text(path, limit=250_000))
        if conflicts:
            problems.append(
                Problem(
                    level="warning",
                    code="agentctx_marker_conflict",
                    file=relative.as_posix(),
                    message="Found ambiguous or malformed agentctx markers.",
                    suggestion="Remove or repair conflicting agentctx markers before running sync.",
                )
            )


def _score(files: Dict[str, bool], problems: List[Problem], commands: Dict[str, List[str]]) -> int:
    score = 100
    if not files.get("AGENTS.md", False):
        score -= 25
    if not files.get("README.md", False):
        score -= 15
    if not files.get("HANDOFF.md", False):
        score -= 8
    for file_name in ["CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursor/rules/"]:
        if not files.get(file_name, False):
            score -= 5
    if not commands.get("test"):
        score -= 10
    for problem in problems:
        if problem.code == "missing_path_reference":
            score -= 5
        elif problem.code == "out_of_sync":
            score -= 5
        elif problem.code == "test_command_conflict":
            score -= 5
        elif problem.code == "agentctx_marker_conflict":
            score -= 5
    return max(0, min(100, score))


def score_rating(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Needs work"
    return "Poor"


def format_scan_text(result: ScanResult) -> str:
    lines: List[str] = []
    lines.append("Agent Context Doctor")
    lines.append("")
    lines.append(f"Repository: {result.repository}")
    lines.append(f"Score: {result.score}/100 ({result.rating})")
    lines.append("")
    found = [name for name, exists in result.files.items() if exists]
    missing = [name for name, exists in result.files.items() if not exists and name in CONTEXT_FILES]
    lines.append("Found:")
    if found:
        for name in found:
            lines.append(f"  ✅ {name}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Missing:")
    if missing:
        for name in missing:
            lines.append(f"  ⚠️ {name}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Detected commands:")
    for kind in ["install", "test", "build"]:
        values = result.commands.get(kind, [])
        display = ", ".join(values) if values else "none"
        lines.append(f"  {kind}: {display}")
    lines.append("")
    lines.append("Problems:")
    if result.problems:
        for problem in result.problems:
            prefix = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(problem.level, "•")
            location = f" [{problem.file}]" if problem.file else ""
            lines.append(f"  {prefix}{location} {problem.message}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Suggestions:")
    if result.suggestions:
        for suggestion in result.suggestions:
            lines.append(f"  - {suggestion}")
    else:
        lines.append("  - No immediate action needed.")
    return "\n".join(lines)
