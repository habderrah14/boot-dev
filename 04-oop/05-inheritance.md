# Chapter 05 — Inheritance

> "Inheritance is a hammer. Most problems are not nails."

## Learning objectives

By the end of this chapter you will be able to:

- Create a subclass and override methods.
- Call the base class correctly with `super()` and explain what it actually does.
- Read and interpret Python's method resolution order (MRO) for multiple inheritance.
- Apply the Liskov Substitution Principle to judge whether an inheritance relationship is valid.
- Know when to prefer composition over inheritance — and articulate why.
- Use mixins safely for cross-cutting concerns.

## Prerequisites & recap

- [Classes](02-classes.md) — defining classes, `__init__`, `self`.
- [Abstraction](04-abstraction.md) — ABCs, Protocols, contracts.

## The simple version

Inheritance lets you create a new class that starts with everything an existing class has and then adds or changes behavior. `Dog(Animal)` means "a Dog is an Animal with some extra behavior." The subclass inherits all methods and attributes from the parent, and can override any of them.

The catch: inheritance creates tight coupling. Every change to the parent ripples into every child. If the "is-a" relationship isn't genuinely true — if a `Square` can't be used everywhere a `Rectangle` is expected — inheritance will fight you. In those cases, *composition* (holding a reference to another object instead of inheriting from it) is almost always the better tool.

## Visual flow

```
  ┌──────────────┐
  │    Animal     │
  │  + speak()    │
  └──────┬───────┘
         │ inherits
    ┌────┴─────┐
    │          │
  ┌─▼──┐   ┌──▼──┐
  │ Dog │   │ Cat │
  │     │   │     │
  └──┬──┘   └─────┘
     │ inherits
  ┌──▼────┐
  │ Loud  │
  │ Dog   │
  └───────┘

  MRO for LoudDog: LoudDog → Dog → Animal → object

  ┌──────────────────────────────────────────────────┐
  │        Composition alternative                    │
  │                                                   │
  │  ThrottledClient                                  │
  │    ._client ──────► HttpClient  (has-a, not is-a) │
  │    ._rate                                         │
  └──────────────────────────────────────────────────┘
```
*Figure 1 — Inheritance (left) vs. composition (right). Use "is-a" for the first, "has-a" for the second.*

## Concept deep-dive

### Single inheritance

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says woof"
```

`Dog` *is-a* `Animal`. `isinstance(Dog("Rex"), Animal)` returns `True`. The subclass inherits `__init__` from `Animal`, so `Dog("Rex")` sets `self.name` automatically.

Why single inheritance works well: when the relationship is genuinely "is-a" and the parent is stable, inheritance gives you code reuse with zero boilerplate. The child gets all parent methods for free.

### `super()` — what it actually does

`super()` doesn't call "the parent." It calls *the next class in the MRO*:

```python
class LoudDog(Dog):
    def speak(self) -> str:
        return super().speak().upper() + "!"
```

Use `super().__init__(...)` in constructors that extend the parent:

```python
class ServiceDog(Dog):
    def __init__(self, name: str, task: str):
        super().__init__(name)
        self.task = task
```

Why `super()` instead of `Dog.__init__(self, name)`? Because `super()` respects the MRO, which matters in multiple inheritance. Hardcoding the parent class breaks cooperative inheritance and creates subtle bugs when the hierarchy changes.

### Method resolution order (MRO)

For multiple inheritance, Python uses **C3 linearization** to determine the order in which classes are searched for a method:

```python
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...

D.__mro__
# (D, B, C, A, object)
```

The MRO guarantees: (1) a class always comes before its parents, (2) the left-to-right order of bases is preserved, and (3) no class appears twice. `super()` walks this chain, calling the next class in line — not necessarily the "parent" you might expect.

Why C3? Because naive depth-first search can call a method on `A` before `C`, skipping `C`'s override entirely. C3 linearization prevents this by enforcing a consistent, predictable order.

### Mixins

A mixin is a small class designed to be combined with others to add a specific capability:

```python
from datetime import datetime, timezone


class TimestampMixin:
    def touch(self):
        self.updated_at = datetime.now(timezone.utc)


class User(TimestampMixin, BaseModel):
    ...
