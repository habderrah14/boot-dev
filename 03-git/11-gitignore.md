# Chapter 11 — Gitignore

> `.gitignore` is the second file you should create in any new repo (the first is `README.md`). It's the contract that keeps your repo free of noise.

## Learning objectives

By the end of this chapter you will be able to:

- Write `.gitignore` patterns correctly using globs, anchoring, and negation.
- Nest `.gitignore` files per subdirectory for scoped rules.
- Untrack a file that's already been committed.
- Configure a global ignore file for editor and OS artifacts.
- Use `.gitattributes` for line endings and merge strategy.

## Prerequisites & recap

- [Repositories](02-repositories.md) — you understand the working tree, index, and committed history.

Every `git add` and `git status` consults `.gitignore` to decide which files to consider. Without it, your repo fills up with build artifacts, dependency directories, environment files, and OS junk. This chapter covers the pattern syntax, the precedence rules, and the edge cases that catch everyone at least once.

## The simple version

`.gitignore` is a text file that tells Git which files and directories to pretend don't exist. When Git sees a file matching a pattern in `.gitignore`, it won't show it in `git status`, won't include it in `git add .`, and won't commit it. The file is invisible to Git — but only if Git isn't *already* tracking it. If you committed a file before adding it to `.gitignore`, the ignore rule has no effect until you explicitly untrack it.

Think of `.gitignore` as a bouncer at a door: it can stop new files from entering, but it can't kick out files that are already inside. For those, you need `git rm --cached`.

## In plain terms (newbie lane)

This chapter is really about **Gitignore**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How Git decides whether to track a file:

```
New file appears in working tree
         |
         v
Is it already tracked?
    |            |
   YES           NO
    |            |
    v            v
Git keeps     Does it match
tracking it   .gitignore?
              |          |
             YES         NO
              |          |
              v          v
         Invisible    Shown in
          to Git     git status
```

## Concept deep-dive

### Pattern syntax

```
# Lines starting with # are comments
*.log                  # match any .log file at any depth
build/                 # match the build directory at any depth
/secret.env            # match only at the repo root
!important.log         # re-include a file matched by an earlier pattern
src/**/__pycache__/    # globstar: match __pycache__ at any depth under src/
```

**Rules in detail:**

| Pattern element | Meaning |
|---|---|
| Blank lines | Ignored (use for readability) |
| Leading `/` | Anchors to the directory containing this `.gitignore` |
| Trailing `/` | Matches only directories, not files |
| `*` | Matches anything except `/` |
| `**` | Matches anything including `/` (zero or more directories) |
| `?` | Matches any single character except `/` |
| `[abc]` | Matches any one character in the set |
| `!` | Negates a previous pattern (re-includes a file) |

**The negation limitation:** you cannot re-include a file if its *parent directory* is ignored. Git never enters an ignored directory to check for negation patterns. This is the single most common source of confusion.

```
# This WON'T work:
secret/
!secret/keep.txt      # Git never enters secret/ to see this rule

# This WILL work:
secret/*               # ignore files inside secret, but not the dir itself
!secret/keep.txt       # now this re-include applies
```

### Language-specific templates

Don't write `.gitignore` from scratch — start from [github/gitignore](https://github.com/github/gitignore) and customize:

**Python:**
```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

**Node.js:**
```
node_modules/
dist/
.next/
.nuxt/
.env
.env.local
```

**OS/Editor (belongs in global ignore, not per-repo):**
```
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp
*~
```

### Nested `.gitignore` files

You can place a `.gitignore` in any subdirectory. Its patterns apply relative to that directory. This is useful when a subdirectory has its own build tooling or generated files:

```
project/
├── .gitignore          # repo-wide rules
├── src/
├── docs/
│   └── .gitignore      # docs-specific: ignore _build/
└── experiments/
    └── .gitignore      # experiments-specific: ignore *.csv, *.dat
