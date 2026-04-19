# Chapter 09 — Sum Types

> "A sum type (a.k.a. tagged union, variant, algebraic data type) is a type that is *one of* several shapes. They make invalid states unrepresentable."

## Learning objectives

By the end of this chapter you will be able to:

- Distinguish product types (AND — "has a name AND an age") from sum types (OR — "is a Success OR a Failure").
- Model sum types in Python using enums, dataclasses, `Union`, and the `|` syntax.
- Use `match/case` (Python 3.10+) for exhaustive pattern matching.
- Explain why sum types are safer than sentinel values, None-checks, and untyped exceptions.

## Prerequisites & recap

- [Classes and dataclasses](../04-oop/02-classes.md) — defining data-carrying classes.
- [Pure functions](03-pure-functions.md) — functions that return values instead of raising.

## The simple version

Most types you've used are *product types*: they combine fields with AND. A `User` has a name AND an age AND an email. A sum type works differently — it says a value is one of several possible shapes. A `Result` is *either* a `Success` with a value *or* a `Failure` with an error. Not both, not neither — exactly one.

Why does this matter? Because it forces you to handle all the possibilities. Instead of returning `None` and hoping the caller checks, or raising an exception and hoping someone catches it, you return a sum type that the caller *must* inspect. Pattern matching (`match/case`) makes this natural — you write a case for each variant, and your type checker can warn you if you forget one.

## Visual flow

```
  Product type (AND):                Sum type (OR):
  +------------------+              +------------------+
  | User             |              | Result           |
  | - name: str      |              |   |              |
  | - age: int       |              |   +-- Success    |
  | - email: str     |              |   |   value: T   |
  +------------------+              |   |              |
  All fields present                |   +-- Failure    |
  simultaneously                    |       error: str |
                                    +------------------+
                                    Exactly ONE variant
                                    at a time

  Pattern matching:
  +----------+      +-------------------+
  | Result r | ---> | match r:          |
  +----------+      |   case Success(v):|
                     |     use v        |
                     |   case Failure(e):|
                     |     handle e     |
                     +-------------------+

  vs. the old way:
  +----------+      +-------------------+
  | value    | ---> | if value is None: |
  | or None  |      |     ???           |  <-- easy to forget
  +----------+      | else:             |
                     |     use value     |
                     +-------------------+

  Caption: Sum types force you to handle every case.
  None/sentinel approaches let you forget.
```

## Concept deep-dive

### Product vs. sum — the fundamental split

Types in programming combine in two ways:

- **Product types** — a combination of fields: `(name: str, age: int)`. Dataclasses, named tuples, dicts with known keys. The "product" name comes from the number of possible values being the *product* of each field's possibilities.
- **Sum types** — one of several variants: `Success(value) | Failure(error)`. The "sum" name comes from the total possible values being the *sum* of each variant's possibilities.

Sum types come from the ML family of languages: Haskell's `Either`, Rust's `Result` and `enum`, OCaml's variants, TypeScript's discriminated unions. Python doesn't have native sum types, but you can express them idiomatically.

### Approach 1: `Enum` for simple variants

When your variants carry no per-variant data, `Enum` is the right tool:

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
```

This is better than using raw strings (`status = "pending"`) because:
- Typos like `"pendign"` fail loudly at definition time.
- IDE autocompletion and type checkers understand `Status.PENDING`.
- `match/case` works with enum values.

### Approach 2: Tagged dataclasses (Python's main idiom)

When variants carry different data, use dataclasses plus `Union` or `|`:

```python
from dataclasses import dataclass

@dataclass
class Success:
    value: object

@dataclass
class Failure:
    error: str

Result = Success | Failure   # Python 3.10+ syntax

def divide(a: float, b: float) -> Result:
    if b == 0:
        return Failure("division by zero")
    return Success(a / b)
```

Each variant is a separate class. The union type `Result = Success | Failure` tells the type checker that a `Result` is one or the other.

### Pattern matching (Python 3.10+)

`match/case` lets you destructure sum types cleanly:

```python
def show(r: Result) -> str:
    match r:
        case Success(value=v):
            return f"ok: {v}"
        case Failure(error=e):
            return f"err: {e}"
