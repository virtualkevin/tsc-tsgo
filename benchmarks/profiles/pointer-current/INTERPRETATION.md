# Interpretation limits after capture

The copied reports and preservation plan retain their original bytes and preparation-time wording. This directory now contains the planned files; original absolute paths can be mapped through preservation-plan.json.

Allocation data is sampled and can omit the newest allocations. The pinned Go1.26.9 runtime/pprof documentation (src/runtime/pprof/pprof.go:126) describes heap-profile data as of the latest completed collection; runtime.MemProfile (src/runtime/mprof.go:927) allows data up to two GC cycles old. The compiler’s internal/pprof.ProfileSession.Stop writes the allocs profile without forcing a final GC. Reported alloc_space/alloc_objects totals and fractions therefore describe the collected profile, not an exact, fully flushed whole-run allocation census. They are neither live heap nor peak RSS.

CPU samples cover the profiled compiler; overlapping cumulative caller/callee costs must not be added. These captures use the retained pointer-table binary with explicit four checkers, default GC and round-robin. They do not measure dependency scheduling or prove a speedup. Independent benchmark evidence remains in PERF.md and benchmarks/results/.
