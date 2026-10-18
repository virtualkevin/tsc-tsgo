# Bounded instantiation-window observer

At HEADeaf5d09, production source216d40c7/defaultbinary8fe4bd80 remain unchanged. This is a diagnostic overlay, not a wider semantic cache or optimization. It follows the earlier detailed census recommendation to observe requests across execution rather than stopping after an initial set of keys. The completed capture and verification are recorded below; no optimization performance claim follows.

The hook runs only after the existing active-mapper cache misses and its original limit checks/counters. Aliased requests are counted/excluded. Alias-free(input type,mapper identity) keys are selected by a mixed hash residue (nominal1/128), using the already assigned typeID and one-way mapper-address hashing. Selected requests map to4096weak slots per checker using separate hash bits. Selection is deterministic and allocator-dependent, not a proven random sample; results must not be extrapolated by multiplying128.

Each slot keeps weak input/mapper/result/current-node references and scalar state. Hash collisions evict prior records throughout execution. FirstInWindow includes both first-ever and forgotten requests; eviction censors recurrence. Exact weak identities prevent address reuse from becoming a false match. Nested requests encountering a pending identical key are separate from repeats of completed records. Serial tokens prevent an outer finish from overwriting a slot reused by nested work. EvictedBeforeFinish explicitly records lost outcomes.

Selected observed state consists of input flags/objectFlags, current-node identity and a generation incremented on clearActiveMapperCaches. It does not include all inference generations, mapper contents, contextual queries, recursive state, resource budgets or diagnostic effects. Equal state and equal result pointers are not cache eligibility. Invalidation during a call can change the next observation without changing the current result. All original cache lifetime/diagnostic behavior remains in force.

DescendantInstantiations measures changes in the existing cumulative uint32 counter during selected worker calls, excluding that call's pre-hook increment. Nested windows overlap, so these counts are not additive unique work, CPU time, wall-time savings or removable cost. Wraparound is reported separately. Observer overhead includes hashing, weak handles, fixed tables and entry/exit instrumentation; no timing from this binary may be credited as optimization.

The original three focused tests cover completed repeated results/state-generation changes, pending recursion and active-slot eviction, selection partition and exclusive output. Normal/race/checkptr validation61975 completed. The expanded validation adds weak-root lifetime coverage; completed controls and independent verification are described below. No production integration or broad compiler correctness claim follows from focused observer tests.

The initial preparation stopped on an incorrect uniqueness assertion for stopTracing; the source has two sites. No tests ran then. The corrected overlay hooks the final CLI program location, as recorded by the complete patch and preparation-note.txt. Staged source and validation controllers were frozen during their respective runs.

## Completed capture and independent verification

Expanded validation/build16616 completed normally: four focused tests each normal/race/checkptr, including weak semantic-root collection. Diagnosticbinary77e30f6b01a5908444dc12655ecf6775f188b88195b7d4a384ecb04ad5ce98e3. Capture1396 and verifier7019 exited0 atHEADeaf5d09. All12baseline/disabled/enabled controls had clean diagnostics/status and exact pinned physical inputs. The independent verifier also reread raw focused-test coverage, build metadata, overlay hashes and all counter partitions. Three Python counter-validator tests passed. Earlier preparation/validation sections describe intermediate checkpoints.

| Workload | Actual misses | Selected | Completed repeats | Same result pointer | Changed result pointer | Evictions | Descendant count on completed repeats | Minimum repeats with zero descendants |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|TypeORM|425723|3308|702|702|0|208|165|537|
|tRPC|222416|1715|415|415|0|53|112|303|
|VSCode|5915965|45452|7886|7886|0|22817|2668|5218|
|Sentry|11722854|88972|38449|38445|4|34951|12424|26025|

Sentry observed one selected pending recursive request; others zero. No pending entries, lost finishes or counter wraps remained. Same-observed-state-and-result repeats:466/362/5647/35660 respectively. All4Sentry changed-result observations were outside that partial-state-equal subset; this does not make that subset safe for caching.

Because each repeat with a positive descendant count contributes at least one, max(0,completedRepeats-descendantCount) is a lower bound on zero-descendant repeats in this observed window. This arithmetic is valid even though nested work counts overlap. It is not a bound on direct execution cost: a worker can perform other expensive work without calling another instantiation. No CPU/removable-work budget follows from these counts.

Single fixed-order control durations (baseline/disabled/enabled seconds): TypeORM2.853/2.342/2.389; tRPC.522/.519/.517; VSCode33.118/33.694/35.208; Sentry28.603/26.263/26.852. Variation and instrumentation prevent treating these as compiler speedups or precise overhead estimates. They are diagnostic controls only, excluded from PERF.md.

Decision: no broader cache implementation yet. Distinguish repeat type/mapper families and cost, then prove context and budget behavior; equal weak identity/selected state alone is insufficient. The4changed results and eviction censoring must remain explicit. Production is unchanged and the10×native-relative goal remains unmet.

summarize.py independently revalidates raw counters against report hashes and reproduces summary.json, including unrounded durations and limitations. verify.py requires the original captureHEAD and must run before committing; later use the stored hashes/reproducer for evidence readback. Manifest hashes all committed profile files except itself. No performance rows are added for diagnostic counts.
