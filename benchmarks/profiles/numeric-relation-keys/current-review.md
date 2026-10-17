# Numeric relation keys: current-source independent review

Prepared against main 8291ee5c9dc14ee2a2c244a4ec56b5c4128a0568, with the parent's unrelated CommonJS guard still uncommitted. No shared source edits, builds, tests, profiles, or binary inspection. Gofmt of the new test and `git apply --check /tmp/tsc-relation-keys-current/relation-keys.patch` passed. This is ready for validation, not validated for adoption.

The original design/proof remains in `/tmp/tsc-relation-keys/AUDIT.md`. This refreshed patch applies that production change unchanged to current checker.go/relater.go, preserves both original test files, and adds a direct diagnostic-position regression. `metadata.json` records base/draft source and patch hashes. Original and refreshed artifacts remain separate.

## What the change actually replaces

All five checker-owned `Relation.results` maps change from `map[CacheHashKey]RelationComparisonResult` to `map[RelationKey]RelationComparisonResult`; the maybe-stack slice/set also use 64-bit keys. It is not just a packing fast path in front of the unchanged 128-bit result maps. All four key callers in relater.go use the owning checker. There are no other production results-map accesses outside Relation.get/set/size.

Ordinary source/target IDs below 2^30 with current state bits pack exactly into uint64. The old xxh3 serialization is skipped for those calls. Generic references still run the same full 128-bit hash construction, then probe a new checker-local map from that complete hash to a tagged uint64 ID. Exceptional ordinary IDs/state bits use that interner too. Thus the generic path adds a map lookup and retains every distinct probed hash, including comparisons which never produce a result entry. It does not remove generic hashing, allocate exact token spellings, or replace Go maps with the native custom table.

Native references are local `packages/tsc-ts/src/compiler/relations.ts`: numeric packing/interning around 801 onward (355eb96), token interning (7483396), and numeric open-addressing results around 240 (8e85d67). Native string-allocation savings do not transfer to Go's existing binary hash builder.

## Fresh exposure and bounds

Use committed `benchmarks/profiles/pointer-current`, not old expansion estimates. These are sampled profile snapshots, not paired timings or allocation census; top-300 omissions are not zero. The collection caveats in the capture/summary evidence still apply.

| Workload | Relation.set sampled allocation | Fraction of captured allocation |
| --- | ---: | ---: |
| TypeORM | 5.64 MiB | 1.01% |
| tRPC | absent from displayed top 300 | unavailable |
| VS Code | 36.93 MiB | 0.72% |
| Sentry | 289.38 MiB | 6.28% |

Sentry Relation.get is 5.82s / 4.71% cumulative sampled CPU (0.05s / 0.04% flat), while getRelationKey is 2.22s / 1.80% cumulative (0.74s / 0.60% flat). The cumulative map costs are not removable wrapper work, and must not be added to broad runtime-map totals. Relation.set is not shown in the CPU top300, which gives no zero-cost claim.

On the measured 64-bit Go1.26.9 layout, compiler source `cmd/compile/internal/reflectdata/map.go` constructs a group as an 8-byte control word and 8 `{key; elem}` slots:

- Old key16 + result4 + alignment => nominal slot24, group200 bytes.
- New key8 + result4 + alignment => nominal slot16, group136 bytes.
- Added fallback key16 + numericID8 => nominal slot24, group200 bytes.

This is a 32% reduction in result-group payload before allocator rounding, capacity choices and map headers, not a 50% reduction in the whole map. Applying 32% mechanically to the Sentry sampled allocation would give about 92.60 MiB (2.01% of the captured total), but **that is only layout arithmetic, not a predicted saving**: it excludes interner allocations, growth overlap, changed distribution, and allocation size classes. There is no justification for treating all 289.38 MiB as avoidable.

If R and G denote occupied-capacity slots rather than logical entries, a rough payload balance is 8R bytes saved versus approximately25G bytes added (24-byte interner slot plus group-control share). The interner must stay substantially below roughly one third of result capacity for this narrow accounting to win. Common generic keys shared across the five relation kinds can amortize the added table; probe-only keys and broadest-equivalent recursion probes push the other direction. Current profiles do not reveal that mix. No threshold is an acceptance gate without actual measurement.

