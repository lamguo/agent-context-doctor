# Usage

Agent Context Doctor is designed for local repository checks.

## Basic workflow

1. Run `agentctx scan` to see the current health score.
2. Run `agentctx init --all` to create missing context files.
3. Edit `AGENTS.md` as the source of truth.
4. Run `agentctx sync --from AGENTS.md` to update generated sections, including Cursor rules.
5. Run `agentctx scan --fail-under 80` in CI if you want a minimum context score.
6. Run `agentctx doctor` to preview safe automatic repairs, or `agentctx doctor --fix` to apply them.
7. Run `agentctx handoff` at the end of a long AI coding session.
8. Run `agentctx pack` before moving work into a new AI chat or agent session.
