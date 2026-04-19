# Mini-project — 02-variables

_Companion chapter:_ [`02-variables.md`](../02-variables.md)

**Goal.** Ship `tip.py` — compute and print how much each diner owes after tax and tip.

**Acceptance criteria.**

- Constants for `TAX_RATE` and `TIP_RATE` at the top in `SCREAMING_SNAKE_CASE`.
- A function `split(subtotal: float, num_people: int) -> dict` returning `{"per_person": ..., "total": ...}`.
- The function raises `ValueError` for `num_people <= 0` or `subtotal < 0`.
- A `main()` prints `per_person` rounded to two decimals — no magic numbers in the print statements.
- The whole script runs as `python3 tip.py` and is silent when imported.

**Hints.** Use the `if __name__ == "__main__":` guard. Use `round(x, 2)` for display rounding, not `f"{x:.2}"` — the latter rounds to two *significant* figures, which is different.

**Stretch.** Add a CLI: `python3 tip.py 84.50 4` (subtotal, num_people). Use `sys.argv` for now; `argparse` comes later.
