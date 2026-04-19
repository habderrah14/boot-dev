# Chapter 10 — GitHub

> GitHub is not Git. It's a web product built around Git. Knowing the distinction — and using the web product well — is critical for collaboration and for [getting hired](../16-job-hunt/README.md).

## Learning objectives

By the end of this chapter you will be able to:

- Create a repository on GitHub and push to it.
- Open, review, and merge pull requests using the CLI and web UI.
- Use issues, labels, and milestones to scope work.
- Protect the main branch with rulesets.
- Set up a basic CI pipeline with GitHub Actions.

## Prerequisites & recap

- [Remote](09-remote.md) — you know how to add remotes, fetch, pull, and push.
- A GitHub account with an SSH key uploaded ([ch. 01](01-setup.md)).

You can do everything in the previous chapters without ever touching a web browser — Git is fully local. GitHub adds a collaboration layer on top: pull requests for code review, issues for task tracking, Actions for CI/CD, and branch protection to enforce quality gates. This chapter covers the GitHub-specific workflows that modern teams rely on daily.

## The simple version

GitHub is a hosting platform for Git repositories that adds collaboration features Git itself doesn't have. The core loop is: you push a feature branch to GitHub, open a pull request (PR) to propose merging it into `main`, teammates review the code and CI runs automated tests, and once everything is green the PR gets merged. Issues track what needs doing, labels organize those issues, and branch protection rules prevent anyone from pushing broken code directly to `main`.

Think of GitHub as the project management shell around your Git repository. Git handles the version control; GitHub handles the human coordination.

## In plain terms (newbie lane)

This chapter is really about **GitHub**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The standard contribution loop on GitHub:

```
Developer workstation                     GitHub
-----------------------                   ------

1. git switch -c feat/foo          
2. ...make commits...              
3. git push -u origin feat/foo  -------->  Branch appears
                                           
4. gh pr create                 -------->  PR opened
                                           CI runs (Actions)
                                           Reviewers comment
                                           
5. git push (more commits)      -------->  PR updates, CI re-runs
                                           
6. gh pr merge --squash         -------->  Merged into main
                                           Branch deleted
                                           
7. git switch main && git pull  <--------  Local main updated
```

## Concept deep-dive

### Creating a repository

Three paths to get a repo on GitHub:

**1. Web UI** — easiest for beginners. Create an empty repo on github.com, copy the commands shown, run them locally:

```bash
git remote add origin git@github.com:you/myproj.git
git push -u origin main
```

**2. GitHub CLI (`gh`)** — one command from an existing local repo:

```bash
gh repo create myproj --public --source=. --remote=origin --push
```

**3. Import** — migrate an existing repo from another host (Bitbucket, GitLab, etc.) through GitHub's import tool.

**Why `gh`?** The GitHub CLI wraps the GitHub API into shell commands. Anything you can do in the web UI, you can do from the terminal — creating repos, opening PRs, reviewing code, managing issues. It's scriptable, which means you can automate repetitive workflows.

### Pull requests

A pull request is a *proposal* to merge one branch into another, bundled with a space for code review, discussion, and automated checks. It's GitHub's most important collaboration feature.

**The PR lifecycle:**

```bash
git switch -c feat/login
# ...make commits...
git push -u origin feat/login

gh pr create --fill                # opens PR, uses commit messages as body
# reviewers comment, you push more commits to the same branch
gh pr merge --squash --delete-branch
```

**Three merge strategies on GitHub:**

| Strategy | Result on base branch | When to use |
|---|---|---|
| **Merge commit** | All PR commits preserved + a merge commit | When full history matters |
| **Squash & merge** | One clean commit | When PR has messy WIP commits |
| **Rebase & merge** | PR commits replayed linearly | When you want linear history without squashing |

Pick one strategy per team and enforce it via repository settings. Mixing strategies makes `git log` inconsistent and harder to reason about.

### Issues and labels

Issues track *what* needs doing. They're the backbone of project management on GitHub.

**Linking commits to issues:**

```
feat: add login page (#42)
```

Including `#42` in a commit message creates a clickable link. Using `Closes #42` or `Fixes #42` in a PR description auto-closes the issue when the PR merges.

**Labels** make triage scannable: `bug`, `enhancement`, `good-first-issue`, `help-wanted`, `breaking-change`. GitHub provides defaults; customize them to match your team's workflow.

**Milestones** group issues into release targets. Assign issues to a milestone, and GitHub shows completion percentage.

### Branch protection

Branch protection rules prevent dangerous operations on critical branches. For `main`, a typical setup:

- **Require pull request reviews** — at least one approval before merge.
- **Require status checks to pass** — CI must be green.
- **Require conversation resolution** — all review comments addressed.
- **Require signed commits** — optional, for high-security projects.
- **Block force-push and deletion** — prevents accidental history rewrites.

**Why this matters:** without branch protection, any developer with push access can push directly to `main`, bypassing code review and CI. One bad commit can break production. Branch protection turns `main` into a gate that requires passing through a defined quality process.

