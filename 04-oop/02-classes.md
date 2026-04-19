# Chapter 02 — Classes

> "A class is a blueprint. An instance is a house built from it. The class says what every house will have; the instance carries the values for *this* one house."

## Learning objectives

By the end of this chapter you will be able to:

- Define a class with `__init__`, instance methods, and type hints.
- Distinguish instance attributes from class attributes and explain when each is appropriate.
- Use `self` correctly and explain what Python does with it behind the scenes.
- Implement `__repr__` and `__eq__` so your objects are debuggable and comparable.
- Use `@dataclass` to eliminate boilerplate for value-oriented types.
- Choose between instance methods, class methods, and static methods.

## Prerequisites & recap

- [Clean code](01-clean-code.md) — naming, small functions, single responsibility.
- [Functions](../01-python/03-functions.md) — parameters, return values, scope.

## The simple version

A class is a way to bundle related data and the functions that operate on that data into a single named unit. Instead of passing a `name`, `balance`, and `owner_id` around as separate variables (and hoping you never mix up whose balance belongs to whom), you create an `Account` object that carries its own data and knows how to `deposit`, `withdraw`, and describe itself. The class is the template; each object you create from it is an instance with its own values.

Why bother? Because as your program grows, loose data and free functions become impossible to keep straight. Classes give you a namespace, a constructor, and a guarantee that the data and its operations travel together.

## Visual flow

```
  ┌─────────────────────────────────┐
  │         class Point             │  ◄── The blueprint
  │  ┌───────────────────────────┐  │
  │  │  __init__(self, x, y)    │  │  ◄── Constructor
  │  │  distance_to(self, other)│  │  ◄── Instance method
  │  │  __repr__(self)          │  │  ◄── Developer-facing string
  │  │  __eq__(self, other)     │  │  ◄── Equality check
  │  └───────────────────────────┘  │
  └────────────┬────────────────────┘
               │
       ┌───────┴───────┐
       │               │
  ┌────▼────┐    ┌─────▼────┐
  │ a = Point│    │ b = Point│     ◄── Instances
  │ x=0 y=0 │    │ x=3 y=4  │
  └─────────┘    └──────────┘

  a.distance_to(b)  →  5.0
  a == Point(0, 0)  →  True
```
*Figure 1 — One class, two instances, each holding its own `x` and `y`.*

## Concept deep-dive

### Anatomy of a class

```python
class Point:
    """A 2-D point in Cartesian space."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"Point({self.x!r}, {self.y!r})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
```

```python
a = Point(0, 0)
b = Point(3, 4)
a.distance_to(b)   # 5.0
a == Point(0, 0)   # True
```

Every method receives `self` as its first parameter, which is the instance the method was called on. `__init__` is the initializer — it runs right after the instance is created and sets up its state.

### `self` — what it really is

`self` is a convention (not a keyword) for the instance passed implicitly as the first parameter. When you write `a.distance_to(b)`, Python translates it to `Point.distance_to(a, b)`. Understanding this removes the mystery: `self` is just the object on the left side of the dot.

### Instance vs. class attributes

```python
class Dog:
    species = "Canis familiaris"     # class attribute — shared by all Dogs

    def __init__(self, name: str):
        self.name = name              # instance attribute — unique to this Dog
```

Class attributes live on the class object and are shared across every instance. If you mutate a class attribute through the class (`Dog.species = "wolf"`), every instance sees the change. If you assign through an instance (`fido.species = "wolf"`), you create a *shadow* — an instance attribute that hides the class attribute for that instance only.

Why this distinction matters: mutable class attributes (especially lists and dicts) are a notorious bug source. If you write `class C: xs = []`, every instance shares the same list. Move mutable defaults into `__init__`.

### `__repr__` and `__str__`

- `__repr__` — unambiguous, developer-facing. Shown in the REPL, in debuggers, and in log output. Ideally produces a string that could reconstruct the object.
- `__str__` — user-friendly. Falls back to `__repr__` if not defined.

Always define `__repr__`. It's three lines that save you hours of `print(type(x), x.__dict__)` debugging.

### Dataclasses — eliminating boilerplate

For types that are primarily data carriers, `@dataclass` generates `__init__`, `__repr__`, and `__eq__` for you:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

With `frozen=True`, instances are immutable and hashable — safe to use as dict keys and set members. You get value semantics (two `Point(0, 0)` are equal) without writing any boilerplate.

