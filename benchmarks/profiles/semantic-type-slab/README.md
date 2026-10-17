# Typed semantic allocation slabs

This candidate batches only `ObjectType` and `TypeReference` allocations in checker-private typed slabs of 32 objects. Headers remain embedded and the TypeData interface representation is unchanged. IDs, flags, constructor order and published pointer identity are preserved. There is no unsafe pointer conversion, reset, global pool or reuse of published storage.

The allocator roots only its current slab. An escaped object roots its own slab and may retain up to 31 neighbors and their transitive graphs; an obsolete slab with no escaped objects is collectible. Initial-page slack and graph retention are explicit costs to measure. The slab capacity is fixed before timing.

The normal-flag retained-build allocation profiles attribute about 2.31% of Sentry's and 2.68% of VS Code's estimated allocation-object counts to the selected shapes. `selection.json` links line-level decodes to baseline source and raw profile hashes. These sampled cumulative counts are not live heap, an exact census, CPU-removal budgets, or evidence of a path to 10× alone. Current Type and TypeMapper headers are already embedded, so no second header allocation is assumed. The earlier rejected compact-Type representation is not repeated.

Thirty focused test records pass across six top-level tests: slab rollover with 1,025 objects/references, stable identity/zero state, separate checker ownership, copied-header graph retention, obsolete-page collection, and existing accessor/tail contracts. Full validation is in progress. The preserved candidate is `packages/tsc-go/dist/tsc-go-semantic-type-slab`; exact identities and three-file source delta are in `screen.json` and `build.json`.

Screening and confirmation requirements are frozen in `COMPARISON_POLICY.md`. No timing or promotion is established by the focused tests or allocation-site evidence.

Full correctness validation completed: normal/race/checkptr each pass 30 focused records; root units pass 2,342 records across ten packages; conformance passes 12,789 fully checked plus eight partially checked cases, with 2,118 unsupported skips and zero failures; native parity passes 80/80 and actual-Go API/emit/project tests 12/12. Twenty-one raw evidence files are archived in `validation.tar.gz`, indexed by `validation-archive.json`, with reports under `benchmarks/validation/semantic-type-slab-*.json`.

`restoration.json` verifies production source/default executable were restored to retained node-pointer Go. The slab candidate remains separately preserved. Screening preflight verifies both build identities and the restored workspace; no performance result or promotion follows from validation alone.

Screening **failed**: aggregate ratio-of-medians 0.984859 and paired-median 0.987576 are below 1.01, and the workload minimum gate fails. RSS passes. Full evidence is in `../../results/semantic-type-slab-screen/recording/proposal.json`. The candidate is rejected with no confirmation runs or slab-size tuning; retained node-pointer Go remains in production. This experiment does not establish a general benefit from batching semantic allocations.
