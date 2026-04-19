# Chapter 08 — Reset

> `git reset` is a magic wand that can also cut off your hand. This chapter is the safety briefing.

## Learning objectives

By the end of this chapter you will be able to:

- Distinguish `--soft`, `--mixed`, and `--hard` reset modes.
- Undo a commit, a staged file, or a working-tree change.
- Recover from a bad reset with `git reflog`.
- Pick `revert` over `reset` on shared history.

## Prerequisites & recap

- [Repositories](02-repositories.md) — you know the three areas: working tree, index (staging area), and committed history.
- [Rebase](07-rebase.md) — you understand that rewriting history changes SHAs.

Git's three areas are a pipeline: working tree → index → commit. `reset` walks backward along that pipeline to different degrees depending on the mode you choose. Understanding which area each mode touches is the whole game.

## The simple version

Think of `git reset` as a "move the branch pointer" command. You tell Git: "pretend my branch is at *this* commit instead of where it is now." The three modes control how much collateral cleanup happens. `--soft` only moves the pointer (your staged files and working directory stay exactly as they are). `--mixed` moves the pointer *and* clears the staging area (but your files on disk are untouched). `--hard` moves the pointer, clears the staging area, *and* overwrites your files on disk — anything uncommitted is gone.

If you need to undo something on a branch other people are using, `reset` is the wrong tool. Use `revert` instead — it creates a new commit that reverses the damage, keeping the shared history intact.

## In plain terms (newbie lane)

This chapter is really about **Reset**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How each reset mode affects the three areas when moving HEAD back one commit:

```
             Branch ptr    Index (staging)    Working tree
             ----------    ---------------    ------------
--soft          moved        unchanged          unchanged
--mixed         moved        reset to commit    unchanged
--hard          moved        reset to commit    OVERWRITTEN

Before:   A ── B ── C  (HEAD on C)
After:    A ── B  (HEAD on B)
                \
                 C still exists in reflog for ~90 days
```

## Concept deep-dive

### The three modes in detail

`git reset <mode> <commit>` always moves the current branch pointer to `<commit>`. The modes differ in side effects:

| Mode | Branch pointer | Index | Working tree | When to use |
|---|---|---|---|---|
| `--soft` | moved | unchanged | unchanged | Undo a commit but keep everything staged for a redo |
| `--mixed` (default) | moved | reset | unchanged | Undo a commit and unstage, but keep files on disk |
| `--hard` | moved | reset | **overwritten** | Throw away everything and go back to a known state |

**Why three modes?** Because "undo" means different things in different situations. Sometimes you committed too early and want to amend the message (soft). Sometimes you staged the wrong files and want to restage from scratch (mixed). Sometimes you want to nuke a broken experiment entirely (hard). A single command with three modes covers all three without requiring three separate commands.

### Common undo recipes

**Unstage a file (keep the working-tree version):**

```bash
git reset HEAD path/to/file
```

Modern Git equivalent: `git restore --staged path/to/file`. Same result, narrower scope, harder to misuse.

**Undo the last commit, keep changes staged (ready to re-commit):**

```bash
git reset --soft HEAD~1
```

**Undo the last commit, unstage changes (keep them in working tree for editing):**

```bash
git reset HEAD~1          # --mixed is the default
```

**Discard everything and return to the last commit (destructive):**

```bash
git reset --hard HEAD
```

**Roll back three commits entirely (destructive):**

```bash
git reset --hard HEAD~3
```

### `restore` and `switch` — the narrower, safer alternatives

Git introduced `restore` and `switch` to decompose `checkout` and `reset` into focused commands that are harder to misuse:

- `git restore <file>` — discard unstaged working-tree changes for a file.
- `git restore --staged <file>` — unstage a file (equivalent to `git reset HEAD <file>`).
- `git restore --source=<commit> <file>` — pull a specific version of a file from any commit without moving HEAD.

**Why these exist:** `git reset` does too many things. A developer meaning "unstage this file" might accidentally type `git reset --hard` and lose work. `restore` can't move the branch pointer, so it's a safer default for file-level operations.

### Reset vs. revert

This is a critical distinction for teamwork:

- **`reset`** rewrites history by moving the branch pointer backward. Commits "after" the new pointer become unreachable (though they persist in the reflog). If you've already pushed those commits, resetting requires a force-push — and that's dangerous on shared branches.

- **`revert`** creates a *new* commit that applies the inverse of a prior commit. History only moves forward. It's safe on any branch, shared or private.

```bash
git revert <sha>              # create a commit undoing <sha>
git revert HEAD               # undo the most recent commit
git revert --no-commit A B C  # stage inverse of multiple commits without committing yet
```

**When to use which:** if the commit is local and unpushed, `reset` is fine. If it's been pushed and others might have pulled it, `revert`.

