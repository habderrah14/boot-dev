# Chapter 06 — Polymorphism

> "Polymorphism — 'many shapes' — lets the same function handle different concrete types as long as they speak the same interface."

## Learning objectives

By the end of this chapter you will be able to:

- Recognize and apply the three kinds of polymorphism: subtype, ad-hoc (overloading), and parametric (generics).
- Use duck typing to write flexible code, and explain when to formalize it with a Protocol.
- Override dunder methods to plug your classes into Python's language features (`for`, `+`, `len`, `with`, `sorted`).
- Use `functools.singledispatch` for free-function polymorphism.
- Know when polymorphism helps and when a simple `if isinstance` is clearer.

## Prerequisites & recap

- [Inheritance](05-inheritance.md) — subclassing, `super()`, MRO.
- [Abstraction](04-abstraction.md) — ABCs, Protocols, contracts.

## The simple version

Polymorphism means "one interface, many implementations." When you write `for x in collection`, Python doesn't care whether `collection` is a list, a set, a generator, or your custom class — as long as it implements `__iter__`. The loop code is the same; the behavior adapts to the concrete type at runtime.

This is powerful because it lets you write *generic* code that works with any type satisfying a contract, without knowing (or caring) what that type is. You write `total_area(shapes)` once, and it works with circles, rectangles, and any shape you invent next year — zero changes to the calling code.

## Visual flow

```
                  caller: s.area()
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │  Circle  │ │ Rectangle│ │ Triangle │
     │          │ │          │ │          │
     │ area() = │ │ area() = │ │ area() = │
     │ π·r²     │ │ w·h      │ │ Heron's  │
     └──────────┘ └──────────┘ └──────────┘

  Same call site, different behavior — that's polymorphism.

  ┌──────────────────────────────────────────────┐
  │  singledispatch: render(x)                    │
  │                                               │
  │  x is int   → render.register(int)            │
  │  x is list  → render.register(list)           │
  │  x is dict  → render.register(dict)           │
  │  x is ???   → fallback: str(x)                │
  └──────────────────────────────────────────────┘
```
*Figure 1 — Subtype polymorphism (top) dispatches on the object's type. Singledispatch (bottom) dispatches on the first argument's type.*

## Concept deep-dive

### Subtype polymorphism

This is the classic form: call the same method on different types, and each responds appropriately:

```python
def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)
```

`shapes` may contain `Circle`, `Rectangle`, `Triangle`, or anything else with an `.area()` method. The call site doesn't know or care which concrete type each element is. This is the OOP payoff: you add a new shape by writing one class, not by modifying every function that touches shapes.

Why this works in Python: method lookup happens at runtime. When Python executes `s.area()`, it looks up `area` on `s.__class__`, finds the concrete implementation, and calls it. No compilation, no vtable — just attribute lookup.

### Duck typing

Python doesn't require shared inheritance for polymorphism. If it walks like a duck and quacks like a duck:

```python
def save(item):
    item.serialize()    # works for anything with .serialize()
```

No base class, no interface declaration — if the object has the method, it works. This is incredibly flexible but can be dangerous in large codebases: you won't know something is broken until runtime. Protocols (Chapter 04) give you static type checking for duck-typed interfaces.

When duck typing shines: small scripts, glue code, and situations where requiring inheritance would be invasive (e.g., accepting file-like objects from the standard library, third-party libraries, and your own code).

### Ad-hoc polymorphism (overloading)

Python doesn't support method overloading by argument types the way C++ or Java do. You can't write two `def area(circle)` / `def area(rect)` functions — the second one silently replaces the first. Python's alternatives:

**Default arguments** for minor variation:

```python
def connect(host: str, port: int = 5432) -> Connection: ...
```

**Alternative constructors** (`@classmethod`) for different input shapes:

```python
Temperature.from_celsius(100)
Temperature.from_fahrenheit(212)
```

**`functools.singledispatch`** for truly polymorphic free functions:

