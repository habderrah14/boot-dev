# Mini-project — 10-binary-trees

_Companion chapter:_ [`10-binary-trees.md`](../10-binary-trees.md)

**Goal.** Build a complete BST with insert, contains, delete, and all four
traversals. Stress-test it with 10,000 random integers and 10,000 sorted
integers, printing the height after each batch.

**Acceptance criteria:**

- `insert`, `contains`, and `delete` all work correctly (verified by tests).
- In-order traversal always produces sorted output.
- Printed heights demonstrate the difference between random (≈ log n) and
  sorted (= n − 1) insertion order.
- Include at least 5 assertions that serve as automated tests.

**Hints:**

- Use `random.sample(range(100_000), 10_000)` for random input.
- After sorted inserts, try calling `contains` on the last element and time
  it — you'll feel the O(n) pain.

**Stretch:** Implement a `rebalance()` method that rebuilds the tree from its
sorted in-order output into a perfectly balanced BST (hint: pick the middle
element as root, recurse on each half).
