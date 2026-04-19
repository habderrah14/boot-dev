# Module 02 — Learn Linux

> Backend engineering happens on Linux. Even when your laptop runs macOS or Windows, your code will land on a Linux server, inside a Linux container, running under a Linux kernel. This module makes the OS stop being a black box.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Linux"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Navigate a filesystem, inspect processes, and manage files from a terminal with no GUI.
- Read and write a short shell pipeline using redirection, pipes, and standard streams.
- Explain Unix permissions (ugo/rwx, octal, setuid) and apply the principle of least privilege.
- Install, update, and remove software through a package manager without fighting dependencies.
- Tell the difference between a shell _command_ (built-in), a _program_ (executable file), and a _script_.

## Prerequisites

- Completed [Module 01: Python](../01-python/README.md) — you need to be able to run a script.
- Access to a Linux environment: a real Linux laptop, WSL2 on Windows, a cloud VM, or a Docker container (`docker run -it --rm debian:stable bash`).

## Chapter index

1. [Terminals and Shells](01-terminals-and-shells.md)
2. [Filesystems](02-filesystems.md)
3. [Permissions](03-permissions.md)
4. [Programs](04-programs.md)
5. [Input/Output](05-input-output.md)
6. [Packages](06-packages.md)

## How this module connects

- Every future module assumes terminal fluency — from running `git`, to `npm`, to `docker`, to `psql`.
- _Permissions_ re-appears in HTTP-server authentication (Module 12) and AWS IAM (Module 13).
- _I/O streams and redirection_ is the mental model you reuse for Node.js streams (Module 08) and Docker logs (Module 14).

## Companion artifacts

- Exercises:
  - [01 — Terminals and Shells](exercises/01-terminals-and-shells-exercises.md)
  - [02 — Filesystems](exercises/02-filesystems-exercises.md)
  - [03 — Permissions](exercises/03-permissions-exercises.md)
  - [04 — Programs](exercises/04-programs-exercises.md)
  - [05 — Input/Output](exercises/05-input-output-exercises.md)
  - [06 — Packages](exercises/06-packages-exercises.md)
- Extended assessment artifacts:
  - [07 — Debugging Incident Lab](exercises/07-debugging-incident-lab.md)
  - [08 — Code Review Task](exercises/08-code-review-task.md)
  - [09 — System Design Prompt](exercises/09-system-design-prompt.md)
  - [10 — Interview Challenges](exercises/10-interview-challenges.md)
- Solutions:
  - [01 — Terminals and Shells](solutions/01-terminals-and-shells-solutions.md)
  - [02 — Filesystems](solutions/02-filesystems-solutions.md)
  - [03 — Permissions](solutions/03-permissions-solutions.md)
  - [04 — Programs](solutions/04-programs-solutions.md)
  - [05 — Input/Output](solutions/05-input-output-solutions.md)
  - [06 — Packages](solutions/06-packages-solutions.md)
- Mini-project briefs:
  - [01 — Shell Environment Audit (Bonus project)](mini-projects/01-shell-environment-audit.md)
  - [01 — Terminals and Shells (Core chapter project)](mini-projects/01-terminals-and-shells-project.md)
  - [02 — Filesystems](mini-projects/02-filesystems-project.md)
  - [03 — Permissions](mini-projects/03-permissions-project.md)
  - [04 — Programs](mini-projects/04-programs-project.md)
  - [05 — Input/Output](mini-projects/05-input-output-project.md)
  - [06 — Packages](mini-projects/06-packages-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Terminals and Shells.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  You quote `"My Documents"` because unquoted whitespace splits one path into multiple arguments.
  - 7.  `which` only reports executable paths; `type` also reports aliases, shell functions, and built-ins, so they differ when a name resolves to a non-executable shell construct.
- **Ch. 02 — Filesystems.** 1) b, 2) b, 3) b, 4) a, 5) c.
  - 6. Linux uses a single root-mounted directory tree (`/`) and mounts additional filesystems into that tree, so drive letters are unnecessary.
  - 7. Prefer `rg` when you need fast recursive text search that respects `.gitignore` and scales well on large repos.
- **Ch. 03 — Permissions.** 1) a, 2) b, 3) d, 4) a, 5) c.
  - 6. On a directory, `rwx` controls listing/traversal/entry creation; on a file, `rwx` controls read/write/execute of file content.
  - 7. SSH blocks world-readable private keys because secrets must be owner-only to preserve authentication integrity.
- **Ch. 04 — Programs.** 1) b, 2) b, 3) c, 4) a, 5) a.
  - 6. `#!/usr/bin/env python3` is more portable because it resolves `python3` from the active `PATH` rather than assuming a fixed absolute path.
  - 7. `SIGTERM` is catchable and allows graceful cleanup; `SIGKILL` is immediate and cannot be handled.
- **Ch. 05 — Input/Output.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6. Write diagnostics/errors to stderr so stdout remains clean and pipeable as data.
  - 7. `xargs -0` is safer because it uses NUL delimiters, correctly handling spaces/newlines/special characters in filenames.
- **Ch. 06 — Packages.** 1) b, 2) b, 3) b, 4) c, 5) c.
  - 6. `sudo pip install` can corrupt distro-managed Python environments and introduces root-level risk from package install scripts.
  - 7. A manifest declares desired direct dependencies; a lockfile pins the exact resolved graph for reproducible installs, so both should be committed.
