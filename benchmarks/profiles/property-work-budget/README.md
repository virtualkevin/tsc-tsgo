# Property-consumer work budget

Offline audit after merged-substitution rejection dfd68f1. Uses exact hash-checked retained-production normal CPU profiles identified by normal-map-attribution/inputs.json. No new compiler runs or optimization timings. The parser fails closed on unknown sample locations; two focused tests exercise overlapping categories and unparsed locations. report.json records all patterns, source profile/raw hashes and mutually exclusive sample buckets.

| Workload | Property relation inclusive % | Property lookup inclusive % | Member materialization inclusive % | Union counted once % | Mapper execution inclusive % |
|---|---:|---:|---:|---:|---:|
|trpc|12.690|9.137|10.152|22.335|3.046|
|typeorm|5.189|7.124|6.157|13.456|0.352|
|vscode|6.984|6.572|7.371|15.629|1.401|
|sentry|10.415|20.428|14.521|30.662|1.703|

These are historical sampled CPU paths including callees, not wall time, exclusive function costs, duplicated-work counts, removable fractions or a speedup prediction. The union is genuinely deduplicated across overlapping categories; individual percentages must not be added. Background GC induced by these operations is not assigned to them. Even removing this entire union would not establish the requested10× result. A broad redesign must address additional work and representation costs.

## Source review and next boundary

propertiesRelatedTo first performs getUnmatchedProperty, then excess-property checks where required, then ordered target-property comparisons. propertyRelatedTo consumes modifier/private-origin/optionality information and subsequently type information. getPropertyOfTypeEx performs apparent-type reduction, structured resolution, type-only export checks, value-symbol classification and Object/Function augmentation. These operations cannot be replaced by a bare name-to-type map without preserving their effects.

Next architecture prototype: a property-view consumer boundary that carries original symbol identity, mapper context and declaration metadata while retaining the existing fallback/materialized facade. It must preserve missing-property checks and their order, private/protected origins, alias identity, optionality, mapper composition, type-query counters, recursive state and diagnostics. Published API symbol identity must remain stable. Reusing the already-rejected indexed-property join or direct-member-materialization implementation unchanged is not proposed.

Before production integration, define and test the view-to-symbol correspondence against the existing materialized consumer in independent stateful fixtures. Restrict eligibility before effects; retain original materialization for unsupported cases. Use this budget to prioritize the consumer boundary, not to claim it will meet10×. No production source or PERF change.
