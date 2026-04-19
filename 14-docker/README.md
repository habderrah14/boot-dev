# Module 14 — Learn Docker

> "It works on my machine" is a debugging sentence, not a shipping plan. Docker makes _your machine_ the thing you ship.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Docker"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Install Docker Engine / Docker Desktop and run your first container.
- Explain what a container is (a process namespace + filesystem view) and what it is _not_ (a VM).
- Use volumes, bind mounts, and networks appropriately.
- Write a small, production-quality `Dockerfile` (multi-stage, non-root, pinned bases).
- Debug a misbehaving container via `logs`, `exec`, and `inspect`.
- Publish an image to a registry (Docker Hub, GHCR).

## Prerequisites

- [Module 02: Linux](../02-linux/README.md) — namespaces and processes.
- At least one language module you can containerize (Python or TypeScript).

## Chapter index

1. [Install](01-install.md)
2. [Containers](02-containers.md)
3. [Storage](03-storage.md)
4. [Execute](04-execute.md)
5. [Networks](05-networks.md)
6. [Dockerfiles](06-dockerfiles.md)
7. [Debug](07-debug.md)
8. [Publish](08-publish.md)

## How this module connects

- Docker is the deployment target for every server in Modules 12, 13, 15.
- `docker compose` is the easiest way to run RabbitMQ locally (Module 15).

## Companion artifacts

- Exercises:
  - [01 — Install](exercises/01-install-exercises.md)
  - [02 — Containers](exercises/02-containers-exercises.md)
  - [03 — Storage](exercises/03-storage-exercises.md)
  - [04 — Execute](exercises/04-execute-exercises.md)
  - [05 — Networks](exercises/05-networks-exercises.md)
  - [06 — Dockerfiles](exercises/06-dockerfiles-exercises.md)
  - [07 — Debug](exercises/07-debug-exercises.md)
  - [08 — Publish](exercises/08-publish-exercises.md)
- Extended assessment artifacts:
  - [09 — Debugging Incident Lab](exercises/09-debugging-incident-lab.md)
  - [10 — Code Review Task](exercises/10-code-review-task.md)
  - [11 — System Design Prompt](exercises/11-system-design-prompt.md)
  - [12 — Interview Challenges](exercises/12-interview-challenges.md)
- Solutions:
  - [01 — Install](solutions/01-install-solutions.md)
  - [02 — Containers](solutions/02-containers-solutions.md)
  - [03 — Storage](solutions/03-storage-solutions.md)
  - [04 — Execute](solutions/04-execute-solutions.md)
  - [05 — Networks](solutions/05-networks-solutions.md)
  - [06 — Dockerfiles](solutions/06-dockerfiles-solutions.md)
  - [07 — Debug](solutions/07-debug-solutions.md)
  - [08 — Publish](solutions/08-publish-solutions.md)
- Mini-project briefs:
  - [01 — Docker First Run (Bonus project)](mini-projects/01-docker-first-run.md)
  - [01 — Install (Core chapter project)](mini-projects/01-install-project.md)
  - [02 — Containers](mini-projects/02-containers-project.md)
  - [03 — Storage](mini-projects/03-storage-project.md)
  - [04 — Execute](mini-projects/04-execute-project.md)
  - [05 — Networks](mini-projects/05-networks-project.md)
  - [06 — Dockerfiles](mini-projects/06-dockerfiles-project.md)
  - [07 — Debug](mini-projects/07-debug-project.md)
  - [08 — Publish](mini-projects/08-publish-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Install.** 1) b, 2) b, 3) a, 4) a, 5) a.
  - 6.  Adding your user to the `docker` group lets you run containers without `sudo`, because the Docker socket is owned by root:docker.
  - 7.  Docker contexts let one CLI switch between local and remote engines without SSH-ing into the host.
- **Ch. 02 — Containers.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Dockerfile instructions produce shared read-only layers, improving pull/cache efficiency.
  - 7. Container writable layers are ephemeral; persist data via volumes/external stores.
- **Ch. 03 — Storage.** 1) b, 2) b, 3) b, 4) b, 5) a.
  - 6. Bind mounts speed edit loops; volumes suit persistent runtime data.
  - 7. Docker Desktop bind mounts can be slower due to host-to-VM filesystem sync.
- **Ch. 04 — Execute.** Quiz key unavailable in chapter source; key publication deferred.
- **Ch. 05 — Networks.** Quiz key unavailable in chapter source; key publication deferred.
- **Ch. 06 — Dockerfiles.** Quiz key unavailable in chapter source; key publication deferred.
- **Ch. 07 — Debug.** Quiz key unavailable in chapter source; key publication deferred.
- **Ch. 08 — Publish.** Quiz key unavailable in chapter source; key publication deferred.
