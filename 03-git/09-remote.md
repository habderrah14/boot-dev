# Chapter 09 — Remote

> A remote is another repository Git knows about. Usually that's GitHub, but it can also be another folder on the same disk.

## Learning objectives

By the end of this chapter you will be able to:

- Add, remove, and inspect remotes.
- Fetch, pull, and push — and explain when to use each.
- Understand remote-tracking branches and "ahead/behind" counts.
- Work with multiple remotes (origin + upstream) in an open-source workflow.

## Prerequisites & recap

- [Branching](05-branching.md) — you know how branches work as movable pointers to commits.
- [Setup](01-setup.md) — you have Git configured with SSH or HTTPS credentials.
- [Reset](08-reset.md) — you understand that force-pushing rewrites remote history.

So far, everything you've done has been local — commits, branches, merges, rebases, all living on your machine. This chapter connects your local repository to the outside world. A remote is just a named URL pointing to another Git repository. The most common remote is `origin` (your primary server copy), but you can have as many as you like.

## The simple version

A remote is a bookmark to another copy of your repository, usually hosted on a server like GitHub. When you `clone` a repo, Git automatically names that server `origin`. From there, three commands handle all traffic: `fetch` downloads new commits from the remote without touching your branches, `pull` does a fetch and then merges (or rebases) the new commits into your current branch, and `push` uploads your local commits to the remote.

The key insight is that Git never talks to the remote automatically. Every sync is explicit — you choose when to download, when to integrate, and when to upload. This is a feature, not a limitation. It means you always have full control over your local state, and network failures never corrupt your work.

## In plain terms (newbie lane)

This chapter is really about **Remote**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The relationship between your local repo, remote-tracking refs, and the remote server:

```
+--------------+      fetch       +-------------------+
|              | <--------------- |                   |
|   Remote     |                  |  Remote-tracking  |
|   server     |      push       |  refs (local)     |
|  (origin)    | <--------------- |  origin/main      |
|              |                  |  origin/feat      |
+--------------+                  +-------------------+
                                          |
                                   merge / rebase
                                          |
                                          v
                                  +-------------------+
                                  |  Local branches   |
                                  |  main, feat       |
                                  +-------------------+
```

## Concept deep-dive

### Remotes are named URLs

A remote is nothing more than a name (like `origin`) mapped to a URL. You can inspect, add, rename, and remove them:

```bash
git remote -v
# origin  git@github.com:alice/repo.git (fetch)
# origin  git@github.com:alice/repo.git (push)

git remote add upstream git@github.com:acme/repo.git
git remote rename origin github
git remote remove old-remote
```

**Why named instead of bare URLs?** Because you'll type them constantly. `git push origin main` is easier than `git push git@github.com:alice/repo.git main`. The name also appears in remote-tracking branch names (`origin/main`), tying everything together.

### Fetch vs. pull — and why fetch is safer

`git fetch` downloads new objects (commits, trees, blobs) from the remote and updates your remote-tracking references (`origin/main`, `origin/feat`, etc.). It never touches your local branches or working tree. It's always safe.

