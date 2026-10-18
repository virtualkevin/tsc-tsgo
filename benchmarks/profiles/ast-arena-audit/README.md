# AST arena allocation audit

After three rejected sparse-property approaches, this investigates the broader storage/GC hypothesis in OPTI_ANALYSIS_01.md using retained normal profiles. No compiler optimization or new benchmark was run. The four original heap profiles and archive are hash-verified before decoding with pinned Go1.26.9 pprof and retained binary8fe4bd80. The first capture attempt used the manifest-relative archive member name without the node-pointer-normal/ prefix and failed before decoding; the corrected capture handles that prefix.

Each sampled allocation with an Arena frame is counted once, attributed to its innermost arena operation and nearest outer project caller after contiguous Arena wrappers. Only owners in internal/ast qualify as AST-owned arenas; other AST allocations are excluded. Six analyzer tests cover attribution, wrappers/inlining, non-arena exclusion, non-AST ownership, multiple samples and missing location rejection. Exact report reproduction passes.

| Workload | AST arena allocation objects % | AST arena allocated bytes % | AST arena profile in-use bytes % |
|---|---:|---:|---:|
| TypeORM | 4.069 | 22.001 | 30.265 |
| tRPC | 10.720 | 51.097 | 61.355 |
| VS Code | 5.960 | 39.347 | 46.952 |
| Sentry | 3.244 | 16.332 | 26.947 |

These are sampled cumulative allocation estimates, not exact counts, CPU shares, peak RSS, final-GC retained heap, or removable runtime. Profiles were collected without a final forced GC and may omit recent allocations. AST-owned arena is a subset of arena storage, not an additional category to add to it. Identifier construction is the largest AST arena byte owner in every workload: about534.82MiB on VSCode and241.15MiB on Sentry. This supports auditing representation across phases; it does not establish a performance gain.

## Source ownership findings

Arena.New allocates a fresh typed slab at capacity; it does not copy published objects when growing. Growth doubles to a256-element ceiling. An interior pointer keeps its containing typed slab and sibling pointer graphs reachable. Changing slab size therefore changes retention as well as allocation overhead; the previous semantic-type slab rejection remains relevant and this audit does not propose retuning it.

NodeDefault embeds Node; concrete generated AST types embed the corresponding bases. newNode obtains the already-embedded Node from data.AsNode(), then stores the concrete value as a nodeData interface on that header. Identifier creation allocates one concrete arena slot, not a separate Node header allocation. The interface points back into the same concrete object. Generated AsIdentifier and other accessors perform checked type assertions; nodeData also dispatches traversal/cloning/field access. A compact replacement must preserve concrete type discrimination even if Kind is changed and cannot simply derive all type identity from Kind. GetNodeId uses a lazy atomic process-global ID, so removing or narrowing it needs separate overflow/identity/concurrency analysis. TextRange already uses two int32 positions.

Next: use the measured layout output to identify a concrete representation change with an explicit ownership and API compatibility proof, then inspect CPU attribution/GC scanning before proposing any runtime gain. No new cache, unsafe conversion, slab policy or compiler source change is adopted by this audit.

Measured amd64 layouts: Node 48 bytes, Identifier 72 bytes, PropertyAccessExpression 88 bytes, CallExpression 96 bytes, Symbol 96 bytes, NodeFactory 1192 bytes. The layout harness passed; its initial report parser failed on chunked Go test output. Fixed output reassembly decoded the preserved passing log without rerunning tests. The temporary harness was removed by finally cleanup. layout.json records field offsets, sizes and kinds; it is not a runtime GC bitmap.
