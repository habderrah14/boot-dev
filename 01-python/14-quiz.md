# Chapter 14 — Module Quiz

> A 30-question self-assessment covering everything in Module 01. If you miss more than four, re-read the chapters they pulled from.

## Learning objectives

By the end of this chapter you will be able to:

- Self-assess readiness for Module 02.
- Identify weak areas to revisit before moving on.

## Prerequisites & recap

- Chapters 01–13 of this module.

## The simple version

A 30-question, mixed-format quiz. Closed book, 30 minutes. Use it to find your weak spots — not to "pass". A perfect score means nothing if you can't reproduce the underlying skill on Module 02's first chapter.

## In plain terms (newbie lane)

This chapter is really about **Module Quiz**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How to use this quiz to plan your re-reading.

```
   Take quiz                       Score
   (30 min)   ──▶  Mark answers ──▶  ?
                                    │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
            ≥ 26                 21–25                ≤ 20
              │                    │                    │
              ▼                    ▼                    ▼
   Proceed to Module 02   Re-read top 2-3        Re-read entire
                          weak chapters,         module before
                          retake quiz            continuing
```

## Concept deep-dive

### Instructions

- **Closed book.** No grep, no IDE, no REPL.
- **30 minutes.** Time pressure simulates how you'll recall under interview/work conditions.
- **Mark each answer letter** before checking — it's tempting to "remember" the right answer once you see it.
- **Map wrong answers to chapters** using the mapping at the bottom; re-read those chapters before continuing.

### Why timed quizzes matter

Long-term retention research (Karpicke & Roediger, 2008) shows that **retrieval practice** — being asked to recall, not re-read — is the single most effective learning move. A timed quiz is retrieval practice with friction, which is the point.

## Why these design choices

- **30 questions, mixed difficulty.** Enough to surface weak chapters; short enough to take in one sitting.
- **Single-best-answer multiple choice.** Easy to self-grade. Short-answer questions live in each chapter.
- **No partial credit.** You either know `xs.sort()` returns `None` or you don't.
- **Chapter mapping in the answer key.** Tells you *which* chapter to re-read, not just that you missed.
- **When you'd choose differently.** A live mock interview is a stronger test for a job-hunt context (see [Module 16, chapter 08](../16-job-hunt/08-interviewing.md)). For *learning*, this format wins.

## Production-quality code

This chapter is a quiz. The "production" lives in chapters 01–13.

## Security notes

**N/A — this is a self-assessment chapter.** Re-read [chapter 12](12-errors.md) for security-adjacent content (custom exceptions, never logging secrets in messages).

## Performance notes

**N/A — this is a self-assessment chapter.** Re-read [chapter 06](06-computing.md) and [chapter 09](09-lists.md) for the cost models that matter.

## Common mistakes

- **Looking up answers as you go.** Symptom: 30/30 score, no real signal. Fix: closed book.
- **Re-reading without retaking.** Symptom: same wrong answers next time. Fix: re-read, then retake the relevant questions a day later.
- **Skipping the mapping.** Symptom: vague "I should review Python". Fix: identify the *chapter* and re-read it specifically.
- **Treating this as a gate, not a diagnostic.** Symptom: anxiety on retakes. Fix: the goal is signal, not score.

## The quiz

1. What does `python3` display when run with no arguments?
    (a) error (b) help (c) the REPL (d) the version
2. Which is **not** a Python literal?
    (a) `3_000` (b) `0b101` (c) `"str"` (d) `{key:}`
3. What is the type of `3 / 2`?
    (a) `int` (b) `float` (c) `Decimal` (d) error
4. `7 // -2` equals:
    (a) `-3` (b) `-4` (c) `3` (d) `-3.5`
5. Which of these is falsy?
    (a) `"False"` (b) `"0"` (c) `0.0` (d) `[False]`
6. What does `is` check?
    (a) equality (b) identity (c) subtype (d) truthiness
7. `x = 5; y = x; x = 10` — `y` is:
    (a) 5 (b) 10 (c) alias of x (d) `None`
8. Which creates an empty set?
    (a) `{}` (b) `set()` (c) `()` (d) `[]`
9. `len({1, 1, 2})`:
    (a) 1 (b) 2 (c) 3 (d) undefined
10. A dict's key must be:
    (a) a str (b) hashable (c) unique and hashable (d) an int
11. `"a b c".split()`:
    (a) `["a", " ", "b", " ", "c"]` (b) `["a", "b", "c"]` (c) `"abc"` (d) error
