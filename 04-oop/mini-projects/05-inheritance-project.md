# Mini-project — 05-inheritance

_Companion chapter:_ [`05-inheritance.md`](../05-inheritance.md)

**Goal.** Implement a shape hierarchy with both inheritance and composition, then compare.

**Acceptance criteria:**

- `Shape(ABC)` with `area()` and `perimeter()` abstract methods.
- `Circle`, `Rectangle`, `Triangle` subclasses with validation in `__post_init__` or `__init__`.
- A `ColoredShape` that adds a `color` attribute via *composition* (holds a `Shape`, delegates `area` and `perimeter`).
- Tests for each shape (including edge cases: zero radius, degenerate triangles).
- Tests for `ColoredShape` proving it works with any `Shape` implementation.

**Hints:** Use `@dataclass(frozen=True)` for the shapes. Use Heron's formula for triangle area.

**Stretch:** Add a `ScaledShape(shape, factor)` via composition that scales area by `factor²` and perimeter by `factor`. Stack it: `ScaledShape(ColoredShape(Circle(1), "red"), 3)`.
