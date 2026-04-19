# Chapter 03 — Internals

> If you understand blobs, trees, commits, and refs, you will never again be surprised by Git.

## Learning objectives

By the end of this chapter you will be able to:

- Describe Git's four object types and how they relate to each other.
- Use plumbing commands to inspect the `.git/` directory.
- Explain what a branch, a tag, and `HEAD` actually are on disk.
- Articulate why Git stores snapshots rather than diffs, and why that matters.

## Prerequisites & recap

- [Repositories](02-repositories.md) — you can init, add, commit, and read `git log`.

You've been using the "porcelain" commands — the user-facing surface. This chapter pulls off the cover and shows you the machinery underneath. Understanding it isn't required for daily work, but it makes every confusing situation solvable.

## The simple version

Git is a content-addressed object database with four object types. A **blob** holds the raw bytes of a single file (no filename — just content). A **tree** is a directory listing that maps names to blobs or other trees. A **commit** points to one tree (the full project snapshot) and to its parent commit(s). A **tag** is a signed label pointing to any object.

Branches aren't copies of anything — they're tiny text files, each holding the 40-character SHA of the commit they point to. Creating a branch writes one file. Switching a branch updates `HEAD`. That's it.

## In plain terms (newbie lane)

This chapter is really about **Internals**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How objects reference each other:

```
  refs/heads/main
        │
        ▼
  ┌──────────┐    parent    ┌──────────┐
  │ commit C2 │ ──────────► │ commit C1 │
  └─────┬─────┘             └─────┬─────┘
        │ tree                    │ tree
        ▼                        ▼
  ┌──────────┐             ┌──────────┐
  │  tree T2  │             │  tree T1  │
  ├───────────┤             ├───────────┤
  │ README.md │──►blob A    │ README.md │──►blob A  (same content
  │ main.py   │──►blob B'   │ main.py   │──►blob B   = same blob)
  └───────────┘             └───────────┘
```

## Concept deep-dive

### The four object types

Every object lives in `.git/objects/` and is named by its SHA-1 hash (40 hex characters; newer Git optionally supports SHA-256). The hash is derived from the object's content, which means identical content always produces the same hash.

| Object | Stores | Key property |
|--------|--------|--------------|
| **blob** | Raw file bytes (no filename) | Two identical files = one blob |
| **tree** | List of `(mode, type, sha, name)` | A directory snapshot |
| **commit** | Tree hash, parent(s), author, committer, message | A full project snapshot |
| **tag** | Pointer to another object + optional GPG signature | A human-friendly label |

The hashing works like this: take a file's contents → SHA-1 → blob hash. List a directory's entries → SHA-1 → tree hash. Combine a tree, parent(s), author info, and message → SHA-1 → commit hash. Every hash is the *identity* of the thing it names.

### A commit is a snapshot, not a diff

This is the most important mental-model correction in Git. Most people think commits store "what changed." They don't. Each commit points to a complete tree — the full state of every tracked file at that moment.

Git is efficient despite storing full snapshots because of content addressing: if a file hasn't changed between commits, the new tree points to the same blob as the old tree. No duplication. Across a thousand commits where only a few files change each time, the vast majority of blobs are shared.

### Refs — branches, tags, and HEAD

A **ref** is a file under `.git/refs/` (or packed into `.git/packed-refs` for efficiency) that contains a single SHA — a named pointer to a commit.

```bash
cat .git/refs/heads/main
# 0d7a9b3f…   ← the commit that 'main' currently points at
```

Creating a branch is literally a one-line file write. That's why it's instant and costs almost nothing.

**`HEAD`** is the file `.git/HEAD`. In normal mode, it contains an indirect reference:

```
ref: refs/heads/main
```

This means "the commit that the `main` branch currently points at." When you commit, Git advances the ref that `HEAD` points to.

In **detached HEAD** state (after `git checkout <sha>`), `HEAD` contains a SHA directly instead of a ref. This isn't broken — it just means your commits aren't anchored to a named branch, so they'll become unreachable if you switch away without creating a branch first.

### Porcelain vs. plumbing

The commands you use daily — `git add`, `git commit`, `git log` — are "porcelain." Underneath, they call lower-level "plumbing" commands that operate directly on objects:

