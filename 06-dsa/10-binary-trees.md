# Chapter 10 — Binary Trees

> "Give a node two children and you get logarithmic search, sorted output, and half of computer science."

## Learning objectives

By the end of this chapter you will be able to:

- Build a binary tree and traverse it in pre-order, in-order, post-order, and level-order.
- Implement a binary search tree (BST) with insert, search, and delete.
- Explain why an unbalanced BST degenerates into a linked list and why self-balancing matters.
- Compute tree height, check if a tree is balanced, and reason about BST invariants.

## Prerequisites & recap

- [Recursion](../05-fp/04-recursion.md) — you'll lean on recursive thinking throughout.
- [Linked lists](09-linked-lists.md) — binary trees generalize the idea of node-based structures.

## The simple version

Imagine a game of "20 questions." Each question splits the remaining
possibilities roughly in half. A binary tree works the same way: every node
has at most two children — left and right — and by choosing which branch to
follow, you can eliminate half the data at each step.

A **binary search tree** (BST) adds one rule: everything in the left subtree
is smaller than the current node, and everything in the right subtree is
larger. That single rule is what turns a tree into a search structure — you
compare your target to the current node and know immediately which half to
explore. When the tree is balanced, every operation takes O(log n) time
because the height stays proportional to log n.

## Visual flow

```
 A BST holding [1, 2, 3, 5, 7, 8, 9]:

            5
          /   \
         2     8
        / \   / \
       1   3 7   9

 In-order traversal (left, root, right) yields:
   1 → 2 → 3 → 5 → 7 → 8 → 9   (sorted!)

 Degenerate BST from sorted inserts [1,2,3,4,5]:

   1
    \
     2
      \
       3        ← height = n - 1, every op is O(n)
        \
         4
          \
           5
```

## Concept deep-dive

### Why trees?

Arrays give you O(1) random access but O(n) insert/delete in the middle.
Linked lists give you O(1) splice but O(n) search. Trees split the
difference: with O(log n) search *and* O(log n) insert/delete — *if* the
tree stays balanced. That's why trees are the backbone of databases (B-trees),
file systems, compilers (ASTs), and in-memory sorted containers.

### The node

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None
```

A tree is just a reference to its root node. `None` means "no child" or
"empty tree."

### Traversals — four ways to walk a tree

Every traversal visits every node exactly once — O(n). They differ in *when*
you process the current node relative to its children.

| Traversal | Order | Typical use |
|---|---|---|
| Pre-order | root, left, right | Copying / serializing a tree |
| In-order | left, root, right | BST → sorted output |
| Post-order | left, right, root | Deleting a tree (children first) |
| Level-order (BFS) | top-down, level by level | Shortest path in unweighted tree |

### Binary search tree (BST) invariant

For every node *n*: all values in `n.left` < `n.value` < all values in
`n.right`. This invariant is what makes O(h) search possible — at each node
you know which subtree to explore.

**Insert:** walk down the tree using the BST rule until you find a `None`
slot; place the new node there.

**Search:** same walk; return `True` if you find the value, `False` if you
hit `None`.

**Delete:** three cases:
1. *Leaf* — just remove it.
2. *One child* — replace the node with its child.
3. *Two children* — replace the node's value with its in-order successor
   (smallest value in the right subtree), then delete the successor.

### Height and balance

The *height* of a tree is the length of the longest root-to-leaf path. For a
balanced BST, h ≈ log₂ n. For a degenerate BST (sorted inserts), h = n − 1.
All BST operations are O(h), so keeping h small is critical. Self-balancing
variants (AVL, red-black — Chapter 11) guarantee h = O(log n) by
restructuring the tree after each mutation.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| BST over sorted array | O(log n) insert vs. O(n) shift | If your data is static (no inserts), a sorted array + binary search is simpler and cache-friendlier |
| Recursive traversal | Clean, expressive code | Iterative + explicit stack when tree depth can exceed Python's recursion limit (~1000) |
| In-order successor for delete | Preserves BST property with minimal disruption | In-order predecessor works equally well; some implementations alternate to keep the tree more balanced |
| No balancing (plain BST) | Simpler code | Almost never in production — one sorted input stream and you're at O(n). Use a balanced variant |

## Production-quality code

```python
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class TreeNode:
    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None


