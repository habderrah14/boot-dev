# Mini-project — 03-internals

_Companion chapter:_ [`03-internals.md`](../03-internals.md)

**Goal.** Write a script `git-internals-demo.sh` that creates a tiny repository and uses plumbing commands to explore its internal structure.

**Acceptance criteria:**

- Creates a fresh repo in a temp directory, commits two files.
- Prints the commit SHA, tree SHA, and blob SHA for each file using only plumbing commands (`cat-file`, `ls-tree`, `rev-parse`).
- Pretty-prints the content of each object.
- Verifies (with an assertion or comparison) that the tree lists the expected number of entries.
- Cleans up the temp directory on exit (use a `trap`).

**Hints:** Start with `git rev-parse HEAD` to get the commit SHA, then `git cat-file -p <sha>` to extract the tree SHA from the commit, then `git ls-tree <tree-sha>` to list entries.

**Stretch:** Extend the script to also demonstrate blob sharing — add two files with identical content and verify they have the same blob hash.