`git pull` is `fetch` + `merge` (or `fetch` + `rebase` if you've set `pull.rebase = true`). It modifies your current branch. That means it can trigger merge conflicts if you have local commits.

Prefer `fetch` + deliberate integration:

```bash
git fetch origin

# See what's new
git log --oneline origin/main..main     # commits you have that origin doesn't
git log --oneline main..origin/main     # commits origin has that you don't

# Integrate when ready
git merge origin/main                   # or: git rebase origin/main
```

This two-step approach gives you a chance to review upstream changes before they hit your branch. `pull` combines these steps — convenient, but you lose the inspection window.

### Push

Push uploads your local commits to the remote and fast-forwards the remote branch:

```bash
git push                          # push current branch to its upstream
git push -u origin feat           # first push: set upstream tracking to origin/feat
git push origin HEAD              # push current HEAD to same-named remote branch
git push --delete origin feat     # delete a remote branch
```

**Setting upstream with `-u`:** the first time you push a new branch, use `-u` (short for `--set-upstream`). This tells Git which remote branch to track, so future `git push` and `git pull` commands work without extra arguments.

**Force-push safety:**

```bash
git push --force-with-lease       # force-push only if remote hasn't moved since last fetch
```

Never use bare `--force` on shared branches. `--force-with-lease` is a compare-and-swap: it checks that the remote ref is where you think it is before overwriting. See [ch. 07](07-rebase.md) for details.

**Pushing tags:**

```bash
git push --follow-tags            # push annotated tags along with commits
git push origin v1.0.0            # push a specific tag
```

### Remote-tracking branches

`origin/main` is a *local* reference that mirrors the last-known state of `main` on the `origin` remote. It updates only on `fetch` or `push` — never automatically in the background.

```bash
git branch -vv
# * main   0d7a9b3 [origin/main: ahead 2, behind 1] add readme
#   feat   a1b2c3d [origin/feat] add login
```

"Ahead 2, behind 1" means your local `main` has 2 commits that `origin/main` doesn't, and `origin/main` has 1 commit that your local `main` doesn't. This is exactly when you need to integrate before pushing (or force-push if you rebased).

### Open-source workflow: origin + upstream

When you fork a repository, you end up with two remotes:

- **`origin`** — your fork on GitHub (you have push access).
- **`upstream`** — the original project (you can only fetch, unless you're a maintainer).

```bash
git clone git@github.com:you/repo.git
cd repo
git remote add upstream git@github.com:acme/repo.git

# Stay current with the original project
git fetch upstream
git rebase upstream/main
git push --force-with-lease origin main    # update your fork
```

This keeps your fork's `main` in sync with the original. Feature branches go to `origin`, and PRs target `upstream`.

### Multiple remotes beyond open-source

You're not limited to two remotes. Some setups use:

- `origin` for the primary host (GitHub).
- `deploy` pointing to a production server.
- `backup` pointing to a secondary host (GitLab, Bitbucket).

Each remote is independent — you fetch from and push to them individually.

## Why these design choices

**Why doesn't Git auto-sync with the remote?** Because Git was designed for distributed, offline-first workflows. Linus Torvalds built it for Linux kernel development, where developers might be offline for days. Explicit sync means you're never surprised by someone else's changes appearing mid-work, and you can work entirely offline for as long as you want.

**Why separate `fetch` and `pull`?** `fetch` is the primitive; `pull` is the convenience. Separating them gives you an inspection point. In practice, experienced developers tend to `fetch` + `rebase` rather than `pull`, because they want to see upstream changes before integrating.

**Why `--force-with-lease` instead of `--force`?** Because distributed systems need optimistic concurrency control. `--force-with-lease` is Git's version of a compare-and-swap: "update the ref only if it still equals the value I last saw." This prevents blind overwrites when multiple people push to the same branch.

## Production-quality code

### Publishing a new repository

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <repo-name> [--private]" >&2
    exit 1
fi

REPO_NAME="$1"
VISIBILITY="--public"
if [ "${2:-}" = "--private" ]; then
    VISIBILITY="--private"
fi

if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit"
fi

if ! command -v gh &>/dev/null; then
    echo "ERROR: GitHub CLI (gh) is required. Install from https://cli.github.com" >&2
    exit 1
fi

gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push

echo "Repository created and pushed: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
```

### Syncing a fork with upstream

```bash
#!/usr/bin/env bash
set -euo pipefail

if ! git remote get-url upstream &>/dev/null; then
    echo "ERROR: No 'upstream' remote configured." >&2
    echo "Add one with: git remote add upstream <url>" >&2
    exit 1
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Fetching upstream..."
git fetch upstream

BEHIND=$(git rev-list --count HEAD..upstream/main)
if [ "$BEHIND" -eq 0 ]; then
    echo "Already up to date with upstream/main."
    exit 0
fi

echo "Rebasing $BRANCH onto upstream/main ($BEHIND new commits)..."
git rebase upstream/main

echo "Pushing to origin..."
git push --force-with-lease origin "$BRANCH"

echo "Done. $BRANCH is synced with upstream/main."
```

### Diagnosing diverged history

```bash
#!/usr/bin/env bash
set -euo pipefail

git fetch origin

AHEAD=$(git rev-list --count origin/main..main)
BEHIND=$(git rev-list --count main..origin/main)

echo "Local main vs. origin/main:"
echo "  Ahead:  $AHEAD commit(s)"
echo "  Behind: $BEHIND commit(s)"

if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -gt 0 ]; then
    echo ""
    echo "History has DIVERGED. Options:"
    echo "  1. git rebase origin/main   (linear history, then force-push)"
    echo "  2. git merge origin/main    (merge commit, normal push)"
elif [ "$BEHIND" -gt 0 ]; then
    echo ""
    echo "You're behind. Run: git merge origin/main"
elif [ "$AHEAD" -gt 0 ]; then
    echo ""
    echo "You're ahead. Run: git push"
else
    echo ""
    echo "Fully synchronized."
fi
```

## Security notes

- **SSH vs. HTTPS authentication** — SSH keys are generally preferred for push access because they don't expire like personal access tokens (PATs) and aren't entered interactively. Store SSH keys with a passphrase and use `ssh-agent` to avoid retyping it. If using HTTPS, use a credential helper (`git config --global credential.helper store` or OS keychain integration) — never paste tokens in URLs, as they'll be visible in `git remote -v` and shell history.
- **Leaking credentials in remote URLs** — `https://user:token@github.com/...` embeds the token in `.git/config`. Anyone with read access to the repo directory can extract it. Use credential helpers instead.
- **Malicious upstream rebases** — if you blindly `fetch` + `reset --hard origin/main`, an attacker who compromised the remote could inject arbitrary code. Review `git log origin/main..` after fetching to see what changed before integrating.

## Performance notes

- `git fetch` is incremental — Git only downloads objects it doesn't already have, using pack negotiation. The cost is proportional to the number of new objects, not the total repo size.
- `git clone` of a large repository can be expensive. Use `--depth 1` for a shallow clone (only the latest commit) when you don't need full history. Use `--filter=blob:none` for a blobless clone (downloads blobs on demand).
- Push performance scales with the number and size of new objects being uploaded. Large binary files (media, datasets) should be managed with Git LFS to avoid bloating the pack file.
- Remote operations are network-bound. On slow connections, `fetch` frequently in small increments rather than waiting for a massive sync.

## Common mistakes

1. **Symptom:** `git pull` fails with "refusing to merge unrelated histories."
   **Cause:** The local and remote repositories were initialized independently (e.g., `git init` locally, then adding a remote that has its own initial commit).
   **Fix:** `git pull --allow-unrelated-histories` to perform a one-time merge of the two root commits. Going forward, always `clone` from the remote or push to an empty remote.

2. **Symptom:** `git push` says "Updates were rejected because the remote contains work that you do not have locally."
   **Cause:** Someone else pushed to the same branch since your last fetch. Your push can't fast-forward.
   **Fix:** `git fetch origin && git merge origin/<branch>` (or `rebase`), then push again. Don't force-push unless you intentionally rebased.

3. **Symptom:** You forgot `-u` on the first push and now `git push` asks "Where do you want to push?"
   **Cause:** No upstream tracking is configured for the branch.
   **Fix:** `git push -u origin <branch>`. After this, plain `git push` works.

4. **Symptom:** `git pull` with a dirty working tree aborts mid-merge.
   **Cause:** `pull` triggers a merge, and Git won't merge if you have uncommitted changes that conflict.
   **Fix:** Commit or stash your changes first: `git stash && git pull && git stash pop`.

5. **Symptom:** HTTPS push prompts for username/password every time.
   **Cause:** No credential helper is configured.
   **Fix:** `git config --global credential.helper store` (plaintext, Linux) or `git config --global credential.helper osxkeychain` (macOS). On Linux, consider `libsecret` for encrypted storage.

## Practice

**Warm-up.** Run `git remote -v` in any cloned repository. Identify the remote name and its URL.

**Standard.** Fork a public repository on GitHub, clone your fork, add `upstream`, fetch from upstream, and check how many commits you're behind with `git rev-list --count`.

**Bug hunt.** `git pull` says "refusing to merge unrelated histories." Explain what happened and how to fix it.

**Stretch.** Delete a remote branch with `git push --delete origin <branch>` and verify with `git branch -r`.

**Stretch++.** Use `git push --dry-run` (or `-n`) to preview what would be pushed without actually pushing. Explain the output.

<details><summary>Show solutions</summary>

**Bug hunt.** The local repo and the remote repo were initialized independently — they have separate root commits with no common ancestor. This happens when you `git init` locally and then `git remote add` a remote that already has commits. Fix with `git pull --allow-unrelated-histories`, which merges the two independent histories. To avoid this, either clone the remote from the start, or push to a fresh empty remote.

**Stretch++.** `git push --dry-run` (or `git push -n`) performs all the push logic — pack negotiation, ref updates — but stops short of actually transmitting data. The output shows which refs would be updated (e.g., `abc1234..def5678 main -> main`) and how many objects would be sent. Useful for verifying you're pushing what you expect.

</details>

## Quiz

1. `git fetch` modifies:
    (a) the working tree (b) your local branches (c) only remote-tracking refs (d) nothing at all

2. `git pull` is equivalent to:
    (a) fetch + merge (or rebase, per config) (b) fetch only (c) push + fetch (d) reset to origin

3. `origin/main` is:
    (a) the remote branch itself (b) a local reference tracking the remote's state (c) a tag (d) a merge commit

4. Which command(s) delete a remote branch?
    (a) `git push origin :feat` (b) `git push --delete origin feat` (c) both work (d) only via web UI

5. `--force-with-lease` differs from `--force` because it:
    (a) is identical to `--force` (b) refuses if the remote ref has moved since your last fetch (c) disables force-push (d) only works locally

**Short answer:**

6. Why is `fetch` safer than `pull`?
7. What is the purpose of `upstream` in an open-source fork workflow?

*Answers: 1-c, 2-a, 3-b, 4-c, 5-b*

*6. `fetch` only updates remote-tracking refs — it never modifies your local branches or working tree, so it can't cause merge conflicts or unexpected changes. `pull` automatically merges into your current branch, which can fail or surprise you.*

*7. `upstream` points to the original project you forked from. You fetch from `upstream` to stay current with the project, and push to `origin` (your fork). PRs go from `origin` to `upstream`.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-remote — mini-project](mini-projects/09-remote-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Remotes are named URLs pointing to other copies of your repository — `origin` is the conventional default.
- `fetch` downloads without modifying your branches; `pull` fetches and merges; `push` uploads.
- Remote-tracking refs (`origin/main`) are your local snapshot of the remote's state, updated only on explicit sync.
- In open-source workflows, `origin` is your fork and `upstream` is the original project.

## Further reading

- [Pro Git — Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes) — covers adding, fetching, pushing, and inspecting remotes.
- [Git documentation — git-remote](https://git-scm.com/docs/git-remote) — full reference for remote management commands.
- Next: [GitHub](10-github.md).
