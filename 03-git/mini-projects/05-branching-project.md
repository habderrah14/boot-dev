# Mini-project — 05-branching

_Companion chapter:_ [`05-branching.md`](../05-branching.md)

**Goal.** Simulate a multi-branch workflow in an existing repository.

**Acceptance criteria:**

- Create branches `feat/docs` and `chore/lint` from `main`.
- Make at least one commit on each branch.
- Push both branches with upstream tracking set.
- Delete one branch locally after confirming its commits are on the remote.
- Run `git branch -vv` and verify the tracking information is correct.

**Hints:** Use `git switch -c <name>` to create and switch in one step. Use `git push -u origin <name>` on first push. After deleting locally, `git branch -a` should still show the remote-tracking ref.

**Stretch:** Add a third branch `spike/experiment`, make commits, then delete it without merging. Use `git reflog` to prove you could recover it if needed.