```python
from functools import singledispatch

@singledispatch
def render(x) -> str:
    return str(x)

@render.register(int)
def _(x: int) -> str:
    return f"{x:,}"

@render.register(list)
def _(x: list) -> str:
    return "[" + ", ".join(render(e) for e in x) + "]"

@render.register(dict)
def _(x: dict) -> str:
    pairs = (f"{k}={render(v)}" for k, v in x.items())
    return "{" + ", ".join(pairs) + "}"
```

`singledispatch` dispatches on the *first argument's type*. It's the Pythonic answer to visitor patterns and type-based branching.

### Parametric polymorphism (generics)

Python supports generics through type hints, checked statically by mypy/pyright:

```python
from typing import TypeVar

T = TypeVar("T")

def first(xs: list[T]) -> T:
    if not xs:
        raise ValueError("empty list")
    return xs[0]
```

`first` works with `list[int]`, `list[str]`, `list[Point]` — the type variable `T` is filled in by the type checker. At runtime, Python doesn't enforce this — it's purely a static analysis tool. But it catches bugs before they ship.

### Dunder methods — Pythonic polymorphism

Implementing specific dunder methods plugs your class into Python's language features:

| Dunder | Language feature | Example |
|---|---|---|
| `__len__` | `len(x)` | Collections |
| `__iter__` / `__next__` | `for x in obj` | Iterables |
| `__getitem__` / `__setitem__` | `obj[k]`, `obj[k] = v` | Subscriptable types |
| `__add__` / `__radd__` | `a + b` | Arithmetic |
| `__mul__` / `__rmul__` | `a * b` | Scalar multiplication |
| `__eq__` / `__lt__` | `==`, `<`, `sorted()` | Comparison |
| `__enter__` / `__exit__` | `with obj:` | Context managers |
| `__call__` | `obj(args)` | Callable objects |
| `__contains__` | `x in obj` | Membership tests |

Implementing these makes your class *behave like a Python value*. A `Vector2D` with `__add__` and `__mul__` works with `sum()`. A `Playlist` with `__iter__` and `__len__` works with `for` loops and `len()`. This is polymorphism in its most Pythonic form.

### When `isinstance` is clearer

Not everything needs polymorphic methods. If you're handling 2-3 types in one place and the logic is short, an `isinstance` check is perfectly readable:

```python
def format_value(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (int, float)):
        return f"{v:,.2f}"
    return str(v)
```

The test for when to switch: if you find yourself writing `isinstance` chains longer than 3-4 cases, or repeating them in multiple places, that's a signal to refactor toward polymorphic methods or `singledispatch`.

## Why these design choices

**Why duck typing instead of declared interfaces?** Python was designed for rapid development. Requiring interface declarations for every function parameter would slow down prototyping and make the language feel like Java. Duck typing is faster to write, more flexible, and works well for small-to-medium codebases.

**Why add Protocols later?** As Python codebases grew to millions of lines, duck typing's "you'll find out at runtime" became a liability. Protocols give you the best of both worlds: duck typing's flexibility with static type checking's safety.

**Why `singledispatch` instead of `isinstance` chains?** `singledispatch` is *open* — you can add new type handlers without modifying the original function. An `isinstance` chain requires editing the function every time you add a type. In library code, `singledispatch` lets consumers extend your dispatch without touching your source.

**When you'd pick differently:** In a small script with 3 types that will never change, `isinstance` is simpler than setting up `singledispatch`. In performance-critical code, a direct method call is faster than dispatch machinery.

## Production-quality code