```

**Precedence:** patterns in a deeper `.gitignore` override patterns from shallower ones. A pattern in `docs/.gitignore` takes priority over the root `.gitignore` for files within `docs/`.

### Untracking already-committed files

This is the most common "gotcha." If a file was committed before you added it to `.gitignore`, Git continues to track it. The ignore rule only applies to *untracked* files:

```bash
git rm --cached secret.env            # stop tracking, keep local file on disk
echo "secret.env" >> .gitignore
git commit -m "chore: stop tracking secret.env"
```

For directories:

```bash
git rm -r --cached node_modules/
echo "node_modules/" >> .gitignore
git commit -m "chore: stop tracking node_modules"
```

`--cached` is critical — without it, `git rm` deletes the file from your working tree too.

### Global ignore file

For artifacts that are personal to your development environment (OS files, editor configs), don't pollute every project's `.gitignore`. Set a global one:

```bash
git config --global core.excludesFile ~/.gitignore_global
```

Then add your OS and editor patterns there. This keeps project `.gitignore` files focused on project-specific noise.

### `.gitattributes` — the complementary file

`.gitattributes` doesn't ignore files — it controls *how* Git handles them:

```
*              text=auto          # normalize line endings (LF in repo)
*.png          binary             # never diff/merge as text
*.lock         linguist-generated # hide from GitHub language stats
docs/**        merge=ours         # on conflict, prefer our side
```

**Why `text=auto` matters:** Windows uses `\r\n`, Unix uses `\n`. Without normalization, the same file shows up as "modified" on every platform swap. `text=auto` stores files with `\n` in the repo and converts to the platform's native endings on checkout.

### Debugging ignore rules

When a file isn't being ignored (or is being ignored unexpectedly), use:

```bash
git check-ignore -v path/to/file
# .gitignore:3:*.log    path/to/file.log
```

This shows which `.gitignore` file and which line is responsible for the match. Invaluable for debugging complex nested ignore setups.

## Why these design choices

**Why doesn't `.gitignore` affect already-tracked files?** Because tracking is a property of the index, not the working tree. Once Git is tracking a file, ignoring it would silently drop changes — a dangerous data-loss path. Requiring explicit `git rm --cached` forces you to make a conscious decision to stop tracking, which is safer.

**Why is negation limited by directory ignoring?** Performance. If Git had to scan inside every ignored directory looking for negation patterns, `git status` would be dramatically slower on large repos with massive ignored directories like `node_modules/` (hundreds of thousands of files). The rule "Git never enters an ignored directory" is a performance optimization that trades flexibility for speed.

**Why support nested `.gitignore` files?** Because monorepos and multi-language projects have different noise patterns in different directories. A Go subdirectory doesn't need Node.js ignore rules and vice versa. Nested files let each part of the project define its own policy without cluttering the root file.

## Production-quality code

### Comprehensive Python/Node mixed-project `.gitignore`

```
# === Python ===
__pycache__/
*.py[cod]
*.so
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
htmlcov/
.coverage
.coverage.*

# === Node.js ===
node_modules/
.next/
.nuxt/

# === Environment & secrets ===
.env
.env.*
!.env.example

# === Build output ===
dist/
build/
out/

# === OS artifacts ===
.DS_Store
Thumbs.db

# === Editor (prefer global ignore for these) ===
.idea/
.vscode/settings.json
.vscode/launch.json
*.swp
*~
```

### Script to audit and clean a repo

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Files that should probably be ignored ==="

SUSPECTS=(
    "node_modules"
    "__pycache__"
    ".venv"
    "venv"
    ".env"
    ".DS_Store"
    "Thumbs.db"
    ".pytest_cache"
    ".mypy_cache"
    "dist"
    "build"
    "*.pyc"
)

FOUND=0
for PATTERN in "${SUSPECTS[@]}"; do
    MATCHES=$(git ls-files "$PATTERN" 2>/dev/null || true)
    if [ -n "$MATCHES" ]; then
        echo ""
        echo "TRACKED (should be ignored): $PATTERN"
        echo "$MATCHES" | head -20
        FOUND=$((FOUND + 1))
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "Repository is clean — no commonly-ignored files are tracked."
    exit 0
fi

echo ""
echo "=== To fix, run for each pattern: ==="
echo "  git rm -r --cached <path>"
echo "  echo '<pattern>' >> .gitignore"
echo "  git commit -m 'chore: stop tracking <pattern>'"
```

### `.gitattributes` starter file

```
# Normalize line endings
*              text=auto

# Explicitly declare text files
*.py           text diff=python
*.js           text
*.ts           text
*.md           text eol=lf
*.yml          text eol=lf
*.yaml         text eol=lf
*.json         text eol=lf
*.sh           text eol=lf

# Binary files — no diff, no merge
*.png          binary
*.jpg          binary
*.gif          binary
*.ico          binary
*.woff         binary
*.woff2        binary
*.ttf          binary
*.zip          binary
*.tar.gz       binary

# Lock files — generated, don't merge manually
package-lock.json   linguist-generated merge=ours
poetry.lock         linguist-generated merge=ours
```

## Security notes

- **Committed secrets** — the most critical `.gitignore` failure mode. If `.env`, `credentials.json`, or any file with secrets is committed even once, the secret is in Git history permanently. Adding it to `.gitignore` later only prevents future commits. You must: (1) rotate the secret immediately, (2) remove the file from history with `git filter-repo`, and (3) force-push. Assume any committed secret is compromised.
- **`.env.example` pattern** — use `!.env.example` to track a template file showing required variables without values. This documents what environment variables the project needs without exposing real secrets.
- **Pre-commit hooks** — tools like `detect-secrets` or `gitleaks` can scan staged files for secrets before they're committed. This catches mistakes at the earliest possible point. See GitHub's built-in secret scanning for server-side detection.

## Performance notes

- **`git status` speed** — Git checks every untracked file against `.gitignore` patterns. On repos with large ignored directories (like `node_modules/` with 100k+ files), pattern matching can slow down `git status`. Trailing `/` on directory patterns helps: Git skips the entire directory tree instead of checking each file individually.
- **Pattern ordering** — Git evaluates patterns top to bottom, last match wins. While order doesn't affect correctness (except for negation), putting the most frequently matched patterns first can marginally speed up evaluation on very large repos.
- **`core.fsmonitor`** — on large repos, Git's filesystem monitor can dramatically speed up `git status` by watching for filesystem events instead of scanning every file. Enabled by default on recent Git versions with supported platforms.

## Common mistakes

1. **Symptom:** You added `secret.env` to `.gitignore` but `git status` still shows changes to it.
   **Cause:** The file was committed before the ignore rule was added. `.gitignore` only affects untracked files.
   **Fix:** `git rm --cached secret.env`, commit, then the ignore rule takes effect.

2. **Symptom:** `!secret/keep.txt` doesn't re-include the file.
   **Cause:** The parent directory `secret/` is ignored. Git never enters ignored directories to check for negation patterns.
   **Fix:** Change `secret/` to `secret/*` (ignore contents, not the directory itself). Then `!secret/keep.txt` works.

3. **Symptom:** `.DS_Store` keeps appearing in PRs from macOS developers.
   **Cause:** It's not in the project's `.gitignore`, or each developer hasn't set up a global ignore file.
   **Fix:** Add `.DS_Store` to the project's `.gitignore` as a baseline. Better: each developer configures `core.excludesFile` with their OS/editor artifacts.

4. **Symptom:** You committed `.env` with production database credentials.
   **Cause:** No `.gitignore` rule, or the rule was added after the first commit.
   **Fix:** **Rotate all credentials immediately** — the secret is compromised the moment it's pushed. Then: `git rm --cached .env`, add to `.gitignore`, commit. To remove from history entirely, use `git filter-repo --path .env --invert-paths` and force-push.

5. **Symptom:** Build artifacts (`dist/`, `build/`) bloat the repository and make clones slow.
   **Cause:** These directories were committed, and `.gitignore` wasn't set up before the first `git add .`.
   **Fix:** `git rm -r --cached dist/ build/`, add to `.gitignore`, commit. For already-pushed repos, the old objects remain in history — consider `git filter-repo` for large artifacts.

## Practice

**Warm-up.** Create a fresh repo and add `*.pyc` and `__pycache__/` to its `.gitignore`. Verify with `git status` that Python bytecode files are hidden.

**Standard.** Take a Node project that committed `node_modules/`. Untrack it, add the ignore rule, and commit the cleanup.

**Bug hunt.** Explain why `!secret/keep.txt` doesn't re-include the file when `secret/` is in `.gitignore`. Fix it.

**Stretch.** Configure a global `~/.gitignore_global` for `.DS_Store`, `.idea/`, and `*.swp`. Verify with `git config --global core.excludesFile`.

**Stretch++.** Write a `.gitattributes` file that normalizes line endings (`text=auto`), marks `*.md` as `text eol=lf`, and marks `*.png` as `binary`. Explain what each directive does.

<details><summary>Show solutions</summary>

**Bug hunt.** Git never enters a directory that matches an ignore pattern. When `secret/` is ignored, Git skips the entire directory tree, so it never sees the negation rule for `keep.txt`. Fix: change `secret/` to `secret/*` — this ignores the *contents* of the directory rather than the directory itself. Now Git enters `secret/`, sees the negation `!secret/keep.txt`, and tracks that file.

**Stretch++.**

```
*        text=auto      # auto-detect text/binary; normalize text to LF in repo
*.md     text eol=lf    # always use LF for markdown, even on Windows checkouts
*.png    binary         # never attempt text diff or merge on PNG files
```

- `text=auto` lets Git detect whether a file is text or binary. Text files get line-ending normalization (stored as LF in the repo, converted to platform native on checkout).
- `text eol=lf` forces LF endings on all platforms, even Windows. Useful for files that will be processed by Unix tools.
- `binary` marks files as non-text: no line-ending conversion, no text diff, no text merge.

</details>

## Quiz

1. `/foo` vs. `foo` in `.gitignore`:
    (a) identical behavior (b) `/foo` matches only at the repo root; `foo` matches at any depth (c) `/foo` matches everywhere (d) neither works

2. To untrack a committed file without deleting it from disk:
    (a) just add to `.gitignore` (b) `git rm --cached FILE` then add to `.gitignore` (c) `git restore FILE` (d) manually edit `.git/index`

3. `**` in a `.gitignore` pattern means:
    (a) a single character (b) any path including `/` (zero or more directories) (c) comment syntax (d) negation

4. The global ignore file is configured with:
    (a) an environment variable (b) `core.excludesFile` in Git config (c) `/etc/gitconfig` only (d) it's hardcoded and can't be changed

5. `.gitattributes` is used for:
    (a) ignoring files (b) declaring file attributes like binary/text and merge strategies (c) signing commits (d) GitHub-specific UI settings

**Short answer:**

6. What does `!pattern` do in `.gitignore` and what is its limitation?
7. Why must a leaked `.env` be rotated, not just removed from the repo?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

*6. `!pattern` negates a previous ignore rule, re-including a file that would otherwise be ignored. Its limitation: it cannot re-include a file whose parent directory is ignored, because Git never enters ignored directories to evaluate nested patterns.*

*7. Because Git stores every version of every file in its history. Even if you delete the file or remove it from history, anyone who cloned or forked the repo before the cleanup has a copy. The secret must be assumed compromised — the only safe response is to revoke the old credentials and issue new ones.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-gitignore — mini-project](mini-projects/11-gitignore-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `.gitignore` prevents untracked files from being added — it does not affect already-tracked files.
- Use `git rm --cached` to stop tracking a file before `.gitignore` rules apply to it.
- Start from language-specific templates; put OS/editor patterns in a global ignore file.
- `.gitattributes` complements `.gitignore` by controlling line endings, diff behavior, and merge strategies.

## Further reading

- [Git documentation — gitignore](https://git-scm.com/docs/gitignore) — full pattern syntax reference.
- [github/gitignore](https://github.com/github/gitignore) — community-maintained templates for every language and framework.
- [Git documentation — gitattributes](https://git-scm.com/docs/gitattributes) — line endings, binary markers, and custom merge drivers.
- Next module: [Module 04 — OOP](../04-oop/README.md).