```

This is more than a fancy if/elif chain. `match` destructures the object — it extracts fields by name and binds them to local variables in one step. It also enables exhaustiveness checking: if you add a third variant later, tools like `mypy` can warn you about unhandled cases (using `typing.assert_never` in the default case).

### Why sum types beat None + exceptions

Consider a function that finds a user:

```python
# The old way: return None on failure
user = find(users, is_admin)
if user is not None:
    user.promote()        # forget the check → crash at runtime
```

The problem: nothing forces the caller to check for `None`. The crash happens far from the cause, at runtime, possibly in production.

With sum types:

```python
match find(users, is_admin):
    case None:
        log("no admin found")
    case User() as u:
        u.promote()
```

The `match` forces you to address both cases. Even better, use a custom `Found | NotFound` type to make the intent explicit.

### Typed exceptions as sums

For *expected* failure modes, a sum-type return is often cleaner than raising:

```python
def parse(s: str) -> Success | Failure:
    try:
        return Success(int(s))
    except ValueError as e:
        return Failure(str(e))
```

Use exceptions for *exceptional* conditions (disk failure, network timeout, bugs). Use sum types for *expected alternatives* (validation errors, "not found" results, parse failures).

### Enforcing exhaustiveness

Add a default case that uses `typing.assert_never` to catch unhandled variants at type-check time:

```python
from typing import assert_never

def handle(r: Result) -> str:
    match r:
        case Success(value=v):
            return f"ok: {v}"
        case Failure(error=e):
            return f"err: {e}"
        case _ as unreachable:
            assert_never(unreachable)
```

If you add a third variant to `Result` and forget to handle it, `mypy` will flag the `assert_never` call as an error.

## Why these design choices

**Why doesn't Python have native sum types?** Python is dynamically typed. In statically typed languages (Rust, Haskell), the compiler enforces exhaustive matching. Python relies on runtime checks and optional type checkers like `mypy`. The `dataclass + |` pattern is the pragmatic compromise.

**When are sum types overkill?** For simple boolean outcomes (`found` / `not found` where None is obvious), a plain `Optional[T]` is fine. Don't create `Found(value) | NotFound()` when `T | None` communicates the same thing more simply.

**When are sum types essential?** When you have three or more variants, or when variants carry different data. `Ok(body) | Redirect(url) | NotFound(reason) | Error(code, message)` — no amount of None-checking or exception-catching models this as cleanly.

**Why use `match/case` instead of `isinstance` chains?** `match` destructures in one step, binds fields to local variables, and reads as a declaration of "these are the cases." An `isinstance` chain is imperative — it checks one type at a time and requires manual attribute access.

## Production-quality code

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, assert_never

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class Failure:
    error: str


Result = Success[T] | Failure


def divide(a: float, b: float) -> Result[float]:
    if b == 0:
        return Failure("division by zero")
    return Success(a / b)


def map_result(r: Result[T], fn) -> Result:
    """Apply fn to the value if Success, pass through Failure."""
    match r:
        case Success(value=v):
            return Success(fn(v))
        case Failure():
            return r
        case _ as unreachable:
            assert_never(unreachable)


# --- HTTP outcome example ---
@dataclass(frozen=True, slots=True)
class Ok:
    body: dict

@dataclass(frozen=True, slots=True)
class Redirect:
    url: str

@dataclass(frozen=True, slots=True)
class NotFound:
    reason: str

@dataclass(frozen=True, slots=True)
class ServerError:
    code: int
    message: str

HttpOutcome = Ok | Redirect | NotFound | ServerError


def render(outcome: HttpOutcome) -> dict:
    match outcome:
        case Ok(body=b):
            return {"status": 200, "data": b}
        case Redirect(url=u):
            return {"status": 302, "location": u}
        case NotFound(reason=r):
            return {"status": 404, "error": r}
        case ServerError(code=c, message=m):
            return {"status": c, "error": m}
        case _ as unreachable:
            assert_never(unreachable)


# --- Expression AST example ---
@dataclass(frozen=True)
class Num:
    value: int | float

@dataclass(frozen=True)
class Add:
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul:
    left: Expr
    right: Expr

Expr = Num | Add | Mul


def evaluate(e: Expr) -> int | float:
    match e:
        case Num(value=v):
            return v
        case Add(left=l, right=r):
            return evaluate(l) + evaluate(r)
        case Mul(left=l, right=r):
            return evaluate(l) * evaluate(r)
        case _ as unreachable:
            assert_never(unreachable)


# --- Usage ---
assert divide(10, 3) == Success(10 / 3)
assert divide(10, 0) == Failure("division by zero")
assert map_result(divide(10, 2), lambda x: x * 2) == Success(10.0)
assert evaluate(Add(Num(1), Mul(Num(2), Num(3)))) == 7
assert render(Ok({"id": 1})) == {"status": 200, "data": {"id": 1}}
```