```python
from __future__ import annotations

from dataclasses import dataclass
from functools import singledispatch, total_ordering
import math


@total_ordering
@dataclass(frozen=True)
class Vector2D:
    """Immutable 2D vector with full arithmetic support."""

    x: float
    y: float

    @property
    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    @property
    def angle(self) -> float:
        """Angle in radians from the positive x-axis."""
        return math.atan2(self.y, self.x)

    def normalized(self) -> Vector2D:
        m = self.magnitude
        if m == 0:
            raise ValueError("cannot normalize the zero vector")
        return Vector2D(self.x / m, self.y / m)

    def __add__(self, other: object) -> Vector2D:
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other: object) -> Vector2D:
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, scalar: object) -> Vector2D:
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar: object) -> Vector2D:
        return self.__mul__(scalar)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def __matmul__(self, other: object) -> float:
        """Dot product via the @ operator."""
        if isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Vector2D):
            return self.magnitude < other.magnitude
        return NotImplemented

    def __abs__(self) -> float:
        return self.magnitude

    @classmethod
    def zero(cls) -> Vector2D:
        return cls(0.0, 0.0)

    @classmethod
    def from_polar(cls, r: float, theta: float) -> Vector2D:
        return cls(r * math.cos(theta), r * math.sin(theta))


# ── Custom iterable ─────────────────────────────────────

class CountDown:
    """Iterator that counts down from `start` to 1."""

    def __init__(self, start: int):
        if start < 0:
            raise ValueError("start must be non-negative")
        self._current = start

    def __iter__(self) -> CountDown:
        return self

    def __next__(self) -> int:
        if self._current <= 0:
            raise StopIteration
        value = self._current
        self._current -= 1
        return value

    def __repr__(self) -> str:
        return f"CountDown(remaining={self._current})"


# ── singledispatch for free-function polymorphism ───────

@singledispatch
def pretty(x: object) -> str:
    """Human-readable representation, dispatched by type."""
    return repr(x)

@pretty.register(int)
def _pretty_int(x: int) -> str:
    return f"{x:,}"

@pretty.register(float)
def _pretty_float(x: float) -> str:
    return f"{x:,.2f}"

@pretty.register(list)
def _pretty_list(x: list) -> str:
    items = ", ".join(pretty(e) for e in x)
    return f"[{items}]"

@pretty.register(dict)
def _pretty_dict(x: dict) -> str:
    pairs = ", ".join(f"{pretty(k)}: {pretty(v)}" for k, v in x.items())
    return "{" + pairs + "}"

@pretty.register(Vector2D)
def _pretty_vector(x: Vector2D) -> str:
    return f"({x.x:.1f}, {x.y:.1f})"
```

## Security notes

N/A — polymorphism is a dispatch mechanism, not a security boundary. However, in systems that accept plugin classes or user-defined types, be careful about what dunder methods you invoke on untrusted objects. A malicious `__eq__` or `__hash__` could perform arbitrary operations. In sandboxed environments, restrict which dunder methods are called on external objects.

## Performance notes

- **Method dispatch** in Python is an attribute lookup on the MRO — O(depth of hierarchy), typically 3-5 levels. Fast enough for virtually all backend code.
- **`singledispatch`** adds a dictionary lookup on the first argument's type. Negligible for most use cases, but in a hot inner loop processing millions of items, direct method calls will be faster.
- **Dunder methods** are looked up on the *type*, not the instance (for correctness reasons). This means Python skips instance `__dict__` and goes straight to the class, which is actually slightly faster than normal attribute access.
- **`@total_ordering`** generates comparison methods from `__eq__` and one of `__lt__`/`__le__`/`__gt__`/`__ge__`. The generated methods are slower than hand-written ones because they involve an extra function call, but the difference is negligible unless you're sorting millions of items.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Long `if isinstance(x, A): ... elif isinstance(x, B): ...` chains scattered across the codebase | Using type-checking instead of polymorphic dispatch | Refactor: move the behavior into methods on each type, or use `singledispatch`. |
| 2 | `TypeError: unsupported operand type(s) for +` when adding your custom objects | Dunder method (`__add__`) not defined, or returns wrong type | Implement `__add__` and return `NotImplemented` (not raise) for unsupported types so Python can try `__radd__` on the other operand. |
| 3 | `sorted([obj1, obj2])` raises `TypeError` | Missing `__lt__` — Python's `sorted()` uses `<` for comparisons | Define `__lt__`, or use `@functools.total_ordering` with `__eq__` and one comparison method. |
| 4 | `__eq__` defined but objects can't be used as dict keys or in sets | `__eq__` without `__hash__` makes the class unhashable | Use `@dataclass(frozen=True)`, or define `__hash__` explicitly when you define `__eq__`. |
| 5 | `singledispatch` always hits the fallback, ignoring registered types | Registering on a base class but passing a subclass, or a typo in the registered type | Check that the registered type matches the actual runtime type. `singledispatch` uses `type(arg)`, not `isinstance`. |