class BST:
    """Unbalanced binary search tree with insert, search, delete,
    and all four standard traversals."""

    def __init__(self) -> None:
        self.root: Optional[TreeNode] = None

    # -- Mutation --------------------------------------------------------

    def insert(self, value: int) -> None:
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional[TreeNode], value: int) -> TreeNode:
        if node is None:
            return TreeNode(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node

    def delete(self, value: int) -> None:
        self.root = self._delete(self.root, value)

    def _delete(
        self, node: Optional[TreeNode], value: int
    ) -> Optional[TreeNode]:
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = self._min_node(node.right)
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        return node

    @staticmethod
    def _min_node(node: TreeNode) -> TreeNode:
        while node.left is not None:
            node = node.left
        return node

    # -- Query -----------------------------------------------------------

    def contains(self, value: int) -> bool:
        node = self.root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def height(self) -> int:
        return self._height(self.root)

    def _height(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    # -- Traversals ------------------------------------------------------

    def inorder(self) -> Iterator[int]:
        yield from self._inorder(self.root)

    def _inorder(self, node: Optional[TreeNode]) -> Iterator[int]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield node.value
        yield from self._inorder(node.right)

    def preorder(self) -> Iterator[int]:
        yield from self._preorder(self.root)

    def _preorder(self, node: Optional[TreeNode]) -> Iterator[int]:
        if node is None:
            return
        yield node.value
        yield from self._preorder(node.left)
        yield from self._preorder(node.right)

    def postorder(self) -> Iterator[int]:
        yield from self._postorder(self.root)

    def _postorder(self, node: Optional[TreeNode]) -> Iterator[int]:
        if node is None:
            return
        yield from self._postorder(node.left)
        yield from self._postorder(node.right)
        yield node.value

    def level_order(self) -> Iterator[int]:
        if self.root is None:
            return
        q: deque[TreeNode] = deque([self.root])
        while q:
            node = q.popleft()
            yield node.value
            if node.left is not None:
                q.append(node.left)
            if node.right is not None:
                q.append(node.right)
```

## Security notes

N/A — binary trees are in-process data structures with no direct attack
surface. The only concern is **algorithmic complexity attacks**: if an
adversary controls the insertion order of an unbalanced BST, they can force
O(n) operations by feeding sorted input. Use a self-balancing tree (Chapter
11) or a hash map when processing adversarial input.

## Performance notes

| Operation | Balanced BST | Degenerate BST | Sorted array |
|---|---|---|---|
| Search | O(log n) | O(n) | O(log n) — binary search |
| Insert | O(log n) | O(n) | O(n) — shift |
| Delete | O(log n) | O(n) | O(n) — shift |
| In-order traversal | O(n) | O(n) | O(n) — already sorted |
| Space | O(n) | O(n) | O(n) |

**Recursion depth.** Python's default recursion limit is ~1000. A degenerate
BST of 10,000 nodes will blow the stack. For large trees, use iterative
traversals or increase `sys.setrecursionlimit` (with caution — deep
recursion can segfault).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | In-order traversal produces unsorted output | Violated BST invariant during insert (e.g., used `>=` instead of `>` for right branch) | Strictly enforce `left < node < right`; decide on a duplicate policy |
| 2 | Deleting a node with two children corrupts the tree | Replaced node value but forgot to delete the successor from the right subtree | Always delete the successor *after* copying its value |
| 3 | `RecursionError` on large trees | Tree is degenerate (height ≈ n) or even balanced but n > 1000 | Switch to iterative traversal or use a balanced tree |
| 4 | Inserting duplicates silently disappears | Insert returns the existing node unchanged when `value == node.value` | Decide: reject, count, or consistently place duplicates on one side |

## Practice

**Warm-up.** Build a BST from `[5, 2, 8, 1, 3]`. Print the in-order
traversal and verify it's sorted.

**Standard.** Implement `bst.delete(value)` for all three cases (leaf, one
child, two children). Test by deleting the root of a 7-node tree.

**Bug hunt.** You insert `[1, 2, 3, 4, 5]` into an empty BST and get O(n)
search performance. Explain *exactly* what shape the tree takes and why
`contains(5)` touches every node.

**Stretch.** Compute tree height iteratively (no recursion) using a queue and
level counting.

**Stretch++.** Write a function `is_valid_bst(root)` that checks the BST
invariant for every node. Don't just check immediate children — check that
all nodes in the left subtree are less than the root (pass min/max bounds
downward).

<details><summary>Show solutions</summary>

**Warm-up:**

```python
bst = BST()
for v in [5, 2, 8, 1, 3]:
    bst.insert(v)
print(list(bst.inorder()))  # [1, 2, 3, 5, 8]
```

**Bug hunt:** Inserting `[1, 2, 3, 4, 5]` in order produces a right-leaning
chain: each new value is greater than the current root, so it always goes
right. The resulting tree has height 4 (five nodes in a line), and
`contains(5)` walks all five nodes — exactly like a linked list.

**Stretch++:**

```python
def is_valid_bst(
    node: Optional[TreeNode],
    lo: float = float("-inf"),
    hi: float = float("inf"),
) -> bool:
    if node is None:
        return True
    if not (lo < node.value < hi):
        return False
    return (
        is_valid_bst(node.left, lo, node.value)
        and is_valid_bst(node.right, node.value, hi)
    )
```

</details>

## In plain terms (newbie lane)
If `Binary Trees` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. The BST invariant states:
    (a) both subtrees have equal height
    (b) left subtree values < node < right subtree values
    (c) all nodes are unique
    (d) nodes are stored level-by-level

2. In-order traversal of a BST produces:
    (a) reverse-sorted output  (b) sorted output  (c) post-order output  (d) random order

3. The worst-case time complexity for search in an unbalanced BST is:
    (a) O(log n)  (b) O(n)  (c) O(n²)  (d) O(1)

4. Level-order traversal uses:
    (a) a stack  (b) a queue  (c) a heap  (d) a hash table

5. When deleting a BST node with two children, you replace it with:
    (a) its parent
    (b) its in-order successor (or predecessor)
    (c) the root
    (d) you remove the entire subtree

**Short answer:**

6. Why does in-order traversal of a BST produce sorted output?

7. What is the practical consequence of a degenerate BST, and how do you
   prevent it?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6) The BST invariant guarantees that all left-subtree values come before the node and all right-subtree values come after — in-order follows this exact sequence. 7) A degenerate BST has height n, so every operation is O(n) instead of O(log n). Prevent it by using a self-balancing tree (AVL, red-black).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-binary-trees — mini-project](mini-projects/10-binary-trees-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A binary tree gives each node at most two children; a BST adds an ordering
  invariant that enables O(h) search, insert, and delete.
- Four traversals (pre/in/post/level) each have distinct use cases; in-order
  on a BST yields sorted output.
- An unbalanced BST degenerates to a linked list (h = n − 1). Self-balancing
  variants (Chapter 11) keep h = O(log n).
- In Python, watch recursion depth — switch to iterative approaches for deep
  or adversarially-constructed trees.

## Further reading

- *CLRS* ch. 12 — Binary Search Trees.
- Sedgewick & Wayne, *Algorithms* ch. 3.2 — excellent BST visualizations.
- Next: [Red-black trees](11-red-black-trees.md).
