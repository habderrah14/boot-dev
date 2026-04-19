# Chapter 02 — Repositories

> A Git repository is a directory plus a hidden database. Everything else in Git is commands that read or update that database.

## Learning objectives

By the end of this chapter you will be able to:

- Initialize a new repository or clone an existing one.
- Explain the relationship between working tree, index (staging area), and repository.
- Stage changes selectively, commit them, and inspect history.
- Read and interpret the output of `git status`, `git log`, and `git diff`.

## Prerequisites & recap

- [Setup](01-setup.md) — Git is installed and your name, email, and editor are configured.

You should be able to run `git config user.name` and see your name. If not, revisit the previous chapter.

## The simple version

Git tracks your project across three areas. The **working tree** is the files as you see them on disk — what you edit. The **index** (also called the staging area) is a draft of your next commit — you decide exactly what goes in. The **repository** (the `.git/` directory) is the permanent record of every commit you've ever made.

The core workflow is always the same: edit files, stage the changes you want, commit them. Everything else in Git — branches, merges, rebases — is built on top of this simple loop.

## In plain terms (newbie lane)

This chapter is really about **Repositories**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The three-area workflow:

```
┌─────────────┐  git add   ┌─────────────┐  git commit  ┌──────────────┐
│ Working     │ ─────────► │   Index     │ ──────────► │  Repository  │
│ Tree        │            │  (staging)  │             │   (.git/)    │
│             │ ◄───────── │             │             │              │
└─────────────┘  git       └─────────────┘             └──────────────┘
                 restore                                      │
      ▲                                                       │
      │                  git checkout / git switch             │
      └───────────────────────────────────────────────────────┘
```

## Concept deep-dive

### The three areas in detail

- **Working tree** — the actual files in your project directory. This is what your editor opens, what your compiler reads, what your tests run against. Git doesn't track anything here automatically; you tell it what to care about.

- **Index / staging area** — a snapshot-in-waiting. When you run `git add`, Git copies the current state of that file into the index. You can stage files one at a time, or stage only specific hunks within a file. The index lets you craft precise commits rather than dumping everything in at once.

- **Repository** — the `.git/` directory at the root of your project. It holds the full commit history as a graph of immutable objects (more on this in the next chapter). Once something is committed, it's extremely hard to lose.

`git status` shows you the difference between each adjacent pair: working tree vs. index, and index vs. last commit.

### Creating a repository

Two starting points: create one from scratch, or clone an existing one.

```bash
mkdir myrepo && cd myrepo
git init                              # creates .git/
echo "# My Repo" > README.md
git status                            # README.md shows as untracked
git add README.md                     # moves it into the index
git status                            # README.md shows as staged
git commit -m "initial commit"        # records the snapshot
git log --oneline                     # one commit, one line
```

`git init` creates the `.git/` directory with everything Git needs: an empty object database, a default config, and an initial `HEAD` pointing at a branch that doesn't have any commits yet.

### Cloning

Cloning copies the entire repository — all commits, all branches, all history — to your machine:

```bash
git clone git@github.com:alice/repo.git
cd repo
git remote -v        # origin is set automatically, pointing back to the source
```

HTTPS works too (`https://github.com/alice/repo.git`), but SSH avoids credential prompts if you set up keys in the previous chapter.

### What's inside a commit

Each commit records:

- A **tree hash** — the snapshot of every file at that moment.
- **Parent hash(es)** — the commit(s) this one was built on.
- **Author** — who wrote the change (name, email, timestamp).
- **Committer** — who applied it (usually the same person).
- **Message** — why the change was made.

```bash
git log -1 --format=fuller
```

The commit hash is derived from all of these fields. Change any one of them — even a single character in the message — and you get a different hash. This is what makes Git's history tamper-evident.

### Reading diffs

`git diff` compares two of the three areas:

```bash
git diff                  # working tree vs. index (unstaged changes)
git diff --staged         # index vs. last commit (what would be committed)
git diff HEAD             # working tree vs. last commit (all uncommitted changes)
git diff main..feat       # tip of main vs. tip of feat
```

### Partial staging

You don't have to stage entire files. `git add -p` walks you through each changed "hunk" and lets you accept (`y`), skip (`n`), or split (`s`) them:

```bash
git add -p README.md     # interactive hunk selection
git diff --staged        # verify what you staged
git commit -m "refine intro paragraph"
```

This is how you split unrelated changes into separate, well-scoped commits — which makes code review, bisecting, and reverting vastly easier.

## Why these design choices

**Staging area exists for a reason.** Many VCS tools go straight from "modified" to "committed." Git's index gives you an editing buffer between those states. You can make five changes across three files and commit them as two logical units. This pays for itself every time a reviewer reads your history.

