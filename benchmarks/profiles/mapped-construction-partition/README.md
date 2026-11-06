# Mapped-member construction cost

Offline follow-up to contextual-type-partition at 8f7629d. Uses the same pinned
normal-build CPU archive and checker source, with no workload execution or compiler
change. Six ownership/source tests pass; a second run reproduces the report exactly.
Archive, individual raw texts, parser, inputs, source and prior totals are checked.

Each sample belongs to its innermost resolveMappedTypeMembers method or closure.
The corresponding source line selects an operation. Nested mapped resolutions
therefore do not also charge the caller's stage. Stage and flat rows partition the
selected samples; inclusive descendant rows overlap. Compiler source attribution
can include adjacent instructions. Unknown lines remain explicit. This measures
historical sampled CPU, not wall time, call counts, allocation/GC savings, repeated
work, or semantics that can safely be skipped.

| Workload | All mapped construction CPU % | Index-value instantiation % | Modifier-index lookup % | Link tables % | Symbol creation % |
| --- | ---: | ---: | ---: | ---: | ---: |
| tRPC | 1.015 | 0 sampled | 0 sampled | 0 sampled | 0 sampled |
| TypeORM | 0.352 | 0 sampled | 0 sampled | 0 sampled | 0 sampled |
| VS Code | 0.475 | 0.006 | 0 sampled | 0.089 | 0.013 |
| Sentry | 9.297 | 5.323 | 1.645 | 0.617 | 0.049 |

Sentry's largest stage is not predominantly mapper dispatch: indexed-access
resolution appears beneath 5.315% of total CPU in the index-value stage, and
findApplicableIndexInfo beneath 4.796%. That lookup also accounts for 1.645% in
the separate modifier-index stage. Because those stages are disjoint, their
lookup subtotal is 6.442%; other inclusive rows within each stage must not be
added. This leads back to the index-applicability/relation bottleneck already
investigated, rather than establishing a new allocation-dominated path.

Decision: do not build a lazy mapped-symbol plan or repeat mapper specialization
based on this evidence. The path is small on three workloads, and Sentry's work
is concentrated in semantic relation evaluation. A literal-property query can
trigger construction of index signatures, but delaying those operations can
change resolution cycles, counters/limits and diagnostics. Existing template
relation/cache experiments remain rejected; this audit does not reopen them.

The earlier contextual audit identified a plausible construction boundary. This
broader partition narrows that hypothesis: coallocation or a different property
container does not address most measured cost. No candidate or PERF row is added,
and no 10× performance mechanism is established. Production stays unchanged.

Reproduce with `python3 -B -m unittest discover -s benchmarks/profiles/mapped-construction-partition`
and `python3 -B benchmarks/profiles/mapped-construction-partition/analyze.py`.
