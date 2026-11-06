# Instantiated-symbol storage contract

This is a reviewed refinement argument plus executable tests, not a machine-checked or whole-compiler proof. The implementation is isolated by overlay.json; production remains retained Go.

## Supported transition

The changed call is newInstantiatedSymbolWithLinks. If the input is already instantiated, the existing target selection and mapper composition run first, unchanged. Argument evaluation, symbol-count increment, transient flags and name assignment retain their original order. The candidate allocates one typed record containing a symbol and zero-initialized links instead of obtaining them from two separate arenas. Intervening assignments of CheckFlags, Declarations, Parent and ValueDeclaration perform no semantic callback. The candidate publishes the two pointers to the same authoritative table at the old New call site, then writes target, mapper and nameType in the original order.

Relate reference and candidate states by a bijection between corresponding new symbol identities and links identities, equal visible symbol fields, equal links fields under that bijection, equal SymbolCount and equal table associations. The new symbol is fresh and cannot already be present in the table. Its links remain unpublished until the original insertion point. No memoization, callback elimination, type reuse, diagnostic suppression or change to resolution order is introduced. Type counts, IDs, resource-limit checks and mapper-composition operations are untouched.

Allocation failure and allocator/GC scheduling are outside this logical transition argument. Allocation occurs earlier for the links portion, and memory residency can change. Test agreement is limited to executed cases.

## Install container operation

Install accepts a typed key (including nil) and a nonnil typed value. It publishes exactly that value pointer; it does not zero, clone or allocate a replacement value. On a missing key it increments cardinality once, growing at the same 75% threshold as the retained implementation. On an existing key it replaces the association without changing cardinality. Growth preserves every stored pointer. Nil value is rejected before state mutation because nil is the table's empty-slot marker. Published old values remain valid when separately rooted. New and Get remain unchanged and interoperate with installed values.

The constructor is the only production caller introduced by this overlay and always supplies fresh zero-valued storage. Install is not a general license to share mutable links between checkers. Typed roots and the retained pointer hash/probing implementation are unchanged; the existing non-moving-runtime assumption still applies. Mutation requires exclusive ownership. No weak pointer, integer-only owner, unsafe pointer reconstruction, reset or pool is introduced.

## Lifetime difference requiring measurement

An interior pointer to either record member keeps the complete slab alive. An escaped instantiated symbol can now retain its links and transitive type/checker graph. A later replacement retains the old embedded links as long as the original symbol remains live, even if the table points elsewhere. This is an intentional storage consequence, not identical reclamation behavior. It may negate locality benefits or make this representation unsuitable for long-lived API clients. CLI RSS gates cannot prove arbitrary API-client memory equivalence.

The record is 152 bytes on this amd64 toolchain: 96 symbol plus 56 links, with no payload saving. Two independent arena growth streams become one for these pairs; actual allocator size classes, page occupancy, GC scanning and live graph retention remain workload-dependent. No smaller-heap or lower-allocation forecast is inferred from layout alone.

## Evidence and remaining gates

The exact inverse source audit checks the checker field and constructor edits. Focused candidate tests cover table growth, nil keys, replacement, nil-value rejection, New interoperability, nested instantiation, flags, counters and resolved identity. Existing tests cover actual instantiated graphs over many slab/table growths and GC, published links surviving replacement, differential table histories and completed concurrent reads. The constructor history is also run on retained Go, differing only in layout logging. Normal, race and checkptr modes are verified from raw logs.

Full compiler/services/conformance, normal and instrumented CLI parity, API/emit/project integration, standard build provenance, restored production identity and fixed matched workload measurements remain required before promotion. Refer to validation reports for completed versus pending stages. Passing this contract's tests does not establish the requested 10× speedup.
