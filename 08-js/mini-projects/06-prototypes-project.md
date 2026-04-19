# Mini-project — 06-prototypes

_Companion chapter:_ [`06-prototypes.md`](../06-prototypes.md)

**Goal.** Build an old-school (ES5-style) inheritance system and a parallel `class`-based version. Verify they produce identical prototype chains.

**Acceptance criteria:**

- Implement `Rectangle` and `Square extends Rectangle` using the ES5 `function` + `inherits` pattern.
- Implement the same hierarchy with `class` / `extends`.
- Write a `walkChain(obj)` function that returns an array of prototype names.
- Tests verify `walkChain(square)` produces the same sequence for both implementations.
- Tests verify `instanceof` works correctly for both.

**Hints:**

- In the ES5 version: `Child.prototype = Object.create(Parent.prototype)` and `Child.prototype.constructor = Child`.
- Use `constructor.name` to label each prototype level.

**Stretch:** Add a `mixin(target, ...sources)` function that copies methods from multiple source objects onto a target prototype. Test with a `Serializable` mixin that adds `toJSON`.
