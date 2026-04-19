# Mini-project — 07-stacks

_Companion chapter:_ [`07-stacks.md`](../07-stacks.md)

**Goal.** Build a tiny RPN (Reverse Polish Notation) calculator CLI.

**Acceptance criteria:**

- Reads a single line of space-separated tokens from stdin (or a hardcoded string).
- Supports `+`, `-`, `*`, `/` operators and integer/float operands.
- Uses a stack to evaluate the expression.
- Prints the final result, or a clear error message if the expression is invalid.
- Handles edge cases: division by zero, too few operands, too many operands (leftover values on stack).

**Hints:**

- `"3 4 + 2 *"` → push 3, push 4, see +, pop 4 and 3, push 7, push 2, see *, pop 2 and 7, push 14 → result: 14.
- For the CLI, `input("rpn> ")` gives you a prompt.

**Stretch:** Add support for `^` (exponentiation), `%` (modulo), and unary negation (`neg`). Also support multi-line input where the user can build up a computation across lines (the stack persists between lines until explicitly cleared).
