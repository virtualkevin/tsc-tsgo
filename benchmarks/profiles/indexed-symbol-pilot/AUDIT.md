# Indexed symbol links: architectural pilot from OPTI_ANALYSIS_01

Status: formatted experimental source with six focused tests passing under normal, race and checkptr Go-overlay runs. No full compiler build, full compiler validation, profile or workload measurement has run for this pilot. Production is restored to the measured saturated-keybuilder baseline after the inconclusive512-probe cache experiment. No subagents are used for this pilot.

This applies the report's indexed ValueSymbolLinks experiment with an explicit handle-cost control. It is a limited storage pilot, not a broad semantic-graph redesign or a prediction of multiple-times speedup. Numeric relation keys in the supplied report are stale: that earlier candidate has since been measured and reverted. Its architectural recommendations remain hypotheses to investigate.

## Three variants, with distinct attribution

1. The accepted unmodified compiler baseline, preserved with source/binary/build identities after the cache decision (source SHA25678b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337).
2. Allocation handles on binder/checker symbols, while retaining PointerLinkStore. This includes the new symbol field, allocator state, atomic block reservation and allocation-layout effects.
3. Exactly those handles plus sparse indexed ValueSymbolLinks. The final adoption comparison is3 versus1, not merely3 versus2.

handles.patch constructs variant2; indexed-over-handles.patch adds variant3; indexed-combined.patch is the combined source draft. All overlay files are formatted. Both base-applicable patches pass git apply --check. Focused validation is recorded below; it is not full compiler validation.

## Handle lifetime and domain

A private uint32 Symbol.linkIndex is assigned by ast.SymbolAllocator before publication. Binder.symbolArena and Checker.symbolArena become this allocator; their New calls and symbol initialization order remain unchanged. Both currently use only Arena.New. The wrapper retains the same typed core.Arena allocation/lifetime model. Other direct symbol allocations remain handle0 and use pointer-key fallback.

Handles are independent of ast.GetSymbolId and its lazy atomic counter. Each allocator reserves256-handle blocks using a separate atomic counter, then assigns within its exclusively owned block without further atomics. Blocks are process-unique and never recycled, including unused tails when a binder is pooled/reset. This is NOT a dense program-local semantic-ID space. Sparse radix storage allocates only touched regions; it never creates a slice through the largest observed handle. The first block is1, reserving0 as the unindexed sentinel. At32-bit exhaustion, the counter saturates and all later allocations remain unindexed; no wraparound reuse or semantic failure is introduced.

A handle is immutable after publication. Symbol already contains a non-copyable-after-use atomic field; production cloneSymbol explicitly constructs a new symbol rather than copying the header. Distinct symbols with a copied handle are nevertheless kept separate by checking the typed pointer key and falling back on a collision. Mutating an existing published symbol's private handle is outside the allocator contract; the compiler has no such mutation. Full source review must still check for whole-header replacement outside the two allocation sites before applying this design.

## Indexed storage and reachability

A checker-local store uses four8-bit radix components: a256-pointer root, lazily allocated directory and branch arrays, and256-entry leaf pages. Full uint32 extremes are supported. Published values remain separately arena-allocated and stable; growing the radix never relocates them. Each occupied leaf stores typed key and value pointers. A duplicate New allocates a fresh zero value; callers retaining the displaced value keep its complete typed allocation alive. No pointer is converted to an integer or reconstructed in this new store. The existing pointer fallback retains its original implementation/assumptions.

Lookup reads root/directory/branch/page and compares the actual key pointer. A copied-handle collision uses the existing PointerLinkStore; it does not replace the first symbol's indexed entry. Handle0 and nil symbols also use that fallback. TryGet/Has never allocate or reserve handles. Get on an existing entry is read-only. Concurrent mutation remains unsupported, matching existing checker ownership; post-population concurrent reads are covered by a prepared race fixture.

The ast.IndexedSymbolLinks wrapper reads the private handle and preserves Get/New/TryGet/Has call shapes. Checker-owned values are never published on shared symbols. The new typed pages preserve the old store's key/value reachability rather than retaining whole Program/Checker owners through backpointers. Sparse pages and arena siblings can still increase retention, which must be measured.

## Costs that the control must expose

- A new uint32 field likely rounds Symbol from96 to104bytes onamd64; this is source-layout arithmetic, not an executed size/allocation result. Actual size classes and slab memory need measurement.
- SymbolAllocator adds a cursor to its arena and reserves blocks atomically; short-lived binder owners waste unused handle slots. Lazy leaf pages can amplify sparse per-file usage.
- The indexed store has a2KiB root plus up to two2KiB metadata pages per new radix region and a nominal4KiB leaf for256 key/value pairs. Directory reuse reduces this for adjacent regions. These are nominal64-bit layouts, not allocator/RSS measurements.
- Lookup replaces hashing/probing with dependent loads, nil checks, decoding and a pointer-identity check. Bounds checks/inlining and actual callers must be inspected; no unsafe bounds-check bypass is planned.
- Fallback and indexed arenas coexist. Page occupancy and fallback frequency, plus retained values after API escape, must be observed separately from timing.

The old pointer-slot profile fraction was only1.33%–3.33% inclusive. This pilot cannot itself explain10×. Its value is evidence about whether an indexed access family can lower cost without consuming the saving in ownership/handle overhead; expansion requires a larger measured aggregate budget.

## Prepared tests and outstanding gates

New source fixtures cover lazy semantic-ID ordering, block boundaries and saturation, concurrent independent handle owners; sparse page/branch/root extremes, pointer-domain collision, nil/unindexed fallback, duplicate New and displaced values, read-only hits/misses, and GC retention across2048 key/value graphs. All six top-level fixtures pass in each of normal, race and checkptr overlay runs across core and ast, with no skipped or failed test records. Exact commands, file hashes and raw JSON logs are preserved in focused-validation/. Production source/HEAD remained unchanged throughout. These tests do not compile or exercise the modified binder/checker integration. Existing actual checker ValueSymbolLinks lifetime tests must remain enabled in the full validation.

Before promotion: complete integration review and actual symbol-wrapper/checker validation; run repository, full conformance, native/API/emission gates and separate race-instrumented CLI coverage because binder/checker allocation now crosses parallel ownership boundaries. Preserve all three builds, matching settings and exact source deltas. Inspect layout/codegen and diagnostic-only page occupancy; do not infer performance from them.

Use same-binary A/A variation to predeclare one confirmation protocol before examining confirmation results. Screen all four pinned workloads with identical wrappers/arguments/environment and peak RSS, then apply a declared practical gain/regression/memory rule. Inconclusive small effects are not promotion evidence. Run a contemporaneous original-native milestone rather than multiplying historical Go/Go ratios. Cross-process caches remain outside the fresh-process full-compilation benchmark contract.

The report's second architectural direction—cost-weighted cross-checker duplication—remains a separate diagnostic task. It should classify complete context and completion state without forcing lazy IDs/queries, leave cyclic/unresolved identities unclassified, and avoid adding overlapping inclusive costs. No shared semantic cache is proposed merely from object-count inflation.
