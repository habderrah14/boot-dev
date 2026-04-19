# Mini-project — C Calculator

## Goal

Build a small command-line calculator in C that demonstrates compilation, headers, functions, and error handling.

## Deliverable

A 2–3 file C program plus a `Makefile`.

## Required behavior

1. Accept two integers and an operator (`+`, `-`, `*`, `/`).
2. Print usage to `stderr` on invalid arguments.
3. Split declarations into a header and implementations into a source file.
4. Compile with `cc -Wall -Wextra -std=c17 -O2`.
5. Exit non-zero on invalid input or divide-by-zero.

## Acceptance criteria

- Build works from a clean directory with one `make`.
- Uses `fprintf(stderr, ...)` for errors.
- No undefined behavior on invalid input.
- README explains build and run steps.

## Hints

- `strtol` is safer than `atoi` for parsing integers.
- Keep arithmetic helpers separate from CLI parsing.
- Use `EXIT_FAILURE` for error exits.

## Stretch goals

1. Support chaining multiple operations.
2. Add floating-point mode.
3. Add tests or a simple validation script.
