# Mini-project — Docker First Run

## Goal

Install Docker, verify it works, and explore a container interactively.

## Deliverable

A short README or notes file showing installation, verification, and an interactive shell inside a container.

## Required behavior

1. `docker run --rm hello-world` succeeds.
2. `docker run -it --rm ubuntu bash` opens a shell.
3. A package can be installed inside the container.
4. The container disappears after exit because of `--rm`.

## Acceptance criteria

- Installation path is documented.
- Commands are reproducible by someone else.
- You demonstrate the difference between host and container environments.

## Hints

- Use `-it` for interactive shells.
- Use `--rm` to avoid cleanup confusion.
- Try a simple `apt update && apt install -y curl` inside Ubuntu.

## Stretch goals

1. Add a remote Docker context.
2. Compare Docker Desktop and Colima.
3. Record `docker info` output.
