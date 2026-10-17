# Independent source review: 512-probe relation table

Reviewed isolated patch `6c6444df531023cbbb0b77c11233ca8399d1d4565a8cce20dcb9f69a878ea78e` against the previously reviewed 64-probe draft. No builds, tests, Go commands, workload runs or main edits. No correctness blocker found in this parameter-only production change.

Production relation_results.go differs only in relationResultProbeLimit64→512; relater.go is byte-identical (`b6a0747b797f5811b21ca5d3a6352a1526b2f73879e5f25034d0773ecb447633`). Full key comparison, all uint32 result bits, separate occupancy/count, nil reset, checked capacity arithmetic, replacement-before-growth, transactional rebuild and permanent randomized-map fallback are unchanged. The search/insertion invariant remains distance<min(capacity,512). Small tables still wrap at capacity, while larger tables stop at512; no key inserted under this bound becomes unreachable. The last admissible same-home entry is at distance511; entry513 triggers fallback. This increases worst-case table lookup work eightfold versus64; it is a performance/latency tradeoff, not an unconditional improvement.

Test adaptation is adequate for the changed bound:

- Differential pool576 exceeds512, and the test still asserts table versus fallback mode after its deterministic operation sequence. Its successful execution remains unverified here.
- The wrapped ProbeFallback chain contains512 keys, checks a missing lookup without mutation, replaces distance511 before any fallback/growth, then inserts distinct Hi1000 to trigger fallback. Hi1000 remains outside the chain0..511. Fallback nil-reset/reinsert assertions remain.
- Rehash cases512/513 allocate2048 old slots and use Lo increments1024. Their old keys split between two home buckets, each with at most257 entries, within the512 bound. Rebuilding into1024 slots collapses all homes:512 originals fit and the pending key fails;513 originals fail during old-entry copying. Tests retain the entire original map oracle and compare old backing arrays unchanged. This is a deliberate shrinking test, not a claim that doubling naturally creates that pattern.
- Concurrency pool513 guarantees a colliding branch exceeds the bound, while distinct low words have distinct homes at the eventual1024 capacity. Read-only concurrency remains the contract; no concurrent writes are introduced.
- Zero/flags/count/isolation, load-threshold overwrite and integer-boundary tests are unchanged.

Seven cache parents and six children remain13 pass records. With retained API3+2 and primitive1+860, focused total remains879 records across11 top-level tests. The two changed child names are entries512 and entries513.

The new controller is a separate copy; original64 artifacts are untouched. Its only differences are reviewed patch/cache/test hashes, rehash child names, and explicit512 candidate description. All existing source/HEAD captures, parent-approved full-source requirement, saturated builder pins, fixture pins, exact package scope, normal/race/checkptr, root npm/full conformance, numeric exits/signals, log hashes, fail-fast behavior and process cleanup remain intact. Python syntax was parsed only; controller has not run.

Synthetic observations in the author's AUDIT use adaptively selected fixed sequences and do not prove performance or a failure probability on compiler keys. Actual new-binary validation, workload timing and peak-memory evidence remain necessary. The existing64 validation does not validate512.
