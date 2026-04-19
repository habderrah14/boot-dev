# Chapter 06 — Computing

> Computers are dumb, fast, and surprisingly bad at arithmetic. This chapter is about the "surprisingly bad" part.

## Learning objectives

By the end of this chapter you will be able to:

- Use Python's arithmetic operators (`+ - * / // % **`) and predict their result types.
- Distinguish integer, true, and floor division and pick the right one.
- Explain *why* `0.1 + 0.2 != 0.3` and reach for `Decimal` (or integer cents) for money.
- Use `math` and `divmod` for common numeric tasks.

## Prerequisites & recap

- [Variables](02-variables.md) — types travel with values.

Recap: `int` is exact and unbounded; `float` is an IEEE-754 double; the type of an expression is determined by its operands and operator.

## The simple version

Python `int` is **exact, arbitrarily large**. Python `float` is **fixed-precision binary** — fast, but only an *approximation* of most decimals you write down. For anything where exactness matters (money, counts, hashes) use `int`. For physics and statistics, use `float`. For dollars and cents, use `Decimal` or store integer cents.

If you remember nothing else: never use `float` for money, never compare floats with `==`.

## In plain terms (newbie lane)

This chapter is really about **Computing**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The numeric type ladder and what each conversion costs.

```
   int  ──── exact, unbounded ────────────────┐
    │                                          │
    │ float()                                  │ Decimal(str(x))
    ▼                                          │
   float ──── IEEE-754, ~15-17 decimal digits ─┤
    │                                          │
    │ Decimal(str(x))   (avoid Decimal(float))│
    ▼                                          ▼
   Decimal ── exact decimal, slow, base-10 ────┘
```

`int → float` is lossy past 2⁵³. `float → Decimal` *via the float* preserves the binary garbage (`Decimal(0.1)` ≠ `Decimal("0.1")`). Always go through `str()` when converting a float to a Decimal.

## Concept deep-dive

### Operators

| Op   | Meaning                | `a=7, b=2` |
|------|------------------------|------------|
| `+`  | sum                    | `9`        |
| `-`  | difference             | `5`        |
| `*`  | product                | `14`       |
| `/`  | true division (float)  | `3.5`      |
| `//` | floor division         | `3`        |
| `%`  | remainder              | `1`        |
| `**` | exponent               | `49`       |

Precedence (high to low): `**` > unary `-` > `* / // %` > `+ -`. Same level associates left-to-right (with `**` as the exception — right-to-left). When in doubt, parenthesize. The reader will thank you.

### Integers are exact and unbounded

```python
2 ** 200
# 1606938044258990275541962092341162602522202993782792835301376
```

CPython implements `int` as a variable-width "bignum". Cost: arithmetic on huge ints is O(n²) in their digit count for multiplication, vs. O(1) for `float`. For most code this never matters.

### Floats are approximate

Floats are binary fractions. Most decimals you can write don't have an exact binary representation:

```python
0.1 + 0.2          # 0.30000000000000004
0.1 + 0.2 == 0.3   # False
```

Compare floats with a tolerance:

```python
import math
math.isclose(0.1 + 0.2, 0.3)   # True (rel_tol=1e-09 by default)
```

### Money: never use floats

```python
from decimal import Decimal, ROUND_HALF_UP

price = Decimal("19.99")
tax = (price * Decimal("0.07")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
total = price + tax            # Decimal('21.39')
```

Or — equally valid and often faster — store **integer cents** and only render dollars at the UI edge: `1999` cents → display as `"$19.99"`.

Floats and money produce audits, not refunds.

### `divmod`, `math`, `abs`, and friends

```python
divmod(17, 5)        # (3, 2) — quotient and remainder in one call

import math
math.sqrt(16)        # 4.0
math.floor(3.7)      # 3
math.ceil(3.2)       # 4
math.pi              # 3.141592653589793
math.inf, math.nan   # special floats

abs(-3.2)            # 3.2  — built-in, works on int/float/complex
round(2.675, 2)      # 2.67  ← banker's rounding; surprising the first time
```

Banker's rounding (round half to even) keeps long sums unbiased. If you need "schoolbook" rounding for display, use `Decimal.quantize` with `ROUND_HALF_UP`.