### `git reflog` — your safety net

Git records every movement of HEAD — commits, resets, rebases, checkouts — in the reflog. Entries survive for ~90 days by default.

```bash
git reflog
# 0a1b2c3 HEAD@{0}: reset: moving to HEAD~3
# d4e5f6a HEAD@{1}: commit: add payment processing
# 7b8c9d0 HEAD@{2}: commit: add user model
```

To recover from a bad `--hard` reset:

```bash
git reflog                    # find the SHA from before the reset
git reset --hard d4e5f6a      # go back to that state
# or, safer:
git switch -c rescue d4e5f6a  # create a rescue branch without overwriting current
```

Almost nothing is ever truly lost in Git — as long as it was committed at least once and you act within 90 days.

### `reset` on paths vs. commits

There's an important subtlety: `git reset <file>` doesn't move the branch pointer at all. It only updates the index for that file to match HEAD. This is purely an unstaging operation. `git reset <commit>` (without a path) moves the branch pointer. These are two different behaviors behind the same command — another reason the Git team created `restore` as a clearer alternative.

## Why these design choices

**Why does `--hard` not prompt for confirmation?** Git follows the Unix philosophy of trusting the user. The reflog exists as the safety net, and uncommitted changes are considered ephemeral by design. If you want guardrails, use `restore` for file-level operations and reserve `reset` for branch-level rewinding.

**Why does `revert` create a new commit instead of erasing the old one?** Because Git's data model is append-only by design. Erasing commits from shared history causes the same problems as rebasing shared branches — diverged histories for every collaborator. A revert commit is explicit: everyone can see what was undone and why.

**Why keep both `reset` and `restore`?** Backward compatibility. Millions of scripts and muscle-memory patterns depend on `reset`. `restore` is the recommended path for new users, but `reset` isn't going anywhere.

## Production-quality code

### Safe undo of the last commit (script)

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ -z "$(git log --oneline -1 2>/dev/null)" ]; then
    echo "ERROR: No commits to undo." >&2
    exit 1
fi

LAST_MSG=$(git log -1 --format='%s')
echo "Undoing commit: \"$LAST_MSG\""

read -rp "Keep changes staged (soft) or unstaged (mixed)? [s/m]: " MODE

case "$MODE" in
    s|S)
        git reset --soft HEAD~1
        echo "Commit undone. Changes are staged — ready to re-commit."
        ;;
    m|M)
        git reset HEAD~1
        echo "Commit undone. Changes are in working tree — edit and re-stage."
        ;;
    *)
        echo "ERROR: Expected 's' or 'm'." >&2
        exit 1
        ;;
esac

git status --short
```

### Revert a bad deploy on shared branch

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <commit-sha>" >&2
    echo "Reverts the given commit on the current branch and pushes." >&2
    exit 1
fi

SHA="$1"

if ! git cat-file -e "$SHA" 2>/dev/null; then
    echo "ERROR: Commit $SHA does not exist." >&2
    exit 1
fi

SUBJECT=$(git log -1 --format='%s' "$SHA")
echo "Reverting: \"$SUBJECT\" ($SHA)"

git revert --no-edit "$SHA"
echo "Revert committed locally. Pushing..."
git push
echo "Done. The revert is live."
```

## Security notes

- **`--hard` destroys uncommitted work** — if an attacker or a careless script runs `git reset --hard` in a production checkout (e.g., a deploy directory), any in-flight changes are gone. Protect deploy directories with filesystem permissions and avoid running arbitrary scripts in them.
- **Resetting pushed commits then force-pushing** can erase audit-relevant history. In regulated environments, use `revert` to keep an explicit record of what was undone and why. Some compliance frameworks require a complete, unaltered commit history.
- **Reflog is local only** — it's not pushed to remotes. If someone compromises a remote and force-pushes, the reflog on other developers' machines is the only recovery source. Server-side backups and branch protection rules are essential complements.

## Performance notes

- `reset --soft` is essentially free — it only updates one ref pointer.
- `reset --mixed` updates the ref and rewrites the index, which is **O(n)** in the number of tracked files.
- `reset --hard` does everything `--mixed` does plus writes files to disk, so cost scales with repository size. On repos with hundreds of thousands of files, this can take seconds.
- `revert` is a commit operation — it computes a reverse diff and writes a new commit. Cost is proportional to the size of the diff being inverted, not the size of the repo.

## Common mistakes

1. **Symptom:** You ran `git reset --hard` and your uncommitted work is gone.
   **Cause:** `--hard` overwrites the working tree without prompting. If the work was never committed, it's not in the reflog.
   **Fix:** If you staged the files first (`git add`), some data survives in `.git/objects` and can be recovered with `git fsck --lost-found`. If you never staged, the data is genuinely gone. Prevention: commit early and often, even as "wip" commits.

