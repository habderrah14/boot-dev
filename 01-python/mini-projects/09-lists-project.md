# Mini-project — 09-lists

_Companion chapter:_ [`09-lists.md`](../09-lists.md)

**Goal.** Build `gradebook.py` storing a `list[tuple[str, float]]` and supporting: `add`, `average`, `median`, `top_n(n)`, `sorted_by_name`, `sorted_by_score`. Include a test file covering empty inputs and ties.

**Acceptance criteria.**

- `Gradebook` is a class (preview of [Module 04](../04-oop/02-classes.md)) wrapping a list.
- `average` of an empty gradebook returns `0.0`.
- `median` of empty raises `ValueError`.
- `top_n(0)` returns `[]`; `top_n(n)` for `n > len(grades)` returns all entries sorted by score descending.
- Six unit tests, all green in under a second.
- The list is internal — exposed only via methods, never returned by reference.

**Hints.** Use `sorted(self.entries, key=lambda e: e[1], reverse=True)`. Return *copies* from getter methods (`return list(self.entries)`) so external code can't mutate the internal list.

**Stretch.** Add a CSV import (`from_csv(path) -> Gradebook`) using only the standard library's `csv` module.
