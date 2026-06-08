import json

from agentctx.cli import main
from agentctx.doctor import doctor_repository


def test_doctor_plans_safe_repairs(tmp_path):
    result = doctor_repository(tmp_path, fix=False)
    assert result["fixed"] is False
    assert "create AGENTS.md" in result["planned_actions"]
    assert not (tmp_path / "AGENTS.md").exists()


def test_doctor_fix_creates_context_files(tmp_path):
    result = doctor_repository(tmp_path, fix=True)
    assert result["fixed"] is True
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "HANDOFF.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".cursor" / "rules" / "agentctx.md").exists()
    assert result["score_after"] >= result["score_before"]


def test_cli_doctor_json(tmp_path, capsys):
    code = main(["doctor", "--root", str(tmp_path), "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "planned_actions" in data
    assert code == 1
