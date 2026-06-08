# GitHub Setup Checklist

Some project settings cannot be applied from a source ZIP. After pushing the repository, set these in GitHub.

## 1. Create and push the `main` branch

```bash
git init
git branch -M main
git add .
git commit -m "Initial release"
git remote add origin https://github.com/lamguo/agent-context-doctor.git
git push -u origin main
```

The included CI workflow now runs on every pushed branch, every pull request, and manual `workflow_dispatch`. It no longer depends on `main` existing before the first push.

## 2. Set GitHub Topics

Open the repository page, click the gear icon next to **About**, and add:

```text
ai
coding-agents
agents-md
claude-code
gemini-cli
github-copilot
cursor
developer-tools
cli
python
```

## 3. Check the CI badge

The README uses this badge:

```md
[![CI](https://github.com/lamguo/agent-context-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/lamguo/agent-context-doctor/actions/workflows/ci.yml)
```

It will start showing real status after the first workflow run on GitHub.

## 4. Optional repository settings

- Enable Issues.
- Enable Discussions only if you want public support questions.
- Protect `main` after the first stable release.
- Require CI before merge once the project has external contributors.