## Security notes

- **Sentinel values leak logic:** Using magic strings (`"error"`, `""`, `"-1"`) as error indicators is fragile and can be confused with valid data. Sum types make the error case structurally distinct, reducing the chance of treating an error as a valid value.
- **Exhaustive matching prevents silent failures:** With `assert_never` in the default case, adding a new variant (like a new error type) forces you to handle it. Without exhaustive matching, new error modes can silently fall through to a catch-all.

## Performance notes

- **Dataclass overhead:** `@dataclass(frozen=True, slots=True)` instances are slightly cheaper to create and access than regular classes. `slots=True` eliminates `__dict__` overhead.
- **`match/case` speed:** `match` on class patterns is roughly equivalent to an `isinstance` check + attribute access — no significant overhead versus manual type dispatch.
- **Sum types vs. exceptions for control flow:** Creating an exception object is ~5–10x more expensive than creating a dataclass instance. If your function returns a `Failure` on 30% of calls, using a sum type is measurably cheaper than raising an exception.
- **Generic dataclasses:** `Generic[T]` has zero runtime cost in CPython — type parameters are erased at runtime.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | New variant silently ignored | `match` has no default case or `assert_never` — new variants fall through | Always add `case _ as x: assert_never(x)` as the final case. Run `mypy` to check. |
| 2 | Using `status = "pending"` instead of an enum | Stringly-typed variants — typos pass silently, no autocompletion | Use `Enum` for fixed sets of simple variants. |
| 3 | `match` case doesn't destructure properly | Wrong pattern syntax — e.g., `case Success(v)` instead of `case Success(value=v)` | Use keyword patterns for dataclasses: `case Success(value=v)`. Positional patterns only work with `__match_args__`. |
| 4 | Using sum types where `Optional[T]` is clearer | Over-engineering — creating `Found(T) | NotFound()` when `T | None` is fine | Use `Optional[T]` for simple "value or absent" cases. Reserve sum types for 3+ variants or variants with different data. |
| 5 | Returning `(value, error)` tuples instead of typed variants | Go-style error handling without type safety | Use `Success(value) | Failure(error)` — the type checker can verify you handle both cases. |

## Practice

**Warm-up.** Define `Shape = Circle | Square | Triangle` as dataclasses with appropriate fields, and write a `area(shape)` function using `match`.

<details><summary>Solution</summary>

```python
from dataclasses import dataclass
import math

@dataclass
class Circle:
    radius: float

@dataclass
class Square:
    side: float

@dataclass
class Triangle:
    base: float
    height: float

Shape = Circle | Square | Triangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return math.pi * r ** 2
        case Square(side=s):
            return s ** 2
        case Triangle(base=b, height=h):
            return 0.5 * b * h

assert area(Circle(5)) == math.pi * 25
assert area(Square(4)) == 16
assert area(Triangle(6, 3)) == 9.0
```

</details>

**Standard.** Refactor a function that returns `(result, error)` tuples into proper `Success | Failure` types.

<details><summary>Solution</summary>

```python
from dataclasses import dataclass

# Before: tuple-based
def parse_int_old(s):
    try:
        return (int(s), None)
    except ValueError as e:
        return (None, str(e))

# After: sum types
@dataclass
class Success:
    value: object

@dataclass
class Failure:
    error: str

def parse_int(s: str) -> Success | Failure:
    try:
        return Success(int(s))
    except ValueError as e:
        return Failure(str(e))

match parse_int("42"):
    case Success(value=v):
        print(f"Parsed: {v}")
    case Failure(error=e):
        print(f"Error: {e}")
```

</details>

**Bug hunt.** Your `match` falls through silently for a new variant you just added. How do you enforce exhaustiveness?

<details><summary>Solution</summary>

Add a default case using `typing.assert_never`:

```python
from typing import assert_never

def handle(r: Result) -> str:
    match r:
        case Success(value=v):
            return f"ok: {v}"
        case Failure(error=e):
            return f"err: {e}"
        case _ as unreachable:
            assert_never(unreachable)
```

If you add a third variant to `Result` and forget to handle it:
- At runtime: `assert_never` raises `AssertionError`.
- With `mypy`: the type checker flags it as an error before you run the code.

