# Chapter 02 — Variables

> A variable is not a box. It is a *name* you have chosen for a value. The distinction seems pedantic until the day it saves you.

## Learning objectives

By the end of this chapter you will be able to:

- Define a variable, assign to it, and reassign it.
- List the basic built-in types: `int`, `float`, `str`, `bool`, `None`.
- Convert between types using `int()`, `float()`, `str()`, `bool()`.
- Write identifiers that follow Python's naming rules and community style (`snake_case`).
- Explain in one sentence the difference between a *name* and an *object*.

## Prerequisites & recap

You should already be comfortable with:

- Running a Python file ([chapter 01](01-introduction.md)).

Recap: Python source becomes bytecode that runs on the CPython VM. You have both REPL and file modes available.

## The simple version

Think of a variable as a **sticky note** with a name written on it, attached to a value that lives in memory. Assignment moves the sticky note. The value isn't copied; the *reference* is.

That single mental model — names point at values, values do the work — explains every "weird" Python behaviour you'll meet for the rest of the book.

## In plain terms (newbie lane)

This chapter is really about **Variables**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Two names, one underlying value, one mutation visible through both.

```
   name 'x'  ──┐
                ▼
              ┌──────────────┐
              │ [1, 2, 3, 4] │  ◀── one list object in memory
              └──────────────┘
                ▲
   name 'y'  ──┘

   y.append(4)  →  the list mutates  →  x sees [1, 2, 3, 4] too
   y = [9, 9]   →  rebinds 'y' only  →  x still sees the old list
```

Mutation reaches through every name pointing at the value. Rebinding only changes the one sticky note.

## Must know now

- The chapter's core mental model and one working example.
- The most common beginner bug for this topic.
- Enough to finish the matching exercise L1 and L2 tasks.

## Can skip for now

- Advanced performance caveats.
- Rare edge cases and deep language internals.
- Optional tooling depth that is not needed for this chapter's checkpoint.

## Concept deep-dive

### Names and values

```python
x = 5         # bind name 'x' to the integer object 5
x = "five"    # rebind 'x' to the string object "five"; the int 5 still exists, just unreferenced
```

You did not "convert x". You moved the sticky note. The type travels with the *value*, not the name. This is **dynamic typing**.

When all references to a value disappear, CPython's reference counter notices and frees the memory. We cover the mechanism in [Module 07 — Refcounting GC](../07-c-memory/10-refcounting-gc.md).

### Built-in types you need today

| Type   | Example literal       | Purpose                              |
|--------|-----------------------|--------------------------------------|
| `int`  | `42`, `-7`, `0`       | integers of arbitrary size           |
| `float`| `3.14`, `2e10`        | IEEE-754 doubles                     |
| `str`  | `"hello"`, `'hi'`     | text (Unicode)                       |
| `bool` | `True`, `False`       | truthy / falsy                       |
| `None` | `None`                | the singleton "absence of a value"   |

You can always ask: `type(x)` returns the type object.

### Type conversion

```python
int("42")      # 42
float("3.14")  # 3.14
str(42)        # "42"
bool(0)        # False
bool("")       # False
bool("False")  # True  ← surprise: any non-empty string is truthy
```

**Falsy values** in Python: `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False`. Everything else is truthy. Memorize this list — it's the foundation of `if some_value:` shortcuts.

### Naming rules and style

Rules (enforced by the language):

- Starts with a letter (A–Z, a–z) or `_`.
- Rest can include letters, digits, and `_`.
- Cannot be a keyword (`if`, `for`, `class`, …).
- Identifiers are case-sensitive: `total` and `Total` are different.