```

Mixins work because of the MRO — `TimestampMixin.touch()` is found when `User` doesn't define its own `touch()`. Rules for safe mixins:

1. A mixin should add behavior, not state (or minimal state).
2. A mixin must use `super()` in `__init__` so the MRO chain continues.
3. Name mixins with a `Mixin` suffix so the intent is clear.

### Liskov Substitution Principle (LSP)

A subclass should be usable *everywhere* the parent is expected, without surprises. If code works with a `Rectangle`, it should work with any subclass of `Rectangle`.

The classic violation: `Square(Rectangle)`. If a caller does `rect.width = 5` and expects `rect.height` to remain unchanged, a `Square` breaks that expectation because width and height must be equal. The "is-a" relationship is mathematically true but *behaviorally* false.

How to check: can you substitute the subclass in every test written for the parent, and have all tests pass? If not, the inheritance relationship is wrong.

### Prefer composition

```python
# Inheritance — often wrong for this case
class ThrottledClient(HttpClient):
    ...

# Composition — usually right
class ThrottledClient:
    def __init__(self, client: HttpClient, rate_per_second: int):
        self._client = client
        self._rate = rate_per_second

    def get(self, url: str) -> Response:
        self._wait_for_slot()
        return self._client.get(url)
```

Why composition wins here: you can swap the underlying `HttpClient` at runtime (real client in production, fake in tests). You avoid inheriting methods you don't want. You don't need to worry about the parent's `__init__` changing. And you can compose multiple behaviors (throttling + retrying + caching) without diamond inheritance problems.

**The rule of thumb:** Use inheritance when "is-a" genuinely holds and the parent is under your control. Use composition for everything else — especially when you're tempted to inherit just to reuse a few methods.

## Why these design choices

**Why does Python allow multiple inheritance?** Because mixins and cooperative inheritance solve real problems (logging, timestamping, serialization) that would require either code duplication or decorator gymnastics otherwise. The MRO (C3 linearization) makes it predictable.

**Why prefer composition?** Inheritance couples the child to the parent's implementation, not just its interface. If the parent adds a method, every child inherits it — even if it doesn't make sense. Composition couples only to the interface, giving you more flexibility and less fragility.

**When inheritance is clearly right:** Framework extension points (`unittest.TestCase`, Django's `View`), genuine taxonomies where "is-a" holds at every level, and ABCs where you want to enforce a contract with shared default behavior.

**When you'd pick differently:** In small scripts or prototypes, inheritance is faster to write than composition. The coupling cost only hurts when the code lives long enough to evolve.

## Production-quality code

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


class Shape(ABC):
    """Base class for geometric shapes with area and perimeter."""

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.2f})"


@dataclass(frozen=True)
class Circle(Shape):
    radius: float

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError(f"radius must be non-negative, got {self.radius}")

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


@dataclass(frozen=True)
class Rectangle(Shape):
    width: float
    height: float

    def __post_init__(self):
        if self.width < 0 or self.height < 0:
            raise ValueError("dimensions must be non-negative")

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


@dataclass(frozen=True)
class Triangle(Shape):
    a: float
    b: float
    c: float

    def __post_init__(self):
        sides = sorted([self.a, self.b, self.c])
        if sides[0] <= 0:
            raise ValueError("sides must be positive")
        if sides[0] + sides[1] <= sides[2]:
            raise ValueError("triangle inequality violated")

    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


# ── Composition instead of inheritance for cross-cutting behavior ──

@dataclass
class ColoredShape:
    """Adds a color to any shape via composition, not inheritance."""
    shape: Shape
    color: str

    def area(self) -> float:
        return self.shape.area()

    def perimeter(self) -> float:
        return self.shape.perimeter()

    def __repr__(self) -> str:
        return f"ColoredShape({self.shape!r}, color={self.color!r})"


def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)
```

## Security notes

N/A — inheritance itself is not a security boundary. However, be aware that overriding a method in a subclass can silently change security-critical behavior. If a parent class's `authenticate()` method is correct, a subclass that overrides it without calling `super()` might skip authentication entirely. In security-sensitive code, consider making critical methods `final` (by convention or with a `__init_subclass__` check) or using composition so the security logic can't be accidentally overridden.

## Performance notes

