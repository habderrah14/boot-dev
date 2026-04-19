# Mini-project — 01-introduction

_Companion chapter:_ [`01-introduction.md`](../01-introduction.md)

**Goal.** Ship `introduce.py` — a four-line introduction about yourself that demonstrates variables, string formatting, and the `__main__` guard.

**Acceptance criteria.**

- File is named `introduce.py`.
- Running `python3 introduce.py` produces exactly four lines.
- At least two variables hold pieces of the introduction (e.g., `city`, `goal`).
- An `if __name__ == "__main__":` guard wraps the printing.
- A docstring at the top explains what the file does.

**Hints.** Use f-strings: `print(f"My name is {name} and I live in {city}.")`. Don't worry about taking input from the terminal yet.

**Stretch.** Add a `print_intro(name, city, food, goal)` function and call it from `main()`. Bonus: try `python3 -c "from introduce import print_intro; print_intro('A','B','C','D')"` and confirm the four lines still print.
