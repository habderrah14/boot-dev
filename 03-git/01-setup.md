# Chapter 01 — Setup

> A good Git setup is five minutes you will be glad you spent every day for the rest of your career.

## Learning objectives

By the end of this chapter you will be able to:

- Install Git and verify a working version.
- Configure name, email, default branch, and editor.
- Explain the difference between `--system`, `--global`, and `--local` config tiers.
- Generate an SSH key and connect it to GitHub.
- Create aliases for your most-used commands.

## Prerequisites & recap

- A Linux/macOS/WSL shell ([Module 02](../02-linux/README.md)).

You should be comfortable opening a terminal, running commands, and editing files. Everything in this chapter happens on the command line.

## The simple version

Git needs to know two things before you make your first commit: your name and your email. These get baked into every commit you create, so getting them right from the start matters. Beyond that, a handful of sensible defaults — your preferred editor, a default branch name, a couple of aliases — save you from friction that compounds over months of daily use.

Think of Git config as a stack of three files. The bottom one (`--system`) covers everyone on the machine, the middle one (`--global`) covers all of your repos, and the top one (`--local`) covers just one repo. When Git looks up a setting, it reads bottom-to-top and the last value wins — so a per-repo override always beats the global default.

## In plain terms (newbie lane)

This chapter is really about **Setup**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Config tier lookup order (last match wins):

```
┌──────────────────────────────────────────────────────┐
│  Git reads config bottom → top; last value wins      │
│                                                      │
│  ┌──────────────┐                                    │
│  │   --system   │  /etc/gitconfig                    │
│  │  (all users) │  lowest priority                   │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │   --global   │  ~/.gitconfig                      │
│  │  (your user) │  overrides system                  │
│  └──────┬───────┘                                    │
│         ▼                                            │
│  ┌──────────────┐                                    │
│  │   --local    │  .git/config                       │
│  │  (this repo) │  highest priority — wins           │
│  └──────────────┘                                    │
└──────────────────────────────────────────────────────┘
```

## Concept deep-dive

### Installing Git

Package managers are the simplest route. After installing, verify the version — this book assumes 2.40 or later, when `git switch` and the `ort` merge strategy are both stable.

```bash
sudo apt install git           # Debian / Ubuntu
brew install git               # macOS (Homebrew)
git --version                  # expect 2.40+
```

Why check the version? Older Git ships with `master` as the default branch name and the older `recursive` merge strategy. Both still work, but newer defaults are saner and commands like `git switch` didn't exist before 2.23.

### First-time config

These five settings eliminate the most common first-day annoyances:

```bash
git config --global user.name  "Ada Lovelace"
git config --global user.email "ada@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase false           # or true — pick one and be consistent
git config --global core.editor  "code --wait"  # vim, nano, emacs — whatever you prefer
```

`user.name` and `user.email` appear in every commit you make. If you skip them, Git refuses to commit and prints `Please tell me who you are`. Setting `init.defaultBranch` to `main` avoids the deprecation warning you'd otherwise see each time you run `git init`.

### Config tiers — system, global, local

| Tier | File | Scope | Typical use |
|------|------|-------|-------------|
| `--system` | `/etc/gitconfig` | All users on the machine | Rarely touched by hand |
| `--global` | `~/.gitconfig` | All your repos | Your identity, editor, aliases |
| `--local` | `.git/config` | This repo only | Per-project overrides |

Inspect everything at once — including which file each value comes from — with:

```bash
git config --list --show-origin
```

### Diff tool and aliases

Aliases reduce the keystrokes you repeat most:

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.lg "log --oneline --graph --decorate --all"
```

Now `git st` expands to `git status`, `git co` to `git checkout`, and `git lg` prints a compact visual log. You can define as many as you like; there is no performance cost.

### SSH keys for GitHub

HTTPS remotes work but prompt for credentials. SSH key authentication is a one-time setup that removes that friction:

```bash
ssh-keygen -t ed25519 -C "ada@example.com"
cat ~/.ssh/id_ed25519.pub      # copy this output
# paste into GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com          # expect: "Hi ada! You've successfully authenticated…"
```

Ed25519 is the current recommendation: shorter keys, faster operations, and no known weaknesses. If you're on an older system that doesn't support ed25519, fall back to RSA with at least 4096 bits (`ssh-keygen -t rsa -b 4096`).

## Why these design choices

**Three tiers instead of one file.** A single config would mean choosing between per-machine and per-repo settings. The tiered model lets teams enforce repo-level conventions (line endings, merge style) without touching your personal editor choice.

**SSH over HTTPS.** HTTPS works everywhere, but SSH keys are stateless — no credential managers, no token rotation. For daily development where you push dozens of times a day, SSH wins on convenience. HTTPS is better when you're behind a corporate proxy that blocks port 22.

**`pull.rebase false` as starting default.** Merge-on-pull is easier to reason about when you're learning. Once you understand rebase (covered in a later chapter), you may flip this to `true` for a linear history — but the choice should be deliberate, not accidental.

## Production-quality code

### Verifying your setup

```bash
#!/usr/bin/env bash
set -euo pipefail

required_keys=("user.name" "user.email" "init.defaultBranch" "core.editor")

