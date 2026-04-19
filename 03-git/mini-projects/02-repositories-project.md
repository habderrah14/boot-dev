# Mini-project — 02-repositories

_Companion chapter:_ [`02-repositories.md`](../02-repositories.md)

**Goal.** Initialize a Python project and build a clean three-commit history that a reviewer would be happy to read.

**Acceptance criteria:**

- First commit: `README.md` and `.gitignore` (ignoring `__pycache__/`, `*.pyc`, `.env`).
- Second commit: `main.py` with a minimal but runnable entry point.
- Third commit: `test_main.py` with at least one passing test.
- Each commit message explains *why*, not just *what*.
- `git log --oneline --stat` shows exactly three commits with the expected files.

**Hints:** Write `.gitignore` first so you never accidentally stage cached files. Use `git diff --staged` before each commit to double-check what you're about to record.

**Stretch:** Add a fourth commit using `git add -p` that changes only one function in `main.py` while leaving other modifications uncommitted.
