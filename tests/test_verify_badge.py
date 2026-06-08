import json

from agentctx.cli import main


def test_verify_passes_for_healthy_repository(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Demo\n\nRun `pytest`.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text(
        "# AGENTS.md\n\n## Setup\nInstall with pip.\n\n## Testing\nRun `pytest`.\n\n## Security\nNo secrets.\n",
        encoding="utf-8",
    )
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF.md\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE.md\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text("# GEMINI.md\n", encoding="utf-8")
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "copilot-instructions.md").write_text("# Copilot\n", encoding="utf-8")
    (tmp_path / ".cursor" / "rules").mkdir(parents=True)
    (tmp_path / ".cursor" / "rules" / "agentctx.md").write_text("# Cursor\n", encoding="utf-8")
    code = main(["verify", "--root", str(tmp_path), "--min-score", "80"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Verification passed" in out


def test_verify_fails_for_low_score(tmp_path, capsys):
    code = main(["verify", "--root", str(tmp_path), "--min-score", "90"])
    out = capsys.readouterr().out
    assert code == 1
    assert "Verification failed" in out


def test_verify_json(tmp_path, capsys):
    code = main(["verify", "--root", str(tmp_path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert data["passed"] is False
    assert "result" in data


def test_badge_outputs_markdown(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    code = main(["badge", "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("![agentctx:")
    assert "img.shields.io" in out


def test_badge_json(tmp_path, capsys):
    code = main(["badge", "--root", str(tmp_path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert "markdown" in data
    assert "url" in data
