# Chapter 07 — Comparisons

> Every branch in your code is a comparison. Make sure each one compares what you think it compares.

## Learning objectives

By the end of this chapter you will be able to:

- Use `==`, `!=`, `<`, `<=`, `>`, `>=` on numbers, strings, and containers.
- Distinguish `==` (value equality) from `is` (identity) and pick correctly.
- Combine comparisons with `and`, `or`, `not` and exploit short-circuiting.
- Chain comparisons idiomatically (`0 <= x < 10`).
- Avoid the classic "treat any non-empty as `True`" footguns.

## Prerequisites & recap

- [Variables](02-variables.md) — names point at objects.
- [Computing](06-computing.md) — float comparisons need tolerance.

Recap from chapter 02: the same value can have multiple names. That fact is the heart of the `==` vs. `is` distinction in this chapter.

## The simple version

`==` asks "are the *values* the same?" `is` asks "are these the *same object* in memory?" Use `==` 99% of the time. Use `is` only when comparing against the singletons `None`, `True`, `False`.

Boolean `and`/`or` short-circuit and *return one of the operand values*, not necessarily a bool. That's a feature you'll lean on for safe attribute access and default values.

## In plain terms (newbie lane)

This chapter is really about **Comparisons**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How short-circuit evaluation traverses an `and`/`or` chain.

```
   user is not None  AND  user.verified  AND  user.address
        │                       │                  │
        ▼                       ▼                  ▼
       True ─────────────▶    True ────────────▶ "1 Main St"
        │
       False ──┐
                ▼
           short-circuits → returns False, never touches user.verified
```

`and` stops at the first falsy operand; `or` stops at the first truthy one. The expression's value is the *last operand it evaluated*.

## Concept deep-dive

### Value equality vs. identity

```python
a = [1, 2, 3]
b = [1, 2, 3]

a == b    # True  — same values
a is b    # False — two distinct list objects in memory

c = a
a is c    # True  — same object
```

The one place `is` is correct: comparing with sentinels.

```python
if x is None:        # ✓ idiomatic, fast, unambiguous
    ...

if x == None:        # works, but unidiomatic and overridable
    ...
```

`==` can be overridden by `__eq__`; `is` cannot. For `None`, `True`, `False`, use `is`.

### Chained comparisons

```python
0 <= x < 10           # equivalent to (0 <= x) and (x < 10)
a == b == c           # all three equal
3 > x > 0             # decreasing chain — works, but harder to read
```

The expression evaluates the middle term **once**. With function calls in the middle, that matters:

```python
0 < produce_value() < 10     # produce_value runs exactly once
```

### Boolean operators and truthiness

- `and`: returns the *first falsy* operand, or the last operand if all are truthy.
- `or`: returns the *first truthy* operand, or the last operand if all are falsy.
- `not`: returns `True`/`False`.

```python
"" or "fallback"       # "fallback"
"name" or "fallback"   # "name"
None and f()           # None — f never called
0 and crash_here()     # 0 — short-circuits
```

This makes `and`/`or` double as defaults and guards:

```python
port = config.get("port") or 8080         # default port if missing or 0
shipping = user is not None and user.address     # safe attribute access
```

But beware: `or` for defaults treats `0`, `""`, `[]` as "missing". For real "missing only", use `if x is None`.

### Comparing strings

```python
"apple" < "banana"   # True — alphabetical
"Z" < "a"            # True — uppercase has lower Unicode code points
```

Strings compare **code-point by code-point**. For human-meaningful comparison (case-insensitive, locale-aware), use `str.casefold()`:

```python
"Apple".casefold() == "APPLE".casefold()   # True
```

### Comparing across types

```python
1 == "1"     # False — different types
1 == 1.0     # True  — int and float compare numerically
1 == True    # True  — bool *is* a subclass of int
1 < "1"      # TypeError: '<' not supported between 'int' and 'str'
```

Equality is defined across types and may return `False`. Ordering between unrelated types raises.

## Why these design choices

- **`is` reserved for identity.** Some types (e.g. user-defined classes) override `__eq__` to compare by content. Without `is`, you couldn't ask "are these literally the same object?" — and you'd be unable to write "the singleton `None` check" reliably.
- **Short-circuit returning operand values, not bools.** It enables the default-value (`x or default`) and guard (`obj and obj.attr`) idioms without an `if`. Other languages return `bool` and require `??` and `?.` operators to recover the same expressiveness.
- **Chained comparisons.** Mathematical notation (`0 ≤ x < 10`) is universally readable; making it a single expression eliminates duplicated subexpression evaluation.
- **`==` returning `False` across types instead of raising.** Lets you write `x == None` or compare values from heterogeneous sources without try/except. The downside is that `1 == True == "1" * 1` does odd things; the upside is far fewer crashes.
- **When you'd choose differently.** In strict-typed code (mypy, Pydantic), often you'd rather have `1 == "1"` flagged as a type error. Linters with strict-equality rules give you that without changing Python.

## Production-quality code

### Example 1 — Safe attribute traversal

```python
"""Compute a shipping line, gracefully handling missing user fields."""

from dataclasses import dataclass


@dataclass
class User:
    verified: bool
    address: str | None


def shipping_label(user: User | None) -> str | None:
    """Return the address if the user exists, is verified, and has one."""
    if user is None or not user.verified or not user.address:
        return None
    return user.address.strip()


if __name__ == "__main__":
    print(shipping_label(None))                              # None
    print(shipping_label(User(verified=False, address="X"))) # None
    print(shipping_label(User(verified=True, address=None))) # None
    print(shipping_label(User(verified=True, address="1 Main St"))) # 1 Main St
```

