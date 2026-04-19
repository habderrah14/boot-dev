# Mini-project — Search Benchmark

## Goal

Build a benchmark script that compares linear search and binary search across multiple input sizes.

## Deliverable

A Python script that reports average search time for both algorithms at increasing scales.

## Required behavior

1. Implement linear search and binary search from scratch.
2. Benchmark sizes from 100 to 1,000,000.
3. Run 100 random target lookups per size.
4. Print a readable comparison table.
5. Keep the binary-search input sorted before timing begins.

## Acceptance criteria

- No use of `bisect` or other built-in search helpers.
- Benchmark excludes sorting time for the binary search input.
- Output clearly shows the speed ratio for each size.
- Script runs from the command line with no manual intervention.

## Hints

- Use `time.perf_counter()`.
- `list(range(n))` gives sorted data instantly.
- Include some misses so you exercise worst-case behavior.

## Stretch goals

1. Add a log-log plot if `matplotlib` is available.
2. Output an ASCII chart fallback.
3. Save results as CSV for later analysis.
