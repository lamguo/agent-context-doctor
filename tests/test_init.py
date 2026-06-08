from agentctx.cli import main
from agentctx.initializer import init_context_files


def test_init_creates_default_files(tmp_path):
    result = init_context_files(tmp_path)
    assert "AGENTS.md" in result["created"]
    assert "HANDOFF.md" in result["created"]
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "HANDOFF.md").exists()


def test_init_all_creates_tool_files(tmp_path):
    result = init_context_files(tmp_path, include_all=True)
    assert ".github/copilot-instructions.md" in result["created"]
    assert ".cursor/rules/agentctx.md" in result["created"]
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "GEMINI.md").exists()


def test_init_does_not_overwrite_without_force(tmp_path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("custom", encoding="utf-8")
    result = init_context_files(tmp_path)
    assert "AGENTS.md" in result["skipped"]
    assert agents.read_text(encoding="utf-8") == "custom"


def test_init_force_overwrites(tmp_path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("custom", encoding="utf-8")
    result = init_context_files(tmp_path, force=True)
    assert "AGENTS.md" in result["overwritten"]
    assert "Project Overview" in agents.read_text(encoding="utf-8")


def test_cli_init_dry_run(tmp_path, capsys):
    code = main(["init", "--root", str(tmp_path), "--all", "--dry-run"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Would create" in out
    assert not (tmp_path / "AGENTS.md").exists()


def test_init_all_uses_existing_agents_as_source(tmp_path):
    custom = "# Custom Agents\n\nRun `pytest`.\n"
    (tmp_path / "AGENTS.md").write_text(custom, encoding="utf-8")
    result = init_context_files(tmp_path, include_all=True)
    assert "AGENTS.md" in result["skipped"]
    claude_text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    cursor_text = (tmp_path / ".cursor" / "rules" / "agentctx.md").read_text(encoding="utf-8")
    assert "# Custom Agents" in claude_text
    assert "# Custom Agents" in cursor_text
