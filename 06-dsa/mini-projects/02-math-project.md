# Mini-project — 02-math

_Companion chapter:_ [`02-math.md`](../02-math.md)

**Goal.** Create `hash_demo.py` that hashes a list of strings into buckets and measures the load distribution.

**Acceptance criteria:**

- Read a list of at least 1000 words (generate them or use `/usr/share/dict/words` if available).
- Hash each word into buckets using `hash(word) % num_buckets`.
- Test with bucket counts of 7, 16, 31, 64, 127, 256.
- For each bucket count, report: min bucket size, max bucket size, standard deviation, and a simple visual histogram.
- Observe whether prime-number bucket counts produce more even distribution.

**Hints:**

- Use `collections.Counter` to count items per bucket.
- Standard deviation: `statistics.stdev(bucket_counts)`.
- A "good" hash distribution has low standard deviation relative to the mean.

**Stretch:** Compare Python's built-in `hash()` against a simple sum-of-ord hash. Which distributes more evenly?
