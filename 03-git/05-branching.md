# Chapter 05 — Branching

> Branches make it safe to try things. Use them generously.

## Learning objectives

By the end of this chapter you will be able to:

- Create, switch, list, rename, and delete branches.
- Explain why branches are essentially free (and what that means for your workflow).
- Use a naming convention that scales across a team.
- Set up tracking branches so `push`, `pull`, and `fetch` work without extra arguments.
- Recover from accidental branch deletion using the reflog.

## Prerequisites & recap

- [Internals](03-internals.md) — you know that a branch is a file in `.git/refs/heads/` containing a commit SHA.
- [Config](04-config.md) — you have `fetch.prune=true` set so stale remote branches clean up automatically.

A branch is a pointer, not a copy. Creating one writes a 41-byte file. Switching one updates `HEAD` and the working tree. That's the entire mechanism — and it's why Git encourages you to branch constantly.

## The simple version

A branch is a named pointer to a commit. When you create one, Git writes a tiny file containing the SHA of the commit you're currently on. When you switch to it, Git updates your working tree to match that commit and sets `HEAD` to track the branch. When you make new commits, the branch pointer advances automatically.

Because branches are so cheap, the convention is to create one for every piece of work — every feature, every bug fix, every experiment. You never work directly on `main`. This keeps `main` stable and makes it easy to throw away, review, or merge work independently.

## In plain terms (newbie lane)

This chapter is really about **Branching**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Branch divergence and HEAD tracking:

```
           main
             │
             ▼
  A ◄── B ◄── E        (main advanced independently)
          │
          └──── C ◄── D
                       ▲
                       │
                   feat/login
                       │
                      HEAD
```

## Concept deep-dive

### Core commands

```bash
git branch                        # list local branches (* marks current)
git branch -a                     # include remote-tracking branches
git branch feat-login             # create a branch (doesn't switch to it)
git switch feat-login             # switch to it
git switch -c feat-login          # create + switch in one step
git switch -                      # toggle back to the previous branch

git branch -m old-name new-name   # rename a branch
git branch -d feat-login          # delete (only if fully merged)
git branch -D feat-login          # force delete (even if unmerged)
```

`git checkout` can do everything `switch` and `restore` do (and more). Newer Git splits the responsibility between two focused commands: `switch` for changing branches, `restore` for discarding file changes. Prefer the narrower commands — they're harder to misuse.

### Why branches cost nothing

A branch is literally one SHA (40 characters + newline) in a file under `.git/refs/heads/`. Creating a hundred branches adds a few kilobytes. No files are copied, no history is duplicated. The only "cost" is cognitive — keeping track of which branches exist and what they're for — which is why naming conventions matter.

### Naming conventions

A consistent naming scheme helps everyone on the team understand a branch's purpose at a glance:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New feature | `feat/signup-email` |
| `fix/` | Bug fix | `fix/42-null-avatar` |
| `chore/` | Build, infra, deps | `chore/upgrade-node-20` |
| `spike/` | Throwaway exploration | `spike/rewrite-router` |
| `docs/` | Documentation only | `docs/api-quickstart` |

