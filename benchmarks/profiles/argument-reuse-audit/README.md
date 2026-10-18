# Overload argument reuse: executable boundary audit

Two focused tests pass against retained production source216d40c7 at `f285fd7`. They run through a Go source overlay; no production file or executable was changed. This investigates the context-complete memoization strategy in OPTI_ANALYSIS_01.md after the rejected direct-symbol storage experiment. No performance measurement or new full-conformance claim is made.

## Proven constraints

1. **Syntactically context-insensitive arguments are not context-independent results.** The same string-literal AST node reports false from `isContextSensitive`. Checking it against `string` returns its fresh literal type, while checking it against a string-literal contextual type returns the regular literal type. Their regularized identities match, but the returned type pointers and freshness differ. Returning to the broad context returns the original fresh pointer. A cache keyed only by argument node and the context-sensitive predicate would conflate those results.
2. **An identical returned type does not imply a side-effect-free query.** Repeating the same argument/context/mode request returns the same type pointer but resets `instantiationCount` from17 or4,000,000 to0. Returning a previously stored pointer without preserving that reset changes checker state. This test does not itself demonstrate a TS2589 diagnostic difference; it proves a concrete budget-state obligation that a memoization design must address.

The first run failed to compile because the audit fixture used int for a uint32 counter. That fixture and raw failure/report are preserved under `initial-build-failure/`. Changing the fixture's slice element type to uint32 produced two passing tests without compiler source changes. No failed run is counted as semantic evidence.

## Source review

- `resolveCall` may first choose by subtype and then by assignability; the relation and candidate order are semantic inputs.
- `chooseOverload` creates inference contexts, may change argument-check mode after skipped generic/context-sensitive work, instantiates candidate signatures, and may repeat inference and applicability. Common argument syntax does not establish equivalent requests.
- `isSignatureApplicable` calls `checkExpressionWithContextualType` using each candidate parameter type. JSX, this-arguments, rest/spread handling and error-reporting paths are distinct.
- `checkExpressionWithContextualType` pushes contextual and inference state, calls `checkExpressionEx`, clears collected intra-expression inference sites when appropriate, and may regularize literal freshness through an instantiated contextual type.
- `checkExpressionEx` sets/restores currentNode and resets the instantiation budget before checking. Its returned value alone does not describe the operation.
- `isContextSensitive` is documented as recognizing nested function/arrow forms subject to contextual typing. It is not a general purity or cache-validity predicate.

The two tests establish narrow counterexamples, not that every argument cache is impossible. Including contextual type identity addresses the first fixture but does not automatically capture mutable inference generations, flow state, diagnostics, resolution recursion or budget effects. Replaying one counter assignment is not proof that all effects are covered.

## Decision and next evidence

Do not implement an argument-node-only cache or infer reusable work from the inclusive cost of signature resolution. Before a narrower cache prototype, measure repeated requests within one call-resolution lifetime with their candidate parameter type, mode, inference identity/generation and flow/resolution state. Keep unresolved contexts unclassified and distinguish result equality from semantic equivalence. Measure the non-overlapping cost of the repeated subset rather than counting an entire expensive caller as removable. No eligible reuse budget is established here.

`run.py` records the command, raw log hashes, focused test source hash, inspected source hashes and unchanged production source/HEAD before and after execution. It expects the pinned Go toolchain and uses local Go cache access. Re-running it writes a new audit report in this directory. `report.json` is the successful recorded run. PERF.md is unchanged because this audit contains no timing data.
