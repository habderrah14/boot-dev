# Mini-project — 02-first-class-functions

_Companion chapter:_ [`02-first-class-functions.md`](../02-first-class-functions.md)

**Goal.** Implement a `pipeline(*stages)` function where each stage is a generator function. Demonstrate it on a simulated million-line log file, extracting error lines, parsing timestamps, and counting errors per hour.

**Acceptance criteria:**

- [ ] `pipeline` accepts any number of generator-based stages and composes them lazily.
- [ ] Processing a 1-million-line simulated log uses constant memory (verify with a generator source, not a list).
- [ ] At least three stages: filter errors, parse timestamps, group by hour.
- [ ] Final output is a dict mapping hour (int) → error count.
- [ ] Unit tests for each individual stage function.

**Hints:**

- Generate test data with a generator: `(f"2025-01-15 {h:02d}:{m:02d} {'ERROR' if random.random() < 0.1 else 'INFO'} msg" for h in range(24) for m in range(60) for _ in range(694))`.
- `itertools.groupby` can help with grouping, but you'll need the data sorted by hour first.

**Stretch:** Add a `tee` stage that writes matching lines to a debug file without breaking the pipeline.
