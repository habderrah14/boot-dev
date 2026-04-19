# Chapter 06 — Merge

> Merging is how parallel work rejoins. The conflict markers you dread are Git's way of saying "I need you to decide."

## Learning objectives

By the end of this chapter you will be able to:

- Perform a fast-forward merge and explain when it applies.
- Perform a three-way merge and read the resulting commit graph.
- Resolve merge conflicts step-by-step, including with `diff3` markers.
- Abort a bad merge cleanly.
- Choose between merge strategies (`ort`, `--squash`, `--ff-only`) based on the situation.

## Prerequisites & recap

- [Branching](05-branching.md) — you can create branches, switch between them, and push with upstream tracking.
- [Config](04-config.md) — you've set `merge.conflictStyle=diff3` for better conflict markers.

You have two branches that diverged. Now you need to bring them back together. That's what merge does — and understanding the two modes (fast-forward and three-way) removes all the mystery.

## The simple version

When you run `git merge feat` on `main`, Git asks one question: has `main` moved since `feat` branched off? If not, Git simply slides `main`'s pointer forward to the tip of `feat` — a fast-forward. No new commit is created because no actual "merging" was needed.

If both branches have new commits, Git performs a three-way merge: it finds the common ancestor, compares what each branch changed, and combines the results into a new merge commit with two parents. When both branches changed the same lines, Git can't decide for you — it marks the file with conflict markers and asks you to resolve it.

## In plain terms (newbie lane)

This chapter is really about **Merge**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Fast-forward vs. three-way merge:

```
FAST-FORWARD (main has not moved):

  before:   main         feat
              │            │
              ▼            ▼
        A ◄── B      C ◄── D
              └──────┘

  after:    main = feat
              │
              ▼
        A ◄── B ◄── C ◄── D


THREE-WAY MERGE (both branches moved):

  before:   main              feat
              │                 │
              ▼                 ▼
        A ◄── B ◄── E    C ◄── D
              └──────────┘

  after:          main
                    │
                    ▼
        A ◄── B ◄── E ◄── M    (merge commit)
              │            │
              └── C ◄── D ─┘
```

## Concept deep-dive

### Fast-forward merge

If `main` hasn't moved since `feat` was created, merging is trivial — Git advances `main`'s pointer to `feat`'s tip:

```bash
git switch main
git merge feat              # fast-forward: no merge commit
git log --oneline --graph   # linear history
```

You can enforce fast-forward-only merges to keep history strictly linear:

```bash
git merge --ff-only feat    # refuses if fast-forward isn't possible
```

This is useful when you want to guarantee a clean, linear history — if the merge can't fast-forward, you know you need to rebase first.

### Three-way merge

When both branches have new commits, Git finds their **merge base** (the most recent common ancestor), compares each branch's changes against the base, and combines them:

```bash
git switch main
git merge feat/docs         # three-way merge → creates merge commit M
git log --graph --oneline   # shows the two-parent topology
```

The merge commit `M` has two parents — the tip of `main` and the tip of `feat/docs`. This preserves the full history of both branches.

### Merge strategies

| Strategy | When | Trade-off |
|----------|------|-----------|
| `ort` (default since 2.33) | Standard three-way merge | Robust, handles renames well |
| `--ff-only` | Enforce linear history | Fails if branches diverged |
| `--squash` | Condense feature branch into one diff | Loses individual commit history; no merge commit |
| `--no-ff` | Force a merge commit even on fast-forward | Makes branch topology visible in the log |

`--squash` deserves attention: it copies all changes from the feature branch into the index as a single staged diff, but creates no merge commit and records no parent relationship. This is popular in PR-based workflows where you want a single commit per feature in `main`, but it means the branch history is lost — `git branch -d feat` will warn "not fully merged" because there's no merge commit linking them.

### Conflict markers

When both branches changed the same region of a file, Git writes conflict markers:

```
<<<<<<< HEAD
Hello, main.
=======
Hello, feature.
>>>>>>> feat
```

With `merge.conflictStyle=diff3` (which you should have set in [Config](04-config.md)), you also see the common ancestor:

```
<<<<<<< HEAD
Hello, main.
||||||| merged common ancestors
Hello.
=======
Hello, feature.
>>>>>>> feat
```

The ancestor is invaluable — it tells you what the original text was, so you can understand what each side *intended* to change, rather than guessing.

### Resolving conflicts

The process is always the same:

1. Open the conflicted file in your editor.
2. Find the markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Decide what the correct result should be — often a combination of both sides.
4. Delete all marker lines. The file should now be valid code/text.
5. Stage the resolution: `git add <file>`.
6. Complete the merge: `git commit` (Git pre-fills the merge message).

For multiple conflicted files, repeat steps 1-5 for each, then commit once.

### Aborting a merge

If you realize mid-conflict that you're not ready to merge, or that you're merging the wrong branch:

```bash
git merge --abort             # restores the pre-merge state completely
```