12. `"abc"[::-1]`:
    (a) `"abc"` (b) `"cba"` (c) error (d) `""`
13. Which is immutable?
    (a) list (b) set (c) dict (d) tuple
14. `range(1, 10, 3)`:
    (a) `1, 4, 7` (b) `1, 3, 6, 9` (c) `1, 2, ..., 9` (d) `[1, 10, 3]`
15. A `def f(x=[])` default is dangerous because:
    (a) lists aren't allowed (b) the default is shared across calls (c) Python copies it (d) only `None` may be a default
16. `try/except/else`: `else` runs when:
    (a) exception was caught (b) no exception (c) always (d) never
17. `with open(...)` ensures:
    (a) file exists (b) file flushes each write (c) file is closed (d) file is locked
18. Bare `except:` also catches:
    (a) only user exceptions (b) `SystemExit` and `KeyboardInterrupt` (c) only `Exception` subclasses (d) nothing
19. `{"a": 1}.get("b", 9)`:
    (a) `None` (b) `9` (c) raises (d) `0`
20. `[x*x for x in range(3)]`:
    (a) `[0, 1, 4]` (b) `[1, 4, 9]` (c) generator (d) `[2, 4, 6]`
21. `a, b = b, a` does:
    (a) errors (b) swap (c) equal-assignment (d) creates a tuple
22. `sorted({3, 1, 2})`:
    (a) `[1, 2, 3]` (b) `{1, 2, 3}` (c) `None` (d) `(1, 2, 3)`
23. LEGB describes:
    (a) loop order (b) name resolution (c) exception order (d) file I/O
24. `nonlocal` is for:
    (a) globals (b) enclosing non-global names (c) class attributes (d) imports
25. `breakpoint()` in 3.12 opens:
    (a) gdb (b) pdb (c) ipdb (d) whatever `PYTHONBREAKPOINT` points at
26. Which sort is stable in CPython?
    (a) `sorted` (b) `list.sort` (c) both (d) neither
27. Which is O(1) average on a dict?
    (a) `in` (b) `keys()` (c) iteration (d) `copy`
28. `assert` is removed by:
    (a) `-O` (b) `-v` (c) `-B` (d) nothing
29. Prefer `{0, 1, 2}` over `[0, 1, 2]` when:
    (a) order matters (b) membership is the dominant op (c) you need indexing (d) duplicates are meaningful
30. Which measures of progress does this module encourage?
    (a) LOC (b) tests green + runnable code (c) stars on GitHub (d) books read

## Answer key (with chapter mapping)

```
 1.  c (ch.01)    11. b (ch.13)    21. b (ch.02)
 2.  d (ch.02)    12. b (ch.09)    22. a (ch.09)
 3.  b (ch.06)    13. d (ch.09)    23. b (ch.04)
 4.  b (ch.06)    14. a (ch.08)    24. b (ch.04)
 5.  c (ch.02)    15. b (ch.03)    25. d (ch.05)
 6.  b (ch.07)    16. b (ch.12)    26. c (ch.09)
 7.  a (ch.02)    17. c (ch.12)    27. a (ch.10)
 8.  b (ch.11)    18. b (ch.12)    28. a (ch.05)
 9.  b (ch.11)    19. b (ch.10)    29. b (ch.11)
10.  c (ch.10)    20. a (ch.08)    30. b (ch.05)
```

### Retake policy

- **≥ 26/30** — proceed to [Module 02 — Linux](../02-linux/README.md).
- **21–25** — re-read your two or three weakest chapters, retake the related questions in 24 hours.
- **≤ 20** — re-read the whole module before continuing. The cumulative weight of the gaps will compound across later modules.

## Practice

Take the quiz once now. Take it again in 7 days, closed book, and compare scores. Spaced retrieval is how this material moves from "I read it" to "I know it".

## Quiz

This chapter *is* the quiz.

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [14-quiz — mini-project](mini-projects/14-quiz-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

You now know the core of Python: values, names, control flow, functions, the big-three containers (list, dict, set), plus how to test and handle failure. The rest of the path trusts these.

## Further reading

- Karpicke & Roediger, [*The Critical Importance of Retrieval for Learning*](https://science.sciencemag.org/content/319/5865/966) (2008) — why timed retrieval beats re-reading.
- *Effective Python* by Brett Slatkin — for items you wish were in this module.
- Next module: [Module 02 — Linux](../02-linux/README.md).
