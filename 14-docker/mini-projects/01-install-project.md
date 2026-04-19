# Mini-project — 01-install

_Companion chapter:_ [`01-install.md`](../01-install.md)

**Goal.** Install Docker, verify it works, and explore a container interactively.

**Acceptance criteria:**

- Docker installed and `docker run --rm hello-world` succeeds.
- `docker run -it --rm ubuntu bash` opens a shell inside an Ubuntu container.
- Inside the container, install a package (`apt update && apt install -y curl`), run `curl --version`, then exit.
- After exiting, verify the container is gone (`docker ps -a` shows no trace because of `--rm`).

**Hints:**

- Use `--rm` to auto-remove the container on exit.
- `-it` gives you an interactive terminal.
- The container is an isolated Ubuntu — it has its own filesystem, processes, and network.

**Stretch:** Create a Docker context pointing to a second machine (or a VM) and run `hello-world` remotely.
