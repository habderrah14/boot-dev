# Chapter 06 — Packages

> Software is rarely one file. A *package* is the bundle — binary + config + docs + dependency list. A *package manager* is the tool that understands the bundle and keeps dependencies sane.

## Learning objectives

By the end of this chapter you will be able to:

- Use your distro's system package manager (`apt`, `dnf`, `pacman`, `brew`).
- Install language-specific packages (`pip`, `npm`) in **isolated environments**.
- Distinguish system-level, user-level, and project-level package scopes.
- Keep installations reproducible with manifests and lockfiles.
- Avoid the classic "works on my machine" trap.

## Prerequisites & recap

- [Programs](04-programs.md) — `$PATH` and how the shell finds executables.
- [Permissions](03-permissions.md) — `sudo` and ownership.

## The simple version

Three scopes matter:

- **System** — `/usr/bin`, managed by `apt`/`dnf`/`brew`. Shared across users, needs `sudo`.
- **User** — `~/.local/`, `~/.cargo/`, `~/bin`. Per-user, no `sudo`.
- **Project** — `./.venv/`, `./node_modules/`. Per-directory, most reproducible.

**Favor project scope.** It isolates versions per project, survives wiping your laptop, and keeps you and your CI in exact agreement.

A **manifest** says what you depend on (`requirements.txt`, `package.json`). A **lockfile** records the exact versions that were resolved (`poetry.lock`, `package-lock.json`). Commit both.

## In plain terms (newbie lane)

This chapter is really about **Packages**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Scopes and how dependencies resolve.

```
   ┌─────────────────────────────────────────────────────────────┐
   │ SYSTEM scope    /usr/bin, /usr/lib                          │
   │   apt install / dnf install / brew install                  │
   │   → shared, needs sudo, affects every user                  │
   └─────────────────────────────────────────────────────────────┘
   ┌─────────────────────────────────────────────────────────────┐
   │ USER scope      ~/.local/bin, ~/.cargo/bin, ~/.npm          │
   │   pip install --user / pipx install / cargo install         │
   │   → your account only, no sudo                              │
   └─────────────────────────────────────────────────────────────┘
   ┌─────────────────────────────────────────────────────────────┐
   │ PROJECT scope   ./.venv, ./node_modules                     │
   │   pip install (inside venv), npm install                    │
   │   → reproducible; committed manifest + lockfile define it   │
   └─────────────────────────────────────────────────────────────┘

             Manifest ─ "what I want" ─▶ Resolver ─ exact versions ─▶ Lockfile
             (requirements.txt,                                      (poetry.lock,
              package.json)                                           package-lock.json)
```

## Concept deep-dive

### System package managers

| OS              | Tool   | Install                    | Update                           | Remove                      |
|-----------------|--------|----------------------------|----------------------------------|-----------------------------|
| Debian/Ubuntu   | `apt`  | `sudo apt install pkg`     | `sudo apt update && sudo apt upgrade` | `sudo apt remove pkg`  |
| Fedora/RHEL     | `dnf`  | `sudo dnf install pkg`     | `sudo dnf upgrade`               | `sudo dnf remove pkg`       |
| Arch            | `pacman` | `sudo pacman -S pkg`     | `sudo pacman -Syu`               | `sudo pacman -Rns pkg`      |
| macOS           | `brew` | `brew install pkg`         | `brew update && brew upgrade`    | `brew uninstall pkg`        |

These install to system paths (`/usr/bin`, `/usr/lib`, or `/opt/homebrew`). They manage dependencies automatically but apply **globally** — every user on the machine sees the same versions.

### Language package managers

#### Python

Always use a **virtual environment**. Never `sudo pip install` on a system Python; modern distros even refuse with PEP 668.

```bash
python3 -m venv .venv
source .venv/bin/activate     # prompt shows (.venv)
pip install requests
pip freeze > requirements.txt
deactivate
```

Modern alternatives:

- **`uv`** — by far the fastest (Rust-based); resolves and installs in seconds.
- **`poetry`** — opinionated project manager with lockfile by default.
- **`pipx`** — installs *CLI tools* each in their own venv (for `black`, `ruff`, `httpie`).

#### Node.js

Dependencies go under `./node_modules/` automatically.

```bash
npm init -y
npm install express
npm install --save-dev typescript @types/node

# In CI (strict, from lockfile):
npm ci
```

`pnpm` and `yarn` are faster, disk-efficient alternatives with identical flows.

### Manifests and lockfiles

| Ecosystem      | Manifest                          | Lockfile                                           |
|----------------|-----------------------------------|----------------------------------------------------|
| Python (pip)   | `requirements.txt` or `pyproject.toml` | `requirements.lock`, `poetry.lock`, `uv.lock` |
| Node           | `package.json`                    | `package-lock.json`, `pnpm-lock.yaml`              |
| Rust           | `Cargo.toml`                      | `Cargo.lock`                                       |
| Ruby           | `Gemfile`                         | `Gemfile.lock`                                     |
| Go             | `go.mod`                          | `go.sum`                                           |

