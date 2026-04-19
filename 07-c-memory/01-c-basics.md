# Chapter 01 — C Basics

> "C is a small language with big stakes. You tell the machine exactly what to do; it does exactly that — including the wrong thing, if you asked for it."

## Learning objectives

By the end of this chapter you will be able to:

- Compile and run a C program with `gcc`/`clang` and explain what each compiler flag does.
- Use the core types: `int`, `float`, `double`, `char`, `size_t`, and their fixed-width cousins.
- Write functions with proper prototypes and split code across multiple files.
- Use `stdio.h` basics: `printf`, `scanf`, `fprintf`, `stderr`.
- Recognize and avoid the most common forms of undefined behavior.

## Prerequisites & recap

- A Linux/macOS terminal with a C compiler installed (`sudo apt install build-essential` on Debian/Ubuntu, or Xcode Command Line Tools on macOS).
- Comfort reading any programming language — you don't need prior C experience.

## The simple version

C is a thin wrapper over what the CPU actually does. You declare variables (the compiler picks registers or memory for them), call functions (the CPU jumps to their address), and return values. There is no garbage collector, no runtime, no hidden magic. The compiler translates your `.c` file into machine code, a linker glues pieces together, and you get a single binary. If you forget to handle something — say, a null pointer or an uninitialized variable — the program doesn't throw a friendly exception. It just does something unpredictable, which C calls *undefined behavior*.

Think of C as driving a manual-transmission car: more control, more responsibility, and a very real chance of stalling if you skip a step.

## Visual flow

```
  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
  │  .c file │──▶│   cpp    │──▶│    cc     │──▶│   .o     │──▶│  a.out   │
  │ (source) │   │(preproc) │   │(compile)  │   │(object)  │   │(binary)  │
  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
       │                                              │
       │         #include expands headers              │
       │         #define expands macros                 │
       └── .h ──────────────────────────────────────────┘
                                                linker merges
                                                all .o files
```

*Caption: The C build pipeline — preprocessor, compiler, linker.*

## Concept deep-dive

### Why C for backend developers?

You're here because you want to understand what happens *below* Python, Go, or Node. Every runtime you'll ever use is written in C or C++. Understanding C makes you better at debugging performance problems, reasoning about memory, and reading systems code. The language is small — roughly 30 keywords — but the responsibility model is different from anything managed.

### Hello, backend

```c
#include <stdio.h>

int main(void) {
    printf("Hello, backend!\n");
    return 0;
}
```

Compile and run:

```bash
cc -Wall -Wextra -std=c17 -O2 hello.c -o hello
./hello
```

Why those flags?

- `-Wall -Wextra` — enable most warnings. C lets you write dangerous code silently; these flags make the compiler speak up.
- `-std=c17` — use the C17 standard. Without this, your compiler picks a default that may be C89 or a GNU extension soup.
- `-O2` — optimize reasonably. You get faster code *and* some extra warnings that only appear during optimization analysis.

### Types

| Type | Size (typical) | Notes |
|---|---|---|
| `char` | 1 byte | Signedness is implementation-defined |
| `int` | 4 bytes | Platform-dependent; spec guarantees ≥ 16 bits |
| `long` | 4 or 8 | 8 on most 64-bit Linux/macOS |
| `long long` | ≥ 8 | Guaranteed at least 64 bits |
| `float` | 4 | IEEE-754 single precision |
| `double` | 8 | IEEE-754 double precision |
| `size_t` | 4 or 8 | Unsigned, from `<stddef.h>` |

Why is `int` not always 4 bytes? Because C was designed to run on everything from 16-bit microcontrollers to 64-bit servers. The spec says `int` is "the natural word size" — deliberately vague.

The fix: `#include <stdint.h>` gives you `int32_t`, `uint64_t`, etc. Use these when you need a specific width. Use `int` when the exact size doesn't matter (loop counters, boolean-ish flags).

### Formatted I/O

```c
int x = 42;
double pi = 3.14159;
printf("x=%d pi=%.2f\n", x, pi);
```

Key format specifiers:

| Specifier | Type |
|---|---|
| `%d` | `int` |
| `%u` | `unsigned int` |
| `%ld` / `%lu` | `long` / `unsigned long` |
| `%lld` | `long long` |
| `%f` / `%e` / `%g` | `double` (and `float` via promotion) |
| `%s` | `char *` (string) |
| `%c` | `char` |
| `%p` | pointer |
| `%zu` | `size_t` |

