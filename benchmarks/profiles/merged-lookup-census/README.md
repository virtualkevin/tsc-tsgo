# Diagnostic merged-symbol lookup census

The retained normal-profile attribution places getMergedSymbol map-path samples at1.236% of VSCode CPU and0.716% of Sentry CPU. This observer measures lookup outcomes and map sizes before choosing whether a negative-lookup filter is worthwhile. These modest sampled fractions do not establish a route to10× performance.

Source instrumentation preserves the existing map lookup and returned symbol. Nonnil input increments lookups; a nonnil map value increments replacements; otherwise unchanged increments. Thus unchanged includes both absent entries and explicitly nil-valued entries. Nil input bypasses lookup and is not counted. Writes and peak map size are counted after the authoritative assignment. Bucket0 means an empty map, bucket k means size in [2^(k-1),2^k-1]. Counts are not CPU costs, equivalent-result counts, or removable work.

Counter records are checker-owned, and the mutex-protected registry retains only counters, not symbols or checker objects. CLI serialization runs after checking completes; its registry lock does not make live snapshots safe. This is diagnostic-only code, controlled by TSC_GO_MERGED_LOOKUP_CENSUS. An enabled observer adds increments, length checks and histogram updates, and serializes at exit. Disabled mode still changes binary layout and adds branch checks. Neither is a production optimization.

`capture.mjs` requires completed unit/race/checkptr validation and verified build/source identities, then runs the retained baseline, observer-disabled binary and observer-enabled binary sequentially on each pinned workload. Each must have exact clean diagnostics and unchanged physical inputs. Single-run elapsed times include serialization and host/order effects; they are observer controls, not causal overhead measurements or PERF.md data. No CPU sampling, trace or extended diagnostics is enabled.

Three focused tests cover nil-input bypass, absent/nil-value behavior, replacement updates, size buckets, independent counter records and disabled semantics. Full ten-package, race and checkptr results remain pending at this preparation checkpoint. Keep experimental source and HEAD fixed while validation/capture provenance checks are active. Baseline files are preserved under `/tmp/tsc-merged-lookup-census/baseline-*`; restore only after archiving results and verifying all candidate source hashes.

## Completed collection

All12baseline/disabled/enabled CLI runs pass exact clean diagnostics and unchanged-input/source checks. Unit validation passes2342test records/118top-level tests across10packages; focused normal/race/checkptr each pass3tests. Raw logs and census JSON are in `evidence.tar.gz`, with per-file hashes in `evidence-manifest.json`; `summary.json` preserves per-workload counts and observer-control elapsed times.

| Workload | Lookups | Non-nil replacements | Unchanged fraction | Peak keys per checker |
|---|---:|---:|---:|---:|
| TypeORM | 2,772,580 | 60,863 | 97.805% | 709 |
| tRPC | 655,374 | 6,159 | 99.060% | 1,332 |
| VSCode | 51,235,490 | 415,468 | 99.189% | 2,515 |
| Sentry | 25,432,841 | 251,843 | 99.010% | 9,317 |

Each capture has four checker counter records. Empty-map lookups are only464/4244/2877/3414 respectively, so merely checking map length would not eliminate most probes. High unchanged rates support investigating a negative-lookup filter, not extending semantic caching. The observer does not distinguish absent from nil-valued map entries, retain key identities, count repeated distinct queries, or measure actual filter occupancy. No filter false-positive rate is established. A future filter must preserve map lookup on potential membership, update on every write, and never yield false negatives. Existing pointer hashes depend on the pinned runtime's non-moving heap; that assumption cannot be silently broadened to future runtimes.

Single-run observer elapsed times vary in both directions and are not causal overhead estimates or optimization evidence. No PERF row is added. Guarded restoration has returned production source/default binary exactly to retained216d40c7/8fe4bd80; diagnostic binary7a8b0d48 remains separate. The10× target is unmet.
