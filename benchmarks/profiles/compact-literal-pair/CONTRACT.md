# Compact literal-pair refinement contract

Candidate only. Production remains unchanged. This is a reviewed representation argument and focused tests, not a whole-compiler proof or measured speedup.

The old LiteralType holds an arbitrary literal value and two pointers. Every production write to the pointers is in newLiteralType, boolean initialization, computed-enum initialization, or getFreshTypeOfLiteralType. Preserve those write sites and their order. The generic newType constructor, TypeCount/ID allocation, symbol assignment, flags, payload, interning maps, and tracer call remain unchanged.

Use one partner pointer and three bits of private metadata in existing Type header alignment padding. No pointer tagging, integer addresses, ID decoding, global roots, or changed exposed TypeFlags/ObjectFlags.

| State | Metadata | Partner | Old RegularType | Old FreshType |
| --- | --- | --- | --- | --- |
| Zero/uninitialized | 0 | nil | nil | nil |
| Regular allocated | 1 | nil | canonical self | nil |
| Regular linked | 1 | fresh | canonical self | fresh |
| Fresh allocated | 3 | regular | regular | nil |
| Fresh linked | 7 | regular | regular | canonical self |

Canonical self is `data.AsType()`, not the address of the accessor receiver. This preserves accessors on copied exported LiteralType values and copied Type headers. The existing TypeData interface strongly retains the canonical object. Both pair directions remain strong pointer edges. No whole-checker lifetime or permanent decoder is introduced.

The allocated-but-unlinked fresh state is intentionally separate. `newType` can call tracing before newLiteralType initializes the pair metadata, just as before the original regular pointer assignment; accessors remain nil at that point. A fresh self-link write validates that the written pointer is canonical self. Every production write satisfies this by construction. Regular writes preserve their actual partner, including nil if exercised privately.

Expected amd64 layouts: Type remains 56 bytes; LiteralType shrinks from 88 to 80 bytes (runtime allocation size-class savings must be verified separately). This adds state branches and canonical-self dispatch to accessors. It may lose runtime despite saving storage. No performance claim follows from sizeof or count profiles.

Before promotion: source write/read audit, state transitions and copied-value tests, allocation count/identity/GC tests, normal/race/checkptr validation, broader compiler and pinned-oracle API/CLI/emit/conformance checks, provenance build, fixed matched performance screening and confirmations. Performance policy is the repository's existing four-workload policy; no relaxed thresholds. The 10× native-relative objective remains unmet.
