# Mini-project — 04-recursion

_Companion chapter:_ [`04-recursion.md`](../04-recursion.md)

**Goal.** Implement a recursive-descent parser for simple arithmetic expressions: `1 + 2 * (3 - 4)`. Build an AST and evaluate it.

**Acceptance criteria:**

- [ ] A `parse(tokens)` function that recursively builds an AST from a token list.
- [ ] An `evaluate(ast)` function that recursively evaluates the AST to a number.
- [ ] Correct operator precedence: `*` binds tighter than `+`/`-`.
- [ ] Parentheses work: `(1 + 2) * 3` → `9`.
- [ ] At least five unit tests covering edge cases (single number, nested parens, precedence).

**Hints:**

- Define AST nodes as dataclasses: `Num(value)`, `BinOp(op, left, right)`.
- Write three mutually recursive functions: `parse_expr`, `parse_term`, `parse_factor`.
- Tokenize first: split the input into numbers, operators, and parens.

**Stretch:** Add support for unary minus (`-3`, `-(1 + 2)`) and division with zero-division handling.