Why dataclasses? Because hand-writing `__init__`, `__repr__`, and `__eq__` for every value type is tedious, error-prone, and adds noise. Dataclasses let you declare *what* a type holds and let Python handle the *how*.

### Method kinds

- **Instance method** — takes `self`, operates on a specific instance.
- **Class method** — decorated with `@classmethod`, takes `cls`. Used for alternative constructors.
- **Static method** — decorated with `@staticmethod`, takes neither. A plain function that lives in the class namespace for organizational reasons.

```python
class Temperature:
    def __init__(self, kelvin: float):
        if kelvin < 0:
            raise ValueError("temperature cannot be negative Kelvin")
        self.kelvin = kelvin

    @classmethod
    def from_celsius(cls, c: float) -> "Temperature":
        return cls(c + 273.15)

    @staticmethod
    def absolute_zero() -> float:
        return 0.0
```

`from_celsius` is an *alternative constructor* — the Pythonic answer to constructor overloading. It returns a new instance via `cls(...)`, which means it works correctly with subclasses too.

## Why these design choices

**Why `self` instead of an implicit `this`?** Python's philosophy is "explicit is better than implicit." Making the instance an explicit parameter means there's no hidden magic — you can see exactly what every method receives.

**Why `__repr__` before anything else?** Debugging is the most common activity in programming. A class without `__repr__` prints as `<__main__.Point object at 0x...>`, which tells you nothing. Three lines of `__repr__` pay for themselves the first time you hit a bug.

**Why frozen dataclasses?** Immutable objects are easier to reason about, safe to share across threads, and usable as dict keys. You should default to `frozen=True` and only drop it when you have a concrete reason to mutate.

**When you'd pick differently:** If your class has complex initialization logic, validation, or mutable state with invariants, a hand-written class gives you more control than a dataclass. If your type is a one-off internal structure, a `NamedTuple` or plain dict might be simpler.

