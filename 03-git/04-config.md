# Chapter 04 — Config

> Config is the invisible hand behind every Git command. Learn to read it and you'll never say "I don't know why Git did that" again.

## Learning objectives

By the end of this chapter you will be able to:

- Navigate the three config tiers (system, global, local) and predict which value wins.
- Set, unset, and inspect common options.
- Use `includeIf` to manage multiple identities automatically.
- Build aliases — simple and shell-escaped — for frequent operations.
- Choose sensible defaults for pull strategy, conflict style, and remote tracking.

## Prerequisites & recap

- [Setup](01-setup.md) introduced the basics of `git config --global`.
- [Internals](03-internals.md) — you know that `.git/config` is the local config file inside the repository database.

This chapter goes deeper: the full config format, the options that shape your daily workflow, and the patterns that prevent identity mistakes across personal and work projects.

## The simple version

Git config is a plain-text INI file that controls how almost every command behaves. There are three of these files, layered from broadest scope to narrowest: system (all users), global (your user account), and local (one repository). When the same key appears in multiple files, the narrowest scope wins.

The practical payoff is that you set your identity and preferences once at the global level, and override only what's different per project. Combined with `includeIf`, you can automate even those overrides based on where a repository lives on disk.

## In plain terms (newbie lane)

This chapter is really about **Config**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Config resolution with includeIf:

```
┌─────────────────────────────────────────────────────┐
│  Resolution order (last match wins)                 │
│                                                     │
│  /etc/gitconfig          ──► system tier            │
│         │                                           │
│         ▼                                           │
│  ~/.gitconfig            ──► global tier            │
│    └─ includeIf "gitdir:~/work/"                    │
│         └─ ~/.gitconfig-work   (merged into global) │
│         │                                           │
│         ▼                                           │
│  .git/config             ──► local tier (wins)      │
└─────────────────────────────────────────────────────┘
```

## Concept deep-dive

### The INI format

Git config is plain INI with sections and key-value pairs:

```ini
[user]
    name = Ada Lovelace
    email = ada@example.com

[core]
    editor = code --wait
    autocrlf = input

[alias]
    st = status
    lg = log --oneline --graph --decorate --all
```

Indentation is cosmetic but conventional. Section names are case-insensitive; key names are case-insensitive; values are case-sensitive.

### Inspecting and mutating config

```bash
git config --list                       # all effective values
git config --list --show-origin         # each value with its source file
git config user.email                   # read a single key
git config --global user.email "a@b.c"  # write to global
git config --unset user.email           # remove from local
git config --global --unset-all alias.lg  # remove all instances of a key
```

`--show-origin` is your debugging superpower. When a setting behaves unexpectedly, this command tells you exactly which file is responsible.

### Essential options

| Option | Recommended value | Why |
|--------|-------------------|-----|
| `core.editor` | Your preferred editor | Opens for commit messages, rebase todo lists, interactive commands |
| `core.autocrlf` | `input` (Linux/macOS), `true` (Windows) | Normalizes line endings to LF in the repo, prevents phantom diffs |
| `init.defaultBranch` | `main` | Avoids the deprecation warning; matches most hosting platforms |
| `pull.rebase` | `true` or `false` — pick one | Controls whether `git pull` merges or rebases; consistency matters |
| `pull.ff` | `only` | Rejects non-fast-forward pulls, forcing you to handle divergence explicitly |
| `merge.conflictStyle` | `diff3` | Shows the common ancestor in conflict markers, making resolution much easier |
| `rerere.enabled` | `true` | Remembers conflict resolutions so Git applies them automatically next time |
| `push.default` | `current` | Pushes the current branch to a same-named remote branch |
| `fetch.prune` | `true` | Removes stale remote-tracking branches on every fetch |
| `branch.autoSetupRebase` | `always` | New tracking branches default to rebase-on-pull (pairs with `pull.rebase=true`) |

### `includeIf` — automatic identity switching

Rather than remembering to set your work email in every work repo, tell Git to do it based on directory:

```ini
# ~/.gitconfig
[user]
    name = Ada Lovelace
    email = ada@personal.com

[includeIf "gitdir:~/work/"]
    path = ~/.gitconfig-work
```

```ini
# ~/.gitconfig-work
[user]
    email = ada@work.com
```

Any repo under `~/work/` automatically uses `ada@work.com`. Repos elsewhere use the global `ada@personal.com`. No manual per-repo config needed.

