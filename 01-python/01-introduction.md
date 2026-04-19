# Chapter 01 — Introduction

> You are about to spend a year writing code. This chapter invests in one small, powerful idea: programming is a conversation between you and a machine that cannot guess what you meant.

## Learning objectives

By the end of this chapter you will be able to:

- Install Python 3.12+ and run a program from both the REPL and a file.
- Describe what an interpreter does and how it differs from a compiler.
- Explain why Python is a good starting language for a backend developer.
- Read the shape of a Python program (indentation, statements, expressions, comments).

## Prerequisites & recap

You should already be comfortable with:

- A working terminal. See [Module 02 ch. 01](../02-linux/01-terminals-and-shells.md) if yours is uncooperative.
- That's it.

This is the first chapter — there is nothing to recap.

## The simple version

A **program** is a list of instructions written in a language a computer can execute. Python is one such language; the *Python interpreter* (a program named `python3` on your machine) reads your file line by line and performs each instruction immediately. You write text, you run it, the machine acts.

The whole rest of this module is just learning what kinds of instructions Python understands and how to combine them into useful behavior.

## In plain terms (newbie lane)

This chapter is really about **Introduction**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

What happens when you run `python3 hello.py`.

```
   hello.py            python3 (CPython)            terminal
   ────────            ─────────────────            ────────
   print("hi")  ─────▶ parse to bytecode  ─────▶
                       execute on VM      ──▶ stdout: hi
                                         └──▶ exit code: 0
```

Your file becomes bytecode (often cached in `__pycache__/*.pyc`), the virtual machine runs it, output goes to standard output (your terminal by default), and the process exits with a status code.

## Concept deep-dive

### What is Python?

Python is a high-level, **interpreted**, **dynamically-typed**, general-purpose language designed in 1989 by Guido van Rossum. In backend practice you use it for:

- Web services (FastAPI, Django).
- Data processing and glue code (parsing files, calling APIs).
- Scripting and automation (DevOps, infrastructure tooling).
- Machine-learning workloads, increasingly part of every backend.

"Interpreted" means a program (`python3`, the **CPython** reference implementation) reads your source and runs it on a virtual machine — there's no separate "compile then ship binary" step. "Dynamically typed" means types are checked while the code runs, not before. Both are trade-offs you'll re-examine in [Module 09: TypeScript](../09-ts/README.md).

### The shape of a Python program

```python
# Comments start with '#'.
greeting = "hello"
name = "world"
print(f"{greeting}, {name}!")
```

Key observations:

