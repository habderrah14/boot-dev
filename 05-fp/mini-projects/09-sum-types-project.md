# Mini-project — 09-sum-types

_Companion chapter:_ [`09-sum-types.md`](../09-sum-types.md)

**Goal.** Implement a mini expression language with an AST, evaluator, and pretty-printer. Support: numbers, addition, multiplication, variables, and `let` bindings.

**Acceptance criteria:**

- [ ] AST nodes: `Num(value)`, `Add(left, right)`, `Mul(left, right)`, `Var(name)`, `Let(name, value_expr, body_expr)`.
- [ ] `evaluate(expr, env: dict)` recursively evaluates the AST, looking up variables in `env`.
- [ ] `pretty(expr)` returns a human-readable string representation.
- [ ] `let x = 2 in x + 3` evaluates to `5`.
- [ ] At least six unit tests: one per node type plus an integration test for nested expressions.
- [ ] Exhaustive `match` with `assert_never` on every pattern match function.

**Hints:**

- `Let(name, value_expr, body_expr)` evaluates `value_expr`, binds it to `name` in a new environment, then evaluates `body_expr`.
- Use `{**env, name: evaluated_value}` to create a new environment without mutating the original.

**Stretch:** Add `Sub` and `Div` nodes. Handle division by zero by returning `Failure("division by zero")` instead of raising.
