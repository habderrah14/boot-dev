# Chapter 13 — Practice

> Reading about code is like reading about running. You will feel productive; you will not get fit. This chapter is the track.

## Learning objectives

By the end of this chapter you will be able to:

- Apply chapters 01–12 to small, complete problems with a repeatable workflow.
- Decompose a problem into named functions before writing them.
- Pick the right built-in data structure by recognizing the access pattern.
- Sustain the make-it-work / make-it-right / make-it-fast discipline.

## Prerequisites & recap

- All previous chapters in this module.

## The simple version

Real programs are built one small problem at a time. Adopt one workflow and apply it to *every* exercise: restate, example, shape, name, implement, test, clean. The discipline matters more than the order.

The shortcut to "expert" is not faster typing. It's pattern-recognition: noticing that "find duplicates" is a set problem, "count occurrences" is a `Counter` problem, "first-seen unique" is a dict-fromkeys problem. This chapter trains those patterns.

## In plain terms (newbie lane)

This chapter is really about **Practice**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The seven-step problem-solving loop.

```
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │  Restate  │ ─▶ │ Examples  │ ─▶ │  Shape    │
   └───────────┘    └───────────┘    │ (data)    │
                                     └─────┬─────┘
                                           ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │   Clean   │ ◀─ │   Tests   │ ◀─ │ Implement │
   └───────────┘    └───────────┘    └───────────┘
                                           ▲
                                           │
                                     ┌───────────┐
                                     │  Name     │
                                     │ functions │
                                     └───────────┘
```

When stuck, go back one box. When refactoring, you can re-enter at "Implement" — the previous boxes are recomputed mentally.

## Concept deep-dive

### The workflow in detail

1. **Restate.** In your own words, what's the input and what's the desired output? If you can't, you don't yet understand the problem.
2. **Examples.** Two or three concrete `(input, output)` pairs by hand. Include an edge case (empty, single element, duplicates).
3. **Shape.** Which data structure(s) carry the work? List? Dict? Set? Counter? Asking this *before* coding eliminates rewrites.
4. **Name functions.** Sketch signatures: `def parse(s: str) -> list[Token]`. Short, noun-named, single-purpose.
5. **Implement** the simplest path. Get the *first* example green.
6. **Tests.** Encode each hand-computed example as a unit test. Add edge cases.
7. **Clean.** Rename, extract, delete dead code. Re-run tests.

"Make it work, make it right, make it fast" — in that order. Trying to optimize before the tests are green wastes hours.

### Pattern recognition cheatsheet

| Phrase in the problem                               | Reach for…                            |
|----------------------------------------------------|---------------------------------------|
| "is X in this large collection?"                   | `set` (or `dict` lookup)              |
| "how many times does X appear?"                    | `Counter`                             |
| "group by Y"                                       | `defaultdict(list)`                   |
| "sorted, unique"                                   | `sorted(set(xs))`                     |
| "first-seen unique, preserve order"                | `dict.fromkeys` or seen-set + list    |
| "moving window"                                    | `collections.deque(maxlen=k)`         |
| "running total / running max"                      | one-pass loop with accumulator        |
| "matches a pattern"                                | `re` module                           |
| "two pointers" / "sorted halves"                   | hand-rolled loop, not slicing         |
| "depends on previous results"                      | memoization (`functools.lru_cache`)   |
| "cleanup must run"                                 | `with` context manager                |

### Reading vs. writing speed

A senior engineer types about as fast as a junior. The difference is the time *between* keystrokes — spent reading docs, reading existing code, sketching on paper, or pacing. Treat that as productive work; the IDE going quiet for two minutes is normal.

## Why these design choices

- **Restate-first beats code-first.** Most "I can't solve this" is "I haven't read the problem closely enough". Five minutes restating saves an hour debugging.
- **Examples before code.** Examples force you to confront the actual shape of input and output, including the edges. They double as the test cases.
- **Pattern recognition over algorithm memorization.** Real problems rarely match a textbook algorithm exactly. They *do* often match a "shape" — and the shape tells you which standard library to import.
- **Tests as a reward, not a chore.** Each green test is a cumulative gain; you can refactor later without fear.
- **When you'd choose differently.** Throw-away scripts and prototypes can skip steps 6–7. But "throw-away" code has a way of becoming production code; budget extra time the moment it survives a week.

## Production-quality code

### Example 1 — Top-K most frequent

```python
"""Top-K frequent words: a one-line problem given the right primitive."""

from collections import Counter
from typing import Iterable


def top_k(words: Iterable[str], k: int) -> list[str]:
    if k < 0:
        raise ValueError("k must be non-negative")
    return [w for w, _ in Counter(words).most_common(k)]


if __name__ == "__main__":
    print(top_k(["a", "b", "a", "c", "b", "a"], 2))   # ['a', 'b']
```

`Counter.most_common(k)` is implemented as a heap: O(n log k), not O(n log n). The standard library wins.

### Example 2 — Two-sum, the right way

```python
"""Find two indices whose values sum to target. O(n) one-pass."""


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}
    for i, n in enumerate(nums):
        j = seen.get(target - n)
        if j is not None:
            return (j, i)
        seen[n] = i
    return None


if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))    # (0, 1)
```