`includeIf` also supports `gitdir/i:` (case-insensitive, useful on macOS), `onbranch:` (match by current branch name), and `hasconfig:remote.*.url:` (match by remote URL pattern).

### Aliases

Simple aliases map a short name to a Git subcommand:

```bash
git config --global alias.co checkout
git config --global alias.s  "status -sb"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.undo "reset --soft HEAD~1"
```

For anything that needs shell features (pipes, multiple commands), prefix with `!`:

```ini
[alias]
    visual = "!gitk"
    cleanup = "!git branch --merged main | grep -v 'main' | xargs -r git branch -d"
```

Shell aliases (`alias gs='git status'` in your `.zshrc`) are separate from Git aliases and won't appear in `git config`.

## Why these design choices

**Three tiers, not one.** System-wide defaults can be set by an admin without touching individual user configs. Global config captures your identity and preferences. Local config lets a project enforce conventions (line endings, merge strategy) that apply to all contributors who clone it — without overriding their personal editor or aliases.

**`merge.conflictStyle=diff3`.** The default two-way conflict marker shows "ours" and "theirs" but not "what was there before." Without the common ancestor, you're guessing. `diff3` shows all three, which lets you reason about what each side *intended* to change.

**`rerere.enabled`.** If you resolve the same conflict once (common during long-lived branches with periodic merges from `main`), `rerere` records the resolution and replays it automatically. The trade-off is a small cache in `.git/rr-cache/`, but the time savings on complex merges are substantial.

**`fetch.prune=true`.** Without it, deleted remote branches linger as stale references in your local clone forever. Pruning on every fetch keeps your branch list honest with no extra effort.

## Production-quality code

### Printing a config value with its source

```bash
git config --show-origin user.email
# file:/home/ada/.gitconfig    ada@personal.com
```

### Setting up rebase-by-default pull

```bash
git config --global pull.rebase true
git config --global rebase.autoStash true
```

With these two settings, `git pull` automatically stashes uncommitted changes, fetches, rebases your unpushed commits on top, and pops the stash. No merge commits cluttering your history, and no "you have unstaged changes" errors blocking the pull.

### Auditing effective config for a repo

```bash
#!/usr/bin/env bash
set -euo pipefail

keys=("user.name" "user.email" "core.editor" "pull.rebase"
      "merge.conflictStyle" "init.defaultBranch" "fetch.prune")

printf "%-25s %-40s %s\n" "KEY" "VALUE" "SOURCE"
printf "%-25s %-40s %s\n" "---" "-----" "------"

for key in "${keys[@]}"; do
  line=$(git config --show-origin "$key" 2>/dev/null || echo "— (not set)")
  printf "%-25s %s\n" "$key" "$line"
done
```

## Security notes

- **`user.email` at `--system` scope** exposes your personal email to every user on the machine. Keep identity settings at `--global` or `--local`.
- **Shell-escaped aliases** (`!` prefix) execute arbitrary shell commands. On a shared machine, a malicious `.git/config` in a cloned repo could define an alias that runs harmful code when invoked. Review local config after cloning untrusted repos.
- **`credential.helper store`** writes HTTPS tokens in plain text to `~/.git-credentials`. Prefer `credential.helper cache` (in-memory, with a timeout) or SSH keys on shared or multi-user systems.

## Performance notes

N/A — Git reads config files once per command invocation and caches the result in memory. Config file size, number of aliases, and number of `includeIf` directives have no measurable impact on command performance. Even a config file with hundreds of entries adds sub-millisecond overhead.

## Common mistakes

1. **Symptom:** `git st` says `git: 'st' is not a git command`.
   **Cause:** The alias was set with `--local` in a different repo, or you forgot `--global`.
   **Fix:** Verify with `git config --list --show-origin | grep alias.st`. If missing from `~/.gitconfig`, re-add with `--global`.

2. **Symptom:** Python or Node files show phantom diffs on every checkout (changed line endings).
   **Cause:** `core.autocrlf=true` on a Linux/macOS machine converts LF to CRLF on checkout.
   **Fix:** Set `core.autocrlf=input` on Linux/macOS (converts CRLF→LF on commit, leaves LF alone on checkout). Add a `.gitattributes` file to the repo for cross-platform consistency.

3. **Symptom:** You committed with your personal email on a work project (or vice versa).
   **Cause:** No `includeIf` or local override; the global email applied everywhere.
   **Fix:** Set up `includeIf` (see above) so the right email activates based on directory. For the already-committed email, `git commit --amend --author="…"` fixes the most recent commit; older history requires a rebase.

