# Mini-project — 06-merge

_Companion chapter:_ [`06-merge.md`](../06-merge.md)

**Goal.** In a scratch repository, simulate a two-developer collision and resolve it cleanly using `diff3` markers.

**Acceptance criteria:**

- Create a repo with a shared file containing at least 10 lines.
- Create two branches that both modify the same region of the file.
- Merge and encounter a conflict.
- Resolve using `diff3` markers — the resolution should incorporate intent from both branches, not just pick one side.
- The final file should be valid, marker-free, and make logical sense.

**Hints:** Set `merge.conflictStyle=diff3` before merging. Use `git diff` after resolving (before committing) to review exactly what changed. `git log --graph --oneline --all` after the merge should show the two-parent topology.

**Stretch:** After resolving, enable `rerere.enabled=true`, undo the merge (`git reset --hard HEAD~1`), and redo it. Observe Git replaying your cached resolution automatically.