```bash
echo "hi" | git hash-object -w --stdin       # create a blob, print its SHA
git cat-file -t <sha>                         # print the object's type
git cat-file -p <sha>                         # pretty-print its contents
git ls-tree HEAD                              # list tree entries at HEAD
git rev-parse HEAD                            # resolve a ref to its SHA
git log --graph --oneline --decorate --all    # visual commit graph
```

These are the tools you reach for when something confusing happens and you want to see exactly what Git sees.

## Why these design choices

**Content addressing (SHA hashes).** Every object is named by the hash of its content, which gives Git three properties for free: deduplication (same content = same hash = stored once), integrity checking (corruption changes the hash, which Git detects), and immutability (changing content creates a new object with a new hash).

**Snapshots over diffs.** Diff-based systems must replay every patch from the beginning to reconstruct a file at a given commit. Git can check out any commit directly because each one points to a complete tree. The trade-off is disk space, but content addressing and pack files make this negligible in practice.

**Refs as plain files.** A branch could have been a complex data structure, but a one-line text file is trivial to read, write, and debug. The simplicity is deliberate — it means you can inspect or even repair Git's state with nothing more than `cat` and `echo`.

## Production-quality code

### Walking the object graph from HEAD

```bash
#!/usr/bin/env bash
set -euo pipefail

commit_sha=$(git rev-parse HEAD)
printf "commit  %s\n" "$commit_sha"

tree_sha=$(git cat-file -p "$commit_sha" | awk '/^tree / {print $2}')
printf "tree    %s\n" "$tree_sha"

printf "\nTree entries:\n"
git ls-tree "$tree_sha" | while IFS=$'\t' read -r meta name; do
  mode_type_sha=($meta)
  sha="${mode_type_sha[2]}"
  type=$(git cat-file -t "$sha")
  printf "  %-6s %-12s %s\n" "$type" "$sha" "$name"
done
```

### Proving two identical files share a blob

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p /tmp/blob-test && cd /tmp/blob-test
git init --quiet

printf "identical content\n" > file_a.txt
cp file_a.txt file_b.txt

git add file_a.txt file_b.txt
git commit -m "two files, same content" --quiet

sha_a=$(git ls-tree HEAD -- file_a.txt | awk '{print $3}')
sha_b=$(git ls-tree HEAD -- file_b.txt | awk '{print $3}')

if [[ "$sha_a" == "$sha_b" ]]; then
  printf "Same blob: %s — Git stored the content once.\n" "$sha_a"
else
  printf "ERROR: different blobs — this should not happen.\n" >&2
  exit 1
