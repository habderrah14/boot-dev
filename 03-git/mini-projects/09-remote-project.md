# Mini-project — 09-remote

_Companion chapter:_ [`09-remote.md`](../09-remote.md)

**Goal.** Fork a small open-source repository, configure both `origin` and `upstream` remotes, keep your fork in sync, and prepare a contribution workflow.

**Acceptance criteria:**

- Your fork is cloned locally with `origin` pointing to your fork.
- `upstream` is configured and points to the original repository.
- You can demonstrate `git fetch upstream && git rebase upstream/main && git push --force-with-lease`.
- `git remote -v` shows both remotes correctly.
- You create a feature branch, push it to `origin`, and show the command to open a PR.

**Hints:** Use `gh repo fork --clone` to fork and clone in one step. Use `git branch -vv` to verify tracking relationships.

**Stretch:** Add a third remote called `backup` pointing to a different Git host (e.g., GitLab). Push your main branch to all three remotes.
