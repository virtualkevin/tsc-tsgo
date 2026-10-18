# Direct links for checker-owned symbols: validated candidate

Candidate source `60633bf2`, binary `846238805dd7dc4701e740b00a978fc3e3d5be3559b85f2c5d4d32cf57fc282e`, sidecar `81eb106d2bb55ffca334294acee0db54d8d316957597a1c14ad7c2cec6530d9c`. Correctness validation is complete; workload performance is unmeasured. Production source `216d40c7` and default binary `8fe4bd80` are restored. The preserved candidate has not been promoted.

This tests the semantic-access strategy in OPTI_ANALYSIS_01.md without global IDs or a radix decoder. The previous indexed-symbol experiment failed confirmation; this direct ownership mechanism does not retune its handles or pages.

## Representation and ownership

`ast.OwnedSymbolLinks[V]` allocates checker-created symbols with immutable metadata in typed arena records. A private interface on Symbol identifies that metadata, which contains a unique nonzero-sized owner token, exact symbol pointer and lazy value pointer. The token does not point back to the store/checker. Shared binder symbols, foreign-owner symbols, nil keys and distinct pointers carrying copied metadata use the retained PointerLinkStore. Checker lookups never mutate shared symbols' metadata.

Allocation alone preserves Has=false/TryGet=nil. Get creates the first zero value. New always creates a fresh zero value; previously published values remain valid through ordinary typed roots. A typed key vector retains each owned key exactly once when links are first created, matching the old table's key-root contract. Unlinked keys are not added; replacement adds no duplicate root. Values remain separately arena-allocated.

Metadata key/owner/interface fields are immutable after publication. Only the owning store reads or changes its value field; foreign stores use their own fallback. Completed stores support concurrent reads. Mutation requires exclusive ownership, as before. No pointer reconstruction, unsafe production access, phase reset or global decoder is added.

## Costs and lifetime limits

Measured amd64 layout: Symbol112 bytes, owned record136, metadata24. The private interface adds16 bytes to every Symbol, including binder symbols. The key vector adds an eight-byte pointer per linked key plus capacity. Direct lookup avoids a hash-table entry but adds a dynamic type check, owner/key checks and dependent metadata load. Owned and fallback value arenas coexist. These costs require end-to-end timing and RSS measurement.

A symbol now roots its current links. Populated links can reach Type.checker and retain more semantic state after a symbol escapes. The token avoids an unconditional checker backpointer, but does not eliminate that new retention path. Typed arena siblings can also affect retention. CLI RSS checks and API correctness tests do not prove identical arbitrary-client memory lifetimes.

Known API serialization uses explicit SymbolResponse fields in api/session.go and api/proto.go. cloneSymbol constructs fresh ownership and copies selected public fields. Private metadata is omitted by ordinary encoding/json. The hash-recorded boundary review does not prove compatibility for every reflection consumer.

## Validation and preserved failure

- Focused normal, race and checkptr: five tests each passed, including the two existing actual-checker graph/replacement lifetime tests.
- Expanded units:21,149 test records across12packages, no failures or skips; includes parser fuzz seeds from the pinned TypeScript fixture.
- Full conformance:14,915 configurations;12,789 fully checked,8partial with inherited output skips,2,118unsupported,0failures.
- Services:219 records/60top-level tests passed, plus the known package with no tests.
- Normal CLI:80 parity cases; API/emit/project:12 cases; all passed without skips.
- Instrumented CLI:80race and80checkptr cases passed without failures or skips.

The first prototype failed the existing graph-retention test: core.Arena roots only its current slab, so direct metadata alone lost older symbols previously rooted by table entries. This was a real ownership bug. `failed-v1/` preserves its source, controllers, four passing/one failing focused results, and deliberately cancelled build/conformance logs with verified hashes. No timing samples were collected. The typed key vector repairs that contract; the original failing checker test was not weakened or changed. Fresh full validation ran on the repaired source.

The successful archive contains27rawfiles,7,589,595compressed bytes. Every archived member was read back and hash-verified. `restore.mjs` verified all five validation reports, exact four-file source delta (two modified/two added), archived added-file bytes and preserved binary identities before restoring production. Restored preflight passes with identical build settings and the intended source differences.

## Generated code and performance gate

`codegen.py` checks both executable hashes and preserves three representative callers. Instruction bytes baseline/candidate: getTypeOfInstantiatedSymbol180/180, newInstantiatedSymbolWithLinks559/560, getTypeOfMappedSymbol1147/1147. Calls switch from PointerLinkStore Get/New to OwnedSymbolLinks Get/New. Counts exclude out-of-line store bodies, data footprint and cache/GC behavior; they establish neither equal cost nor speedup.

The frozen comparison policy uses nine alternating pairs for TypeORM/tRPC and five for VSCode/Sentry, one warmup, fresh processes, default settings and matched RSS. Both aggregate ratios must reach1.01; every workload summary must reach0.98; median RSS must stay within1.05baseline. Passing requires two independent19/11confirmations, second reversed roles, each passing separately. No post-failure samples or payload/layout/owner-check retuning. An accepted change requires a fresh original-native milestone. The10×native-relative goal remains unmet.
