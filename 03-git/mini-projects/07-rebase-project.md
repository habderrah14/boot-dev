# Mini-project — 07-rebase

_Companion chapter:_ [`07-rebase.md`](../07-rebase.md)

**Goal.** Given a branch with messy "wip", "fix typo", "wip 2", "forgot file" commits, produce a clean two-commit history and force-push it safely.

**Acceptance criteria:**

- The branch has at least 4 initial "messy" commits.
- After interactive rebase, exactly 2 well-messaged commits remain.
- The push uses `--force-with-lease`, not `--force`.
- `git log --oneline --graph` shows a linear history.

**Hints:** Start with `git rebase -i $(git merge-base HEAD main)`. Use `fixup` for throw-away messages and `reword` for the keeper commits.

**Stretch:** Set up `git rerere` before the rebase and intentionally create a conflict that repeats — verify that rerere auto-resolves it on the second occurrence.