This is always safe. Your working tree goes back to exactly how it was before `git merge`. Use it without hesitation — an aborted merge is better than a bad resolution.

### The merge checklist

Before merging:

- `git status` — make sure your working tree is clean. Merging with uncommitted changes leads to confusion.
- You're on the **target** branch (usually `main`). The convention is `git switch main; git merge feat`, not the other way.
- Pull the latest `main` first: `git pull`.

After merging:

- Run your test suite. A clean merge is not the same as a correct merge — two changes can merge without conflicts and still break the code.
- `git log --graph --oneline` to verify the topology.

## Why these design choices

**Three-way merge over two-way.** A two-way merge (comparing just "ours" vs. "theirs") can't tell whether a difference is an addition or a deletion. The three-way merge uses the common ancestor to determine intent: if the ancestor had line X, and "ours" removed it while "theirs" kept it, the removal wins. Without the ancestor, you'd get false conflicts on every difference.

**Merge commits preserve topology.** A fast-forward gives you clean linear history, but you lose the information that a feature was developed on a branch. `--no-ff` forces a merge commit even when fast-forward is possible, which makes the branch structure visible in `git log --graph`. Teams that value traceability prefer this; teams that value simplicity prefer fast-forward.

**`--squash` exists for a reason.** In large codebases, individual feature-branch commits ("WIP", "fix typo", "actually fix it") add noise to `main`'s history. Squash merge gives you one clean commit per feature. The trade-off is that `git bisect` can't drill into the individual steps if a bug is introduced.

**`diff3` as default conflict style.** The standard two-section marker (`ours` / `theirs`) forces you to read both sides and reconstruct what was there before. `diff3` shows the ancestor directly, making resolution faster and less error-prone. There's no downside — it's strictly more information.

## Production-quality code

### Clean merge workflow

```bash
git switch main
git pull                          # make sure main is current

git merge feat/login
# If fast-forward: done.
# If three-way: Git opens your editor for the merge message.

git log --graph --oneline -10     # verify topology
# run your test suite here
git push
```

### Conflict resolution workflow

```bash
git switch main
git merge feat/docs
# CONFLICT (content): Merge conflict in README.md

git status                        # lists conflicted files under "Unmerged paths"
$EDITOR README.md                 # open, resolve, delete markers

git diff README.md                # review your resolution
git add README.md                 # mark as resolved
git merge --continue              # same as git commit; completes the merge
```

### Squash merge for PR-based workflow

```bash
git switch main
git pull

git merge --squash feat/signup-flow
# all changes staged as a single diff, no commit yet

git commit -m "feat: add signup flow with email validation"
git push

git branch -D feat/signup-flow    # -D required: no merge commit means git sees it as unmerged
```

## Security notes

- **Conflict markers in production** are a real threat. If a developer commits a file with unresolved `<<<<<<<` markers, the code is broken — and in languages like Python or YAML, it may fail silently or be parsed in unexpected ways. Add a pre-commit hook that rejects files containing conflict markers:
  ```bash
  git diff --cached --name-only | xargs grep -l '^<<<<<<<' && exit 1
  ```
- **Merge of untrusted branches.** If you merge a branch from an untrusted contributor, the merge commit will carry your name as committer. Review the diff carefully — a malicious contributor could hide changes (e.g., a backdoor in a minified file) among legitimate edits.
- **`rerere` replay.** When `rerere.enabled=true`, Git caches conflict resolutions. If an attacker can influence the resolution cache (unlikely in practice, but possible on shared machines), they could cause automatic mis-resolutions.

## Performance notes

- **Fast-forward merges** are O(1) — Git just updates a pointer. No file operations, no diff computation.
- **Three-way merges** compute diffs between three trees. The cost is O(changed files × changed lines). For typical feature branches touching a few files, this is milliseconds. For branches that diverged across thousands of files, expect seconds.
- **`git merge-base`** finding the common ancestor traverses the commit DAG. On repos with a commit-graph file, this is near-instant. Without one, it's O(commit history depth) — noticeable on repos with 100k+ commits.
- **Conflict resolution** itself has no performance cost — it's a human activity. But the longer a branch lives without merging from `main`, the more conflicts accumulate, making resolution slower and riskier. Merge `main` into long-lived branches regularly.

## Common mistakes

1. **Symptom:** Conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) end up committed and pushed.
   **Cause:** The developer committed the file without actually resolving the conflict.
   **Fix:** Edit the file to remove markers, `git add`, `git commit --amend`. Prevent recurrence with a pre-commit hook that greps for markers.

2. **Symptom:** You accepted "ours" or "theirs" everywhere and lost the other side's changes.
   **Cause:** Blindly choosing one side during conflict resolution without understanding what each changed.
   **Fix:** `git reflog` to find the pre-merge state, `git reset --hard <sha>`, and redo the merge carefully. Use `diff3` to see the ancestor and understand intent.

