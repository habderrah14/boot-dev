# Chapter 07 — Stacks

> "A stack is a LIFO pile. Push on top, pop from top. Simple, but surprisingly many problems are stack-shaped."

## Learning objectives

By the end of this chapter you will be able to:

- Implement a stack using a Python list and a linked list.
- Recognize stack-shaped problems: balanced parentheses, undo/redo, DFS, expression evaluation.
- Use Python's `list` or `collections.deque` as a production stack.
- Explain how the call stack works and why `RecursionError` happens.

## Prerequisites & recap

- [Chapter 06 — Data Structures Intro](06-data-structures-intro.md) — you know the complexity cheat sheet.

## The simple version

A stack is a collection where you can only add and remove items from the *top*. Think of a stack of plates in a cafeteria: you put a plate on top (push), and you take a plate from the top (pop). The last plate you put on is the first one you take off — that's LIFO (Last In, First Out).

Why does this matter? Because a huge number of real-world problems follow the LIFO pattern. When you type Ctrl+Z to undo, you're popping the most recent action from a stack. When your Python program calls a function, it pushes a frame onto the call stack. When you check if parentheses are balanced, you push openers and pop when you see closers. Once you learn to spot "the most recent thing matters," you'll reach for a stack instinctively.

## Visual flow

```
  Stack operations (LIFO):

  push(A)    push(B)    push(C)    pop()      peek()
  +-----+    +-----+    +-----+    +-----+    +-----+
  |     |    |     |    |  C  | <--top       |     |
  |     |    |  B  |    |  B  |    |  B  | <--top
  |  A  |    |  A  |    |  A  |    |  A  |    |  A  |
  +-----+    +-----+    +-----+    +-----+    +-----+

  pop() returns C.  peek() returns B (without removing it).
  All operations: O(1).
```
*Figure 7-1: Stack operations. Items enter and leave from the same end — the top.*

## Concept deep-dive

### The API

A stack supports four operations, all O(1):

| Operation | Description |
|---|---|
| `push(x)` | Add x to the top |
| `pop()` | Remove and return the top element |
| `peek()` / `top()` | Return the top element without removing it |
| `is_empty()` / `len()` | Check if the stack has elements |

That's it. The simplicity is the point. A stack deliberately restricts what you can do — no random access, no searching — and in return, every operation is O(1) and the semantics are crystal clear.

### Why LIFO?

LIFO captures the pattern of *nesting*. When things open and close in nested fashion — function calls return in reverse call order, parentheses close in reverse opening order, undo reverses the most recent action — a stack is the natural data structure. Any time the *most recent* item is the one you need to process next, that's a stack.

### Python idiom: just use a list

Python's `list` is a perfectly good stack:

```python
stack = []
stack.append(1)        # push
stack.append(2)        # push
stack[-1]              # peek → 2
stack.pop()            # pop → 2
len(stack) == 0        # is_empty
```

Why does this work? Because `list.append()` and `list.pop()` (without arguments) both operate on the *end* of the list, which is O(1) amortized. The internal array grows from the right, so no elements need to shift.

`collections.deque` also works as a stack and is slightly better in multi-threaded code (its `append` and `pop` are atomic), but for single-threaded use, a plain list is fine.

### When to use a linked-list stack

In Python, almost never — the overhead of per-node object allocation makes it slower than a list for all practical sizes. But understanding the linked-list implementation matters because:

1. It appears in interviews constantly.
2. In lower-level languages (C, Rust), it avoids the occasional O(n) resize that dynamic arrays incur.
3. It illustrates that stacks can be built from *any* collection that supports efficient insert/remove at one end.

### The call stack

Every time you call a function, Python pushes a **stack frame** onto the call stack. The frame holds the function's parameters, local variables, and the return address (where to resume when the function returns). When the function returns, its frame is popped.

This is why recursion works: each recursive call gets its own frame with its own local variables. And it's why deep recursion fails: Python's default call stack limit is ~1000 frames. Exceed it and you get `RecursionError` — the call stack has overflowed.

