# Structural property-comparison census

Diagnostic observer for the final loop in `Relater.propertiesRelatedTo`, after identity/tuple handling and unmatched/fresh-object checks. It does not change lookup or comparison decisions.

At loop entry, classify source using existing fields only: non-object, unresolved object, pending members, materialized callable/module, or ordinary materialized object. These are descriptive shapes, not immutability or optimization-eligibility proofs. Capture initial target property count before exclusions and source raw member-map size for the ordinary class. No extra resolution, property materialization, symbol lookup, or retained semantic object.

Per class count loop entries, visits after exclusions, lookups after predicates, nonnil hits, identical hits, misses and optional-target misses. Fixed matrices record ordinary lookups/misses by initial source/target size buckets: zero empty; k covers [2^(k-1),2^k-1]. Early exits count only work actually executed; recursion has independent local observations. Shapes may change during a loop and this census does not measure that change.

Three focused tests cover classification, unresolved/pending/module/callable distinctions, counters, size boundaries, entry snapshots, and owner isolation. Validation also runs race, strict checkptr and compiler unit suites. Capture requires clean diagnostics for baseline/disabled/enabled runs of all four pinned workloads, matching physical inputs/build settings, and conservation of counter totals. Observer control elapsed times are not benchmark evidence. No PERF rows.

Build and validation passed: three focused race tests, three checkptr tests, and 2,342 root test records (118 top-level tests, ten packages). All 12 captures passed with clean diagnostics and matching physical inputs. Raw evidence is archived and hash-verified. Guarded restoration returned source/default binary to the retained baseline; the patch and observer source remain here.

## Result

| Workload | Final-loop lookups, all classes | Ordinary lookups | Ordinary misses | Ordinary miss % | Lookups: source ≤7, target ≥256 | Misses in that size region |
|---|---:|---:|---:|---:|---:|---:|
| TypeORM | 232732 | 141043 | 98684 | 69.967 | 0 | 0 |
| tRPC | 17844 | 5019 | 2126 | 42.359 | 0 | 0 |
| VS Code | 4645662 | 3793658 | 1857296 | 48.958 | 219547 | 218300 |
| Sentry | 30911038 | 29969142 | 27842005 | 92.902 | 25157305 | 25006183 |

All recorded misses in all classes were optional-target misses. Sentry's ordinary source≤7/target≥256 region contains 25,006,183 misses. The largest cells are source2–3/target256–511 (8,884,732 misses), source1/target256–511 (7,760,010), source4–7/target256–511 (3,959,004), and source0/target256–511 (1,712,807). This supports a targeted sparse-comparison experiment; it does not establish a wall-time gain or immutability.

Source review: `getPropertyOfTypeEx` falls back to global Object properties when source members are absent, and mapped objects can change apparent type. A future skip mechanism must include augmentation, exclude unsupported apparent-type cases, and invalidate or recompute membership after recursive comparison/lookup side effects. It must preserve target traversal order and preliminary checks. The census ordinary class is broader than any such proven-safe fast path; eligible counts are an upper bound, not guaranteed skipped work. Full correctness and matched workload screening remain required for any implementation.
