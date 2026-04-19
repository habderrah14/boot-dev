# Chapter 07 — Rebase

> Rebase rewrites history. Done well, it gives you a clean, linear log. Done poorly, it destroys your teammates' work. Respect it.

## Learning objectives

By the end of this chapter you will be able to:

- Perform a plain rebase onto a new base.
- Use interactive rebase to reorder, squash, and reword commits.
- Recover from a rebase gone wrong.
- Know the "never rebase public history" rule (and the exception).

## Prerequisites & recap

- [Merge](06-merge.md) — you understand how Git combines branches with merge commits and how to resolve conflicts.

Merge gives you a truthful, non-linear history — every join is visible. Rebase gives you the opposite: a straight line where it looks like all work happened sequentially. Both are tools; this chapter shows you when each makes sense.

## The simple version

Imagine you're writing a feature branch. While you work, `main` moves forward with other people's commits. You could merge `main` into your branch, but that creates a merge commit that adds noise and clutters `git log`. Rebase takes a different approach: it lifts your commits off the old base, moves the branch pointer to the tip of `main`, and replays your commits one at a time on top. The result is a clean, straight line of history — as if you started your work after everyone else finished theirs.

The catch is that replaying creates *new* commits with *new* SHA hashes. Your old commits still exist in the reflog, but the branch now points at copies. If anyone else already has the old commits, they'll see a diverged history when they pull. That's why the cardinal rule exists: never rebase commits that have been shared with others (unless the branch is exclusively yours).

## In plain terms (newbie lane)

This chapter is really about **Rebase**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Before and after a rebase of `feat` onto an updated `main`:

```
BEFORE                          AFTER

main:  A ── B ── E              main:  A ── B ── E
              \                                    \
feat:          C ── D           feat:               C' ── D'

C and D are replayed as C' and D' (new SHAs).
```

## Concept deep-dive

### What rebase actually does

When you run `git rebase main` while on `feat`, Git:

1. Finds the common ancestor of `feat` and `main`.
2. Saves the diffs introduced by each `feat` commit since that ancestor.
3. Moves the `feat` branch pointer to the tip of `main`.
4. Applies each saved diff as a new commit, in order.

Because each replayed commit gets a new parent, it necessarily has a new SHA — even if the code changes are byte-for-byte identical. This is the single most important thing to internalize: **rebase creates new commits**.

### Why you'd choose rebase over merge

- **Cleaner `git log`** — no merge commits, no diamond shapes in the graph. A linear history is easier to scan and easier for `git bisect` to binary-search through.
- **Polished PRs** — interactive rebase lets you clean up "wip" and "fix typo" commits before anyone reviews them.
- **Simpler diffs** — reviewers see a tidy sequence of logical changes, not a spaghetti graph.

The trade-off: merge preserves the true timeline. Rebase rewrites it. If auditability matters more than aesthetics (regulatory codebases, for example), prefer merge.

### Interactive rebase

This is where rebase becomes a power tool. `git rebase -i HEAD~5` opens your editor with the five most recent commits:

```
pick 12ab34f Add user model
pick 56cd78e Fix typo in model
pick 9012abc WIP: start validation
pick 3456def WIP: finish validation
pick 7890fed Add tests for validation
```

Change `pick` to one of these keywords:

| Keyword | Short | Effect |
|---|---|---|
| `reword` | `r` | Keep the commit but open an editor to change its message |
| `edit` | `e` | Pause after applying so you can amend the commit's content |
| `squash` | `s` | Meld into the previous commit, combine both messages |
| `fixup` | `f` | Meld into the previous commit, discard this commit's message |
| `drop` | `d` | Delete the commit entirely |

You can also reorder lines to reorder commits. Save and close — Git applies the instructions top to bottom. If a conflict arises at any step, Git pauses and lets you resolve before continuing.

### The never-rebase-public-history rule

Never rebase commits that others have already pulled. Your rebased commits have different SHAs than the originals. When a teammate pulls, Git sees both the old commits (which they already have) and the new ones (which look like unrelated work). The result is duplicate commits, merge conflicts, and confusion.

**The exception:** a feature branch that only you work on. Here, rebase freely. When you push, use `--force-with-lease`:

```bash
git push --force-with-lease origin feat/foo
```

`--force-with-lease` checks that the remote branch hasn't moved since your last fetch. If someone else has pushed to it, the push is rejected — saving you from silently overwriting their work. Plain `--force` has no such check.

