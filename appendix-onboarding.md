# Appendix — Onboarding (zero assumptions)

> Read this **once** before Module 01 if you are new to terminals, editors, or programming. It does not replace [Module 01](01-python/README.md); it removes the “hidden prerequisites” that make day one feel impossible.

## What you need installed

- **Python 3.12+** — `python3 --version` should print 3.12 or higher.
- **Node.js 20+** — needed from Module 08 onward (`node --version`).
- **Git** — `git --version`.
- **A text editor** with a built-in terminal (VS Code is fine).
- **PostgreSQL 16+** — only when you reach [Module 11](11-sql/README.md); install then, not on day one.

### Windows

Use **WSL2** with Ubuntu unless you already love native Windows tooling. Paths in this book look like `~/projects/...` — in WSL that is your Linux home, not `C:\Users\...`.

### macOS / Linux

You are the happy path. Use your package manager (`brew`, `dnf`, `apt`) for Postgres and optional tools later.

## First 30 minutes in the terminal

1. Open a terminal in your editor. Confirm where you are: `pwd`.
2. Make a scratch folder: `mkdir -p ~/mycourses-practice && cd ~/mycourses-practice`.
3. Start Python: `python3`. Type `1 + 1` and press Enter. Exit with `exit()` or Ctrl+D.
4. Create `hello.py` containing `print("hello")`. Run `python3 hello.py`.

If any step fails, copy the **full error text** into a search engine or Boot.dev community — the first skill is learning to read errors without shame.

## Reading Mermaid diagrams in this book

Chapters use [Mermaid](https://mermaid.js.org/) for flowcharts and sequences.

- **Solid arrows** usually mean “data or control flows this way next.”
- **Dashed lines** often mean “optional” or “happens sometimes.”
- **Boxes** are actors (programs, queues, humans). Read top-to-bottom unless arrows say otherwise.

Redraw diagrams by hand on paper once — it sticks faster than scrolling.

## How to read a Python traceback

Bottom line first: the **last** line says the exception type (`TypeError`, `ValueError`, …). The lines **above** show the call stack (who called whom). Your bug is almost always in **your** file, not inside library code — scroll until you see a path under `~/` or your project.

## Minimal repro (when you ask for help)

1. **What you ran** (exact command or “Run” button).
2. **What you expected** (one sentence).
3. **What happened** (paste traceback or wrong output).
4. **Smallest file** that still breaks (delete unrelated code until it still fails).

## Link map — first three modules

- [Module 01 — Python](01-python/README.md) — language + thinking in code.
- [Module 02 — Linux](02-linux/README.md) — shell, files, processes (where your programs run).
- [Module 03 — Git](03-git/README.md) — save history, collaborate, undo safely.

When you finish Module 03, skim [Shipping checklist](appendix-shipping-checklist.md) so future-you knows what “done” looks like on a real repo.