2. **Symptom:** You reset a pushed commit and now `git push` is rejected.
   **Cause:** Reset moved your branch pointer behind the remote. A normal push can't fast-forward.
   **Fix:** On a personal branch, `git push --force-with-lease`. On a shared branch, **don't force-push** — use `git revert` instead and push normally.

3. **Symptom:** Teammate's work vanishes after you reset and force-pushed a shared branch.
   **Cause:** Your force-push replaced the remote history. Teammates who already pulled the old history now have diverged state.
   **Fix:** Have teammates `git fetch && git reset --hard origin/branch`. Going forward, use `revert` on shared branches and enable branch protection to block force-pushes.

4. **Symptom:** `git reset HEAD~1` doesn't seem to undo anything visible.
   **Cause:** `--mixed` (the default) unstages changes but leaves files in the working tree. If you expected files to disappear, you wanted `--hard`. If you expected changes to stay staged, you wanted `--soft`.
   **Fix:** Choose the mode deliberately. Remember: soft = keep staged, mixed = keep on disk, hard = discard.

5. **Symptom:** You used `git reset <file>` but HEAD didn't move.
   **Cause:** Path-based reset only updates the index. It doesn't move the branch pointer.
   **Fix:** This is correct behavior. If you want to move the branch pointer, omit the file path. If you just want to unstage, `git restore --staged <file>` is clearer.

## Practice

**Warm-up.** Stage a file with `git add`, then unstage it using `git reset HEAD <file>`. Verify with `git status`.

**Standard.** Make a commit, then undo it with `git reset --soft HEAD~1`. Confirm the changes are still staged. Re-commit with a better message.

**Bug hunt.** You ran `git reset --hard HEAD~3` and lost three commits. Recover all of them using `git reflog` and a rescue branch.

**Stretch.** Revert a merge commit on `main` (hint: `git revert -m 1 <merge-sha>`). Explain what `-m 1` means.

**Stretch++.** Compare the commit graph (using `git log --oneline --graph`) before and after using `revert` vs. `reset` on the same commit. Document the differences.

<details><summary>Show solutions</summary>

**Bug hunt.** Run `git reflog` and find the SHA from before the reset (the line that says `commit: ...` for the most recent of the three lost commits). Run `git switch -c rescue <sha>` to create a branch at that point. All three commits are now accessible on the rescue branch.

**Stretch.** `git revert -m 1 <merge-sha>` — the `-m 1` flag tells Git which parent of the merge to treat as the "mainline." Parent 1 is the branch you merged *into* (usually `main`). The revert undoes the changes brought in by the merge while keeping the mainline's history. Without `-m`, Git doesn't know which side to invert and refuses.

</details>

## Quiz

1. `git reset --hard HEAD`:
    (a) is the safest mode (b) discards working tree and index changes (c) only moves the branch pointer (d) creates a revert commit

2. To undo a commit but keep changes staged:
    (a) `git reset --soft HEAD~1` (b) `git reset --hard HEAD~1` (c) `git revert HEAD` (d) `git restore HEAD~1`

3. Which command is safe to use on shared history?
    (a) `git reset --hard` (b) `git reset --mixed` (c) `git revert` (d) `git rebase -i`

4. `git reflog` keeps entries for approximately:
    (a) forever (b) 90 days by default (c) 24 hours (d) only until the next push

5. `git restore --staged <file>` is equivalent to:
    (a) `git reset HEAD <file>` (b) `git reset --hard <file>` (c) `git checkout <file>` (d) `git revert <file>`

**Short answer:**

6. Explain `reset` vs. `revert` in one sentence each.
7. When is `--hard` the right choice?

*Answers: 1-b, 2-a, 3-c, 4-b, 5-a*

*6. `reset` moves the branch pointer backward, erasing commits from the branch's history. `revert` creates a new forward commit that undoes a prior commit's changes.*

*7. When you want to throw away all local changes and return to a known clean state — typically on a personal branch or when you're sure nothing uncommitted is worth keeping.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-reset — mini-project](mini-projects/08-reset-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `reset` moves the branch pointer; `--soft`/`--mixed`/`--hard` control how much of the index and working tree are also reset.
- `revert` is the safe alternative for shared history — it creates a new commit that undoes a prior one.
- `reflog` is your personal time machine — nearly anything committed can be recovered for ~90 days.
- Prefer `git restore` for file-level operations; it's narrower and harder to misuse than `reset`.

## Further reading

- [Pro Git — Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified) — the definitive walkthrough of reset's three modes with diagrams.
- [Git documentation — git-reset](https://git-scm.com/docs/git-reset) — the full reference.
- Next: [remote](09-remote.md).
