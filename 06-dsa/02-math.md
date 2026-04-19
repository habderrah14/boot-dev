# Chapter 02 — Math for Algorithms

> "You don't need a math degree. You do need comfort with logarithms, exponents, modular arithmetic, and a dash of logic."

## Learning objectives

By the end of this chapter you will be able to:

- Use logarithms and exponents qualitatively to reason about scale.
- Apply modular arithmetic to hashing and cyclic indices.
- Sum arithmetic and geometric series in closed form.
- State and use De Morgan's laws to simplify boolean conditions.
- Count permutations and combinations.

## Prerequisites & recap

- High-school algebra — nothing more. If you can solve `2x + 3 = 7`, you have enough.
- [Chapter 01 — Algorithms Intro](01-algorithms-intro.md).

## The simple version

Most of DSA math boils down to two ideas. First: logarithms tell you "how many times can I cut this in half?" — which is why binary search is fast and why balanced trees are shallow. Second: modular arithmetic wraps numbers around like a clock — which is why hash tables can map any key to a fixed-size array.

You don't need to prove theorems. You need to *estimate*. When someone says "this is O(n log n)," you should be able to picture that for n = 1,000,000, log₂(n) ≈ 20, so the total work is roughly 20 million operations. That kind of back-of-the-envelope reasoning is what separates an engineer who anticipates problems from one who discovers them in production.

## Visual flow

```
  Exponents (growth)             Logarithms (shrinkage)
  ========================       ========================
  2^1  =          2              log2(2)     =  1
  2^10 =      1,024              log2(1024)  = 10
  2^20 =  1,048,576              log2(10^6)  ~ 20
  2^30 ~ 1,000,000,000           log2(10^9)  ~ 30

  Doubling n adds 1 to log.      Halving n subtracts 1 from log.

  Mod (wrapping)
  ========================
  hash("alice") = 394821
  394821 % 8 = 5            --> bucket 5 of 8
  394821 % 16 = 5           --> bucket 5 of 16
  Clock: (23 + 3) % 24 = 2  --> 2:00 AM
```
*Figure 2-1: Exponents grow explosively; logarithms compress. Mod wraps.*

## Concept deep-dive

### Exponents and logarithms

`log₂(n)` answers the question: "how many times do I halve n to reach 1?" Equivalently, "what power of 2 gives me n?"

```python
import math

math.log2(1024)    # 10.0  — 2^10 = 1024
math.log2(1_000_000)  # ~19.93 — roughly 20 halvings
2 ** 10            # 1024
2 ** 20            # 1_048_576
```

Why does this matter? Because every algorithm that *halves* the problem at each step runs in O(log n) time. Binary search halves. Balanced BSTs halve. Merge sort splits in half at each level. That "halving → log" connection is the most important intuition in all of algorithm analysis.

**Rules of thumb you'll use constantly:**

- 2¹⁰ ≈ 10³ (one thousand)
- 2²⁰ ≈ 10⁶ (one million)
- 2³⁰ ≈ 10⁹ (one billion)
- Doubling the input adds exactly 1 to `log₂(n)` — so O(log n) algorithms barely notice when your data doubles.

### Modular arithmetic

`a % b` gives the remainder when `a` is divided by `b`. You'll use this constantly:

- **Hashing:** `hash(key) % table_size` maps any hash to a valid bucket index.
- **Cyclic indices:** `xs[(i + 1) % n]` wraps around to the start of a circular buffer.
- **Parity checks:** `n % 2 == 0` tests for even numbers.
- **Clock arithmetic:** `(current_hour + offset) % 24` gives you the correct hour.

**Properties you'll rely on** (these let you keep numbers small during computation):

- `(a + b) % m == ((a % m) + (b % m)) % m`
- `(a * b) % m == ((a % m) * (b % m)) % m`

Why do these matter? Because in cryptography and competitive programming, you often need to compute things like `(a^b) % m` where `a^b` is astronomically large. The properties above let you take the modulus at each step, keeping intermediate results small.

### Series sums

Two series appear over and over in complexity analysis:

**Arithmetic series:** 1 + 2 + 3 + … + n = n(n+1)/2

This is why nested loops that count `1 + 2 + ... + n` iterations produce O(n²) complexity. The sum formula gives you the exact count without adding anything up.

**Geometric series:** 1 + 2 + 4 + … + 2ᵏ = 2^(k+1) − 1

This appears in merge sort analysis ("each level does O(n) work across log n levels"), dynamic array resizing ("total cost of all doublings"), and anywhere you see repeated doubling.

### Logic and De Morgan's laws

You use boolean logic in every `if` statement. De Morgan's laws let you simplify complex conditions:

- `¬(a ∧ b) == ¬a ∨ ¬b` — "not (A and B)" equals "not A or not B"
- `¬(a ∨ b) == ¬a ∧ ¬b` — "not (A or B)" equals "not A and not B"

