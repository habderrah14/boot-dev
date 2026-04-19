# Mini-project — 07-currying

_Companion chapter:_ [`07-currying.md`](../07-currying.md)

**Goal.** Build a small validation library using curried predicates. Define predicates like `at_least(n)(x)`, `at_most(n)(x)`, `matches(pattern)(s)`, and `has_length(lo, hi)(s)`. Compose them into a `validate(rules, data)` function.

**Acceptance criteria:**

- [ ] At least four curried predicates.
- [ ] A `validate(rules, data)` function that applies all rules and returns `(True, [])` or `(False, [error_messages])`.
- [ ] Rules are composable: `rules = [at_least(0), at_most(120)]` for age validation.
- [ ] At least five unit tests covering valid data, invalid data, multiple rule failures, and edge cases.

**Hints:**

- Each predicate, when partially applied, should return a function that takes the value and returns `True`/`False` (or a tuple with an error message).
- `validate` iterates the rules, calls each on the data, collects failures.

**Stretch:** Add an `all_of(*predicates)` combinator that composes multiple predicates into one, and an `any_of(*predicates)` that passes if any predicate passes.