- **Indentation is grouping.** Four spaces by convention. Python *refuses to run* if indentation is inconsistent.
- **No semicolons** at line ends, **no braces** around blocks.
- One statement per line (you can stretch a line with `\` or parentheses, but rarely should).
- `#` to end-of-line is a comment.

### Two ways to run Python

1. **REPL (Read–Eval–Print Loop).** Type `python3` in the terminal. You get a `>>>` prompt. Each expression is evaluated and its result printed. Great for quick experiments.
2. **File mode.** Save code to `hello.py`, run `python3 hello.py`. The file executes top-to-bottom.

A typical workflow uses both: prototype in the REPL, paste into a file once it works.

### Interpreter vs. compiler

A **compiler** translates the entire source to machine code ahead of time, producing an executable. A C program is compiled. An **interpreter** reads the source and performs the actions itself. Python sits slightly in the middle: it compiles to bytecode automatically, then interprets the bytecode. Faster than pure interpretation, slower than ahead-of-time machine code.

**Why this matters:** the trade-off you accept by choosing Python is runtime speed in exchange for development speed. We'll quantify this in [Module 06](../06-dsa/README.md) and reach for C in [Module 07](../07-c-memory/README.md) where the trade tilts the other way.

## Why these design choices

- **Why Python first?** Two reasons. (1) Syntax that reads close to English keeps your attention on the *concepts* (variables, functions, scope) instead of the punctuation. (2) Python's standard library is huge — you can build a real backend without taking on a single dependency on day one.
- **Why an interpreter?** It eliminates the build step, which keeps the inner loop short ("edit, run, see") and shortens the time you spend wondering whether a change took effect.
- **Why dynamic typing here, static typing later?** Dynamic typing is faster to write small programs in; static typing pays off as systems grow. Boot.dev's path teaches both because real backend work mixes them.
- **When you'd choose differently.** If your day-one job is writing a numeric kernel, latency-sensitive networking, or an embedded firmware blob, you'd reach for Rust, Go, or C from the start. Python is a poor fit for hard real-time or high-throughput-per-core workloads.

## Production-quality code

### Example 1 — The canonical "hello"

`hello.py`:

```python
"""A minimal Python program — proof your environment works."""

if __name__ == "__main__":
    print("Hello, backend!")
```

Run it:

```bash
$ python3 hello.py
Hello, backend!
```

The `if __name__ == "__main__":` guard is technically optional here, but it's a habit worth forming on day one — it lets you `import hello` from another file later without `print` firing.

### Example 2 — REPL math

```text
$ python3
Python 3.12.0 (...) on linux
>>> 2 + 2
4
>>> seconds_per_day = 60 * 60 * 24
>>> seconds_per_day
86400
>>> seconds_per_year = seconds_per_day * 365
>>> seconds_per_year
31_536_000
```

The REPL evaluates each expression and prints the result. Assignments are silent — that's why `seconds_per_day = ...` produced no output but `seconds_per_day` on its own did. Underscores in numeric literals (Python 3.6+) are purely cosmetic and aid readability.

## Security notes

Day-one Python scripts touch almost no security surface, but two habits start now:

- **Never hard-code secrets** (API keys, passwords, tokens) in source files. Even toy scripts get pushed to GitHub by accident. Use environment variables or a secrets manager from the very first program.
- **Be skeptical of `input()` and `eval()`.** `eval(user_input)` evaluates *arbitrary code*. It's almost never the right tool. We'll cover safe parsing in [Module 10 — JSON](../10-http-clients/06-json.md).

## Performance notes

- Python startup costs ~30–80 ms per `python3` invocation. For one-shot scripts this is negligible; for command-line tools called in tight loops (e.g. shell pipelines), it matters.
- **CPython is single-threaded** for CPU-bound code due to the Global Interpreter Lock (GIL). Concurrency needs `asyncio` (I/O-bound), `multiprocessing` (CPU-bound), or moving to a different runtime.
- A rough cost model for arithmetic: native C does ~10⁹ simple operations/sec; CPython does ~10⁷–10⁸. You will rarely notice for backend code that mostly waits on databases and the network.

## Common mistakes

- **Wrong Python.** Symptom: `print("hi", end="")` syntax errors, or `print "hi"` works. Cause: your `python` is Python 2. Fix: use `python3`; check with `python3 --version`.
- **Mixed indentation.** Symptom: `IndentationError: unexpected indent`. Cause: spaces and tabs mixed in the same block. Fix: configure your editor to insert 4 spaces for the Tab key, then re-indent.
- **Wrong directory.** Symptom: `python3 hello.py` → `No such file or directory`. Cause: your terminal is not where the file is. Fix: `pwd`, then `cd` to the right folder.
- **Stray characters from copy-paste.** Symptom: weird `SyntaxError` on a line that looks fine. Cause: smart quotes (`"` vs `"`) or non-breaking spaces from a webpage. Fix: retype the line.

## Practice

1. **Warm-up.** In a file, print your own name.
2. **Standard.** In the REPL, calculate seconds in a year (assume 365 days). Use intermediate variables with descriptive names.
3. **Bug hunt.** This file won't run — fix it without changing what it prints:

    ```python
    print("one")
      print("two")
    print("three")
    ```

4. **Stretch.** Write `area.py` that prints the area of a 5×7 rectangle. Hard-code the values for now.
5. **Stretch++.** Add a second rectangle of size 3×4 and print the *sum* of the two areas, formatted with `f"Total: {total} sq units"`.

<details><summary>Show solutions</summary>

```python
print("Your Name")
```

```python
seconds_per_minute = 60
seconds_per_hour = seconds_per_minute * 60
seconds_per_day = seconds_per_hour * 24
seconds_per_year = seconds_per_day * 365
print(seconds_per_year)  # 31_536_000
```

Bug hunt: the second `print` is indented for no reason. Indentation in Python only follows colons (`:`). Unindent it.

```python
width = 5
height = 7
print(width * height)
```

```python
a = 5 * 7
b = 3 * 4
total = a + b
print(f"Total: {total} sq units")
```

</details>

## Quiz

1. What does the Python interpreter do?
    (a) Converts source to machine code once, then runs the machine code (b) Reads and executes source (or bytecode) at runtime (c) Checks types before execution (d) Compiles to Java bytecode
2. Which is **not** a valid way to write a comment in Python?
    (a) `# single-line` (b) `// single-line` (c) `"""docstring"""` (d) `# this also works`
3. `python3 hello.py` fails with `No such file or directory`. Most likely cause:
    (a) You are not in the directory containing `hello.py` (b) Python 3 is not installed (c) `hello.py` is empty (d) You forgot a semicolon
4. Which tool do you use to test a one-line expression quickly?
    (a) `cat` (b) An IDE debugger (c) `pip` (d) The REPL
5. Which is *always* true of a Python program?
    (a) It is compiled to an executable before running (b) Indentation groups statements into blocks (c) Statements must end in `;` (d) Files must be named `main.py`

**Short answer:**

6. In one sentence, what does "interpreted" mean?
7. Why does Python's GIL matter for backend developers?

*Answers: 1-b, 2-b, 3-a, 4-d, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-introduction — mini-project](mini-projects/01-introduction-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Python is an interpreted, dynamically-typed language run with `python3`.
- Programs are sequences of statements grouped by *indentation*, not braces.
- Use the REPL to experiment and `.py` files to save your work.
- Never hard-code secrets; never `eval` untrusted input.

## Further reading

- The official [Python tutorial](https://docs.python.org/3/tutorial/), chapters 1–2.
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/) — `import this`.
- Next: [variables](02-variables.md).