Style (enforced by [PEP 8](https://peps.python.org/pep-0008/) and your future teammates):

- `snake_case` for variables and functions.
- `SCREAMING_SNAKE_CASE` for constants.
- `PascalCase` for classes (we'll meet them in [Module 04](../04-oop/README.md)).
- Names describe *what*, not *how* or *type*: `total_seconds` ✅; `i` ❌; `my_int_var` ❌.

### Multiple assignment and unpacking

```python
a, b = 1, 2          # tuple unpacking
a, b = b, a          # swap, no temporary needed
x = y = z = 0        # chained assignment — all three names point at the same 0
```

The right-hand side is evaluated once, then unpacked into the left-hand names.

**Why this matters:** chained assignment with mutable values (`a = b = []`) creates a shared list. With immutables (`a = b = 0`) it's safe because rebinding `a` later doesn't affect `b`. We see the implications in the next subsection.

### Mutation vs. rebinding

This is the single most-misunderstood Python concept:

```python
x = [1, 2, 3]
y = x            # both names point at the same list
y.append(4)      # mutate the shared list
print(x)         # [1, 2, 3, 4]   — visible through x

y = [9, 9]       # rebind y to a new list; x is untouched
print(x)         # [1, 2, 3, 4]
print(y)         # [9, 9]
```

To make `y` an independent copy: `y = list(x)`, `y = x[:]`, or `y = x.copy()`.

## Why these design choices

- **Names, not boxes.** Treating variables as references makes Python's behavior with lists, dicts, and class instances predictable instead of magical. The "box" mental model breaks the moment two names share a list.
- **Dynamic typing.** Trades compile-time safety for development speed. The cost shows up at scale; the upside is small scripts that ship in minutes. Static typing comes back as type hints (covered in [chapter 03](03-functions.md)) and seriously in [Module 09: TypeScript](../09-ts/README.md).
- **`snake_case` everywhere.** Distinguishes variables from `PascalCase` classes at a glance. Most lint configurations enforce it; fighting the convention costs more than learning it.
- **Encode meaning, not type.** `price_cents` survives a refactor that switches the storage type; `price_int` does not.
- **When you'd choose differently.** Numerical-computing libraries (NumPy, Pandas) sometimes break `snake_case` for matrix-math conventions (`X`, `y`, `df`). Follow the local idiom of the library you're inside.

## Production-quality code

### Example 1 — A tiny receipt

```python
"""Compute a receipt total. Stand-in for any 'bind a few values, do arithmetic' task."""

PRICE_APPLE = 0.50
PRICE_BREAD = 2.40
TAX_RATE = 0.07


def receipt(apples: int, loaves: int) -> dict:
    """Return a breakdown of subtotal, tax, and total."""
    if apples < 0 or loaves < 0:
        raise ValueError("counts must be non-negative")
    subtotal = apples * PRICE_APPLE + loaves * PRICE_BREAD
    tax = subtotal * TAX_RATE
    return {"subtotal": subtotal, "tax": round(tax, 2), "total": round(subtotal + tax, 2)}


if __name__ == "__main__":
    print(receipt(apples=6, loaves=2))
```

Constants up top in `SCREAMING_SNAKE_CASE`. Intermediate computations get names so the final expression reads like English. The function returns a dict so callers can choose whether to print, log, or persist.

### Example 2 — Diagnosing a copy bug

```python
"""Demonstrate why 'y = x' on a list is rarely what you wanted."""


def shared_vs_copied():
    a = [1, 2, 3]

    shared = a            # same list object
    independent = a[:]    # shallow copy

    shared.append(99)
    independent.append(7)

    return {
        "a": a,                        # mutated via 'shared' → [1, 2, 3, 99]
        "shared": shared,              # same as 'a'
        "independent": independent,    # [1, 2, 3, 7]
    }


if __name__ == "__main__":
    for name, value in shared_vs_copied().items():
        print(f"{name:12} {value}")
```

Output:

```
a            [1, 2, 3, 99]
shared       [1, 2, 3, 99]
independent  [1, 2, 3, 7]
```

## Security notes

Variables themselves carry no security risk, but two patterns appear early:

- **Don't put secrets in source.** A constant named `API_KEY = "sk-live-..."` will leak the moment the file is committed. Use environment variables: `API_KEY = os.environ["API_KEY"]`.
- **Don't trust string-to-int conversion blindly.** `int(user_input)` raises `ValueError` on bad input — handle it explicitly so your service doesn't crash on the first malformed query parameter. We'll cover error handling in [chapter 12](12-errors.md).

## Performance notes

- Integer objects in CPython are heap-allocated and reference-counted; small ints (-5 to 256) are pre-allocated and shared. Equality of small ints is essentially free.
- `str` is immutable. `s = s + "x"` in a loop creates a new string every iteration — O(n²) total work. Use `"".join(parts)` or an `io.StringIO` buffer instead.
- `list.copy()` / `x[:]` is O(n). Don't reflexively copy in hot paths if you're only going to read.
- **Cost model:** binding a name is O(1). Looking it up walks at most four scopes (local, enclosing, global, built-in) — also O(1) but with a constant factor. The slow part is what you *do* with the value.

## Common mistakes

- **Shadowing built-ins.** Symptom: `TypeError: 'list' object is not callable` from `list([1,2])` later in the file. Cause: an earlier `list = [1]` rebound the name. Fix: rename to `items` (or anything not in `dir(builtins)`).
- **Type encoded in the name.** Symptom: `price_int = "4.99"` works at first, then breaks when arithmetic happens. Cause: name lied about content. Fix: name the meaning (`price_cents`, `price_display_str`).
- **Confusing `=` with `==`.** Symptom: `if x = 5:` raises `SyntaxError`. Cause: `=` assigns; `==` compares. Fix: read the difference in [chapter 07](07-comparisons.md).
- **Assignment vs. mutation.** Symptom: "I changed `y` and now `x` is different too". Cause: `y = x` shared the same list. Fix: copy explicitly when you need independence.
- **Mutable chained assignment.** Symptom: `a = b = []`; appending to `b` also affects `a`. Cause: same list referenced by both. Fix: `a, b = [], []`.

## Practice

1. **Warm-up.** Bind `first` to your first name and `last` to your last name. Print them as `"Last, First"`.
2. **Standard.** Given `seconds = 7325`, compute and print `"2h 2m 5s"`. Name each intermediate value (`hours`, `minutes`, `secs`).
3. **Bug hunt.** Explain why this prints `5`, not `10`:

    ```python
    a = 5
    b = a
    a = 10
    print(b)
    ```

4. **Stretch.** Given two prices `p1` and `p2` (floats), round their average to two decimals in a single expression.
5. **Stretch++.** Without running it, predict the output, then verify:

    ```python
    x = "3"
    y = 4
    print(x * y)
    ```

<details><summary>Show solutions</summary>

```python
print(f"{last}, {first}")
```

```python
seconds = 7325
hours = seconds // 3600
remainder = seconds % 3600
minutes = remainder // 60
secs = remainder % 60
print(f"{hours}h {minutes}m {secs}s")
```

`b = a` bound `b` to the value `5`. Rebinding `a` to `10` doesn't touch `b`. (Same with mutability — appending to `a`'s list *would* affect `b`'s view, because they'd share the list.)

```python
round((p1 + p2) / 2, 2)
```

`"3" * 4 == "3333"`. The `*` operator on a string repeats it.

</details>

## Quiz

1. Which is **not** a valid Python identifier?
    (a) `_total` (b) `total1` (c) `1total` (d) `TotalCount`
2. What is the type of `True`?
    (a) `int` (b) `bool` (c) `str` (d) `None`
3. `bool("False")` returns:
    (a) `True` — any non-empty string is truthy (b) `False` (c) raises an error (d) `None`
4. Which assigns the *same* value to `a`, `b`, and `c`?
    (a) `a = b = c = 0` (b) `a, b, c = 0` (c) `a = 0; b = 0; c = 0` (d) Both a and c
5. `type(3.0 / 2)` is:
    (a) `int` (b) `float` (c) `str` (d) `bool`

**Short answer:**

6. In one sentence, distinguish *name* from *object* in Python.
7. Why is dynamic typing a double-edged sword?

*Answers: 1-c, 2-b, 3-a, 4-d, 5-b.*

## Learn-by-doing mini-project

Use the single module project track and complete **Checkpoint A**:

- [Python Fundamentals Companion Track](mini-projects/00-python-fundamentals-companion-track.md)

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A variable is a name bound to an object; assignment moves the name, not the value.
- Python is dynamically typed — types live with values, not names.
- Mutation reaches through all references; rebinding only changes one name.
- Use `snake_case`, avoid shadowing built-ins, encode meaning rather than type in names.

## Further reading

- [PEP 8 — Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions).
- Python docs: [*Data model* → *Objects, values and types*](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types).
- Next: [functions](03-functions.md).
