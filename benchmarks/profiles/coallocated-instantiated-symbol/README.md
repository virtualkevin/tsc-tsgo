# Coallocated instantiated symbols: isolated prototype

At retained production b6874c0, this five-file Go overlay stores the symbol and its mandatory ValueSymbolLinks together in a typed arena record. Only newInstantiatedSymbolWithLinks uses this representation. All later lookup still uses the retained PointerLinkStore, which keeps both pointers as typed GC roots. No Symbol fields, global IDs, pointer decoding, interface metadata, cache keys, semantic queries, or runtime settings change.

This tests locality and allocation grouping across a concrete storage boundary. Unlike the rejected owned-symbol-links experiment, it adds no ownership interface to every symbol and does not replace table lookup with metadata dispatch. Unlike the rejected semantic-type-slab experiment, both members are already created together and linked by an authoritative table entry. Neither distinction establishes a speedup; the previous rejected candidates remain rejected.

The prototype preserves symbol count increment, visible field construction, mapper composition and the link publication point. Record allocation happens earlier than the old separate links allocation, before the intervening symbol field assignments; none of those assignments invokes a semantic callback. Install rejects nil before mutation, preserves duplicate replacement and typed key/value ownership, and follows the existing growth threshold and probing algorithm. Existing New/Get behavior is unchanged. An exact inverse source audit restores checker.go byte for byte; it is not a semantic proof.

## Lifetime and concurrency contract

Each member pointer now retains its sibling and the whole containing slab. A symbol escaping the checker can therefore retain its links and potentially the checker graph through a resolved type. Replacement also leaves old embedded links retained by the original symbol. This is a real retention cost, not a correctness proof or a free ownership optimization. Slabs are never reset, recycled or decoded from integer addresses; old published pointers remain valid. Only the current slab is rooted directly by the arena; the table roots all installed symbols and links. Mutations remain checker-exclusive. Published table reads keep the existing concurrency contract.

The focused suite runs the existing PointerLinkStore and actual checker graph/replacement tests, plus supplied-storage growth/replacement/nil-key/failure-atomicity and constructor/nested-instantiation identity checks. Normal/race/checkptr validation is in progress; see validation.json and raw logs for authoritative status. Full compiler, pinned conformance, CLI, API/emit/project validation and matched workload measurements are still required. No candidate binary is promoted and no PERF row is warranted.

This is a storage research prototype, not an established route to the requested 10× native-relative improvement. Production files and the default binary remain unchanged.
