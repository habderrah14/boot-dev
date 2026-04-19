# Module 03 — Learn Git

> Git is the universal memory of a software team. If you cannot explain what a commit _is_ (not just how to make one), every branch, merge, and rebase will feel like magic — and that magic will occasionally corrupt your work.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Git"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Describe Git's internal object model (blobs, trees, commits, refs) and use it to reason about any Git command.
- Create, switch, merge, and rebase branches confidently and recover from a mistake.
- Push, pull, and collaborate via a remote (GitHub) with a clean commit history.
- Write a `.gitignore` that ships only what should ship.
- Diagnose an "oh no what did I do" moment using `git reflog` and `git reset`.

## Prerequisites

- [Module 02: Linux](../02-linux/README.md) — you need a terminal.
- Git 2.40+ installed. A free GitHub account.

## Chapter index

1. [Setup](01-setup.md)
2. [Repositories](02-repositories.md)
3. [Internals](03-internals.md)
4. [Config](04-config.md)
5. [Branching](05-branching.md)
6. [Merge](06-merge.md)
7. [Rebase](07-rebase.md)
8. [Reset](08-reset.md)
9. [Remote](09-remote.md)
10. [GitHub](10-github.md)
11. [Gitignore](11-gitignore.md)

## How this module connects

- _Internals_ (blobs/trees/commits) is a real-world example of the content-addressable DAG you'll re-encounter in DSA (Module 06).
- Every subsequent project in the path lives in Git; job hunting (Module 16) directly relies on a clean public GitHub.

## Companion artifacts

- Exercises:
  - [01 — Setup](exercises/01-setup-exercises.md)
  - [02 — Repositories](exercises/02-repositories-exercises.md)
  - [03 — Internals](exercises/03-internals-exercises.md)
  - [04 — Config](exercises/04-config-exercises.md)
  - [05 — Branching](exercises/05-branching-exercises.md)
  - [06 — Merge](exercises/06-merge-exercises.md)
  - [07 — Rebase](exercises/07-rebase-exercises.md)
  - [08 — Reset](exercises/08-reset-exercises.md)
  - [09 — Remote](exercises/09-remote-exercises.md)
  - [10 — GitHub](exercises/10-github-exercises.md)
  - [11 — Gitignore](exercises/11-gitignore-exercises.md)
- Extended assessment artifacts:
  - [12 — Debugging Incident Lab](exercises/12-debugging-incident-lab.md)
  - [13 — Code Review Task](exercises/13-code-review-task.md)
  - [14 — System Design Prompt](exercises/14-system-design-prompt.md)
  - [15 — Interview Challenges](exercises/15-interview-challenges.md)
- Solutions:
  - [01 — Setup](solutions/01-setup-solutions.md)
  - [02 — Repositories](solutions/02-repositories-solutions.md)
  - [03 — Internals](solutions/03-internals-solutions.md)
  - [04 — Config](solutions/04-config-solutions.md)
  - [05 — Branching](solutions/05-branching-solutions.md)
  - [06 — Merge](solutions/06-merge-solutions.md)
  - [07 — Rebase](solutions/07-rebase-solutions.md)
  - [08 — Reset](solutions/08-reset-solutions.md)
  - [09 — Remote](solutions/09-remote-solutions.md)
  - [10 — GitHub](solutions/10-github-solutions.md)
  - [11 — Gitignore](solutions/11-gitignore-solutions.md)
- Mini-project briefs:
  - [01 — Git Bootstrap Script (Bonus project)](mini-projects/01-git-bootstrap-script.md)
  - [01 — Setup (Core chapter project)](mini-projects/01-setup-project.md)
  - [02 — Repositories](mini-projects/02-repositories-project.md)
  - [03 — Internals](mini-projects/03-internals-project.md)
  - [04 — Config](mini-projects/04-config-project.md)
  - [05 — Branching](mini-projects/05-branching-project.md)
  - [06 — Merge](mini-projects/06-merge-project.md)
  - [07 — Rebase](mini-projects/07-rebase-project.md)
  - [08 — Reset](mini-projects/08-reset-project.md)
  - [09 — Remote](mini-projects/09-remote-project.md)
  - [10 — GitHub](mini-projects/10-github-project.md)
  - [11 — Gitignore](mini-projects/11-gitignore-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Setup.** 1) b, 2) c, 3) a, 4) b, 5) b.
  - 6. `--system` affects all users on the machine and can leak personal identity settings in shared environments.
  - 7. Per-repo overrides are useful when one repo must use a different email identity (for example work vs. open source).
- **Ch. 02 — Repositories.** 1) c, 2) b, 3) b, 4) b, 5) b.
- **Ch. 03 — Internals.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 04 — Config.** 1) a, 2) c, 3) b, 4) b, 5) c.
- **Ch. 05 — Branching.** 1) b, 2) c, 3) b, 4) b, 5) b.
- **Ch. 06 — Merge.** 1) b, 2) b, 3) d, 4) b, 5) a.
- **Ch. 07 — Rebase.** 1) b, 2) a, 3) b, 4) b, 5) a.
- **Ch. 08 — Reset.** 1) b, 2) a, 3) c, 4) b, 5) a.
- **Ch. 09 — Remote.** 1) c, 2) a, 3) b, 4) c, 5) b.
- **Ch. 10 — GitHub.** 1) b, 2) a, 3) c, 4) b, 5) c.
- **Ch. 11 — Gitignore.** 1) b, 2) b, 3) b, 4) b, 5) b.