### Operator precedence in practice

```python
2 + 3 * 4           # 14, not 20
-2 ** 2             # -4  ← unary minus binds tighter than ** with one operand? No: ** binds tighter, so it's -(2**2)
(-2) ** 2           # 4
2 ** 3 ** 2         # 512  ← right-associative: 2 ** (3 ** 2)
```

When you wouldn't bet a coffee on the answer, parenthesize.

## Why these design choices

- **`/` always returns `float` in Python 3.** Python 2 returned `int` for `int / int`, which silently truncated and caused bugs across millions of programs. Python 3 made the division explicit: `/` is mathematical, `//` is integer.
- **Unbounded `int` by default.** Most languages have fixed-size ints (32 or 64 bit) and silently overflow. Python prioritizes correctness over speed — a sensible default given Python's typical workloads.
- **`Decimal` exists for money.** IEEE-754 binary floats can't represent `0.1` exactly. Financial systems can't tolerate one-cent rounding errors at scale, so a base-10 fixed-precision type is mandatory. Decimals are slower (~10× a float multiply), but you only need them at the boundaries — keep arithmetic in cents internally if you can.
- **`math.isclose` instead of an `EPS` constant.** A single tolerance doesn't work across magnitudes — `0.0001` matters when comparing `0.0002` and `0.0003`, but is invisible when comparing `1e10` and `1e10 + 0.0001`. `math.isclose` defaults to relative tolerance.
- **When you'd choose differently.** For high-throughput numeric work, NumPy uses fixed-size `int64`/`float64` arrays for orders-of-magnitude speed; bignum and `Decimal` are too slow. For exact rational arithmetic (vector calculus, symbolic math) reach for `fractions.Fraction` or SymPy.

## Production-quality code

### Example 1 — Seconds → HH:MM:SS

```python
"""Format integer seconds as HH:MM:SS, suitable for log lines or progress bars."""


def hms(seconds: int) -> str:
    """Return "HH:MM:SS" for non-negative integer seconds."""
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    print(hms(3725))   # 01:02:05
    print(hms(86399))  # 23:59:59
```

`divmod` keeps both the quotient and remainder in one call — clearer than two separate `//` and `%` lines.

### Example 2 — Money done right

```python
"""Add tax with banker-safe rounding and exact decimal arithmetic."""

from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal("0.075")


def with_tax(price_str: str) -> Decimal:
    """Take a price as a string (so we don't lose precision crossing float).

    >>> with_tax("19.99")
    Decimal('21.49')
    """
    price = Decimal(price_str)
    if price < 0:
        raise ValueError("price must be non-negative")
    tax = (price * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return price + tax


if __name__ == "__main__":
    print(with_tax("19.99"))    # 21.49
    print(with_tax("0.10"))     # 0.11
```

Note the input is a *string*, not a float. `Decimal(0.1)` carries the binary garbage of `0.1`'s float representation; `Decimal("0.1")` does not.

## Security notes

