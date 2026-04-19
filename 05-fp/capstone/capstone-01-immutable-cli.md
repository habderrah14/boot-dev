# Capstone 01 — Immutable CLI (after Module 05)

Build a CLI that transforms structured input with a functional core and imperative shell.

## Goal

Practice pure-function composition, deterministic behavior, and testable boundaries.

## Requirements

- Parse JSON input from stdin/file.
- Process through pure transformation pipeline.
- Emit JSON output to stdout.
- Include unit tests for all core transforms.
- No hidden global state in transformation layer.

## Success criteria

- Reproducible output for identical input.
- Test suite covers happy path + edge cases.
- README includes run/test instructions.

## Stretch

Add configurable pipeline stages via closure-based plugin functions.