### GitHub Actions

Actions is GitHub's built-in CI/CD platform. Workflows are defined in YAML files under `.github/workflows/`:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest --tb=short
```

Every push to `main` and every PR targeting `main` triggers the workflow. Combined with branch protection, this means no code reaches `main` without passing tests.

**Key Actions concepts:**

- **Triggers (`on`)** — events that start the workflow (push, pull_request, schedule, workflow_dispatch).
- **Jobs** — independent units of work, each running on a fresh VM.
- **Steps** — sequential commands within a job. `uses` runs a pre-built action; `run` executes a shell command.
- **Secrets** — encrypted variables (API keys, tokens) stored in repo settings and accessed as `${{ secrets.MY_SECRET }}`.

### Personal profile README

A repository named **exactly** your GitHub username becomes your profile README. When someone visits your profile, the contents of its `README.md` display prominently. A clean, focused profile README is a signal of professionalism. See [Module 16 ch. 03](../16-job-hunt/03-github-profile.md) for guidance.

### The `CODEOWNERS` file

`.github/CODEOWNERS` assigns automatic reviewers to files or directories:

```
# Automatically request review from @backend-team for any changes in src/api/
/src/api/    @backend-team

# All docs changes need tech-writer review
/docs/       @tech-writer
```

When a PR touches matched paths, GitHub auto-assigns the specified reviewers. Combined with branch protection requiring CODEOWNERS approval, this enforces domain expertise in reviews.

## Why these design choices

**Why pull requests instead of direct pushes?** Direct pushes give you speed but no review, no CI gate, and no discussion trail. PRs trade a small amount of friction for dramatically better code quality and team knowledge sharing. The review process catches bugs, spreads context, and creates a searchable record of *why* changes were made.

**Why squash merge?** Many teams prefer squash because feature branches accumulate noise — "wip", "fix lint", "oops". Squashing compresses this into one clean commit on `main`. The trade-off: you lose the granular commit history. If your team writes clean commits from the start (or rebases before merging), rebase-merge preserves useful history without noise.

**Why branch protection?** Because humans make mistakes. Even experienced developers occasionally push to the wrong branch or skip tests "just this once." Branch protection makes the quality process mandatory rather than optional. The cost is slightly more ceremony; the benefit is that `main` is always in a known-good state.

## Production-quality code

### End-to-end PR workflow

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <branch-name> [base-branch]" >&2
    echo "Creates a feature branch, opens a PR after commits are pushed." >&2
    exit 1
fi

FEATURE_BRANCH="$1"
BASE_BRANCH="${2:-main}"

if ! command -v gh &>/dev/null; then
    echo "ERROR: GitHub CLI (gh) is required." >&2
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo "ERROR: Not authenticated. Run 'gh auth login' first." >&2
    exit 1
fi

git fetch origin
git switch -c "$FEATURE_BRANCH" "origin/$BASE_BRANCH"

echo "Branch '$FEATURE_BRANCH' created from '$BASE_BRANCH'."
echo "Make your changes, commit, then run:"
echo "  git push -u origin $FEATURE_BRANCH"
echo "  gh pr create --base $BASE_BRANCH --fill"
```

### CI workflow with caching and linting

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          restore-keys: ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Test
        run: python -m pytest --tb=short --cov=src/ --cov-report=term-missing
