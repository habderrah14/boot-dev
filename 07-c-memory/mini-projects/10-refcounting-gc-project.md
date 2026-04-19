# Mini-project — 10-refcounting-gc

_Companion chapter:_ [`10-refcounting-gc.md`](../10-refcounting-gc.md)

**Goal.** Implement refcounted `RCNode` and `RCString` types. Build a linked list where each node owns its `next` pointer and a refcounted string payload.

**Acceptance criteria:**

- `rcstring_new(const char *)`, `rcstring_retain`, `rcstring_release`.
- `rcnode_new(RCString *payload)`, `rcnode_retain`, `rcnode_release`.
- Node destructor releases both `payload` and `next`.
- Demo: build a 5-node list, release the head, and verify zero leaks under Valgrind.

**Hints:**

- `rcstring` should `malloc` a copy of the string and free it in the destructor.
- Use `calloc` for zero-initialization so `next = NULL` is automatic.

**Stretch:** Add instrumented `retain`/`release` that print to stderr (`[retain] RCString@%p rc=%d → %d`). Use this to trace the lifecycle during your demo.
