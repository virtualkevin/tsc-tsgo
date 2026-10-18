# Instantiation family observer — preparation

Follow-up to the completed weak-window census. Production remains unchanged. This isolated overlay keeps the same sampling/eviction/weak-root policy and adds fixed 16×10 scalar counters per checker for actual worker dispatch family and concrete top-level mapper implementation. Classification never invokes mapper methods, inferred-type queries, lazy IDs or semantic work. Composite/merged children remain unclassified; top-level families are not proofs of purity.

Counts follow each request token, so input mutation or slot eviction does not move its outcome to a different family. Zero-descendant repeats are counted directly, but are not necessarily cheap. Counts remain sampled, allocator-dependent, eviction-censored and overlapping; no population extrapolation or CPU savings claim. No timing instrumentation is added. Six focused tests are prepared, including inherited weak-root lifetime and pending/eviction cases. Validation and workload controls are not yet complete. PERF.md receives no diagnostic counters.

Next: validate normal/race/checkptr, build isolated binary, extend independent schema/conservation checks, then run all four baseline/disabled/enabled controls with frozen source/inputs. No wider cache is implemented or justified by this preparation.

## Completed controls

Validation22524 passed six tests each normal/race/checkptr after preserving the initial cache-permission setup failure. Build49373 succeeded. Capture98340 and independent verification80988 exited0: all12controls clean and exact inputs, family counters conserve aggregate outcomes. Six Python validator tests passed. family-summary.json ranks observed families without extrapolation. Parameter/array repeats lead TypeORM, tRPC and VSCode; Sentry is led by template/function repeats (22694, all zero descendant instantiations). These are identities of completed results, not a CPU saving budget or cache-safety proof. No optimization performance rows added.