```

## Security notes

- **Secret leaks** — the number one GitHub security mistake is committing API keys, tokens, or passwords. GitHub offers built-in secret scanning that detects known token formats (AWS keys, Stripe keys, etc.) and alerts you. Enable it in repository settings. If a secret is leaked, **rotate it immediately** — removing the file or commit is not enough because the secret exists in Git history forever (unless you rewrite history with `git filter-repo`).
- **Actions secrets** — store sensitive values (deploy keys, API tokens) in repository or organization secrets (`Settings → Secrets and variables → Actions`). Never hardcode them in workflow YAML. Secrets are masked in logs but can still be exfiltrated by a malicious action — vet third-party actions before using them (pin to a specific commit SHA, not just a version tag).
- **Fork PRs and secrets** — by default, GitHub does not expose repository secrets to workflows triggered by PRs from forks. This prevents a malicious fork from exfiltrating secrets via a PR workflow. Don't change this default.
- **CODEOWNERS bypass** — without branch protection requiring CODEOWNERS approval, the file is advisory only. Always pair CODEOWNERS with branch protection rules.

## Performance notes

- **Actions billing** — GitHub Actions is free for public repos. For private repos, you get a monthly minutes quota (varies by plan). Long-running workflows cost real money. Optimize by caching dependencies, running jobs in parallel, and skipping unnecessary steps with `if` conditions.
- **Caching dependencies** — the `actions/cache` action can save minutes per run. Cache `node_modules`, `pip` caches, Go modules, etc. Keys should include a hash of the lockfile so the cache invalidates when dependencies change.
- **Shallow clones in CI** — by default, `actions/checkout` does a shallow clone (`--depth 1`). This is fast but means `git log` only shows one commit. If your CI needs full history (e.g., for changelog generation), set `fetch-depth: 0`.
- **Concurrency control** — use the `concurrency` key in workflows to cancel redundant runs. If you push three commits in quick succession, only the latest workflow needs to complete:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Common mistakes

1. **Symptom:** You committed an API key and it's in the Git history even after deleting the file.
   **Cause:** Git stores every version of every file forever. Deleting a file only removes it from the latest commit.
   **Fix:** Use `git filter-repo` to purge the file from all history, then force-push. **Rotate the secret immediately** — assume it's compromised.

2. **Symptom:** PR shows "merge conflicts" and can't be merged.
   **Cause:** The base branch (`main`) advanced since you branched, and changes overlap.
   **Fix:** Locally: `git fetch origin && git rebase origin/main`, resolve conflicts, then `git push --force-with-lease`. Don't rebase while reviewers are mid-review if you can avoid it — it invalidates their comment anchors.

3. **Symptom:** YAML workflow file doesn't trigger Actions.
   **Cause:** Indentation error in the YAML, wrong branch name in `on.push.branches`, or the file isn't in `.github/workflows/`.
   **Fix:** Validate the YAML locally with `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`. Check the Actions tab for workflow parse errors.

4. **Symptom:** Direct pushes to `main` bypass CI and review.
   **Cause:** Branch protection rules aren't configured, or the pusher is an admin with "Include administrators" unchecked.
   **Fix:** Enable branch protection on `main` with required status checks and PR reviews. Check "Include administrators" to apply rules to everyone.

5. **Symptom:** Rebasing your PR branch loses reviewer comments.
   **Cause:** Force-pushing after rebase changes commit SHAs. GitHub's review comments are anchored to specific commits — when those commits disappear, the comments become "outdated."
   **Fix:** Prefer adding fixup commits during review. Squash at merge time using GitHub's "Squash and merge" button.

## Practice

**Warm-up.** Create a private repository using `gh repo create` and push a single-commit project to it.

**Standard.** Add a CI workflow (`.github/workflows/ci.yml`) that runs `python -m pytest` on every push. Verify it runs in the Actions tab.

**Bug hunt.** A PR shows merge conflicts. Resolve them locally by rebasing onto the base branch and force-pushing with lease.

**Stretch.** Enable branch protection on `main` requiring CI to pass and at least one review before merge.

**Stretch++.** Write a `.github/CODEOWNERS` file assigning yourself as owner of `src/` and a teammate as owner of `docs/`.

<details><summary>Show solutions</summary>

**Bug hunt.** `git fetch origin && git switch feat/my-pr && git rebase origin/main`. Resolve each conflict, `git add` the resolved file, `git rebase --continue`. When done: `git push --force-with-lease origin feat/my-pr`. The PR on GitHub updates automatically and the conflict badge disappears.

**Stretch++.**

```
# .github/CODEOWNERS
/src/    @your-username
/docs/   @teammate-username
```

Place this file at `.github/CODEOWNERS`. When branch protection requires CODEOWNERS approval, PRs touching `src/` will automatically request your review, and PRs touching `docs/` will request your teammate's.

</details>

## Quiz

1. A pull request is:
    (a) a Git branch (b) a merge proposal with review and CI integration (c) a tag (d) a remote

2. `gh repo create --push`:
    (a) creates the repo and pushes in one step (b) only creates the repo (c) requires HTTPS (d) doesn't exist

3. Branch protection can require:
    (a) PR review only (b) status checks only (c) both, and more (d) only force-push denial

4. Squash & merge leaves on the base branch:
    (a) every individual PR commit (b) exactly one commit (c) a merge commit with all PR commits (d) nothing

5. `.github/workflows/*.yml` defines:
    (a) issue templates (b) label colors (c) CI/CD pipelines (d) repository access policies

**Short answer:**

6. Why should you require status checks to pass before merging a PR?
7. Name one trade-off between squash, merge-commit, and rebase merge strategies.

*Answers: 1-b, 2-a, 3-c, 4-b, 5-c*

*6. Because without required status checks, broken code can be merged into main — tests might fail, linters might flag issues, but nothing prevents the merge. Required checks ensure every change passes automated quality gates before it reaches the protected branch.*

*7. Squash produces a clean single commit on main but loses granular commit history. Merge commits preserve full history but add visual noise in the log. Rebase-merge keeps individual commits linear but rewrites their SHAs, which can confuse contributors tracking their original commits.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-github — mini-project](mini-projects/10-github-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- GitHub adds collaboration (PRs, issues, Actions, branch protection) on top of Git's version control.
- The standard loop is: branch → push → PR → review + CI → merge.
- Branch protection + required status checks ensures `main` stays in a known-good state.
- The `gh` CLI makes GitHub operations scriptable and fast from the terminal.

## Further reading

- [GitHub Docs — About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) — comprehensive PR guide.
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) — branch protection configuration.
- [GitHub Actions documentation](https://docs.github.com/en/actions) — full CI/CD reference.
- Next: [gitignore](11-gitignore.md).