Understanding this helps you reason about recursive algorithms. Every recursive call costs O(1) stack space, so a recursion of depth d uses O(d) space even if the algorithm doesn't allocate any data structures.

### Classic stack-shaped problems

**Balanced parentheses:** Push openers `([{`, pop when you see a closer `}])`. If the popped opener doesn't match the closer, or the stack isn't empty at the end, the expression is unbalanced. Why a stack? Because the *last* opener must match the *first* closer — that's LIFO.

**Expression evaluation (postfix/RPN):** In postfix notation (`3 4 + 2 *`), operands are pushed; operators pop two operands, compute, and push the result. Why a stack? Because each operator applies to the *most recent* operands.

**Undo/redo:** Each action is pushed onto an undo stack. Ctrl+Z pops and pushes onto a redo stack. Ctrl+Y pops from redo and pushes back to undo. Why a stack? Because you undo the *most recent* action first.

**DFS (Depth-First Search):** DFS explores as deep as possible before backtracking. An explicit stack replaces the call stack, avoiding recursion limits. Why a stack? Because backtracking means returning to the *most recently visited* unexplored node.

## Why these design choices

**Why restrict to LIFO instead of allowing random access?** Because the restriction *is* the feature. A stack communicates intent: "I only need the most recent item." This makes the code self-documenting and prevents accidental misuse. If you find yourself reaching into the middle of a stack, you don't actually have a stack problem — use a different structure.

