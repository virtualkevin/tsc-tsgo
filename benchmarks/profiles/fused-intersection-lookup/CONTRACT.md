# Completed intersection lookup contract

Candidate on retained production at 399a553. This changes execution of existing
lookups, not semantic storage, cache lifetime, resolution order, or symbol identity.
No speedup or whole-compiler proof is established.

`getTypeOfPropertyOfType` first asks a pure helper for an eligible current cached
symbol. On success it calls the original `getTypeOfSymbol`. Otherwise its entire
original body runs unchanged. No result survives in a new cache or descriptor.

The source-linked equivalence argument is:

1. Exact TypeFlagsIntersection excludes instantiable flags and other type branches.
   Mapped dispatch is explicitly excluded even if object flags are unusual.
2. IsNeverIntersectionComputed is set and IsNeverIntersection is clear. Therefore
   the first `getReducedType` returns the input without queries or flag writes.
3. The existing `resolvedApparentType` equals the input. `getApparentType` takes
   its intersection branch with identical original type and returns that cached
   pointer without calling `getTypeWithThisArgument` or creating cachedTypes entries.
4. The second reduction sees the same flags, so also returns the same input.
5. A nonnil entry exists in the current non-augmented property cache. Its map is
   therefore already nonnil; the original GetSymbolTable would not initialize it.
   The original lookup returns that entry without creating a property or populating
   the augmented cache. ReadPartial is clear, so the wrapper returns the entry.
   WritePartial alone is intentionally accepted because the original read path
   does not reject it. Non-augmented precedence remains intact.
6. Both paths invoke `getTypeOfSymbol` on that exact current symbol once. Lazy
   instantiated/mapped/deferred resolution, mutable resolvedType, diagnostics,
   counters and reentrancy in this call remain authoritative and unchanged.

No semantic call occurs between the guard reads and invoking getTypeOfSymbol.
Same-checker concurrent mutation is outside the supported contract. Flags and
published type data are assumed to satisfy existing compiler representation
invariants, just as the original typed accessors require. Checked state is not
remembered across queries or callbacks.

Guard failure is before mutation. It can add ordinary reads but does not warm
semantic caches, allocate symbols, assign IDs, or consume instantiation budgets.
It then falls through to the exact original helper sequence. Missing and partial
properties, different apparent types, not-yet-computed reductions, never results,
unions, primitives, mapped dispatch, and invalidated/replaced maps all fall back.

Four focused state tests exercise eligibility rejection, current cache/symbol
updates, fallback histories and retained lazy instantiated-symbol resolution.
Seven existing union-property cache tests add reentrant population, augmented
precedence, identity and missing/partial histories. Both baseline and candidate
run the same tests under normal/race/checkptr. Baseline includes the same pure
helper for tests, but its production entry never calls the helper.

This is a reviewed source argument with executable differential checks, not a
machine-checked theorem. Full pinned conformance, CLI/API/emit parity and normal
production build provenance remain required before the frozen workload screen.
The goal remains 10× over native, not merely passing these tests or a small gain.