## Practice

**Warm-up.** Add `__len__` and `__contains__` to a custom `Playlist` class so `len(playlist)` and `"song" in playlist` work.

**Standard.** Build a `Vector2D` class supporting `+`, `-`, `*` (scalar), `==`, and `abs()` (magnitude). Verify with tests that `v1 + v2`, `v * 3`, `3 * v`, and `abs(v)` all work.

**Bug hunt.** Why does `sorted([Point(0,0), Point(1,1)])` raise a `TypeError`? Fix it.

**Stretch.** Replace an `isinstance` ladder in your codebase (or write one to practice) with polymorphic methods on the types involved. Compare readability.

**Stretch++.** Use `singledispatch` to implement `pretty(x)` that formats `int`, `float`, `list`, `dict`, and a custom class differently. Add a new type registration from outside the module.

<details><summary>Show solutions</summary>

**Bug hunt.** Python's `sorted()` uses `<` to compare elements, which requires `__lt__`. `Point` doesn't define it.

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __lt__(self, other: Point) -> bool:
        return (self.x, self.y) < (other.x, other.y)
```

**Stretch++.**

```python
from functools import singledispatch

@singledispatch
def pretty(x) -> str:
    return repr(x)

@pretty.register(int)
def _(x: int) -> str:
    return f"{x:,}"

@pretty.register(list)
def _(x: list) -> str:
    return "[" + ", ".join(pretty(e) for e in x) + "]"
```

From another module:

```python
from mymodule import pretty

@pretty.register(MyCustomType)
def _(x: MyCustomType) -> str:
    return f"Custom({x.value})"
```

</details>

## In plain terms (newbie lane)
If `Polymorphism` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Polymorphism lets:
    (a) one function operate on several types through a shared interface  (b) one type perform several unrelated actions  (c) types change at runtime  (d) a class inherit from multiple parents

2. Duck typing relies on:
    (a) declared interfaces  (b) the presence of expected methods at runtime  (c) metaclasses  (d) compile-time reflection

3. Python method overloading by argument types:
    (a) is a native keyword  (b) is not natively supported; use `singledispatch` or default arguments  (c) is done via `__overload__`  (d) requires C extensions

4. Implementing `__iter__` and `__next__` makes your class:
    (a) sortable  (b) iterable in `for` loops  (c) callable  (d) hashable

5. `singledispatch` dispatches on:
    (a) the first argument's type  (b) all arguments' types  (c) the return type  (d) the class hierarchy

**Short answer:**

6. When is a polymorphic method clearer than an `isinstance` ladder?
7. Why is duck typing both powerful and dangerous?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-a. 6 — When you have more than 3-4 cases, when the same dispatch appears in multiple places, or when new types are added frequently. Polymorphic methods put the behavior next to the data and are open to extension without modifying existing code. 7 — Powerful because any object with the right methods works, regardless of inheritance. Dangerous because you won't discover a missing method until runtime — no compiler or type checker warns you (unless you use Protocols).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-polymorphism — mini-project](mini-projects/06-polymorphism-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Polymorphism generalizes behavior lookup: the same interface, many implementations, resolved at runtime.
- Duck typing + dunder methods = Pythonic polymorphism. Implementing `__iter__`, `__add__`, `__len__` makes your class a first-class Python citizen.
- `singledispatch` is the Pythonic answer to free-function polymorphism — open to extension without modifying the original function.
- Use polymorphism when new types are added frequently; use `isinstance` when the set of types is small and stable.

## Further reading

- Python docs: [Data model — Special method names](https://docs.python.org/3/reference/datamodel.html#special-method-names) — the full dunder method reference.
- Python docs: [`functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch).
- *Fluent Python*, Luciano Ramalho, Part IV — covers the Python data model and operator overloading in depth.
- Next module: [Module 05 — Functional Programming](../05-fp/README.md).