Why does mismatching specifier and argument matter so much? Because `printf` trusts you. It reads bytes off the stack according to the format string. If you say `%d` but pass a `double`, it reads 4 bytes of an 8-byte value and interprets them as an integer. That's undefined behavior, and `-Wformat` (included in `-Wall`) catches it at compile time.

### Functions and prototypes

```c
int add(int a, int b);      /* prototype (declaration) */

int main(void) {
    printf("%d\n", add(2, 3));
    return 0;
}

int add(int a, int b) {     /* definition */
    return a + b;
}
```

Why separate declaration from definition? Because C compiles top-to-bottom in a single pass. Without the prototype, the compiler hasn't seen `add` when `main` calls it. In older C standards, the compiler would *guess* the return type is `int` — and sometimes guess wrong. Prototypes eliminate that guessing.

Put prototypes in `.h` header files. Put definitions in `.c` source files. This is how C achieves modularity.

### Undefined behavior — the silent killer

Undefined behavior (UB) means the C standard imposes *no requirements* on what happens. The compiler is free to do anything: crash, silently corrupt data, optimize away your safety check, or — most dangerously — appear to work on your machine and fail on the production server.

Common UB triggers at this stage:

- Reading an uninitialized variable.
- Signed integer overflow.
- Mismatching `printf` format specifiers.
- Dereferencing a null pointer (more in ch. 03).

Your best defense is compiler warnings (`-Wall -Wextra`) and, once you're comfortable, `-Werror` to promote warnings to errors.

## Why these design choices

**Why no runtime safety checks?** C was born at Bell Labs in 1972 to write Unix. Every bounds check or null guard costs CPU cycles. On a PDP-11 with kilobytes of RAM, those cycles mattered. The philosophy: the programmer knows what they're doing. Modern languages chose differently because hardware got fast enough that safety is worth the cost.

**Why headers and separate compilation?** To avoid recompiling everything when one file changes. In a large project, you compile each `.c` to a `.o` independently, then link. Only the changed `.c` needs recompilation.

**When would you pick something different?** If you don't need direct hardware control or extreme performance, use a memory-safe language. Rust gives you C-level performance with compile-time safety. Go gives you garbage collection with decent performance. C is the right choice when you're writing an OS kernel, an embedded system, a language runtime, or when you need to understand the machine at the lowest practical level.

## Production-quality code

### Multi-file project

`mathu.h`:

```c
#pragma once

int add(int a, int b);
int mul(int a, int b);
```

`mathu.c`:

```c
#include "mathu.h"

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }
```

`main.c`:

```c
#include <stdio.h>
#include <stdlib.h>
#include "mathu.h"

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: app <a> <b>\n");
        return EXIT_FAILURE;
    }
    int a = atoi(argv[1]);
    int b = atoi(argv[2]);

    printf("add=%d  mul=%d\n", add(a, b), mul(a, b));
    return EXIT_SUCCESS;
}
```

`Makefile`:

```makefile
CC      = cc
CFLAGS  = -Wall -Wextra -std=c17 -O2

app: main.c mathu.c
	$(CC) $(CFLAGS) main.c mathu.c -o app

clean:
	rm -f app
```

Build and run:

```bash
make && ./app 3 4
# add=7  mul=12
```

### stderr vs. stdout

```c
#include <stdio.h>

int main(void) {
    printf("data goes to stdout\n");
    fprintf(stderr, "errors go to stderr\n");
    return 0;
}
```

Why two streams? So you can redirect data to a file (`./app > out.txt`) while still seeing errors on your terminal. Every production CLI tool relies on this separation.

## Security notes

- **Format string attacks**: never pass user input as the first argument to `printf`. Writing `printf(user_input)` lets an attacker read stack memory with `%x` or write to arbitrary addresses with `%n`. Always use `printf("%s", user_input)`.
- **`gets()` is removed**: it was deleted from the C11 standard because it cannot prevent buffer overflows. Use `fgets(buf, sizeof buf, stdin)` instead.
- **Uninitialized memory**: reading uninitialized stack variables can leak sensitive data from previous function calls.

## Performance notes

