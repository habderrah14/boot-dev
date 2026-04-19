# Mini-project — 14-graphs

_Companion chapter:_ [`14-graphs.md`](../14-graphs.md)

**Goal.** Build a CLI tool that reads a Python project's import statements,
constructs a module dependency graph, and detects circular imports.

**Acceptance criteria:**

- `python cycles.py path/to/project` scans all `.py` files.
- Parses `import` and `from ... import ...` statements (relative and
  absolute).
- Builds a directed graph of module dependencies.
- Reports all modules and edges found.
- Detects and prints any cycles.
- Exit code 0 = no cycles, exit code 1 = cycles found.

**Hints:**

- Use `ast.parse()` to reliably extract imports from Python files.
- Use the DFS three-color cycle detection from the production code.
- Start small: test on a project with 5–10 files before running on a large
  codebase.

**Stretch:** Visualize the dependency graph by generating DOT format output
that can be rendered with Graphviz (`dot -Tpng deps.dot -o deps.png`).
