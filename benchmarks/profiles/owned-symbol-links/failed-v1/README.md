# Direct links for checker-owned symbols: prototype

Experimental source at base `fe9be52`, not promoted or measured. This tests the semantic-access strategy in OPTI_ANALYSIS_01.md without global IDs or a radix decoder. The previous indexed-symbol experiment failed its confirmation; this is a distinct direct ownership mechanism, not a retuning of its pages or handles.

`ast.OwnedSymbolLinks[V]` allocates checker-created symbols and immutable metadata together in typed arena records. A private interface on Symbol identifies that metadata. The metadata has a unique nonzero-sized owner token, exact symbol pointer, and lazily allocated value pointer. Owner tokens do not point back to the store/checker. Other symbols, nil keys, foreign-owner symbols, and distinct pointers with copied metadata use the retained PointerLinkStore. Shared binder symbols are not mutated by checker lookups.

Allocation alone preserves Has=false/TryGet=nil. Get creates the first zero value. New always creates a fresh zero value and replaces only the current pointer; previously published values remain valid through ordinary typed roots. Values remain separately arena-allocated. Metadata key/owner/interface fields are immutable after publication; only the owning store reads or changes its value field. The foreign-reader/owner-writer race test checks that boundary. Completed stores support concurrent reads as before; concurrent mutation of one store is unsupported.

## Costs and lifetime limits

Symbol gains a 16-byte interface on amd64, including binder-created symbols that do not use direct links. A checker-created record adds three pointers (owner/key/value) beyond that larger symbol. The owned path removes a pointer-table entry but adds a dynamic type check, owner/key checks and a dependent metadata load. The fallback and owned value arenas coexist. No footprint or speed improvement follows from source layout alone.

A symbol now roots its current value links. A populated links graph may lead back to Type.checker and retain more semantic state after a symbol escapes. The owner token itself avoids an unconditional checker backpointer, but does not eliminate this new retention path. Typed arena siblings also affect retention. Existing CLI RSS gates and API correctness tests are necessary, not a proof of identical arbitrary-client memory lifetimes. No pointer reconstruction, unsafe production access, phase reset or global decoder is added.

Known API serialization uses explicit SymbolResponse fields (`api/session.go:newSymbolResponse`, `api/proto.go:SymbolResponse`), not the new private metadata. `cloneSymbol` constructs a fresh symbol and copies selected public fields; it does not copy ownership. Private fields are omitted by ordinary encoding/json. These source observations do not replace complete validation or prove all reflection consumers compatible.

## Validation and acceptance

Three new AST tests cover lazy absence, owned/fallback/nil keys, foreign owners, copied metadata, replacement/GC, growth with concurrent completed reads, and foreign reads during owner writes. The two existing actual-checker ValueSymbolLinks lifetime tests remain included. Normal, race, checkptr and expanded unit validation are running with fixed source/HEAD; build is running separately. Full conformance, CLI/API/emit/services and instrumented CLI controllers are prepared but not yet launched.

No timing until validation completes and production source/default binary are restored with hashes checked. Use the existing frozen nine-small/five-large alternating-pair screen with both aggregate ratios >=1.01, every workload summary >=0.98 and median RSS <=1.05 baseline. A passing screen needs two independent 19/11 confirmations, second reversed roles, each passing independently. A failed screen receives no extra samples, payload/layout/owner-check retuning or pooled rescue. Any accepted result needs a fresh original-native milestone; no multiplication of historical ratios. The 10× native-relative goal remains unmet.
