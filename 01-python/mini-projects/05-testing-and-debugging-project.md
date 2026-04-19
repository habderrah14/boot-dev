# Mini-project — 05-testing-and-debugging

_Companion chapter:_ [`05-testing-and-debugging.md`](../05-testing-and-debugging.md)

**Goal.** Ship a `math_utils.py` plus `test_math_utils.py` pair: `average`, `median`, `clamp(x, lo, hi)`. Each function has at least three tests, including empty/edge cases.

**Acceptance criteria.**

- `average([])` returns `0.0`; `median([])` raises `ValueError`; `clamp` raises if `lo > hi`.
- `python3 -m unittest test_math_utils.py` reports green.
- All tests run in under 1 second.
- No test imports anything except `unittest` and the module under test.
- A short README at the top of `math_utils.py` documents the public API in a docstring.

**Hints.** `median` of an even-length list is the average of the two middle elements after sorting. `clamp(5, 0, 10) == 5`; `clamp(-1, 0, 10) == 0`; `clamp(99, 0, 10) == 10`.

**Stretch.** Add a `mode` function with a `MultipleModesError` if the input has no unique most-common value, plus tests for both happy and unhappy paths.
