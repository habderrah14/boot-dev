# Mini-project — Git Bootstrap Script

## Goal

Build `git-bootstrap.sh`, a repeatable script that configures a fresh development machine for Git in under one minute.

## Deliverable

A script plus README that sets core Git config and validates the result.

## Required behavior

1. Configure global `user.name`, `user.email`, `init.defaultBranch`, `pull.rebase`, and `core.editor`.
2. Add aliases `st`, `co`, and `lg`.
3. Generate an Ed25519 SSH key only if one does not already exist.
4. Print a summary table of values at the end.
5. Exit non-zero on any unrecoverable failure.

## Acceptance criteria

- Script uses `#!/usr/bin/env bash` and `set -euo pipefail`.
- Supports non-interactive usage via flags (for automation).
- Idempotent: re-running does not duplicate or corrupt config.
- Clearly reports what changed vs. what already existed.
- Includes a `--dry-run` mode.

## Hints

- `git config --global --get <key>` to detect existing values.
- `ssh-keygen -t ed25519 -C "email"` for key generation.
- `git config --list --show-origin` for validation output.

## Stretch goals

1. Add `--work-email` and write a per-directory `includeIf` config.
2. Add `--strict` that fails if any key is missing after setup.
3. Add shellcheck validation in README instructions.
