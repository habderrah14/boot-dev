# Mini-project — 08-reset

_Companion chapter:_ [`08-reset.md`](../08-reset.md)

**Goal.** In a scratch repository, demonstrate three common undo scenarios and document each one.

**Acceptance criteria:**

- Scenario 1: Unstage a file using `reset HEAD` and verify with `git status`.
- Scenario 2: Undo the last commit with `--soft`, edit, and re-commit with a better message.
- Scenario 3: Recover from `git reset --hard HEAD~3` using `git reflog`.
- Commit a `RESET_NOTES.md` file that documents the commands and output of each scenario.
- All operations are verified — show `git log` and `git status` output after each step.

**Hints:** Use `git log --oneline` liberally to track the state of your branch. For scenario 3, note the SHA from reflog and use `git switch -c rescue <sha>`.

**Stretch:** Add a fourth scenario: revert a merge commit with `-m 1` and explain what happened in your notes.
