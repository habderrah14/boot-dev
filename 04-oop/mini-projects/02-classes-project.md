# Mini-project — 02-classes

_Companion chapter:_ [`02-classes.md`](../02-classes.md)

**Goal.** Build a `Vector2D` class that supports vector arithmetic and integrates with Python's data model.

**Acceptance criteria:**

- `Vector2D(x, y)` with `__repr__` that round-trips.
- `__add__`, `__sub__` for vector addition/subtraction.
- `__mul__` for scalar multiplication (`v * 3`), plus `__rmul__` so `3 * v` works too.
- `__eq__` and `__hash__` so vectors work as dict keys.
- A `@classmethod` `Vector2D.zero()` that returns the zero vector.
- A `magnitude` property.
- At least 10 tests covering normal cases, edge cases, and error cases.

**Hints:** Use `@dataclass(frozen=True)` to get `__eq__` and `__hash__` for free. Return `NotImplemented` (not raise) from dunder methods when the other operand is an unsupported type.

**Stretch:** Add `__matmul__` (`@` operator) for dot product: `v1 @ v2`.