- **Method lookup** walks the MRO on every call. For deep hierarchies (5+ levels), this adds a few microseconds per call — negligible for backend code, but measurable in tight numerical loops.
- **`super()` overhead** is minimal. It creates a lightweight proxy object. Don't avoid `super()` for performance reasons.
- **Composition adds one level of indirection** (attribute lookup + delegation). Again, negligible in Python, where the interpreter overhead dwarfs it.
- **`__slots__`** interacts with inheritance: every class in the hierarchy must declare `__slots__`, or you lose the memory savings. This is a common gotcha with deep hierarchies.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Parent's `__init__` logic doesn't run; attributes are missing | Subclass overrides `__init__` without calling `super().__init__(...)` | Always call `super().__init__(...)` when extending a parent constructor. |
| 2 | Deep hierarchy (5+ levels) where changes to the root break everything | Inheriting for code reuse instead of genuine "is-a" | Flatten the hierarchy. Use composition or mixins for shared behavior. |
| 3 | `Square(Rectangle)` passes its own tests but breaks tests that expect `Rectangle` behavior | Liskov Substitution Principle violation — subclass changes the contract | Remove the inheritance. Model `Square` as a factory: `Rectangle.square(side)`. |
| 4 | Multiple inheritance causes methods to be called in unexpected order | Not understanding the MRO, or not using `super()` cooperatively | Print `ClassName.__mro__` to understand the order. Use `super()` in every method. |
| 5 | Inheriting from a class just to reuse 2 methods, but dragging in 20 others | "Inherit for reuse" instead of "inherit for substitutability" | Use composition: hold a reference to the useful object, delegate the 2 methods. |

## Practice

**Warm-up.** Create `Cat(Animal)` with a `speak()` method that returns `"{name} says meow"`.

**Standard.** Write a subclass that extends a parent constructor with `super().__init__(...)`. Add a new attribute and verify that both parent and child attributes are set correctly.

**Bug hunt.** Why does `class Square(Rectangle)` violate Liskov? Write a test for `Rectangle` that would pass for `Rectangle(5, 3)` but fail for `Square(5)`.

**Stretch.** Implement a `TimestampMixin` that adds a `touch()` method setting `self.updated_at`. Apply it to two unrelated classes and verify both get the behavior.

**Stretch++.** Create a class with multiple inheritance, print its `__mro__`, and explain the order. Then write a test that demonstrates `super()` walking the MRO instead of just calling the "parent."

<details><summary>Show solutions</summary>

**Bug hunt.** A test for `Rectangle`:

```python
def test_independent_dimensions(rect):
    rect.width = 5
    rect.height = 3
    assert rect.width == 5
    assert rect.height == 3   # fails for Square — setting width changes height
```

`Square` can't honor this contract because its width and height must be equal.

**Stretch++.**

```python
class A:
    def greet(self):
        return "A"

class B(A):
    def greet(self):
        return "B->" + super().greet()

class C(A):
    def greet(self):
        return "C->" + super().greet()

class D(B, C):
    def greet(self):
        return "D->" + super().greet()

print(D.__mro__)
# (D, B, C, A, object)

print(D().greet())
# "D->B->C->A"  — super() walks the MRO, not just "parent"
```

</details>

## In plain terms (newbie lane)
If `Inheritance` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `super()` invokes:
    (a) a random ancestor  (b) the next class in the MRO  (c) `object` directly  (d) the statically declared parent

2. Python's MRO is computed by:
    (a) depth-first search  (b) breadth-first search  (c) C3 linearization  (d) alphabetical order

3. The Liskov Substitution Principle says:
    (a) subclasses must override every method  (b) subclasses should be substitutable for their base without breaking expectations  (c) always compose over inherit  (d) mixins are always wrong

4. Composition vs. inheritance:
    (a) they are identical  (b) composition is usually more flexible and less coupled  (c) inheritance is always faster  (d) Python forbids composition

5. A safe mixin should:
    (a) use `@mixin` decorator  (b) add behavior without hijacking state, and use `super()` cooperatively  (c) always define `__init__`  (d) require `__slots__`

**Short answer:**

6. Why is deep inheritance fragile?
7. Give one case where inheritance is clearly the right choice over composition.

*Answers: 1-b, 2-c, 3-b, 4-b, 5-b. 6 — Every change to a parent class ripples into all descendants. A bug fix in the root can break a leaf five levels down, and understanding behavior requires reading every class in the chain. 7 — Framework extension points like `unittest.TestCase` or Django's `View`, where the framework expects subclassing and provides default behavior you genuinely want to inherit and selectively override.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-inheritance — mini-project](mini-projects/05-inheritance-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Inheritance models "is-a" relationships: use it when a subclass can genuinely substitute for its parent everywhere.
- `super()` walks the MRO, not just the direct parent — always use it to keep cooperative inheritance working.
- Prefer composition ("has-a") when you need flexibility, testability, or when the relationship is really "uses-a."
- Mixins are safe when they add behavior without hijacking state and respect `super()`.

## Further reading

- Raymond Hettinger, [*Super Considered Super!*](https://rhettinger.wordpress.com/2011/05/26/super-considered-super/) — the definitive explanation of `super()` and MRO.
- *Effective Python*, Brett Slatkin, Item 40: "Initialize Parent Classes with `super`."
- Next: [Polymorphism](06-polymorphism.md).
