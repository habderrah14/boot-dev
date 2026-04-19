# Mini-project — 07-comparisons

_Companion chapter:_ [`07-comparisons.md`](../07-comparisons.md)

**Goal.** Ship `grade.py` — convert a numeric score (0–100) to a letter grade using chained comparisons, with a clean error path and a test file.

**Acceptance criteria.**

- `grade(score: float) -> str` returns one of `"A"`, `"B"`, `"C"`, `"D"`, `"F"` using chained comparisons.
- Out-of-range input raises `ValueError("score out of [0, 100]: {score}")`.
- `nan` and `inf` raise `ValueError`.
- A `unittest.TestCase` covers boundaries (0, 59, 60, 89, 90, 100), one out-of-range case, and `nan`.
- The grading bands are documented in the function's docstring.

**Hints.** Use `math.isnan` and `math.isinf` for the special-float check. The conventional bands are F < 60 ≤ D < 70 ≤ C < 80 ≤ B < 90 ≤ A.

**Stretch.** Add a `+`/`-` modifier (`A-`, `B+`, etc.) using sub-bands of width 3.33. Be honest about whether your test cases pin down the rounding rule you chose.
