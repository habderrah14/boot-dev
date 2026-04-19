# Mini-project — 01-c-basics

_Companion chapter:_ [`01-c-basics.md`](../01-c-basics.md)

**Goal.** Build a 2-file C project: `mathu.c` / `mathu.h` exports `int add(int, int)` and `int mul(int, int)`. A `main.c` reads two integers from command-line arguments and prints the sum and product. Include a `Makefile`.

**Acceptance criteria:**

- Compiles cleanly with `cc -Wall -Wextra -std=c17 -O2`.
- Prints usage to `stderr` and exits with non-zero status on wrong argument count.
- `make clean && make` works from scratch.

**Hints:**

- `atoi()` converts a string to int. It's not safe for production (no error checking) but fine here.
- Remember `EXIT_SUCCESS` and `EXIT_FAILURE` from `<stdlib.h>`.

**Stretch:** Replace `atoi` with `strtol` and print an error if the argument isn't a valid integer.