</details>

**Stretch.** Implement a `Maybe[T]` pattern with `Some(value: T)` and `Nothing`, plus `map_maybe(m, fn)` that applies `fn` only to `Some`.

<details><summary>Solution</summary>

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, assert_never

T = TypeVar("T")
U = TypeVar("U")

@dataclass(frozen=True)
class Some(Generic[T]):
    value: T

@dataclass(frozen=True)
class Nothing:
    pass

Maybe = Some[T] | Nothing

def map_maybe(m: Maybe[T], fn: Callable[[T], U]) -> Maybe[U]:
    match m:
        case Some(value=v):
            return Some(fn(v))
        case Nothing():
            return Nothing()
        case _ as unreachable:
            assert_never(unreachable)

assert map_maybe(Some(5), lambda x: x * 2) == Some(10)
assert map_maybe(Nothing(), lambda x: x * 2) == Nothing()
```

</details>

**Stretch++.** Write a typed JSON schema decoder that returns `Valid(data) | Invalid(errors: list[str])`. Validate a dict against a schema of required fields with expected types.

<details><summary>Solution</summary>

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Valid:
    data: dict

@dataclass(frozen=True)
class Invalid:
    errors: list[str]

ValidationResult = Valid | Invalid

def validate(data: dict, schema: dict[str, type]) -> ValidationResult:
    errors = []
    for field, expected_type in schema.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(
                f"Field '{field}' expected {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )
    return Invalid(errors) if errors else Valid(data)

schema = {"name": str, "age": int, "email": str}
assert isinstance(validate({"name": "Ada", "age": 36, "email": "a@b.c"}, schema), Valid)
result = validate({"name": "Ada", "age": "old"}, schema)
assert isinstance(result, Invalid)
assert len(result.errors) == 2  # wrong type for age, missing email
```

</details>

## In plain terms (newbie lane)
If `Sum Types` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A sum type means a value is:
    (a) Many of several things at once
    (b) Exactly one of several possible variants
    (c) A numerical sum
    (d) A tuple

2. A product type is:
    (a) A tuple, record, or dataclass — fields combined with AND
    (b) A variant or union
    (c) An enum
    (d) A function

3. `match/case` was added in Python:
    (a) 2.7
    (b) 3.8
    (c) 3.10
    (d) 3.12

4. Sum types can replace:
    (a) Boolean logic entirely
    (b) None + exceptions for expected failure modes
    (c) All classes
    (d) All enums

5. To enforce exhaustive matching:
    (a) It's impossible in Python
    (b) Use `typing.assert_never` in the default case, combined with `mypy`
    (c) Use `else: raise` only
    (d) No action needed — Python enforces it automatically

**Short answer:**

6. Why are sum types safer than sentinel values like `-1` or `""` for errors?
7. When is `Enum` sufficient versus tagged dataclasses?

*Answers: 1-b, 2-a, 3-c, 4-b, 5-b, 6. Sentinel values can be confused with valid data (is -1 an error or a real value?). Sum types are structurally distinct — Success and Failure are different types, so the compiler/type checker can verify you handle both. You can't accidentally treat a Failure as valid data. 7. Enum is sufficient when variants carry no per-variant data (e.g., Status.PENDING, Status.SHIPPED). Use tagged dataclasses when each variant needs its own fields (e.g., Success(value) vs. Failure(error)).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-sum-types — mini-project](mini-projects/09-sum-types-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Sum types model "one of" — a value is exactly one variant at any time, in contrast to product types where all fields are present.
- Python expresses sum types with dataclasses + `|` unions + `match/case` (3.10+).
- Pattern matching destructures variants and binds fields in one step. Use `assert_never` in the default case for exhaustive checking.
- Prefer sum types over sentinel values and exceptions for expected failure modes — they force callers to handle all cases.

## Further reading

- [PEP 636](https://peps.python.org/pep-0636/) — Structural Pattern Matching Tutorial.
- [PEP 634](https://peps.python.org/pep-0634/) — Structural Pattern Matching Specification.
- Python docs: [`typing.assert_never`](https://docs.python.org/3/library/typing.html#typing.assert_never).
- Scott Wlaschin, *Domain Modeling Made Functional* — the definitive guide to modeling with sum types (F# examples, concepts transfer to any language).
- Next module: [Module 06 — Data Structures & Algorithms](../06-dsa/README.md).
