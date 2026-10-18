# Sparse property lookup filter candidate

The structural-comparison census found25,006,183Sentry final-loop misses in initial source≤7/target≥256 comparisons. This candidate keeps target traversal order and every preliminary check. For target property lists≥256, it builds a local256-bit conservative fingerprint of all source and global Object member-map keys, provided source≤7/global≤32 and both are already-resolved, materialized, non-mapped, non-callable, non-module objects. Excludes anyFunctionType. No forced resolution or persistent cache.

A negative fingerprint skips a provably absent lookup. Positive fingerprints use original getPropertyOfType and propertyRelatedTo. After every actual lookup (and subsequent recursive comparison), the next eligible target iteration rebuilds the filter, rechecking shape and bounds. Failed eligibility disables filtering for the remainder of this loop. Nil-valued/non-value keys remain conservative positives. Hash collisions are allowed and do not change results.

Correctness reasoning: exact Object flags exclude primitive/union/intersection/instantiable reductions; mapped flags are excluded so apparent type stays unchanged. Resolved state makes member resolution a no-op. No pending members or signatures means no inherited pending lookup or Function augmentation; anyFunctionType is separately excluded. Global Object keys are included. A negative name is absent from both maps, so neither symbolIsValue nor alias resolution executes in the original path. No semantic action occurs between consecutive skipped properties. Every real lookup/comparison invalidates the local snapshot before the next potential skip. No claim that a type is permanently immutable.

Tradeoffs: fingerprint calculation on every eligible name, map iteration on rebuild, extra branches and stack footprint. Repeated collisions or frequent hits can regress. Fixed thresholds/hash and frozen comparison policy must not be retuned after a failed screen. This is a localized experiment, not evidence of10×native performance.

Four focused tests cover conservative membership/collisions, shape and size fallback, augmentation, rebuilding after mutation, and global bounds. Additional48wide-target CLI cases at widths255/256/511 with exactOptionalPropertyTypes on/off compare candidate/retained/pinned upstream Go, including late mismatches, global augmentation, recursive properties and callable/mapped sources. Full conformance, root, race/checkptr and native/API validation precede any promotion. All validation passed: full pinned conformance14915configuration cases(12789fully checked,8partial,2118unsupported,0failed), root2343test records/119top-level/10packages, four focused race and four checkptr tests,80native parity cases,12API/emit tests and48wide-target cases across three binaries. The first two wide-harness attempts failed on configuration/exit-status assumptions; their reports are preserved alongside successful wide-v3. No compiler change was needed. All368raw validation files are archived with hashes. Guarded restoration returned production source216d40c7 and default binary8fe4bd80; candidate4ce3c7ed/source d8073fc1 is preserved separately. Preflight verifies the exact three-file candidate delta and identical build settings. Frozen screening completed and failed acceptance; retained baseline remains production.

## Screen decision: rejected

Capture31411c8 completed9pairs per small workload and5per large, with identical inputs, clean diagnostics and matched RSS. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Median RSS baseline/candidate MiB |
|---|---:|---:|---:|
| TypeORM | 0.982814 | 0.994954 | 883.211 / 883.949 |
| tRPC | 1.009804 | 0.937791 | 239.875 / 241.125 |
| VS Code | 1.016023 | 0.987939 | 7713.055 / 7801.074 |
| Sentry | 1.175879 | 1.096327 | 5375.582 / 5431.227 |

Aggregate ratio-of-medians1.043503 passes, paired-median aggregate1.002640 fails1.01. tRPC paired0.937791 fails the per-workload0.98floor. RSS passes. No confirmation runs, additional samples or threshold/hash retuning. Production stays retained216d40c7/8fe4bd80. Raw samples and execution copies are in `benchmarks/results/sparse-property-filter-screen/`; PERF has all four rows. Integrity status passed is not performance acceptance. Sentry's favorable summaries do not override the frozen whole-screen failure and do not establish mechanism-specific causality or native-relative progress.