## Production-quality code

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Monetary value with currency, stored as integer cents to avoid float rounding."""

    amount_cents: int
    currency: str = "USD"

    def __post_init__(self):
        if not isinstance(self.amount_cents, int):
            raise TypeError(f"amount_cents must be int, got {type(self.amount_cents).__name__}")
        if self.amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        if len(self.currency) != 3:
            raise ValueError(f"currency must be a 3-letter ISO code, got {self.currency!r}")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"cannot add {self.currency} and {other.currency} — convert first"
            )
        return Money(self.amount_cents + other.amount_cents, self.currency)

    def __str__(self) -> str:
        dollars = self.amount_cents // 100
        cents = self.amount_cents % 100
        return f"{self.currency} {dollars}.{cents:02d}"


class Account:
    """A simple bank account with deposit/withdraw and overdraft protection."""

    def __init__(self, owner: str, balance_cents: int = 0):
        if not owner.strip():
            raise ValueError("owner must be a non-empty string")
        if balance_cents < 0:
            raise ValueError("initial balance cannot be negative")
        self._owner = owner
        self._balance = Money(balance_cents)

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> Money:
        return self._balance

    def deposit(self, amount_cents: int) -> None:
        if amount_cents <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance = self._balance + Money(amount_cents)

    def withdraw(self, amount_cents: int) -> None:
        if amount_cents <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount_cents > self._balance.amount_cents:
            raise ValueError(
                f"insufficient funds: have {self._balance}, need {Money(amount_cents)}"
            )
        self._balance = Money(self._balance.amount_cents - amount_cents)

    def __repr__(self) -> str:
        return f"Account(owner={self._owner!r}, balance={self._balance})"
```

## Security notes

N/A — classes themselves are not a security boundary. However, if you store sensitive data (passwords, tokens, API keys) as plain instance attributes, they'll show up in `__repr__`, `__dict__`, stack traces, and log files. For sensitive fields, override `__repr__` to redact them, or use a dedicated secret-handling type.

## Performance notes

- **Instance creation** is cheap in Python — roughly the cost of a dict allocation plus `__init__`. You can create millions of small objects without concern.
- **`__slots__`** replaces the per-instance `__dict__` with a fixed-size array. This saves ~40 bytes per instance and speeds up attribute access slightly. Use it when you're creating millions of instances of the same class. Otherwise, the readability cost (no dynamic attributes, tricky with inheritance) isn't worth it.
- **Dataclass overhead** is zero at runtime — the generated methods are regular Python functions.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `TypeError: method() takes 1 positional argument but 2 were given` | Forgot `self` in the method signature | Add `self` as the first parameter of every instance method. |
| 2 | All instances share the same list and mutate each other's data | Mutable class attribute (`class C: xs = []`) used instead of instance attribute | Move mutable defaults into `__init__`: `self.xs = []`. |
| 3 | Objects can't be used in sets or as dict keys after defining `__eq__` | Overriding `__eq__` without `__hash__` makes the class unhashable | Use `@dataclass(frozen=True)` (handles both), or define `__hash__` explicitly. |
| 4 | `__repr__` returns `<MyClass object at 0x...>` | Never defined `__repr__` | Always define `__repr__`. Three lines, massive debugging payoff. |
| 5 | Subclass `@classmethod` returns the parent type instead of the subclass | Hardcoding the class name instead of using `cls(...)` | Use `cls(...)` in class methods so subclasses get instances of their own type. |

## Practice

**Warm-up.** Write a `Rectangle(width, height)` class with an `area()` method and a useful `__repr__`.

**Standard.** Convert your `Rectangle` to a `@dataclass`. Add an `is_square` property that returns `True` when width equals height.

**Bug hunt.** Explain why this class misbehaves when you create multiple instances:

```python
class Inventory:
    items = []
    def add(self, item):
        self.items.append(item)
```

**Stretch.** Add a `@classmethod` `Rectangle.square(side)` that returns a square rectangle. Verify that subclasses of `Rectangle` get instances of the subclass, not the parent.

**Stretch++.** Add `__lt__` to `Rectangle` so that `sorted(rectangles)` orders by area. Then add `__hash__` (compatible with your `__eq__`) and verify rectangles work as dict keys.

<details><summary>Show solutions</summary>

**Bug hunt.** `items` is a class attribute — a single list shared by all instances. `Inventory().items.append("sword")` mutates the shared list. Fix: move to `__init__`:

```python
class Inventory:
    def __init__(self):
        self.items = []
    def add(self, item):
        self.items.append(item)
```

**Stretch++.**

```python
def __lt__(self, other):
    if not isinstance(other, Rectangle):
        return NotImplemented
    return self.area() < other.area()

def __hash__(self):
    return hash((self.width, self.height))
```

</details>

## In plain terms (newbie lane)
If `Classes` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `self` is:
    (a) a Python keyword  (b) a convention for the current instance parameter  (c) a class attribute  (d) enforced by the interpreter

2. A frozen dataclass gives you:
    (a) mutation prevention + auto `__hash__`  (b) inheritance  (c) async methods  (d) JSON serialization

3. `__repr__` is:
    (a) optional and pointless  (b) developer-facing, invaluable for debugging  (c) user-facing only  (d) always overrides `__str__`

4. `@classmethod`'s first parameter is:
    (a) `self`  (b) `cls`  (c) nothing  (d) `klass`

5. A class attribute is:
    (a) unique to each instance  (b) shared across all instances  (c) always private  (d) always read-only

**Short answer:**

6. When would you prefer a `@classmethod` over a plain `__init__`?
7. Why is defining `__eq__` without `__hash__` dangerous?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b. 6 — When you need an alternative constructor that accepts different input formats (e.g., `Temperature.from_celsius(100)`). The original `__init__` stays clean, and the classmethod documents the conversion. 7 — Python sets `__hash__` to `None` when you define `__eq__`, making instances unhashable. They can't be used in sets or as dict keys, which fails silently when you try.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-classes — mini-project](mini-projects/02-classes-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Classes bundle data and behavior behind a name, giving you a namespace, a constructor, and encapsulated state.
- `@dataclass` eliminates boilerplate for value types — default to `frozen=True` for safety.
- `__repr__` is the single most valuable method you can write — invest three lines, save hours of debugging.
- Use `@classmethod` for alternative constructors; they respect subclasses via `cls(...)`.

## Further reading

- Python docs: [Data classes](https://docs.python.org/3/library/dataclasses.html) (`dataclasses` module).
- Python docs: [Data model](https://docs.python.org/3/reference/datamodel.html) — the full list of dunder methods.
- Next: [Encapsulation](03-encapsulation.md).