Branch names become directories in `.git/refs/heads/` — `feat/signup-email` creates `refs/heads/feat/signup-email`. Avoid names that conflict with existing directory structures (e.g., don't name a branch `feat` if `feat/something` already exists).

### Tracking branches

When you branch off a remote branch or push with `-u`, Git records the **upstream** — the remote branch that this local branch is paired with:

```bash
git switch -c feat-login origin/main     # creates feat-login tracking origin/main
git branch -vv                            # shows upstream + ahead/behind counts
```

Once tracking is set, `git pull` knows where to fetch from and `git push` knows where to send to — no extra arguments needed.

```bash
git push -u origin feat/signup-email     # -u sets upstream on first push
git push                                  # subsequent pushes just work
```

### HEAD and branches

After `git switch feat-login`, the file `.git/HEAD` contains:

```
ref: refs/heads/feat-login
```

Every new commit advances the `feat-login` ref, and `HEAD` follows along because it points at the ref, not at a fixed SHA. This is what "being on a branch" means — `HEAD` is an indirect pointer through a branch ref.

### Recovering deleted branches

If you accidentally delete a branch, its commits don't vanish immediately. They become "unreachable" but remain in the object database until garbage collection (typically 30 days). Use the reflog to find them:

```bash
git reflog                                # find the commit SHA
git switch -c recovered-branch <sha>      # re-create the branch at that commit
```

## Why these design choices

**`git switch` over `git checkout`.** `checkout` is overloaded — it switches branches *and* restores files, and the behavior differs in subtle ways depending on arguments. `switch` only switches branches; `restore` only restores files. The split eliminates an entire class of "I ran checkout and it did something I didn't expect" problems.

**One branch per change.** Working directly on `main` means every mistake, half-finished feature, and experiment lands in the mainline. Branches give you isolation: you can push, revert, or discard a branch without affecting anyone else's work. The overhead is negligible; the safety is substantial.

**`-d` vs. `-D`.** Git refuses to delete a branch with `-d` if its commits aren't reachable from another branch — because that would make them hard to recover. `-D` overrides the safety check. The two-tier design prevents accidental data loss while still letting you force-delete when you know what you're doing.

## Production-quality code

### Feature branch lifecycle

```bash
git switch main
git pull                                    # start from latest main

git switch -c feat/signup-email
# ... implement the feature across multiple commits ...
git add -p && git commit -m "signup: add email validation"
git add -p && git commit -m "signup: add confirmation endpoint"

git push -u origin feat/signup-email        # push and set upstream
# open pull request, get review, merge on remote

git switch main && git pull                 # incorporate the merge
git branch -d feat/signup-email             # clean up local branch
```

### Throwaway spike

```bash
git switch -c spike/redis-caching
# experiment freely — commit or don't, it doesn't matter
git switch main
git branch -D spike/redis-caching          # -D because it was never merged
```

### Listing branches with context

```bash
git branch -vv --sort=-committerdate
# shows: branch name, upstream, ahead/behind, last commit message
# sorted by most recently committed, so active branches appear first
```

## Security notes

- **Branch names in CI/CD pipelines** can be used for injection if they're interpolated into shell commands without quoting. If your CI uses `$BRANCH_NAME` in a script, a malicious branch name like `feat/$(rm -rf /)` could execute arbitrary commands. Always quote branch names in scripts and validate them against a whitelist pattern.
- **Force-deleting branches** (`-D`) on a shared repo can discard teammates' work. On hosting platforms, configure branch protection rules to prevent deletion of critical branches (`main`, `release/*`).

## Performance notes

N/A — Branch operations (create, switch, delete, list) are effectively O(1). Creating a branch writes one 41-byte file. Switching branches updates the working tree, which is O(changed files) — if only a few files differ between branches, it's near-instant even on large repos. The only performance consideration is `git branch -a` on repos with thousands of remote-tracking branches, which may take a moment to enumerate.

## Common mistakes

1. **Symptom:** You made commits directly on `main` instead of a feature branch.
   **Cause:** You forgot to create and switch to a branch before starting work.
   **Fix:** Create the branch now and reset `main`: `git branch feat/my-work && git reset --hard HEAD~N` (where N is the number of commits to move). Then `git switch feat/my-work`.

2. **Symptom:** `git branch -d feat/foo` fails with "error: not fully merged."
   **Cause:** The branch has commits that aren't reachable from `HEAD` or any other branch.
   **Fix:** If you've already merged via a pull request on the remote, `git pull` first — the merge commit makes the branch reachable. If you genuinely want to discard the work, `git branch -D feat/foo`.

3. **Symptom:** `git push` says "no upstream branch" or prompts for a remote.
   **Cause:** The branch was created locally and never pushed with `-u` to set tracking.
   **Fix:** `git push -u origin feat/foo`. Subsequent pushes will just work.

4. **Symptom:** Remote branches you know were deleted still show up in `git branch -a`.
   **Cause:** `fetch.prune` isn't enabled, so `git fetch` never cleans up stale remote refs.
   **Fix:** `git fetch --prune` for immediate cleanup. `git config --global fetch.prune true` to make it automatic.

5. **Symptom:** You accidentally deleted a branch and lost commits.
   **Cause:** `git branch -D` was used and the commits aren't on any other branch.
   **Fix:** `git reflog` shows recent HEAD positions. Find the commit SHA and recreate: `git switch -c recovered <sha>`. This works as long as garbage collection hasn't run (default: 30 days).

## Practice

1. **Warm-up.** List all branches and print the name of the current one.
2. **Standard.** Create `feat/foo`, make a commit on it, switch back to `main`, and list both branches with `git branch -v`.
3. **Bug hunt.** `git branch -d feat/foo` fails with "not fully merged." What exactly does "fully merged" mean, and what are two ways to resolve the error?
4. **Stretch.** Push a branch, set its upstream in a single command, then verify with `git branch -vv`.
5. **Stretch++.** Given two branches that have diverged from `main`, show the commits unique to each using `git log` range syntax.

<details><summary>Show solutions</summary>

1. `git branch` (the `*` marks the current branch). Or: `git branch --show-current`.

2. ```bash
   git switch -c feat/foo
   echo "new feature" > feature.txt
   git add feature.txt && git commit -m "feat: add feature"
   git switch main
   git branch -v
   ```

3. "Fully merged" means all commits on the branch are reachable from `HEAD` (or the branch you're currently on). Two resolutions: (a) merge the branch first (`git merge feat/foo`), then delete, or (b) force-delete if you want to discard the work (`git branch -D feat/foo`).

4. `git push -u origin feat/foo` — the `-u` flag sets the upstream. Verify: `git branch -vv` shows `[origin/feat/foo]` next to the branch.

5. Commits on `feat-a` that aren't on `main`: `git log main..feat-a --oneline`. Commits on `main` that aren't on `feat-a`: `git log feat-a..main --oneline`. For a symmetric view: `git log --oneline --left-right feat-a...main`.

</details>

## Quiz

1. A branch is physically:
    (a) A copy of all files (b) A file in `.git/refs/heads/` containing a SHA (c) A tag (d) A clone

2. `git switch -c x` does what?
    (a) Creates branch x (b) Switches to x (c) Both creates and switches (d) Errors if x doesn't exist

3. To delete an unmerged branch:
    (a) `git branch -d` (b) `git branch -D` (c) `git remove` (d) Manually edit `.git/refs`

4. Creating a branch costs:
    (a) A full copy of the repo (b) Essentially nothing (c) A remote round-trip (d) A file rename

5. "Tracking" a remote branch means:
    (a) Mirroring it continuously (b) Git records the upstream so fetch/pull/push know where to go (c) CI watches it (d) Nothing practical

**Short answer:**

6. Why is working directly on `main` discouraged?
7. What's the practical difference between `git switch` and `git checkout`?

*Answers: 1-b, 2-c, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-branching — mini-project](mini-projects/05-branching-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Branches are cheap one-line pointer files — create one for every piece of work.
- `git switch -c <name>` creates and switches in one step; prefer it over the overloaded `git checkout`.
- Set upstream tracking with `git push -u` so subsequent push/pull operations require no arguments.
- Deleted branches can be recovered from the reflog within the garbage collection window (default 30 days).

## Further reading

- `man git-switch`, `man git-branch` — the complete command references.
- [Atlassian: Git Branch](https://www.atlassian.com/git/tutorials/using-branches) — visual branch tutorial.
- Next: [Merge](06-merge.md).
