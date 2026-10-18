# Folded simple-substitution plans — isolated prototype

This changes the experimental mapper plan from d51c63a, not production. The first plan only removed recursive control flow; shallow-chain costs showed blanket compilation unsuitable. This version composes consecutive immutable SimpleTypeMapper leaves into a typed pointer map, while preserving the original ordered execution of every other leaf and instantiateType branch.

## Contract and argument (not a machine-checked proof)

A simple substitution changes only its exact source pointer to its target, otherwise returning the input, with no semantic effects. For a finite sequence, any input absent from all source pointers is unchanged. For each distinct source, evaluate the same ordered pointer substitutions at compile time and store the final pointer. Looking up a source therefore returns exactly the original sequence result; all other inputs remain unchanged. Nil keys and nil results require comma-ok lookup. Repeated sources must be evaluated from their original input through the entire sequence, not overwritten by the last source occurrence.

This assumes simple mapper source/target fields are immutable after construction. Initial mapper.go inspection shows writes only in its constructor; integration still requires a whole-source ownership/write audit. Leaf arrays and effectful callbacks are not eligible. Folded mappers retain original typed leaf roots in addition to result maps. Original code offsets remain unchanged, and branch destinations split spans, so a jump cannot enter or skip a partially folded sequence. Compiler counters and diagnostics are neither cached nor replayed.

Added finite exhaustive tests cover9^4four-substitution sequences over{nil,a,b}, checked on all domain values plus an absent pointer. A separate composite branch-entry regression preserves instantiate callback counts and tail substitutions. Inherited tests cover nested stateful histories, panic order, array mutation, fallback and GC retention. These are component tests against the existing local evaluator, not pinned-oracle API equivalence or a formal proof.

Seven tests are undergoing normal/race/checkptr validation. The existing fixed-order1/2/4/8/32leaf evaluation/compile cost benchmark will run afterward; no performance result yet. Full compiler integration, correctness and workload gates remain outstanding. No production change or PERF row.

## Completed pilot

Validation78607 terminal0: seven tests each normal/race/checkptr. Benchmark89391 terminal0; independent verify.py checked source hashes, exact test coverage, and75observations.

| Leaves | Recursive ns | Folded plan ns | Compile ns | Compile allocation bytes | Idealized reuse to repay compile |
|---:|---:|---:|---:|---:|---:|
|1|2.395|9.21|182.1|64|no evaluation gain|
|2|5.364|13.92|687.9|384|no evaluation gain|
|4|11.75|11.13|1057.0|528|1705|
|8|30.33|11.72|2058.0|816|111|
|32|254.2|18.94|15854.0|5888|68|

The32leaf evaluation ratio is13.42×, but this synthetic result is not the compiler target. Compilation grows to15.854µs/5888allocated bytes; idealized68queries excludes retained memory/GC/dispatch cost. Shortchains remain unsuitable. Continue selective integration research with explicit construction/ownership costs; do not enable blanket compilation. Production and PERF unchanged.
