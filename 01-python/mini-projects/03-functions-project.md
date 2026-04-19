# Mini-project — 03-functions

_Companion chapter:_ [`03-functions.md`](../03-functions.md)

**Goal.** Ship a tiny `temp_convert.py` module that converts between Celsius and Fahrenheit and prints a calibration table when run directly.

**Acceptance criteria.**

- Two functions `c_to_f(c: float) -> float` and `f_to_c(f: float) -> float`, each with a docstring and a `ValueError` for inputs below absolute zero.
- A `main()` function that prints a table from 0 °C to 100 °C in steps of 10 °C, two columns, two-decimal alignment.
- Only `main()` prints — `c_to_f` and `f_to_c` return their values.
- `python -c "from temp_convert import c_to_f; print(c_to_f(100))"` works without printing the table.
- A short docstring at the top of the file explains what the module is for.

**Hints.** Use `if __name__ == "__main__": main()` so `main()` runs when you execute the file but not when another module imports it. Use an f-string like `f"{c:>5.1f}  {c_to_f(c):>7.2f}"` for aligned columns.

**Stretch.** Add a `--reverse` CLI flag (using `argparse`) that prints a Fahrenheit→Celsius table from 32 °F to 212 °F in steps of 18 °F.