4. **Symptom:** `git pull` creates a merge commit every time, cluttering the log.
   **Cause:** `pull.rebase` is `false` (or unset) and both your branch and the remote have new commits.
   **Fix:** `git config --global pull.rebase true`. For existing merge commits, `git rebase -i` can clean up the history if the branch hasn't been shared.

5. **Symptom:** Stale remote-tracking branches appear in `git branch -a` long after deletion.
   **Cause:** `fetch.prune` isn't enabled, so `git fetch` never removes deleted remote refs.
   **Fix:** `git config --global fetch.prune true`. For immediate cleanup: `git fetch --prune`.

## Practice

1. **Warm-up.** Print all origins for `user.email` across all tiers.
2. **Standard.** Set `pull.rebase=true`, `fetch.prune=true`, and `merge.conflictStyle=diff3` globally. Verify each with `--show-origin`.
3. **Bug hunt.** You set `alias.st=status` but `git st` doesn't work in a specific repo. How do you diagnose the problem?
4. **Stretch.** Create aliases for `git lg` (visual log), `git undo` (soft reset last commit), and `git cleanup` (delete merged branches). Test each in a real repo.
5. **Stretch++.** Configure `includeIf` so any repo under `~/work/` uses your work email and any repo under `~/oss/` uses a different email. Verify by running `git config user.email` inside repos in each directory.

<details><summary>Show solutions</summary>

1. `git config --list --show-origin | grep user.email` — shows every file that defines it and the value from each.

2. ```bash
   git config --global pull.rebase true
   git config --global fetch.prune true
   git config --global merge.conflictStyle diff3
   git config --show-origin pull.rebase
   git config --show-origin fetch.prune
   git config --show-origin merge.conflictStyle
   ```

3. Check if a local config overrides or shadows the alias: `git config --list --show-origin | grep alias.st`. If the alias was set with `--local` in a *different* repo, it won't exist here. Re-add with `--global` to make it available everywhere.

4. ```bash
   git config --global alias.lg "log --oneline --graph --decorate --all"
   git config --global alias.undo "reset --soft HEAD~1"
   git config --global alias.cleanup "!git branch --merged main | grep -v 'main' | xargs -r git branch -d"
   ```

5. In `~/.gitconfig`:
   ```ini
   [includeIf "gitdir:~/work/"]
       path = ~/.gitconfig-work
   [includeIf "gitdir:~/oss/"]
       path = ~/.gitconfig-oss
   ```

   `~/.gitconfig-work`:
   ```ini
   [user]
       email = ada@work.com
   ```

   `~/.gitconfig-oss`:
   ```ini
   [user]
       email = ada@opensource.org
   ```

</details>

## Quiz

1. Git aliases live under which config section?
    (a) `[alias]` (b) `[commands]` (c) `/usr/local/bin` (d) `~/.aliases`

2. `pull.rebase=true` makes `git pull`:
    (a) Fetch only (b) Hard reset (c) Rebase local commits onto fetched commits (d) Fail on conflict

3. `core.autocrlf=input` does what?
    (a) Converts LF→CRLF on checkout (b) Converts CRLF→LF on commit only (c) Converts both directions (d) Does nothing

4. `includeIf` can scope configuration by:
    (a) Branch name only (b) Repository directory path pattern (c) Remote URL only (d) User name

5. The local config file lives at:
    (a) `~/.gitconfig` (b) `/etc/gitconfig` (c) `.git/config` (d) `.gitignore`

**Short answer:**

6. Why use `includeIf` rather than manually running `git config user.email` in each repo?
7. When would you avoid setting `pull.rebase=true`?

*Answers: 1-a, 2-c, 3-b, 4-b, 5-c*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-config — mini-project](mini-projects/04-config-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Git config is INI-formatted, lives in three tier files, and resolves last-match-wins (local beats global beats system).
- `--show-origin` tells you exactly which file is responsible for any setting.
- `includeIf` automates per-directory identity switching — set it once, never worry about wrong-email commits again.
- Aliases and defaults like `merge.conflictStyle=diff3` and `fetch.prune=true` remove daily friction with zero downside.

## Further reading

- `man git-config` — exhaustive list of every config key.
- [Conditional includes](https://git-scm.com/docs/git-config#_conditional_includes) — official documentation for `includeIf`.
- Next: [Branching](05-branching.md).