### Conflicts during rebase

Because rebase replays commits one at a time, you may hit conflicts at any step. When that happens:

```bash
# 1. Git tells you which file(s) conflict
# 2. Open and resolve them
$EDITOR path/to/conflicted_file

# 3. Stage the resolved files
git add path/to/conflicted_file

# 4. Continue to the next commit
git rebase --continue
```

If things get too messy, bail out entirely:

```bash
git rebase --abort
```

This restores the branch to its exact pre-rebase state. Nothing is lost.

### Rebase onto

`git rebase --onto` gives you surgical control. It lets you transplant a range of commits onto any target:

```bash
# Move commits C..F from feat onto release, skipping A..C
git rebase --onto release C feat
```

This is useful when you branched off the wrong base or need to cherry-pick a range of work onto a different branch.

## Why these design choices

**Why new SHAs?** A commit's SHA is a hash of its content *plus* its parent. When the parent changes (the whole point of rebase), the hash must change. There's no way around this — it's fundamental to Git's integrity model.

**Why not just always merge?** Merge is safe and honest, but on active teams the graph becomes unreadable fast. Many teams adopt a "rebase locally, merge to main" workflow: each developer rebases their feature branch onto `main` before opening a PR, then the PR is merged (or squash-merged) on the server. This gives you linear feature-branch history *and* a merge commit on main that serves as a clear record of the integration.

**Why `--force-with-lease` instead of `--force`?** Because `--force` is a fire-and-forget overwrite. If a colleague pushed a hotfix to your shared branch five minutes ago, `--force` silently erases it. `--force-with-lease` is a compare-and-swap: it only succeeds if the remote ref matches your last-known value.

## Production-quality code

### Keeping a feature branch current with main

```bash
#!/usr/bin/env bash
set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "ERROR: You're on $BRANCH. Switch to a feature branch first." >&2
    exit 1
fi

git fetch origin

BEHIND=$(git rev-list --count HEAD..origin/main)
if [ "$BEHIND" -eq 0 ]; then
    echo "Already up to date with origin/main."
    exit 0
fi

echo "Rebasing $BRANCH onto origin/main ($BEHIND new commits)..."
git rebase origin/main

echo "Force-pushing with lease..."
git push --force-with-lease origin "$BRANCH"

echo "Done. $BRANCH is current with origin/main."
```

### Cleaning up WIP commits before a PR

```bash
#!/usr/bin/env bash
set -euo pipefail

MERGE_BASE=$(git merge-base HEAD origin/main)
COMMIT_COUNT=$(git rev-list --count "$MERGE_BASE"..HEAD)

if [ "$COMMIT_COUNT" -le 1 ]; then
    echo "Only $COMMIT_COUNT commit(s) since main — nothing to clean up."
    exit 0
fi

echo "Opening interactive rebase for $COMMIT_COUNT commits since origin/main..."
git rebase -i "$MERGE_BASE"
```

## Security notes

- **Force-push risks** — a malicious or careless `git push --force` can overwrite production-protecting branches. Combine `--force-with-lease` on the client side with server-side branch protection rules (no force-push to `main`). Defense in depth.
- **Rewritten history hides audit trails** — if your project requires signed commits for compliance, note that rebase invalidates existing GPG signatures because the commit SHAs change. Re-signing after rebase is possible (`git rebase --exec 'git commit --amend --no-edit -S'`) but adds friction.

## Performance notes

- Rebase is **O(n)** in the number of commits being replayed. Each commit is a patch application, so large branches (hundreds of commits) can be slow, especially if conflicts are frequent.
- For very long-lived branches, periodic rebasing is faster than one massive rebase at the end, because each incremental rebase handles fewer new upstream commits.
- `git rerere` (reuse recorded resolution) can automatically resolve conflicts Git has seen you solve before, cutting down repetitive manual work during frequent rebases: `git config --global rerere.enabled true`.

## Common mistakes

1. **Symptom:** Teammate sees dozens of duplicate commits after pulling.
   **Cause:** You rebased a shared branch and force-pushed. They had the old SHAs; Git merged old and new.
   **Fix:** Coordinate with the team. They should `git fetch origin && git reset --hard origin/branch`. Going forward, only rebase branches that belong exclusively to you.

