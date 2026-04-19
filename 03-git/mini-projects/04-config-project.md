# Mini-project — 04-config

_Companion chapter:_ [`04-config.md`](../04-config.md)

**Goal.** Create a canonical, version-controlled Git config that you can deploy to any machine.

**Acceptance criteria:**

- A `dotfiles/git/config` file with your name, email, 5+ aliases, and sane defaults for `pull.rebase`, `merge.conflictStyle`, `fetch.prune`, and `core.autocrlf`.
- An `includeIf` block that switches email for repos under `~/work/`.
- A companion `dotfiles/git/config-work` file with the work email.
- A `setup.sh` script that symlinks both files to the right locations and verifies the result.

**Hints:** Symlink `~/.gitconfig` → `dotfiles/git/config`. Test by creating temp repos inside and outside `~/work/` and checking `git config user.email`.

**Stretch:** Add `includeIf` for a third directory (e.g., `~/oss/`) with yet another email, and extend `setup.sh` to handle all three.
