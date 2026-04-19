# Mini-project — 01-setup

_Companion chapter:_ [`01-setup.md`](../01-setup.md)

**Goal.** Write a script `git-bootstrap.sh` that automates a fresh Git setup on any machine.

**Acceptance criteria:**

- Sets the five global configs (name, email, default branch, pull strategy, editor) from arguments or interactive prompts.
- Creates three aliases: `st`, `co`, and `lg`.
- Generates an Ed25519 SSH key if `~/.ssh/id_ed25519` doesn't already exist.
- Prints a summary of what was configured.
- Exits with a non-zero code if any step fails.

**Hints:** Use `set -euo pipefail`. Check for existing values with `git config --global --get <key>` before overwriting. Print the public key at the end so the user can paste it into GitHub.

**Stretch:** Add a `--dry-run` flag that shows what *would* change without writing anything.