Both old and new result groups are pointer-free; neither stores Type pointers. The old cache does not incur per-key GC pointer scanning that this patch could remove. Smaller byte allocations may reduce heap pressure indirectly; interner groups are also pointer-free but retained for checker lifetime. Result-count limits remain unchanged and do not bound interner size. No new Type/Symbol/AST retention occurs.

## Correctness review

No production blocker found by source review:

1. IDs/state occupy nonoverlapping bits: source [32,61], target [2,31], state [0,1]. Bit63 exclusively marks interned IDs. Zero IDs and unknown state bits fall back; exhaustion panics before wrap. No 128-bit hash truncation is introduced. Existing theoretical hash collisions remain for fallback; ordinary pairs become exact.
2. Identity operand ordering occurs before generic detection exactly as before. State bits do not swap, preserving the original behavior. `ignoreConstraints` is ignored for ordinary pairs exactly as before.
3. Generic detection keeps left-to-right short-circuit evaluation, including `getTypeArguments` effects. Generic serialization, shared type-parameter positions across source/target, recursion depth, constraint calls and broadest-equivalent keys are unchanged.
4. All builder/constraint state remains local through recursive constraint resolution. Interner lookup/insertion happens only after the complete hash exists, so nested comparisons cannot corrupt an in-progress outer key. No pointer into growing storage is retained.
5. `Checker` initializes fresh Relation objects; IDs/interner remain on that checker. No cross-checker sharing is added. Existing per-checker exclusive use remains required; this is not a concurrency-safe API redesign. Unlike the old pure hash helper, a new fallback lookup can mutate the interner even when no result is cached.
6. Result counts still use map length, not interner count. Complexity budgets, overflow/failure/reliability flags, maybe-stack partial commit/discard, and relater pooling are preserved. Key values are never iterated for semantic ordering. Different Go map hash seeds cannot change result semantics.
7. Ordinary hashing previously only wrote already-assigned Type IDs/state; skipping it loses no lazy Symbol/Node ID assignment or diagnostic side effect. Mutation of reference resolution/classification still triggers the same generic detection/key reconstruction on each query.

## Tests and next validation

The original boundary/equivalence matrices, alpha-equivalent recursive generic constraints, fallback full128-bit domain, checker-local interning, exhaustion, size/flags and partial maybe-stack tests remain. The cold recursive-constraint API test deliberately queries before diagnostic collection in both directions on fresh checkers; it does not prove a measured number of nested helper calls.

Added `TestRelationKeysRepeatedFailureDiagnosticsKeepUsePositions`: warm a recursive incompatible assignment through two public API queries, then collect diagnostics twice; require exactly two TS2322 errors at the two assignment starts. It uses no @ts-expect-error, so swallowed/reclassified diagnostics or shared error locations cannot satisfy it. Existing tests retain @ts-expect-error coverage for broader recursive, identity and intersection cases.

After parent approval: run focused `go test ./internal/checker -run '^TestRelationKeys?' -count=1` with the normal untrimmed test build, then checker/compiler units, race, full pinned conformance and native/API parity. Inspect actual codegen for packed/common and fallback helper boundaries separately. Measure all four pinned workloads against the preserved pointer/CJS baseline with identical controls, and collect memory if retained. No speed or total-memory improvement is promised; an unfavorable generic/interner mix is a valid reason to reject this draft.

Independent current review by correctness also found no blocker. The maybe-stack test is representation/accounting coverage: it stores and preserves overflow/reliability flags, but does not trigger actual complexity exhaustion or exercise every cached-overflow diagnostic consumer. Full conformance supplies broader integration coverage; do not label the focused test an end-to-end overflow test. Main advanced to58aedf6 with the unrelated CommonJS guard while this source-only review completed; the refreshed patch changes no declaration-transformer code.
