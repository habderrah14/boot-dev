# Mini-project — 10-github

_Companion chapter:_ [`10-github.md`](../10-github.md)

**Goal.** Ship a small Python CLI on GitHub with a complete professional setup.

**Acceptance criteria:**

- Repository has a `README.md`, `LICENSE` (MIT), and `.gitignore`.
- CI workflow runs `pytest` on every push and PR.
- Branch protection is enabled on `main` requiring CI to pass.
- A feature branch with at least two commits is merged via squash merge through a PR.
- The merged PR is visible in the repository's pull request history.

**Hints:** Use `gh repo create` to bootstrap. Use `gh pr create --fill` and `gh pr merge --squash --delete-branch` for the PR workflow. Check the Actions tab to verify CI runs.

**Stretch:** Add a `CODEOWNERS` file and a second workflow that runs `ruff check .` for linting. Configure the repo to require both CI and lint checks to pass before merge.