The `or` chain expresses the precondition once. An equivalent `and` chain in a return statement is also valid but reads less linearly.

### Example 2 — Range validation via chained comparison

```python
"""Reject inputs out of business range with a clear error."""


def validate_age(age: int) -> int:
    if not (0 <= age <= 120):
        raise ValueError(f"age out of business range [0, 120]: {age}")
    return age


def percent(p: float) -> float:
    if not (0 <= p <= 1):
        raise ValueError(f"percent must be in [0, 1], got {p}")
    return p
```

Chained comparisons read as constraints. `not (lo <= x <= hi)` is more direct than `x < lo or x > hi` and keeps the bounds adjacent.

## Security notes

- **Don't trust `==` for secrets.** A short-circuit `==` on bytes can leak length and prefix via timing. Use [`hmac.compare_digest`](https://docs.python.org/3/library/hmac.html#hmac.compare_digest) to compare tokens, signatures, and password hashes.
- **`if input == "admin"` is not authentication.** It's a constant-time string compare problem dressed as an if-statement. Real authentication runs through hashed credentials and constant-time compares; we cover this in [Module 12 — Authentication](../12-http-servers/07-authentication.md).
- **`x is True` vs. `x == True`.** Don't write either for boolean checks; just `if x:`. Querying with `is True` accidentally rejects truthy non-bools.

## Performance notes

- `==` on built-in types is implemented in C and is essentially free.
- `is` is a pointer comparison — even faster, but rarely the right semantic.
- Short-circuiting saves work: if the first operand of `and` is falsy, the second isn't evaluated. Place cheap, frequently-falsy conditions first.
- Chained comparisons evaluate the middle term once — measurable when that term is a function call or a hot-loop expression.
- Comparing strings is O(n) in their length (until they differ). For large strings used as keys, `==` can dominate; consider hashing once.

## Common mistakes

- **`x == None`.** Symptom: linter warning, occasionally wrong with custom `__eq__`. Cause: idiomatic Python uses `is None`. Fix: `if x is None:`.
- **`if not x:` for "missing".** Symptom: `0`, `""`, `[]` treated as missing when you only meant `None`. Cause: Python's truthiness rules. Fix: `if x is None:` (or `if x is not None:`).
- **Comparing floats with `==`.** Symptom: tests intermittent. Cause: rounding. Fix: `math.isclose`.
- **Mixing `==` and `is` for ints/strings.** Symptom: `x is 256` happens to work, `x is 257` doesn't. Cause: CPython interns small ints; behavior is implementation detail. Fix: never use `is` for value equality.
- **Boolean masquerading as int.** Symptom: `sum([True, True, False]) == 2`. Cause: `bool` is a subclass of `int`. Usually harmless, occasionally surprising in dicts (`{True: "a", 1: "b"}` is one entry).

## Practice

1. **Warm-up.** `bool(0 == False)` — predict, then run.
2. **Standard.** Rewrite as a chained comparison: `x > 0 and x < 100`.
3. **Bug hunt.** Why is this often `False` in CPython?

    ```python
    a = "hello world"
    b = "hello world"
    print(a is b)
    ```

4. **Stretch.** Implement `in_range(x, lo, hi, inclusive=True)`.
5. **Stretch++.** Use `or` and `is None` to compute a "safe int with default": parse `"" | "5" | None` to `int` with default `10`. The `""` case should also fall through to the default — without ambiguity.

<details><summary>Show solutions</summary>

1. `True` — `False` is `0`.
2. `0 < x < 100`.
3. `is` checks object identity. CPython sometimes interns string literals, sometimes doesn't (depends on length, content, source). Never use `is` for string equality.

```python
def in_range(x, lo, hi, inclusive=True):
    return lo <= x <= hi if inclusive else lo < x < hi
```

```python
def parse_int_with_default(s, default=10):
    if s is None or s == "":
        return default
    return int(s)
```

</details>

## Quiz

1. `[] == []` vs. `[] is []`:
    (a) both True (b) both False (c) `==` True, `is` False (d) `==` False, `is` True
2. `None == False`:
    (a) True (b) False (c) error (d) depends on version
3. `1 < 2 < 3` evaluates as:
    (a) `True` (b) `False` (c) syntax error (d) `(1 < 2) < 3 == True < 3 == True`
4. `"abc" or "xyz"` returns:
    (a) `"abc"` (b) `"xyz"` (c) `True` (d) `False`
5. The idiomatic null check:
    (a) `if x == None:` (b) `if not x:` (c) `if x is None:` (d) `if None == x:`

**Short answer:**

6. Difference between `==` and `is`, in one sentence each.
7. Give one situation where short-circuit evaluation prevents a crash.

*Answers: 1-c, 2-b, 3-a, 4-a, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-comparisons — mini-project](mini-projects/07-comparisons-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `==` compares values, `is` compares identity. Use `is None` for null checks.
- Chained comparisons (`lo <= x < hi`) read like math and evaluate the middle once.
- `and`/`or` short-circuit and return one of the operand values, not always a bool.
- Use `hmac.compare_digest` for secrets; never `==`.

## Further reading

- Python docs — [*Comparisons*](https://docs.python.org/3/reference/expressions.html#comparisons), [*Boolean operations*](https://docs.python.org/3/reference/expressions.html#boolean-operations).
- Brett Slatkin, *Effective Python*, item "Use is or is not to compare against None".
- Next: [loops](08-loops.md).