**`list` vs. `deque` for stacks in Python:** Both work. `list` is marginally faster for pure stack operations because `deque` has slightly more overhead per operation (it's optimized for *both* ends). Use `deque` when you might also need `appendleft`/`popleft`, or when thread safety of individual operations matters.

**When would you pick a different structure?** If you need the *minimum* element at any time alongside push/pop, you need a **min-stack** (which stores the current minimum with each element). If you need the element that arrived *first* (not last), you need a **queue**, not a stack.

## Production-quality code

```python
from dataclasses import dataclass
from typing import Optional, Generic, TypeVar
from collections.abc import Iterator

T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    value: T
    next: Optional["_Node[T]"] = None


class Stack(Generic[T]):
    """LIFO stack backed by a singly-linked list.

    All operations are O(1). Useful as a reference implementation;
    in production Python, prefer list or collections.deque.
    """

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._size: int = 0

    def push(self, value: T) -> None:
        self._head = _Node(value, self._head)
        self._size += 1

    def pop(self) -> T:
        if self._head is None:
            raise IndexError("pop from empty stack")
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        return value

    def peek(self) -> T:
        if self._head is None:
            raise IndexError("peek at empty stack")
        return self._head.value

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __iter__(self) -> Iterator[T]:
        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def __repr__(self) -> str:
        items = list(self)
        return f"Stack(top → {' → '.join(map(str, items))})"


def is_balanced(expression: str) -> bool:
    """Check if brackets in expression are balanced. O(n) time, O(n) space."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in expression:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return len(stack) == 0


def eval_postfix(expression: str) -> float:
    """Evaluate a postfix (RPN) expression. O(n) time, O(n) space.

    Tokens must be space-separated. Supports +, -, *, /.
    """
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }
    stack: list[float] = []
    for token in expression.split():
        if token in ops:
            if len(stack) < 2:
                raise ValueError(f"Not enough operands for '{token}'")
            b, a = stack.pop(), stack.pop()
            if token == "/" and b == 0:
                raise ZeroDivisionError("Division by zero in expression")
            stack.append(ops[token](a, b))
        else:
            try:
                stack.append(float(token))
            except ValueError:
                raise ValueError(f"Invalid token: '{token}'")
    if len(stack) != 1:
        raise ValueError(f"Invalid expression: {len(stack)} values remain on stack")
    return stack[0]
```

## Security notes

- **Stack overflow attacks:** In lower-level languages, buffer overflows on the call stack can overwrite return addresses and redirect execution. Python is immune to this specific attack (managed memory, no raw pointers), but deep recursion can still cause denial of service via `RecursionError` or excessive memory consumption.
- **Expression injection:** If you evaluate user-supplied expressions (like the postfix evaluator above), never use `eval()`. The function-based approach above is safe because it only supports the four arithmetic operators — no arbitrary code execution.

## Performance notes

| Operation | list (as stack) | deque (as stack) | Linked-list stack |
|---|---|---|---|
| push | amortized O(1) | O(1) | O(1) |
| pop | O(1) | O(1) | O(1) |
| peek | O(1) | O(1) | O(1) |
| Memory per element | ~8 bytes (pointer in array) | ~8 bytes | ~56 bytes (object overhead) |

The linked-list stack uses ~7× more memory per element due to Python's per-object overhead (`_Node` dataclass: object header + `value` + `next` pointer). For all practical purposes, use `list.append()`/`list.pop()` in Python.

**Common performance trap:** `list.pop(0)` is O(n), not O(1). It removes from the *front*, requiring all elements to shift left. If you see `pop(0)`, the code probably wants a *queue*, not a stack.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `IndexError: pop from empty list` | Popping without checking if the stack is empty | Always check `len(stack) > 0` or `if stack:` before popping |
| 2 | Using `list.pop(0)` for a stack — code is slow | `pop(0)` removes from the front (O(n)), not the top | Use `pop()` (no argument) to remove from the end (O(1)) |
| 3 | Balanced-parens check says `"({)}"` is valid | Not checking that the popped opener *matches* the closer, only that the stack isn't empty | Compare the popped character against the expected opener for each closer |
| 4 | Using a stack when a queue is needed (e.g., BFS) | Confusing LIFO (stack → DFS) with FIFO (queue → BFS) | If you need to process items in *arrival* order, use a `deque` with `popleft()` |
| 5 | `RecursionError` in deep recursive algorithms | Exceeding Python's call stack limit (~1000 frames) | Convert to an iterative solution with an explicit stack, or increase the limit with `sys.setrecursionlimit()` |

## Practice

**Warm-up.** Reverse a string using a stack. Push each character, then pop all characters into a new string.

<details><summary>Show solution</summary>

```python
def reverse_string(s: str) -> str:
    stack = list(s)
    return "".join(stack.pop() for _ in range(len(stack)))

assert reverse_string("hello") == "olleh"
assert reverse_string("") == ""
assert reverse_string("a") == "a"
```

Note: in production, `s[::-1]` is simpler and faster. This exercise is about understanding stacks.

</details>

**Standard.** Implement a **min-stack**: a stack that supports `push`, `pop`, `peek`, and `get_min`, all in O(1) time.

<details><summary>Show solution</summary>

```python
class MinStack:
    def __init__(self):
        self._stack = []

    def push(self, x):
        current_min = min(x, self._stack[-1][1]) if self._stack else x
        self._stack.append((x, current_min))

    def pop(self):
        if not self._stack:
            raise IndexError("pop from empty stack")
        return self._stack.pop()[0]

    def peek(self):
        if not self._stack:
            raise IndexError("peek at empty stack")
        return self._stack[-1][0]

    def get_min(self):
        if not self._stack:
            raise IndexError("min of empty stack")
        return self._stack[-1][1]

ms = MinStack()
ms.push(5); ms.push(3); ms.push(7)
assert ms.get_min() == 3
ms.pop()  # remove 7
assert ms.get_min() == 3
ms.pop()  # remove 3
assert ms.get_min() == 5
```

The trick: each entry stores `(value, min_so_far)`. When you pop, the previous minimum is automatically restored.

</details>

**Bug hunt.** A developer writes `stack.pop(0)` to "pop from the stack." Why is this wrong in two different ways?

<details><summary>Show solution</summary>

1. **Wrong semantics:** `pop(0)` removes from the *front* (bottom of the stack), not the top. Stacks are LIFO — you should remove from the end with `pop()` (no argument).
2. **Wrong performance:** `pop(0)` is O(n) because all remaining elements must shift left by one position. `pop()` is O(1).

</details>

**Stretch.** Implement the Shunting-Yard algorithm to convert infix expressions (like `"3 + 4 * 2"`) to postfix (like `"3 4 2 * +"`).

<details><summary>Show solution</summary>

```python
def infix_to_postfix(expression: str) -> str:
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}
    output = []
    ops = []

    for token in expression.split():
        if token in precedence:
            while (ops and ops[-1] != "(" and
                   ops[-1] in precedence and
                   precedence[ops[-1]] >= precedence[token]):
                output.append(ops.pop())
            ops.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if ops:
                ops.pop()  # discard the "("
        else:
            output.append(token)

    while ops:
        output.append(ops.pop())

    return " ".join(output)

assert infix_to_postfix("3 + 4 * 2") == "3 4 2 * +"
assert infix_to_postfix("( 3 + 4 ) * 2") == "3 4 + 2 *"
```

The operator stack enforces precedence: higher-precedence operators on the stack are flushed to output before lower-precedence operators are pushed.

</details>

**Stretch++.** Implement DFS on an adjacency-list graph using an explicit stack (no recursion). Find all nodes reachable from a given start node.

<details><summary>Show solution</summary>

```python
def dfs_iterative(graph: dict[str, list[str]], start: str) -> set[str]:
    visited: set[str] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
    return visited

graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": [],
    "E": ["A"],
}
reachable = dfs_iterative(graph, "A")
assert reachable == {"A", "B", "C", "D", "E"}
```

Using an explicit stack avoids `RecursionError` on deep graphs and makes the LIFO nature of DFS visible.

</details>

## In plain terms (newbie lane)
If `Stacks` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A stack is:
    (a) FIFO  (b) LIFO  (c) sorted  (d) random access

2. `list.append()` / `list.pop()` on the end:
    (a) O(1) / O(1)  (b) O(n) / O(n)  (c) amortized O(1) / O(1)  (d) O(log n) / O(log n)

3. The call stack holds:
    (a) function frames (parameters, locals, return address)  (b) only return values  (c) global state  (d) heap-allocated data

4. Balanced-parentheses checking uses a stack because:
    (a) random access is needed  (b) the last-opened bracket must match the first-closed  (c) strings require stacks  (d) it's tradition

5. `collections.deque` as a stack is:
    (a) wrong tool  (b) fine — O(1) push/pop on either end  (c) O(log n) per operation  (d) deprecated

**Short answer:**

6. Trace the balanced-parens algorithm on `"((()))"` step by step.
7. Name one non-parentheses problem that is stack-shaped.

*Answers: 1-b, 2-c, 3-a, 4-b, 5-b, 6-Push ( → stack: [(]; push ( → [((]; push ( → [(((]; pop for ) → [((]; pop for ) → [(]; pop for ) → []; stack empty → balanced, 7-Undo/redo, DFS traversal, postfix expression evaluation, browser back button, or function call management.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-stacks — mini-project](mini-projects/07-stacks-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A stack is a LIFO collection: push and pop from the same end, all in O(1). The restriction is the feature — it communicates "most recent first."
- In Python, use `list.append()`/`list.pop()` as your default stack. `collections.deque` works too and is thread-safer.
- Stack-shaped problems are everywhere: balanced brackets, undo/redo, DFS, expression evaluation, and the call stack itself.
- Watch for `pop(0)` — it's O(n) and means you probably want a queue, not a stack.

## Further reading

- Shunting-Yard algorithm (Wikipedia) — converting infix to postfix with operator precedence.
- Python `sys.getrecursionlimit()` / `sys.setrecursionlimit()` — managing the call stack.
- *Introduction to Algorithms* (CLRS), section 10.1 — stacks and queues.
- Next: [Queues](08-queues.md).