3. **Symptom:** Tests pass on both branches independently but fail after merging.
   **Cause:** A "semantic conflict" — two changes that merge cleanly at the text level but break at the logic level (e.g., one branch renames a function, the other adds a call to the old name).
   **Fix:** Always run the full test suite after merging. This is why CI systems run tests on the merge result, not just on each branch.

4. **Symptom:** `git branch -d feat` says "not fully merged" after a squash merge.
   **Cause:** `--squash` doesn't create a merge commit, so Git can't tell that `feat`'s changes are on `main`.
   **Fix:** Use `git branch -D feat` to force-delete. This is expected behavior with squash merges.

5. **Symptom:** You merged `feat` into `main` when you meant to merge `main` into `feat` (or vice versa).
   **Cause:** You were on the wrong branch when you ran `git merge`.
   **Fix:** If you haven't pushed, `git reset --hard HEAD~1` undoes the merge commit. If you have pushed, `git revert -m 1 HEAD` creates a new commit that reverses the merge.

## Practice

1. **Warm-up.** Create a feature branch, make a commit, switch to `main`, and fast-forward merge. Verify no merge commit was created with `git log --oneline`.
2. **Standard.** Create a conflict deliberately (edit the same line on two branches), then resolve it and complete the merge.
3. **Bug hunt.** A teammate reports that conflict markers landed in the production build. What went wrong, and describe two measures that prevent this from happening again.
4. **Stretch.** Enable `merge.conflictStyle=diff3`, redo exercise 2, and explain how the three-section marker helped your resolution.
5. **Stretch++.** Perform a `--squash` merge, inspect the history with `git log --graph`, and write a paragraph explaining when squash merge is appropriate vs. a regular merge.

<details><summary>Show solutions</summary>

1. ```bash
   git switch -c feat/fast
   echo "change" >> file.txt && git add file.txt && git commit -m "feat change"
   git switch main
   git merge feat/fast          # fast-forward
   git log --oneline            # linear, no merge commit
   git branch -d feat/fast
   ```

2. ```bash
   echo "line from main" > conflict.txt && git add conflict.txt && git commit -m "base"
   git switch -c feat/conflict
   echo "line from feat" > conflict.txt && git add conflict.txt && git commit -m "feat edit"
   git switch main
   echo "line from main v2" > conflict.txt && git add conflict.txt && git commit -m "main edit"
   git merge feat/conflict       # CONFLICT
   $EDITOR conflict.txt          # resolve: delete markers, write final text
   git add conflict.txt
   git commit                    # completes merge
   ```

3. A commit containing `<<<<<<<` markers was pushed without review or testing. Prevention: (a) a pre-commit hook that greps staged files for conflict markers and exits non-zero if found, (b) CI that runs tests on the merge commit — tests would fail on invalid syntax.

4. With `diff3`, the conflict shows three sections: HEAD, common ancestor, and the incoming branch. The ancestor tells you what the original text was, so you can see that main changed "Hello" to "Hello, main" and feat changed "Hello" to "Hello, feature" — letting you produce "Hello, main and feature" confidently.

5. ```bash
   git switch main
   git merge --squash feat/signup
   git commit -m "feat: add signup flow"
   git log --graph --oneline    # no merge commit, just a single new commit
   ```
   Squash merge is appropriate when individual branch commits are noisy ("WIP", "fix typo") and the team values a clean main history with one commit per feature. It's inappropriate when you need `git bisect` to drill into individual changes within the feature, or when you want the branch topology preserved in the log.

</details>

## Quiz

1. A fast-forward merge:
    (a) Creates a merge commit (b) Just moves the branch pointer forward (c) Squashes commits (d) Rebases

2. The default merge strategy in modern Git (2.33+) is:
    (a) recursive (b) ort (c) octopus (d) resolve

3. Merge conflict markers include:
    (a) Only `<<<<<<<` and `>>>>>>>` (b) Also `=======` (c) Also `|||||||` when using diff3 (d) All of the above depending on config

4. After resolving a conflict, the correct next steps are:
    (a) `git commit --amend` (b) `git add <file>` then `git commit` (c) `git push` directly (d) `git checkout .`

5. `git merge --abort`:
    (a) Discards the merge attempt and restores pre-merge state (b) Keeps partial progress (c) Deletes the source branch (d) Forces a fast-forward

**Short answer:**

6. How does `diff3` conflict style help with resolution compared to the default?
7. When is `--squash` preferable to a normal merge, and what's the downside?

*Answers: 1-b, 2-b, 3-d, 4-b, 5-a*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-merge — mini-project](mini-projects/06-merge-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Fast-forward merges advance a pointer when the target branch hasn't moved — no merge commit, linear history.
- Three-way merges find the common ancestor and produce a merge commit with two parents when both branches have diverged.
- Conflicts are Git asking a question only you can answer — use `diff3` to see the ancestor and resolve with confidence.
- `git merge --abort` is always safe — never hesitate to back out of a bad merge.

## Further reading

- [Pro Git](https://git-scm.com/book), chapter 3 — branching and merging.
- `man git-merge` — the complete command reference.
- Next: [Rebase](07-rebase.md).