- **Manifest** — human-written, declarative. Lists top-level dependencies and optional version constraints.
- **Lockfile** — machine-generated. Pins exact resolved versions of *every* dep (including transitives) and usually content hashes.

**Commit both.** CI runs `npm ci` / `uv sync` / `cargo build --locked` to install *exactly* what's in the lockfile.

### Reproducibility contract

A teammate should be able to:

```bash
git clone repo
cd repo
<one command>        # e.g. `uv sync` or `npm ci` or `cargo build`
```

and have everything working. If they can't, the project isn't reproducible — treat it as a bug.

### `$PATH` consequences

Per-scope installers put binaries in different places. `$PATH` order decides who wins when there are name collisions.

Typical priority (from a user's perspective):

```
./node_modules/.bin    (if using npm scripts)
~/.venv/bin            (if active)
~/.local/bin           (pip --user, pipx)
~/.cargo/bin           (rustup)
/usr/local/bin         (brew, manual installs)
/usr/bin
/bin
```

When `which tool` returns the wrong path, check `echo $PATH`.

## Why these design choices

- **Project > user > system for development.** Project scope is reproducible, user scope is convenient, system scope is for shared machines and infrastructure. Mixing them creates "works on my laptop" bugs; pick deliberately.
- **Lockfiles over manifests.** Semver is a promise, not a guarantee. `express ^4.18.0` can pull in a subtly different sub-dep tomorrow. The lockfile is the only honest answer to "which versions ran in production".
- **Isolated environments (venv / node_modules).** Packages often depend on specific versions of other packages. Global installs force everything to the *same* version, breaking one project when another upgrades. Isolation prevents "dependency hell".
- **`npm ci` vs. `npm install`.** `install` may update the lockfile if a range matches a newer version; `ci` strictly follows the lockfile and fails if it can't. Always use `ci` in automated environments.
- **When you'd choose differently.** Containers (Docker) often install system-wide inside a clean base image — the image itself is the reproducibility boundary. Ops-managed global tools (`kubectl`, `terraform`) stay system-level because per-project pinning adds no value.

## Production-quality code

### Example 1 — A reproducible Python project, from zero

```bash
mkdir myproj && cd myproj
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install requests
pip freeze > requirements.txt

cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc
.env
EOF

cat > README.md <<'EOF'
# myproj
## Setup
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
EOF
```

A new teammate clones, runs the three commands, and is working.

### Example 2 — A Node + TypeScript starter

```bash
mkdir hello-ts && cd hello-ts
npm init -y

# pin TypeScript compiler and types as dev deps
npm install --save-dev typescript @types/node

# initialize tsconfig.json
npx tsc --init

echo 'console.log("hi");' > index.ts
npx tsc
node index.js      # hi
```

`npx` runs a locally-installed binary from `./node_modules/.bin/` without polluting `$PATH`.

### Example 3 — `uv` for fast, lockfile-driven Python

```bash
# Install uv once (user scope)
curl -LsSf https://astral.sh/uv/install.sh | sh

# In a project
uv init
uv add requests
uv lock               # writes uv.lock
uv run python -c "import requests; print(requests.__version__)"
```

`uv sync` installs exactly the lockfile. 10–100× faster than pip.

### Example 4 — A `Makefile` that hides the ceremony

```makefile
.PHONY: setup install test clean

setup: .venv

.venv:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip

install: .venv
	./.venv/bin/pip install -r requirements.txt

test: install
	./.venv/bin/pytest

clean:
	rm -rf .venv __pycache__ *.pyc
```

`make setup install test` runs the happy path from a clean checkout.

## Security notes

- **`curl ... | bash` is arbitrary code execution.** Read the script first. For tool installers, prefer official signed `.deb`/`.rpm`/`.pkg` or your distro's repo.
- **Pin your lockfile hashes.** Modern lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`) include SHA-256 sums that make tampering detectable.
- **Beware typosquatting.** `reqeusts` instead of `requests`, `loadash` instead of `lodash` — malicious packages squat on typos. Install exactly what the README says.
- **Audit regularly.** `npm audit`, `pip-audit`, `cargo audit` surface known CVEs in your dep tree. Gate CI on them.
- **Don't commit secrets in manifests.** A private dep's URL can embed a token (`git+https://token@host/repo`). Use environment-variable indirection or a private registry with token-based auth.
- **System package updates are security updates.** Run `apt upgrade` / `dnf upgrade` weekly; outdated OpenSSL is a common entry vector.
- **`sudo pip install` is worse than it looks.** Overwrites system files, breaks the OS package manager's view of the world, and runs arbitrary setup.py code as root. Always venv.

## Performance notes

- **`uv` is ~10–100× faster than `pip`** for resolve and install — Rust + aggressive caching. Well worth the switch.
- **`pnpm` is faster and disk-cheaper than `npm`** — a shared content-addressed store avoids copying dependencies per project.
- **`npm ci` skips resolution** (obeys the lockfile) — always faster than `npm install`.
- **CI cache.** Cache `~/.cache/uv`, `~/.npm`, or the equivalent; can turn a 60-second install into 5 seconds.
- **Avoid `pip install` inside every test run.** Build the env once per commit; cache the result.
- **Container image layers.** Copy `requirements.txt` / `package-lock.json` *before* your source code so dependency-layer caches survive code changes. See [Module 14 — Dockerfiles](../14-docker/06-dockerfiles.md).

## Common mistakes

- **`sudo pip install` on system Python.** Symptom: OS `apt` breaks later. Cause: pip overwrote files `apt` manages. Fix: venv; or `pipx` for CLIs; or `--user`.
- **Global `npm install -g`.** Symptom: projects silently pick up a global version that differs from `package.json`. Fix: use `npx` or `npm exec` to run project-scoped binaries.
- **Missing lockfile.** Symptom: CI installs different versions than your laptop. Cause: lockfile not committed. Fix: commit `package-lock.json` / `poetry.lock`.
- **`pip install foo` then `import foo` fails.** Symptom: module not found. Cause: you ran `pip` from one Python but `python3` from another (system vs. venv). Fix: `python3 -m pip install foo`, or check `which pip`.
- **Over-pinning everything.** Symptom: `pip install` fails to resolve because two deps want different versions of a transitive. Cause: `==1.2.3` pins everywhere. Fix: pin top-level only; let the resolver handle transitives.
- **Trust the PyPI name.** Symptom: `pip install crypto` installs something unexpected. Cause: similarly-named packages. Fix: read README carefully; prefer well-known names; audit before use.

## Practice

1. **Warm-up.** Install `htop` with your system package manager.
2. **Standard.** Create a Python venv, install `httpx`, write a 3-line script that fetches `https://example.com` and prints its HTTP status.
3. **Bug hunt.** `pip install foo` reports success, but `python3 -c "import foo"` says `ModuleNotFoundError`. What went wrong? How do you verify the fix?
4. **Stretch.** Write a `Makefile` target `setup` that creates the venv, installs deps from `requirements.txt`, and prints the Python version it'll use.
5. **Stretch++.** Dockerize the Node example so `docker build -t hello .` then `docker run hello` prints `hi`. (Forward reference to [Module 14](../14-docker/README.md).)

<details><summary>Show solutions</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install httpx
python3 -c 'import httpx; print(httpx.get("https://example.com").status_code)'
```

3. Almost always a pip/python mismatch — you ran `pip` from the system Python (which installed the module somewhere `python3` can't see). Diagnose with `which pip && which python3 && python3 -m pip list | grep foo`. Fix: `python3 -m pip install foo` (runs pip for the *specific* Python you just typed).

```makefile
.PHONY: setup
setup:
	python3 -m venv .venv
	./.venv/bin/pip install -r requirements.txt
	@./.venv/bin/python --version
```

</details>

## Quiz

1. Virtual environments isolate:
    (a) the OS (b) Python interpreter + packages per project (c) env vars (d) files
2. `npm ci` vs. `npm install`:
    (a) both identical (b) `ci` strictly obeys the lockfile (c) `ci` ignores the lockfile (d) `ci` is deprecated
3. A lockfile captures:
    (a) what you asked for (b) exact resolved versions including transitives (c) nothing (d) source code
4. `apt`, `dnf`, and `brew` install:
    (a) per-project (b) per-user (c) system-wide (d) in-memory
5. `pip install --user foo` installs:
    (a) system-wide (b) in the current venv (c) under `~/.local` (d) ephemerally

**Short answer:**

6. Why not `sudo pip install` system-wide?
7. What's the difference between a manifest and a lockfile, and why commit both?

*Answers: 1-b, 2-b, 3-b, 4-c, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-packages — mini-project](mini-projects/06-packages-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- System PM for shared tools; language PM per project.
- Virtual environments + lockfiles = reproducibility.
- Commit both manifest *and* lockfile; use `npm ci`/`uv sync` in CI.
- Never `sudo pip install` on system Python; never trust `curl | bash`.

## Further reading

- [PEP 668 — Marking Python base environments as externally managed](https://peps.python.org/pep-0668/).
- [`uv` documentation](https://docs.astral.sh/uv/) — the future of Python packaging.
- Next module: [Module 03 — Git](../03-git/README.md).