fi
```

## Security notes

- **SHA-1 collision resistance.** SHA-1 is theoretically vulnerable to collision attacks (SHAttered, 2017). Git mitigates this with a hardened SHA-1 implementation that detects known collision patterns. For high-security environments, Git supports SHA-256 repositories (`git init --object-format=sha256`), though ecosystem tooling is still catching up.
- **Object integrity.** Git verifies hashes on transfer (`git fsck`, `git transfer.fsckObjects`). Enable `transfer.fsckObjects = true` on servers to reject corrupted or maliciously crafted objects at push time.
- **Orphaned objects** (from amended commits, rebases, or force-pushes) persist until garbage collection. On a shared server, sensitive data in orphaned objects remains accessible to anyone with repo access until `git gc --prune=now` runs.

## Performance notes

- **Object storage** uses zlib compression. A 10 KB source file typically compresses to 2-4 KB as a loose object.
- **Pack files** (`git gc`) delta-compress similar objects together, often shrinking a repository by 50-80%. Git packs automatically when loose object counts exceed a threshold (default ~6700).
- **`git cat-file`** and **`git ls-tree`** are O(1) lookups by hash — effectively constant time regardless of repository size.
- **Large repos** (millions of objects) benefit from the commit-graph file (`git commit-graph write`), which accelerates `git log`, `git merge-base`, and reachability queries from O(n) to near O(1) for cached commits.

## Common mistakes

1. **Symptom:** You think Git is "storing all those diffs somewhere" and worry about performance.
   **Cause:** Incorrect mental model. Git stores snapshots, not diffs. Diffs are computed on the fly when you run `git diff` or `git log -p`.
   **Fix:** Run `git cat-file -p HEAD` and notice the `tree` field — it points to the full file tree, not a patch.

2. **Symptom:** After `git checkout <sha>`, Git prints a scary "detached HEAD" warning.
   **Cause:** `HEAD` now points directly to a commit instead of a branch ref. Any new commits you make won't be on a branch.
   **Fix:** If you want to keep working here, create a branch: `git switch -c my-exploration`. If you just wanted to look, switch back: `git switch main`.

3. **Symptom:** You rewrote history (amend, rebase) and think the old commits are gone.
   **Cause:** Rewriting creates *new* commits with new hashes. The originals still exist as orphaned objects.
   **Fix:** Recover with `git reflog` — it lists recent `HEAD` positions. Old commits persist until garbage collection (default: 90 days for reachable reflog entries, 30 days for unreachable).

4. **Symptom:** `git push` unexpectedly uploads a huge amount of data for a small change.
   **Cause:** Large files (binaries, datasets) were previously committed and are being packed and sent for the first time to this remote.
   **Fix:** Audit with `git rev-list --objects --all | git cat-file --batch-check | sort -k3 -n -r | head -20` to find the largest objects. Consider Git LFS for binaries.

## Practice

1. **Warm-up.** Print the current commit SHA using `git rev-parse HEAD`.
2. **Standard.** Use `git cat-file -p` to walk from `HEAD` → commit → tree → blob of `README.md`. Print the content at each step.
3. **Bug hunt.** A colleague says `git push` uploaded every file in a repository even though only one line changed. What could cause Git to consider many files "changed"? (Hint: think about line endings and the executable bit.)
4. **Stretch.** Create two files with identical content but different names. Commit them and prove they share a single blob.
5. **Stretch++.** Run `git gc` on a repository, then check `.git/objects/pack/`. How does the number of loose objects change? Read about pack files and explain the trade-off between loose objects and packs.

<details><summary>Show solutions</summary>

1. `git rev-parse HEAD` — prints the 40-character SHA of the current commit.

2. Step by step:
   ```bash
   git cat-file -p HEAD               # shows tree SHA, parent, author, message
   git cat-file -p <tree-sha>         # shows entries: mode, type, SHA, filename
   git cat-file -p <readme-blob-sha>  # shows the raw file content
   ```

3. Line ending changes (`core.autocrlf` mismatch) or file permission changes (executable bit flipping between platforms) cause Git to see every file as modified even though the text content is the same. Fix with `core.autocrlf=input` on Linux/macOS and consistent `.gitattributes`.

4. ```bash
   echo "same content" > a.txt
   echo "same content" > b.txt
   git add a.txt b.txt && git commit -m "two files"
   git ls-tree HEAD
   # both entries show the same blob SHA
   ```

5. Before `git gc`: many loose objects in `.git/objects/??/`. After: most are packed into `.git/objects/pack/*.pack` with an index (`.idx`). Loose objects are fast to write (one per `git add`); packs are smaller (delta-compressed) and faster to read in bulk. Git auto-packs periodically.

</details>

## Quiz

1. Git's four object types are:
    (a) file, directory, commit, tag (b) blob, tree, commit, tag (c) blob, tree, commit, branch (d) staged, committed, pushed, merged

2. A commit primarily references:
    (a) A diff of changes (b) A tree (full snapshot) (c) A branch name (d) A remote URL

3. A branch is physically:
    (a) A copy of all files (b) A small file holding a commit SHA (c) A metadata concept with no disk representation (d) A signed tag

4. `HEAD` usually contains:
    (a) A commit SHA directly (b) A ref path like `ref: refs/heads/main` (c) Your username (d) The repository URL

5. Detached HEAD means:
    (a) The repository is corrupt (b) HEAD points directly at a commit, not through a branch ref (c) You've force-pushed (d) A merge conflict exists

**Short answer:**

6. Why are two identical files cheap to store in Git?
7. What does "rewriting history" actually mean in terms of Git's object model?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-internals — mini-project](mini-projects/03-internals-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Git is a content-addressed DAG of four object types: blob, tree, commit, tag.
- Commits store full snapshots; unchanged files are shared via content addressing, making storage efficient.
- Branches are single-SHA pointer files — creating one is instant and essentially free.
- Plumbing commands let you inspect any object directly, which is invaluable for debugging.

## Further reading

- [Pro Git](https://git-scm.com/book), chapter 10 — Git Internals (plumbing and porcelain).
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/) — an excellent deep dive.
- Next: [Config](04-config.md).
