# Mini-project track — Python Fundamentals Companion

## Goal

Build one CLI app that grows with each lesson. Start tiny and keep shipping small milestones.

## Project idea

Create `study_cli.py`, a command-line helper that stores study notes and progress.

## Rules

- Keep one codebase for the whole module.
- Add features only after the required chapter.
- Each checkpoint must stay runnable.

## Checkpoint A — Variables (after Chapter 02)

- Add constants for app name/version.
- Store one note in named variables and print a formatted line.
- Validate that empty input is rejected.

**Done when:** `python study_cli.py` prints exactly this output shape:

```text
Python Study CLI v0.1
Note: <your note text>
Status: valid
```

## Checkpoint B — Functions (after Chapter 03)

- Extract logic into functions: `add_note`, `format_note`, `main`.
- Ensure business logic functions return values (do not print directly).
- Add one small test file or manual test script for happy path.

**Done when:** functions are reusable and output still matches Checkpoint A behavior.

## Checkpoint C — Scope (after Chapter 04)

- Remove accidental globals from feature logic.
- Keep configuration constants global, operational state local.
- Fix one deliberate scope bug (`UnboundLocalError` or shadowed built-in).

**Done when:** no helper function mutates global runtime state by accident.

## Checkpoint D — Loops (after Chapter 08)

- Add a loop-based menu (`add`, `list`, `exit`).
- Use `for` to render all notes and `while` for menu loop.
- Handle invalid commands without crashing.

**Done when:** user can add multiple notes and list them in one run.

## Optional later checkpoints

- Lists/Dicts/Sets chapters: structured in-memory storage.
- Errors chapter: explicit exception handling paths.

## Stretch

- Save/load notes from JSON.
- Add simple tags and deduplication.
