# Mini-project — 02-filesystems

_Companion chapter:_ [`02-filesystems.md`](../02-filesystems.md)

**Goal.** Ship `scaffold.sh` — given a project name, create `name/{src,tests,docs}`, touch `README.md` and `.gitignore` (with sensible defaults), and print the resulting tree.

**Acceptance criteria.**

- Refuses to overwrite an existing directory; exits with code 1 and a clear message.
- Uses `set -euo pipefail`.
- Quoting is correct for project names containing spaces.
- A `--with-git` flag also runs `git init` inside the new project.
- Idempotency-style test: running with `--with-git` twice in different dirs both succeed.

**Hints.** Use `getopts` for flag parsing (or hand-roll for one flag). Use `[[ -e "$name" ]]` for the existence check. The `tree "$name"` at the end gives instant feedback.

**Stretch.** Add a `--lang python|node` flag that pre-creates `pyproject.toml` or `package.json` with placeholder content.