for key in "${required_keys[@]}"; do
  value=$(git config --global "$key" 2>/dev/null || true)
  if [[ -z "$value" ]]; then
    printf "MISSING  %s\n" "$key" >&2
  else
    printf "OK       %-22s = %s\n" "$key" "$value"
  fi
done
```

### Per-repo identity override

When you contribute to an open-source project under a different email:

```bash
cd ~/projects/foss-thing
git config user.email "ada@opensource.org"
# no --global flag → writes to .git/config in this repo only

git config user.email
# ada@opensource.org (local override wins)

cd ~/work/internal-api
git config user.email
# ada@example.com (falls through to global)
```

## Security notes

- **SSH private keys** are the most sensitive file your setup creates. Never commit `~/.ssh/id_ed25519` (the private half). Make sure the file permissions are `600` — `ssh` will refuse to use a world-readable key, and for good reason.
- **`user.email` on `--system`** leaks your personal email to every user on a shared machine. Keep identity settings at `--global` or `--local`.
- **Credential helpers** (`git config credential.helper store`) write HTTPS tokens in plain text to `~/.git-credentials`. Prefer SSH keys or `credential.helper cache` (memory-only, timeout-based) on shared systems.

## Performance notes

N/A — Git config is read once per command invocation and cached in memory. There's no meaningful performance difference between config tiers, file sizes, or alias counts. Even hundreds of aliases add negligible startup cost.

## Common mistakes

1. **Symptom:** `git commit` says `Please tell me who you are`.
   **Cause:** `user.name` or `user.email` isn't set.
   **Fix:** `git config --global user.name "…"` and `git config --global user.email "…"`.

2. **Symptom:** Commits on GitHub show the wrong avatar or "unknown user".
   **Cause:** The email in your commits doesn't match any email on your GitHub account.
   **Fix:** Add the email to your GitHub profile, or update your local config to match an email GitHub already knows about.

3. **Symptom:** `git push` keeps asking for a username/password.
   **Cause:** The remote URL is HTTPS and no credential helper is configured.
   **Fix:** Switch to SSH (`git remote set-url origin git@github.com:user/repo.git`) or configure a credential helper.

4. **Symptom:** You committed as `root@hostname` instead of your name.
   **Cause:** You ran Git from a root shell or `sudo git commit`.
   **Fix:** Avoid committing as root. If it already happened, `git commit --amend --author="Ada Lovelace <ada@example.com>"` fixes the last commit; older history requires a filter-branch or `git rebase -i`.

## Practice

1. **Warm-up.** Print your Git version.
2. **Standard.** Set all five global configs from the deep-dive section and verify them with `git config --list --show-origin`.
3. **Bug hunt.** After cloning a colleague's repo you run `git commit` and Git prints `Please tell me who you are`. What's missing, and at which config tier should you fix it?
4. **Stretch.** Create a `.gitconfig` alias `git unstage <file>` that runs `reset HEAD --`.
5. **Stretch++.** Use `includeIf` to make your `ada@work.com` email auto-apply to any repo under `~/work/`.

<details><summary>Show solutions</summary>

1. `git --version`.

2. Run the five `git config --global …` commands, then `git config --list --show-origin | grep -E 'user\.|init\.|core\.editor'`.

3. `user.name` or `user.email` (or both) are not set. Fix at `--global` unless this repo needs a different identity.

4. `git config --global alias.unstage "reset HEAD --"`. Verify: `git unstage somefile.txt` should behave like `git reset HEAD -- somefile.txt`.

5. In `~/.gitconfig`:

    ```ini
    [includeIf "gitdir:~/work/"]
        path = ~/.gitconfig-work
    ```

    Then create `~/.gitconfig-work`:

    ```ini
    [user]
        email = ada@work.com
    ```

</details>

## Quiz

1. `git config --global` writes to:
    (a) `/etc/gitconfig` (b) `~/.gitconfig` (c) `.git/config` (d) memory only

2. Which tier wins when the same key appears in multiple config files?
    (a) system (b) global (c) local (d) whichever was written most recently

3. What does `git config --list --show-origin` do?
    (a) Prints values with the file each came from (b) Shows only global values (c) Fails unless inside a repo (d) Same as `git log`

4. What is the recommended default branch name for new repos?
    (a) `master` (b) `main` (c) Either — it's cosmetic (d) `trunk`

5. When `ssh -T git@github.com` succeeds, it returns:
    (a) Blank output (b) A greeting or authentication confirmation (c) A shell prompt (d) A clone of the default repo

**Short answer:**

6. Why should you avoid setting `user.email` at the `--system` tier?
7. Give a concrete scenario where per-repo config overrides are useful.

*Answers: 1-b, 2-c, 3-a, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-setup — mini-project](mini-projects/01-setup-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Three config tiers — system, global, local — resolve bottom-to-top; local always wins.
- Set name, email, default branch, pull strategy, and editor before your first commit.
- SSH keys are a one-time setup that eliminates credential prompts for daily Git operations.
- Aliases cost nothing and compound into significant time savings over months.

## Further reading

- `man git-config` — the exhaustive reference for every config key.
- [GitHub: Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
- Next: [Repositories](02-repositories.md).
