# Mini-project — 06-computing

_Companion chapter:_ [`06-computing.md`](../06-computing.md)

**Goal.** Build `change.py` — given an amount in US cents, print the breakdown into quarters, dimes, nickels, pennies. Then add a Decimal-based `bill_total.py` that adds a list of `"19.99"`-style strings with tax.

**Acceptance criteria.**

- `make_change(cents: int) -> dict[str, int]` returns `{"quarters": ..., "dimes": ..., "nickels": ..., "pennies": ...}`.
- `make_change(0) == {"quarters": 0, "dimes": 0, "nickels": 0, "pennies": 0}`.
- `make_change(-1)` raises `ValueError`.
- `bill_total(prices: list[str], tax_rate: str = "0.07") -> Decimal` returns the post-tax total.
- A test file proves: greedy is correct for US coin denominations; tax math matches a hand-calculated reference to the cent.

**Hints.** Use `divmod` for the change-making. For the bill, sum first (still as `Decimal`), then apply tax once at the end — applying per-line then summing accumulates rounding error.

**Stretch.** Add Euro coins (`1€`, `0.50€`, `0.20€`, `0.10€`, `0.05€`, `0.02€`, `0.01€`) and prove greedy still works (it does for every standard coin system; this is not always true).
