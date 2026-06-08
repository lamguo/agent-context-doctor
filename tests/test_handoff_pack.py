from agentctx.cli import main
from agentctx.handoff import collect_handoff_data, render_handoff, write_handoff
from agentctx.packer import create_context_pack


def test_handoff_renders_without_git(tmp_path):
    (tmp_path / "README.md").write_text("Run `pytest`.\n", encoding="utf-8")
    data = collect_handoff_data(tmp_path)
    rendered = render_handoff(data)
    assert "Current Repository State" in rendered
    assert "not a Git repository" in rendered
    assert "pytest" in rendered


def test_write_handoff_creates_file(tmp_path):
    write_handoff(tmp_path)
    assert (tmp_path / "HANDOFF.md").exists()
    assert "Next Recommended Steps" in (tmp_path / "HANDOFF.md").read_text(encoding="utf-8")


def test_pack_creates_project_context(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    output = create_context_pack(tmp_path)
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "PROJECT_CONTEXT.md" in text
    assert "Agent Instructions" in text


def test_cli_handoff_json(tmp_path, capsys):
    code = main(["handoff", "--root", str(tmp_path), "--json"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"repository"' in out


def test_cli_pack(tmp_path, capsys):
    code = main(["pack", "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Wrote PROJECT_CONTEXT.md" in out
    assert (tmp_path / "PROJECT_CONTEXT.md").exists()


def test_pack_tree_excludes_existing_project_context(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "PROJECT_CONTEXT.md").write_text("old", encoding="utf-8")
    create_context_pack(tmp_path)
    text = (tmp_path / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    structure = text.split("## Project Structure", 1)[1].split("## Detected Commands", 1)[0]
    assert "PROJECT_CONTEXT.md" not in structure


def test_cli_pack_stdout_does_not_write_file(tmp_path, capsys):
    from agentctx.cli import main

    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    code = main(["pack", "--root", str(tmp_path), "--stdout"])
    out = capsys.readouterr().out
    assert code == 0
    assert "# PROJECT_CONTEXT.md" in out
    assert not (tmp_path / "PROJECT_CONTEXT.md").exists()