- Compilation flags matter more than you'd expect. `-O2` enables inlining, loop unrolling, and dead-code elimination. `-O0` (the default) produces code that's easy to debug but 2–10× slower.
- `printf` is buffered on `stdout` (line-buffered to a terminal, fully buffered to a file). `stderr` is unbuffered by default. This is why forgetting `\n` in `printf` can make output appear delayed.
- Function calls have near-zero overhead on modern CPUs, but the compiler may inline small functions at `-O2` anyway.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Output doesn't appear until program exits | Missing `\n` in `printf`; stdout is line-buffered | Add `\n`, or call `fflush(stdout)` |
| Compiler says "implicit declaration of function" | Called a function before declaring it; missing `#include` or prototype | Add the correct header or write a prototype |
| `printf` prints garbage for a `double` | Used `%d` instead of `%f` — format/type mismatch is UB | Match specifier to type; compile with `-Wall` |
| "Redefinition of struct" errors | Header included twice without an include guard | Add `#pragma once` or `#ifndef` guards |
| Program segfaults with no useful backtrace | Compiled without debug info | Add `-g` flag; run under `gdb` or `lldb` |

## Practice

**Warm-up.** Compile and run the `hello.c` program from the deep-dive. Experiment with removing `-Wall` and introducing a format mismatch — observe what the compiler catches.

**Standard.** Write a program that reads two integers with `scanf` and prints their sum, difference, and product.

**Bug hunt.** This code compiles without errors on some compilers. What's wrong?

```c
int main(void) {
    double pi = 3.14159;
    printf("%d\n", pi);
    return 0;
}
```

**Stretch.** Split exercise 2 across three files: `math_ops.h` (prototypes), `math_ops.c` (definitions), and `main.c`. Write a `Makefile` that builds them.

**Stretch++.** Write a program that reads lines from `stdin` until EOF using `fgets`, counts the lines and total characters, and prints a summary to `stdout`. Errors go to `stderr`.

<details><summary>Solutions</summary>

**Bug hunt.** `%d` expects an `int`, but `pi` is a `double`. `printf` reads 4 bytes off the stack, interprets them as an integer, and prints garbage. This is undefined behavior. Fix: use `%f` or `%g`.

**Standard.**

```c
#include <stdio.h>
int main(void) {
    int a, b;
    printf("Enter two integers: ");
    if (scanf("%d %d", &a, &b) != 2) {
        fprintf(stderr, "Invalid input\n");
        return 1;
    }
    printf("sum=%d diff=%d prod=%d\n", a + b, a - b, a * b);
    return 0;
}
```

**Stretch++.**

```c
#include <stdio.h>
#include <string.h>
int main(void) {
    char buf[4096];
    size_t lines = 0, chars = 0;
    while (fgets(buf, sizeof buf, stdin)) {
        lines++;
        chars += strlen(buf);
    }
    if (ferror(stdin)) {
        fprintf(stderr, "read error\n");
        return 1;
    }
    printf("lines=%zu chars=%zu\n", lines, chars);
    return 0;
}
```

</details>

## In plain terms (newbie lane)
If `C Basics` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. What does `int main(void)` return?
    (a) void  (b) int  (c) size_t  (d) bool

2. Which type guarantees exactly 32 bits?
    (a) `int`  (b) `int32_t`  (c) `long`  (d) `short`

3. The `%zu` format specifier is for:
    (a) `int`  (b) `size_t`  (c) `char *`  (d) `double`

4. Including a header twice without guards causes:
    (a) nothing  (b) redefinition errors  (c) faster compilation  (d) linker warnings

5. `-Wall -Wextra` flags:
    (a) slow the compiler significantly  (b) enable many useful warnings  (c) disable optimizations  (d) are ignored by clang

**Short answer:**

6. What is undefined behavior and why is it more dangerous than a runtime exception?
7. Why do C projects split declarations into `.h` files and definitions into `.c` files?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-c-basics — mini-project](mini-projects/01-c-basics-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- C compiles source to machine code with no runtime overhead — the compiler flags (`-Wall`, `-Wextra`, `-std=c17`) are what make it livable.
- Headers declare interfaces; source files define implementations. This separation enables incremental compilation.
- Use fixed-width types (`int32_t`, `uint64_t`) when size matters; use `int` when it doesn't.
- Undefined behavior is C's biggest footgun — always compile with warnings enabled.

## Further reading

- *The C Programming Language*, Kernighan & Ritchie — still the canonical introduction.
- *Modern C*, Jens Gustedt — free online, covers C17.
- Next: [Structs](02-structs.md).
