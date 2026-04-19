# Mini-project — 06-polymorphism

_Companion chapter:_ [`06-polymorphism.md`](../06-polymorphism.md)

**Goal.** Build a small expression tree that uses polymorphism for evaluation and formatting.

**Acceptance criteria:**

- Three node types: `Num(value)`, `Add(left, right)`, `Mul(left, right)`.
- Each node has an `evaluate() -> float` method (subtype polymorphism).
- A `pretty(node) -> str` free function using `singledispatch` that formats the expression.
  - `Num(5)` → `"5"`
  - `Add(Num(1), Num(2))` → `"(1 + 2)"`
  - `Mul(Num(3), Add(Num(1), Num(2)))` → `"(3 * (1 + 2))"`
- Both approaches (method-based `evaluate()` and dispatch-based `pretty()`) tested.
- Compare: which approach is easier to extend with a new node type (`Sub`, `Div`)? Which is easier to extend with a new operation (`to_postfix()`)?

**Hints:** The method-based approach (adding `evaluate()` to each class) is easier to extend with new types. The dispatch-based approach (adding `singledispatch` functions) is easier to extend with new operations. This is a fundamental trade-off in OOP known as the "expression problem."

**Stretch:** Add `__add__` and `__mul__` to `Num` so you can write `Num(1) + Num(2) * Num(3)` and get the expression tree built automatically.
