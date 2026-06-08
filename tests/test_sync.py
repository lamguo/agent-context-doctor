from agentctx.cli import main
from agentctx.syncer import sync_context


def test_sync_creates_targets(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n\nRun tests.\n", encoding="utf-8")
    result = sync_context(tmp_path)
    assert "CLAUDE.md" in result["created"]
    assert "GEMINI.md" in result["created"]
    assert ".github/copilot-instructions.md" in result["created"]
    assert "agentctx:hash" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


def test_sync_is_idempotent(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path)
    result = sync_context(tmp_path)
    assert "CLAUDE.md" in result["already_synced"]


def test_sync_check_detects_out_of_sync(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# Changed\n", encoding="utf-8")
    result = sync_context(tmp_path, check=True)
    assert "CLAUDE.md" in result["out_of_sync"]


def test_sync_preserves_user_content_outside_markers(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(claude.read_text(encoding="utf-8") + "\nUser notes stay here.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Changed\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    text = claude.read_text(encoding="utf-8")
    assert "# Changed" in text
    assert "User notes stay here." in text


def test_cli_sync_check_return_code(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# Changed\n", encoding="utf-8")
    code = main(["sync", "--root", str(tmp_path), "--check"])
    assert code == 1


def test_sync_check_detects_corrupted_generated_block_even_if_hash_remains(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(claude.read_text(encoding="utf-8").replace("# Rules", "# Broken"), encoding="utf-8")
    result = sync_context(tmp_path, targets=["claude"], check=True)
    assert "CLAUDE.md" in result["out_of_sync"]


def test_sync_replaces_only_current_generated_block(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    claude = tmp_path / "CLAUDE.md"
    claude.write_text("<!-- agentctx:source old -->\n\n" + claude.read_text(encoding="utf-8") + "\nManual note.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Changed\n", encoding="utf-8")
    sync_context(tmp_path, targets=["claude"])
    text = claude.read_text(encoding="utf-8")
    assert "<!-- agentctx:source old -->" in text
    assert "# Changed" in text
    assert "Manual note." in text


def test_sync_creates_cursor_target(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    result = sync_context(tmp_path, targets=["cursor"])
    assert ".cursor/rules/agentctx.md" in result["created"]
    text = (tmp_path / ".cursor" / "rules" / "agentctx.md").read_text(encoding="utf-8")
    assert "# Rules" in text
    assert "agentctx:hash" in text