- **Avoid `eval()` for math.** Symptom: a "calculator" feature that lets a request body do anything. Cause: `eval(user_input)` is arbitrary code execution. Fix: parse to a token stream and evaluate explicitly, or use [`ast.literal_eval`](https://docs.python.org/3/library/ast.html#ast.literal_eval) for trusted-shape literals.
- **Integer overflow is not your problem in pure Python — but it is across boundaries.** Talking to a 32-bit C library, a SQL `INTEGER` column, or a binary protocol means a Python `int` of 2⁶⁴ might silently corrupt or raise. Validate ranges at the boundary.
- **Time-of-check / time-of-use on float comparisons.** Don't write security checks like `if balance >= threshold` on float balances; use integer cents or `Decimal`.

## Performance notes

- `int` arithmetic for "small" values (fits in a CPU word) is fast — a few nanoseconds per op. Bignum arithmetic gets quadratic in the number of digits; multiplying two 10,000-digit ints is noticeably slow.
- `float` arithmetic is hardware-accelerated; ~1 ns per op.
- `Decimal` is implemented in C in CPython 3.3+. It's still ~10–100× slower than `float` for arithmetic. Use it where correctness matters; otherwise stay in `int`/`float`.
- `divmod(a, b)` is one operation; `a // b, a % b` is two. The difference is usually negligible but real in tight loops.
- Avoid `list` of floats when you mean an array — NumPy's `numpy.ndarray` is ~50× faster for elementwise work and uses ~8× less memory.

## Common mistakes

- **Comparing floats with `==`.** Symptom: tests pass on one machine, fail on another. Cause: tiny rounding differences. Fix: `math.isclose(a, b)` with a sensible tolerance.
- **Using `float` for money.** Symptom: total of 100 invoices is off by a cent; auditor notices. Cause: binary float can't represent decimal cents. Fix: `Decimal` or integer cents.
- **`Decimal(0.1)` instead of `Decimal("0.1")`.** Symptom: surprising precision (`Decimal('0.1000000000000000055511151231257827021181583404541015625')`). Cause: passing a float to `Decimal` preserves the binary representation. Fix: pass strings.
- **Off-by-one in floor division of negatives.** `(-7) // 2 == -4`, not `-3`. Cause: floor rounds toward negative infinity. Fix: use `int(a / b)` if you want truncation toward zero; document which you want.
- **Integer overflow assumed but not checked at the DB boundary.** Symptom: `IntegrityError` when inserting a Python int that doesn't fit a SQL `INTEGER`. Fix: validate before insert, or use `BIGINT`.

## Practice

1. **Warm-up.** Print `2 ** 100`. Note how Python doesn't blink.
2. **Standard.** Given `total_minutes`, print `Hh Mm` (e.g., `2h 5m`).
3. **Bug hunt.** Why is each line "ok" but a different value?

    ```python
    avg = (a + b) / 2     # always float
    mid = (a + b) // 2    # always int
    ```

4. **Stretch.** Implement `is_power_of_two(n: int) -> bool` without loops.
5. **Stretch++.** Write `compound(principal: str, rate: str, years: int)` using `Decimal` and `quantize` to two decimal places.

<details><summary>Show solutions</summary>

```python
hours, minutes = divmod(total_minutes, 60)
print(f"{hours}h {minutes}m")
```

3. Both are correct values; they answer different questions. `(a+b)/2` is the exact midpoint; `(a+b)//2` rounds *toward negative infinity*. For `a=-3, b=0`, `(a+b)//2 == -2`, not `-1`.

```python
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0
```

```python
from decimal import Decimal, ROUND_HALF_UP

def compound(principal: str, rate: str, years: int) -> Decimal:
    amount = Decimal(principal) * (Decimal(1) + Decimal(rate)) ** years
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

</details>

## Quiz

1. `7 / 2` in Python 3 is:
    (a) `3` (b) `3.5` (c) `3.0` (d) error
2. `7 // 2` is:
    (a) `3` (b) `3.5` (c) `4` (d) `3.0`
3. `-7 // 2` is:
    (a) `-3` (b) `-4` (c) `3` (d) `3.5`
4. Which is *exactly* representable as a `float`?
    (a) `0.1` (b) `0.2` (c) `0.5` (d) `0.3`
5. Best type for currency in a financial system:
    (a) `float` (b) `int` cents or `Decimal` (c) `str` (d) `complex`

**Short answer:**

6. Explain why `0.1 + 0.2 != 0.3` in two sentences.
7. When would you pick integer cents over `Decimal` for money?

*Answers: 1-b, 2-a, 3-b, 4-c, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-computing — mini-project](mini-projects/06-computing-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `int` is exact and unbounded; `float` is approximate; `Decimal` is exact decimal.
- `/` is float division, `//` is floor division, `%` is remainder.
- Never compare floats with `==` (use `math.isclose`); never use floats for money.
- Use `divmod` to get quotient + remainder in one call.

## Further reading

- David Goldberg, [*What Every Computer Scientist Should Know About Floating-Point Arithmetic*](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html).
- Python docs — [`decimal`](https://docs.python.org/3/library/decimal.html), [`math`](https://docs.python.org/3/library/math.html).
- Next: [comparisons](07-comparisons.md).
