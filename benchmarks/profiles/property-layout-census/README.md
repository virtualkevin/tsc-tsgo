# Existing target name-layout availability

Extends the property-loop census to count lookups/misses whose target already has a fully materialized pending-member name layout. Requires exact nonmapped Object target and the same nonempty property-slice storage and length as the existing layout. No names/types are retained and no additional resolution or materialization is performed. Counts are snapshots at loop entry; source/target state can change later.

Per source class, record LayoutLookups/LayoutMisses and SmallWideLayoutLookups/SmallWideLayoutMisses. SmallWide requires ordinary materialized source≤7 and target≥256. The observer counts only work the original loop executes, including early exits and recursion. It does not prove safe skipped work, immutable external API behavior, unique target reuse or timing gains.

Source audit: getNamedMembers produces contained-before-inherited order, sorting each partition; target order cannot be replaced by source/map iteration order. Existing pending memberNames maps names to that exact property order and is used authoritatively by pending lookup. Ordinary property slices are exposed by GetPropertiesOfType and can be shared between object types, so inventing a permanent cached index for arbitrary slices would require additional ownership guarantees. This census asks whether the already-existing layout provides enough coverage to pursue an indexed sparse join without a new target cache.

Four focused tests cover existing source classifications/counters/snapshots and new exact-slice target eligibility, mapped fallback and counters. Validation passed: four focused race/checkptr tests each, root2343test records/119top-level/10packages. All12baseline/disabled/enabled captures passed with clean diagnostics and unchanged physical inputs/source/artifacts. Raw evidence is archived with hashes, and guarded restoration returned retained production216d40c7/8fe4bd80. No PERF row; diagnostic elapsed controls are not optimization timings.

## Result

Counts below are in the ordinary-materialized source class. Existing-layout misses are a subset of its original misses. Small/wide means source≤7members and target≥256properties.

| Workload | All ordinary misses | Existing-layout lookups | Existing-layout misses | Small/wide layout lookups | Small/wide layout misses |
|---|---:|---:|---:|---:|---:|
| TypeORM | 98684 | 20612 | 13020 | 0 | 0 |
| tRPC | 2126 | 2551 | 1381 | 0 | 0 |
| VS Code | 1857296 | 417242 | 64753 | 0 | 0 |
| Sentry | 27842005 | 13262792 | 12805723 | 12309787 | 12238154 |

All original class/path counts match the preceding property-loop census. Sentry's12,238,154small/wide layout misses are48.941%of the25,006,183misses in that size region, and43.956%of its ordinary-source misses. This is occurrence coverage, not a wall-time forecast. It does not include checking global Object eligibility, source mutations after entry, or unique target reuse.

This supports an exact sparse-join experiment restricted to the existing layout. Query target positions using current source/global Object names; process the smallest remaining position to retain target order, then recompute after every actual lookup/comparison. Preserve the original remaining loop as fallback when source shape ceases to qualify. No target-index construction or persistent negative cache is justified or needed for this subset. Membership/layout invariants and augmentation still need explicit implementation/tests, and the new algorithm requires independent correctness and performance gates.