The naive O(n²) double loop hangs on 100k inputs. The dict-lookup version stays O(n).

### Example 3 — Caesar cipher with explicit rules

```python
"""Caesar cipher: shift letters by k, preserve case, leave non-letters."""


def caesar(s: str, k: int) -> str:
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - ord("A") + k) % 26 + ord("A")))
        elif "a" <= ch <= "z":
            out.append(chr((ord(ch) - ord("a") + k) % 26 + ord("a")))
        else:
            out.append(ch)
    return "".join(out)
```

Explicit branches over `isupper()` because we need the base character (`A` vs `a`) anyway. `%` handles negative shifts and wraparound.

## Security notes

- **Don't blindly `eval` or `exec` strings** from exercise input — even your own. Build the habit now.
- **Validate sizes** of inputs before allocating. A "process this list" function should reject 10⁹-element inputs with a friendly error rather than OOM your laptop.
- **Sanity-check string parsing.** Real-world `int(s)` calls can receive `"\u202e123"` (right-to-left override) or other Unicode trickery; for security-sensitive parsing, normalize with `unicodedata.normalize` first.

## Performance notes

- The number-one performance fix at this stage is **switching data structures**, not micro-optimizing code. List-to-set membership turns O(n²) into O(n).
- `Counter.most_common(k)` uses a heap and is O(n log k); manual sorting is O(n log n). The difference is large for large `n` and small `k`.
- A pure-Python loop processes ~10⁷ items/second. If you need more, vectorize (NumPy) or push to a different runtime.
- `time.perf_counter()` is the right tool to measure short intervals. Use `timeit` for micro-benchmarks where startup costs would dominate.

## Common mistakes

- **Coding before examples.** Symptom: the function "works on the case I tested". Cause: no other cases were considered. Fix: write 3 example pairs first.
- **One giant function.** Symptom: 80 lines, hard to test. Cause: no decomposition. Fix: extract by noun (`load`, `parse`, `transform`, `summarize`).
- **Premature optimization.** Symptom: an unreadable solution that's only 10% faster. Cause: optimizing before profiling. Fix: make it work, then profile, then optimize the actual hotspot.
- **No tests.** Symptom: a regression three days later. Cause: relying on "I tested it once". Fix: every fix gets a regression test.
- **Wrong structure choice.** Symptom: O(n²) on 100k input. Cause: using a list where a dict/set was right. Fix: re-read the cheatsheet above.

## Practice

These are the "practice" chapter's whole point. Pick five and do them today.

1. **FizzBuzz** — rewrite as a generator.
2. **Anagram check** — `is_anagram(a, b)`.
3. **Vowel count per word** — `{word: vowel_count}`.
4. **Two-sum** — given `nums` and `target`, find indices `i ≠ j` with `nums[i] + nums[j] == target`. One pass with a dict.
5. **Caesar cipher** — shift letters by `k`; preserve case; leave non-letters.
6. **Flatten a nested list** — first one level, then arbitrary depth (recursive).
7. **Streaks** — given daily booleans, return the longest streak of consecutive `True`s.
8. **Matrix transpose** — `list(zip(*rows))`.
9. **Balanced parentheses** — using a list as a stack.
10. **Word frequency from a file** — print the 10 most common words.

<details><summary>Show a few solutions</summary>

```python
def is_anagram(a: str, b: str) -> bool:
    return Counter(a.lower()) == Counter(b.lower())
```

```python
def longest_streak(days: list[bool]) -> int:
    best = current = 0
    for d in days:
        current = current + 1 if d else 0
        best = max(best, current)
    return best
```

```python
def balanced(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
```

```python
def flatten(xs):
    out = []
    for x in xs:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out
```

</details>

## Quiz

1. The first step of the workflow is:
    (a) implement (b) restate the problem (c) write tests (d) optimize
2. "Is x present in a 10M-item list, queried millions of times" suggests:
    (a) sort then binary search (b) convert to a set once (c) `in` on the list (d) two-pointer
3. "Make it work, make it right, make it fast" means:
    (a) ship bugs first (b) correctness comes before speed (c) speed comes first (d) never optimize
4. `Counter.most_common(k)` complexity:
    (a) O(1) (b) O(n log n) (c) O(n log k) (d) O(n²)
5. A good time to extract a new function:
    (a) never (b) when a block stops fitting a single idea (c) only when reused (d) only for tests

**Short answer:**

6. State the workflow in five words or fewer.
7. When is a good time to *stop* refactoring?

*Answers: 1-b, 2-b, 3-b, 4-c, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [13-practice — mini-project](mini-projects/13-practice-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Workflow: restate, example, shape, name, implement, test, clean.
- Pattern recognition over algorithm memorization — match phrases to standard-library tools.
- "Make it work, make it right, make it fast" — in that order.
- The library usually has the right primitive; reach for it before hand-rolling.

## Further reading

- Brian Kernighan & Rob Pike, *The Practice of Programming*.
- *Effective Python* by Brett Slatkin — 90 short, dense items.
- Next: [the module quiz](14-quiz.md).
