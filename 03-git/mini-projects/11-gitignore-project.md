# Mini-project — 11-gitignore

_Companion chapter:_ [`11-gitignore.md`](../11-gitignore.md)

**Goal.** Audit an existing project for committed noise, write a comprehensive `.gitignore`, and clean up the repository.

**Acceptance criteria:**

- Identify all tracked files that should be ignored (build artifacts, caches, OS files, secrets).
- Write a complete `.gitignore` covering the project's language(s) and tooling.
- Untrack all files that should be ignored using `git rm --cached`.
- Create a `.gitattributes` with `text=auto` and appropriate binary markers.
- Commit the cleanup with a clear message.

**Hints:** Use `git ls-files` to see all tracked files. Cross-reference with templates from [github/gitignore](https://github.com/github/gitignore). Use `git check-ignore -v <file>` to verify patterns.

**Stretch:** Write a `cleanup.sh` script that automates the audit: it detects commonly-ignored patterns in tracked files, reports them, and optionally untracks them.