In Python terms:

```python
# These are equivalent:
if not (user.active and user.verified): ...
if not user.active or not user.verified: ...
```

Why learn this? Because flattening nested conditions makes code easier to read, test, and branch-predict. Every time you see `not (... and ...)`, De Morgan tells you how to eliminate the outer negation.

### Counting: permutations and combinations

- **Permutations** of n distinct items: n! (n factorial). Order matters.
- **Combinations** of k from n: C(n, k) = n! / (k! · (n−k)!). Order doesn't matter.

These matter for algorithm analysis because they tell you the size of the search space. If you need to check all permutations, you're in O(n!) territory. All subsets? O(2ⁿ). Knowing this *before* you code saves you from writing an algorithm that will never finish.

```python
import math
math.factorial(10)          # 3_628_800 — 10! permutations
math.comb(10, 3)            # 120 — ways to choose 3 from 10
```

## Why these design choices

**Why closed-form math instead of brute-force summation?** Because closed forms turn O(n) computation into O(1). If you need the sum 1 + 2 + … + n, you can loop (O(n)) or use `n * (n + 1) // 2` (O(1)). In tight inner loops, that difference matters.

**Why modular arithmetic for hashing?** You need to map a potentially huge hash value to a small, fixed-size array. Mod is the simplest way to do that. Alternatives exist (multiplicative hashing, Fibonacci hashing) and can give better distribution, but mod is the baseline you must understand first.

**When would you pick differently?** If you need to distribute keys with minimal clustering, you might use a prime-sized table with double hashing. If you need order-preserving keys, you'd skip hashing entirely and use a balanced BST. The math you're learning here gives you the vocabulary to evaluate those trade-offs.

## Production-quality code

```python
import math
from typing import Sequence


def triangle_sum(n: int) -> int:
    """Sum of 1 + 2 + ... + n in O(1)."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return n * (n + 1) // 2


def bucket_index(key: str, num_buckets: int) -> int:
    """Map a string key to a bucket index via modular hashing."""
    if num_buckets <= 0:
        raise ValueError(f"num_buckets must be positive, got {num_buckets}")
    return hash(key) % num_buckets


def modpow(base: int, exp: int, mod: int) -> int:
    """Modular exponentiation: (base^exp) % mod, computed efficiently.

    Python's built-in pow(base, exp, mod) uses fast binary
    exponentiation internally — O(log exp) multiplications.
    """
    if mod <= 0:
        raise ValueError(f"mod must be positive, got {mod}")
    return pow(base, exp, mod)


def is_balanced(expr: str) -> bool:
    """Demonstrate De Morgan simplification: check that a string
    contains only balanced 'and'/'or' conditions.

    Practical example: validating that required config flags are set.
    """
    required = {"db_host", "db_port", "secret_key"}
    provided = set(expr.split())
    missing = required - provided
    return not missing  # De Morgan: not (a missing or b missing or ...) = all present
```

## Security notes

