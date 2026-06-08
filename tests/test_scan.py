import json

from agentctx.cli import main
from agentctx.scanner import extract_local_path_refs, scan_repository


def test_scan_empty_directory_reports_missing_context(tmp_path):
    result = scan_repository(tmp_path)
    assert result.score < 60
    assert any(problem.code == "missing_agents_md" for problem in result.problems)
    assert result.files["AGENTS.md"] is False


def test_scan_detects_basic_project_context(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n\nRun `pytest`.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n\nUse `pytest`.\n", encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF.md\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    result = scan_repository(tmp_path)
    assert result.files["README.md"] is True
    assert result.files["AGENTS.md"] is True
    assert "pytest" in result.commands["test"]
    assert not any(problem.code == "missing_test_command" for problem in result.problems)


def test_scan_detects_missing_path_reference(tmp_path):
    (tmp_path / "README.md").write_text("See `docs/missing.md`. Run `pytest`.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
    result = scan_repository(tmp_path)
    assert any(problem.code == "missing_path_reference" for problem in result.problems)


def test_extract_local_path_refs_ignores_urls_and_commands():
    text = "See [site](https://example.com), [local](docs/usage.md), and run `pytest tests/`."
    refs = extract_local_path_refs(text)
    assert "docs/usage.md" in refs
    assert "tests" in refs
    assert "https://example.com" not in refs
    assert "pytest" not in refs


def test_cli_scan_json(tmp_path, capsys):
    code = main(["scan", "--root", str(tmp_path), "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["repository"] == tmp_path.name
    assert "score" in data
    assert code == 1


def test_extract_local_path_refs_handles_fenced_code_and_inline_paths():
    text = """
```bash
pytest tests/
```
See `docs/usage.md` and [guide](docs/guide.md).
"""
    refs = extract_local_path_refs(text)
    assert "docs/usage.md" in refs
    assert "docs/guide.md" in refs
    assert "tests" not in refs


def test_command_detection_does_not_duplicate_nested_commands(tmp_path):
    (tmp_path / "README.md").write_text(
        "Install with `python -m pip install -e .` and test with `python -m pytest`.",
        encoding="utf-8",
    )
    result = scan_repository(tmp_path)
    assert result.commands["install"] == ["python -m pip install"]
    assert result.commands["test"] == ["python -m pytest"]


def test_scan_detects_corrupted_generated_block_even_if_hash_remains(tmp_path):
    from agentctx.syncer import sync_context

    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(claude.read_text(encoding="utf-8").replace("# Rules", "# Broken"), encoding="utf-8")
    result = scan_repository(tmp_path)
    assert any(problem.code == "out_of_sync" for problem in result.problems)


def test_cli_scan_fail_under_returns_nonzero(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    code = main(["scan", "--root", str(tmp_path), "--fail-under", "90"])
    assert code == 1
