# Bounded symbol-instantiation request census

Diagnostic overlay only, on retained source 216d40c7. Record actual entries to newInstantiatedSymbolWithLinks before target/mapper flattening; calls that reuse an original symbol are outside this denominator. Each checker owns a bounded map of the first 32,768 distinct weak (symbol, mapper) identities. Known keys remain tracked after capacity; untracked requests remain explicitly unknown. No pointer addresses are serialized or used as integer roots, and weak key equality distinguishes reclaimed objects from later reuse of their storage.

Rows distinguish nil/simple/array/merged/unknown mapper kinds. For tracked requests, compare selected state to the last tracked request: symbol/check flags, declaration count, parent/value declaration, resolved read/write/name types, target and mapper links. The ledger stores weak references plus scalar values, not strong semantic roots. Unknown mapper kinds and equal partial state are not cache eligibility. Hidden mutation, inference generation, declarations with unchanged counts, map content, recursive state and consumer writes are not captured. No semantic IDs, resolution queries, forced GC or new checkers are introduced.

Counts conserve requests as new keys + repeated same observed state + repeated changed observed state + unknown at capacity. New keys equal ledger length. Serialization acquires only existing checker locks at CLI completion, rejects tracing and uses exclusive output creation. Observer bookkeeping perturbs allocation and timing; neither counts nor durations belong in PERF.md. Disabled controls still carry hook/layout overhead. Full pinned baseline/disabled/enabled controls and independent hash/input/count verification are required before using results. No production cache or speedup is proposed.

Validation/build and all twelve controls completed successfully. Three focused observer tests passed normally, with race instrumentation and strict checkptr; three counter-validator tests passed. Independent verifier checked raw counts, physical inputs, immutable source/binary/controllers and clean diagnostics before archival. Production stayed unchanged.

| Workload | Constructor requests | Tracked new keys | Repeated same observed state | Repeated changed observed state | Unknown at capacity |
|---|---:|---:|---:|---:|---:|
| typeorm | 176521 | 131072 | 0 | 0 | 45449 |
| trpc | 37474 | 37474 | 0 | 0 | 0 |
| vscode | 1859702 | 131072 | 0 | 0 | 1728630 |
| sentry | 1688083 | 131072 | 5 | 0 | 1557006 |

No symbol-cache implementation is justified by these observations. tRPC has complete ledger coverage and no repeated key. Large workloads are heavily censored by the capacity limit; absence of tracked repeats must not be generalized to untracked requests. The five Sentry repeats all use unknown mapper kinds and partial-state equality does not establish eligibility. The results also say nothing about structurally equivalent but separately allocated mappers.

A distinct next hypothesis is avoiding a first clone when the original property has a syntactically closed primitive annotation, rather than caching already-created mutable symbols. Existing resolved-type checks already return the original once it is known unaffected; a proposed earlier proof must preserve lazy resolution, optionality, setters, declaration merging, instantiated/synthetic symbols and error behavior. Eligibility and workload frequency remain unmeasured.