- **Modular arithmetic in cryptography:** When implementing crypto primitives (don't!), modular arithmetic errors — like using a non-prime modulus or leaking timing information through non-constant-time mod operations — can break security entirely. Use vetted libraries (`cryptography`, `hashlib`).
- **Hash flooding:** If an attacker controls input keys, they can craft collisions for `hash(key) % table_size`, degrading your hash table from O(1) to O(n). Python mitigates this with hash randomization (`PYTHONHASHSEED`). Be aware when exposing hash-based structures to untrusted input.

## Performance notes

| Operation | Cost | Notes |
|---|---|---|
| `n * (n+1) // 2` | O(1) | Closed-form arithmetic series |
| `sum(range(n))` | O(n) | Brute-force equivalent — avoid in hot paths |
| `hash(key) % m` | O(len(key)) | Hashing cost depends on key size |
| `pow(a, b, m)` | O(log b) | Binary exponentiation built into Python |
| `math.comb(n, k)` | O(min(k, n-k)) | Efficient — avoids computing full factorials |

The key takeaway: whenever a closed-form formula exists, prefer it. It's not just faster — it's also more readable once you know the formula.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `math.log(1000)` returns ~6.9 instead of ~3 | Python's `math.log()` uses natural log (base e) by default | Use `math.log2()` or `math.log(x, 2)` for base-2 |
| 2 | Off-by-one in series sums — e.g., getting 4950 instead of 5050 for sum(1..100) | Using `n * (n - 1) // 2` instead of `n * (n + 1) // 2` | Always verify with n=1: `1*(1+1)//2 = 1` ✓ |
| 3 | `log(0)` raises `ValueError` | Logarithm of zero is undefined | Guard with `if n > 0` before taking log |
| 4 | Negative modulus surprises: `-7 % 3` gives 2 in Python but -1 in C/Java | Python's `%` always returns non-negative when the divisor is positive | Know your language's mod behavior; Python's is usually what you want |
| 5 | Integer overflow in `(lo + hi) // 2` | In Python this isn't a problem (arbitrary precision), but the habit matters for other languages | Use `lo + (hi - lo) // 2` — it translates safely to C/Java/Go |

## Practice

**Warm-up.** Compute `log₂(1_000_000)` rounded up to the nearest integer. What does this number represent for binary search?

<details><summary>Show solution</summary>

```python
import math
result = math.ceil(math.log2(1_000_000))
print(result)  # 20
```

It means binary search on 1 million items takes at most 20 comparisons.

</details>

**Standard.** Implement `modpow(base, exp, mod)` that computes `(base^exp) % mod` efficiently. Then verify it against Python's built-in `pow(base, exp, mod)` for `base=7, exp=256, mod=13`.

<details><summary>Show solution</summary>

```python
def modpow(base, exp, mod):
    """Binary exponentiation: O(log exp) multiplications."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result

assert modpow(7, 256, 13) == pow(7, 256, 13)
```

This is exactly what Python's three-argument `pow` does internally.

</details>

**Bug hunt.** A developer writes `math.log(n)` to estimate binary search depth. Their estimate for n=1024 is 6.93 instead of 10. What went wrong?

<details><summary>Show solution</summary>

`math.log(n)` computes the natural logarithm (base e ≈ 2.718), not log base 2. `ln(1024) ≈ 6.93`, but `log₂(1024) = 10`. Fix: use `math.log2(n)` or `math.log(n, 2)`.

</details>

**Stretch.** Use De Morgan's laws to simplify this condition, then verify both versions produce the same result for all combinations of `a, b, c ∈ {True, False}`:

```python
if not (a and b) or not c:
    do_something()
```

<details><summary>Show solution</summary>

Apply De Morgan to `not (a and b)` → `not a or not b`:

```python
if not a or not b or not c:
    do_something()
```

Verification:

```python
from itertools import product

for a, b, c in product([True, False], repeat=3):
    original = not (a and b) or not c
    simplified = not a or not b or not c
    assert original == simplified, f"Mismatch for {a=}, {b=}, {c=}"
print("All cases match.")
```

</details>

**Stretch++.** Implement the Extended Euclidean Algorithm: given integers `a` and `b`, find `x` and `y` such that `a*x + b*y = gcd(a, b)`.

<details><summary>Show solution</summary>

```python
def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (gcd, x, y) such that a*x + b*y = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

g, x, y = extended_gcd(35, 15)
assert g == 5
assert 35 * x + 15 * y == 5
print(f"gcd=5, x={x}, y={y}, verify: 35*{x} + 15*{y} = {35*x + 15*y}")
```

This is the foundation of modular inverses, which underpin RSA cryptography.

</details>

## In plain terms (newbie lane)
If `Math` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `log₂(1024)` equals:
    (a) 8  (b) 10  (c) 12  (d) 1024

2. `17 % 5` equals:
    (a) 3  (b) 2  (c) 5  (d) 3.4

3. The sum 1 + 2 + ... + 100 equals:
    (a) 100  (b) 5000  (c) 5050  (d) 10100

4. De Morgan's law says:
    (a) `¬(a ∧ b) = ¬a ∨ ¬b`  (b) `a ∧ b = ¬a ∨ ¬b`  (c) it only works for integers  (d) it doesn't simplify anything

5. The fastest way to compute `(a^b) % m` in Python is:
    (a) a loop  (b) `pow(a, b, m)`  (c) recursion only  (d) it's impossible for large b

**Short answer:**

6. Why do hash tables use modular arithmetic?
7. Give one reason modular arithmetic matters for backend development beyond hashing.

*Answers: 1-b, 2-b, 3-c, 4-a, 5-b, 6-To map arbitrarily large hash values to valid array indices (0 to table_size-1), 7-Rate limiting with sliding windows, session token generation, round-robin load balancing, or cyclic buffer indexing.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-math — mini-project](mini-projects/02-math-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Logarithms count halvings — they're why binary search and balanced trees are fast. Exponents count doublings — they're why brute-force subset enumeration is slow.
- Modular arithmetic wraps values into a range, which is the basis of hashing, cyclic buffers, and clock arithmetic.
- Closed-form series sums (like n(n+1)/2) turn O(n) loops into O(1) calculations — use them whenever you can.
- De Morgan's laws simplify boolean conditions, making your code more readable and your tests more thorough.

## Further reading

- *Concrete Mathematics*, Graham, Knuth, and Patashnik — the definitive reference for the math behind algorithms.
- Python `math` module documentation — especially `log2`, `comb`, `factorial`.
- Khan Academy: Logarithms — if you need a refresher on the basics.
- Next: [Big-O Analysis](03-big-o.md).