2. **Symptom:** `git push` is rejected after rebase.
   **Cause:** Rebase rewrites SHAs, so local and remote histories diverge. A normal push refuses.
   **Fix:** Use `git push --force-with-lease`. Never plain `--force` unless you're certain no one else pushed to that branch.

3. **Symptom:** Interactive rebase editor shows `noop` or no commits.
   **Cause:** The range you specified (`HEAD~n`) doesn't cover the commits you want, or you're already at the base.
   **Fix:** Double-check the commit count. Use `git log --oneline` to count commits since the divergence point. Prefer `git rebase -i $(git merge-base HEAD main)` for precision.

4. **Symptom:** You lose a commit after aggressive squashing/dropping.
   **Cause:** You dropped or fixup'd the wrong line in the interactive editor.
   **Fix:** The commit still exists in the reflog for ~90 days. Run `git reflog`, find the SHA from before the rebase, and `git switch -c rescue <sha>`.

5. **Symptom:** Conflicts repeat at every commit during rebase.
   **Cause:** Multiple commits in the branch touch the same lines, and each replay triggers the same conflict.
   **Fix:** Enable `git rerere` to auto-record resolutions, or consider squashing related commits first to reduce the replay surface.

## Practice

**Warm-up.** Run `git rebase -i HEAD~3` in a scratch repo. Read the instruction lines, then quit the editor without changes to abort safely.

**Standard.** Create a feature branch with three commits. Meanwhile, add a commit to `main`. Rebase the feature branch onto `main` and verify with `git log --oneline --graph`.

**Bug hunt.** After `git push --force`, your teammate's commits are gone from the remote. Explain why `--force-with-lease` prevents this and demonstrate the difference.

**Stretch.** Make five "wip" commits on a branch. Use interactive rebase to squash them into two meaningful commits with proper messages.

**Stretch++.** Recover a commit that was accidentally dropped during interactive rebase using `git reflog`.

<details><summary>Show solutions</summary>

**Bug hunt.** `--force` unconditionally overwrites the remote ref. `--force-with-lease` compares the remote ref's current value against your local remote-tracking ref. If someone else pushed in between, the remote ref has moved and `--force-with-lease` refuses the push with a clear error. Demo: have two clones of the same repo; push from clone A, then try `--force-with-lease` from clone B without fetching — it fails.

**Stretch++.** `git reflog` shows every HEAD movement. Find the entry from before the rebase (it will say something like `rebase (start): checkout main`). Copy the SHA from the line above that entry. Run `git switch -c rescue <sha>` to create a branch pointing at the pre-rebase state.

</details>

## Quiz

1. After rebasing, the replayed commits have:
    (a) the same SHAs as before (b) new SHAs because the parent changed (c) no SHAs (d) the base branch's SHA

2. Which push flag prevents overwriting a teammate's new commits?
    (a) `--force-with-lease` (b) `--hard` (c) `--keep` (d) `--no-verify`

3. In interactive rebase, `fixup` differs from `squash` in that:
    (a) `fixup` reorders commits (b) `fixup` discards the commit's message (c) `fixup` keeps the message (d) there is no difference

4. Rebasing commits that others have already pulled is:
    (a) encouraged (b) dangerous — it creates diverged histories (c) impossible (d) free

5. `git rebase --abort`:
    (a) cancels the rebase and restores pre-rebase state (b) continues to next commit (c) undoes the last commit (d) resets to origin

**Short answer:**

6. When does rebase produce a cleaner history than merge?
7. Why is `--force-with-lease` safer than `--force`?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-a*

*6. When incorporating upstream changes into a feature branch — it avoids merge commits, keeping the log linear and easier to bisect.*

*7. `--force-with-lease` checks that the remote ref hasn't moved since your last fetch. If someone else pushed, it refuses. `--force` overwrites unconditionally.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-rebase — mini-project](mini-projects/07-rebase-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Rebase replays commits on a new base, creating new SHAs — it rewrites history.
- Interactive rebase (`-i`) lets you squash, reorder, reword, and drop commits before review.
- Never rebase commits others have pulled; use `--force-with-lease` on personal branches.
- Lost commits survive in `git reflog` for ~90 days — almost nothing is truly gone.

## Further reading

- [Pro Git — Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) — covers plain rebase, `--onto`, and the perils of rebasing public work.
- [Atlassian Git Tutorial — Rewriting History](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase) — interactive rebase walkthrough.
- Next: [reset](08-reset.md).
