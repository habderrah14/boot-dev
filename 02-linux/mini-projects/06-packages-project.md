# Mini-project — 06-packages

_Companion chapter:_ [`06-packages.md`](../06-packages.md)

**Goal.** Produce a fresh-clone reproducible project with two parts: a Python CLI (using `click`) and a Node TS script. Prove reproducibility by wiping `.venv/` and `node_modules/`, running the README instructions, and confirming both still work.

**Acceptance criteria.**

- `README.md` lists exactly the commands a teammate needs.
- `.gitignore` excludes `.venv/`, `node_modules/`, `__pycache__/`, `.env`.
- Python CLI: `hello --name Ada` prints `Hi, Ada!`.
- Node TS script: `npm run start` prints `hi` after compilation.
- Both projects commit their lockfile.
- `rm -rf .venv node_modules && <README commands>` reproduces the working state end to end.

**Hints.** Use `pyproject.toml` + `uv` for Python if you want to try modern tooling; `requirements.txt` is still fine. For Node, `package.json` scripts like `"start": "tsc && node dist/index.js"` work.

**Stretch.** Add a `Makefile` or `justfile` with a `make all` target that runs both projects' setups in parallel.