**Snapshots, not diffs.** Git stores the full state of every tracked file at each commit (deduplicated by content, so it's efficient). This makes checkouts and diffs fast — Git never has to replay a chain of patches to reconstruct a file.

**Immutable history.** Once committed, data is extremely durable. Even "rewriting history" actually creates new commits; the originals persist until garbage-collected. This is a safety net you'll appreciate the first time you accidentally delete a branch.

## Production-quality code

### Two files, one commit

```bash
printf "line1\n" > a.txt
printf "line1\n" > b.txt
git add a.txt b.txt
git commit -m "add initial data files"
git log --stat    # shows which files changed and how many lines
```

### Selective staging with verification

```bash
git add -p README.md

git diff --staged                     # review exactly what will be committed
git diff                              # review what will be left uncommitted
git commit -m "docs: tighten intro"
```

### Inspecting a range of history

```bash
git log --oneline --since="2 weeks ago"
git log --oneline --author="ada"
git log --oneline -- src/              # only commits touching src/
```

## Security notes

- **Secrets in commits** are the single biggest Git security mistake. API keys, passwords, and `.env` files committed even once live in the history forever (until you do an expensive, disruptive history rewrite). Use `.gitignore` to exclude sensitive files, and add a pre-commit hook to scan for known secret patterns.
- **Signed commits** (`git commit -S`) let you prove a commit actually came from you. Worth enabling for any project with compliance requirements.
- **Cloning untrusted repos** can expose you to crafted symlinks or submodule URLs. Stick to well-known forges (GitHub, GitLab) and review `.gitmodules` before initializing submodules.

## Performance notes

- `git add` and `git commit` on a modern machine handle tens of thousands of files with no perceptible delay. The operations are I/O-bound — SSDs make them near-instant.
- `git log` with no path filter reads the commit graph linearly; on very large repos (100k+ commits), add `--max-count` or path filters to avoid scanning the entire history.
- `git diff` is O(n) in the size of the changed files, not the total repo. It only reads files that differ.

## Common mistakes

1. **Symptom:** `git commit` says "nothing to commit, working tree clean" after you edited a file.
   **Cause:** You forgot to stage. Editing a file only changes the working tree; the index still matches the last commit.
   **Fix:** Run `git add <file>` before committing, or use `git commit -am "message"` (but note: `-a` only stages *tracked* files).

2. **Symptom:** A new file you created doesn't appear in the commit.
   **Cause:** `git commit -a` only stages modifications to already-tracked files. Brand-new files must be explicitly added.
   **Fix:** `git add newfile.txt` before committing.

3. **Symptom:** The repo grows unexpectedly large after committing.
   **Cause:** Large binary files (build artifacts, datasets, media) were committed. Git stores the full content of each version.
   **Fix:** Remove them from tracking (`git rm --cached <file>`), add to `.gitignore`, and consider [Git LFS](https://git-lfs.github.com) for binaries you genuinely need to version.

4. **Symptom:** Sensitive data (API keys, passwords) are visible in the repo.
   **Cause:** The file was committed before being added to `.gitignore`.
   **Fix:** `git rm --cached <file>`, add to `.gitignore`, commit, and rotate the exposed secret immediately. The old value persists in history until you rewrite it.

## Practice

1. **Warm-up.** Initialize a repo, create a file, commit it, and show the log.
2. **Standard.** Make three separate commits, each touching a different file, with meaningful messages. Then run `git log --oneline --stat` to review.
3. **Bug hunt.** You edited `server.py` and ran `git commit -m "fix bug"`, but Git says "nothing to commit." What went wrong, and what's the one-command fix?
4. **Stretch.** Use `git add -p` to put only half of a file's changes into one commit and the rest into the next. Verify with `git log --stat`.
5. **Stretch++.** Rename `README.md` to `README.markdown` in one commit. Then run `git log --follow README.markdown` and explain why `--follow` is needed.

<details><summary>Show solutions</summary>

1. `mkdir demo && cd demo && git init && echo "hello" > hello.txt && git add hello.txt && git commit -m "first commit" && git log`

2. Create files one at a time: `echo "a" > a.txt && git add a.txt && git commit -m "add module A"`, repeat for `b.txt` and `c.txt`.

3. You forgot `git add server.py`. Fix: `git add server.py && git commit -m "fix bug"`, or `git commit -am "fix bug"` (only works because `server.py` is already tracked).

4. Edit a file with two distinct changes (e.g., one at the top, one at the bottom). Run `git add -p`, answer `y` for the first hunk and `n` for the second. Commit. Then `git add -p` again, `y` for the remaining hunk, commit.

5. `git mv README.md README.markdown && git commit -m "rename readme"`. `--follow` is needed because Git tracks content, not filenames; without it, `git log` stops at the rename commit.

</details>

## Quiz

1. `.git/` holds:
    (a) The index file only (b) Only blob objects (c) The whole repository database (d) Nothing — it's a cache

2. `git status` compares:
    (a) Only staged vs. committed (b) Working tree vs. index AND index vs. HEAD (c) Working tree vs. origin (d) Config values

3. A commit is identified by:
    (a) Its message text (b) Its SHA hash (c) Its timestamp (d) The author name

4. `git commit -a` stages:
    (a) Everything including untracked files (b) Only tracked, modified files (c) Untracked files too (d) Nothing — it's the same as `git commit`

5. `git diff --staged` shows:
    (a) Working tree vs. index (b) Index vs. HEAD (c) HEAD vs. origin (d) Staged vs. stash

**Short answer:**

6. What's the practical difference between `git diff` (no flags) and `git diff --staged`?
7. Why is splitting unrelated changes into separate commits valuable?

*Answers: 1-c, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-repositories — mini-project](mini-projects/02-repositories-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Git's three areas — working tree, index, repository — form the core workflow: edit, stage, commit.
- The staging area gives you precise control over what goes into each commit.
- `git status` and `git diff` are your eyes into what has changed and where.
- Commits are immutable snapshots identified by their SHA hash — not diffs, not patches, not deltas.

## Further reading

- [Pro Git book](https://git-scm.com/book), chapter 2 — recording changes.
- `man git-diff` — the complete reference for all diff variants.
- Next: [Internals](03-internals.md).
