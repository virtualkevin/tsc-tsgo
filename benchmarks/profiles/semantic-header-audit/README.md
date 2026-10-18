# Semantic header feasibility audit

Source inspection after completed-heap-census rules out the initially proposed header/payload coallocation: TypeBase embeds Type, concrete payloads embed that base, and Checker.newType returns data.AsType(). There is already one concrete allocation, not a separately allocated header to remove. This agrees with the prior semantic-type-slab source audit; its rejection is unchanged.

StructuredType currently stores properties, signatures and indexInfos as ordinary three-word Go slices. A pointer-plus-length representation could nominally remove one word from each on amd64. This changes header storage, not pointer entries in the backing arrays or the semantic graph. No implementation was made. report.json gives explicitly hypothetical 24-bytes-per-construction arithmetic from the historical type census, including non-structured and transient types, alongside separately measured heap sample totals. It is not a retained-byte or allocator upper bound, a matched comparison, or a speed forecast. Size classes can change savings; decoder costs and backing storage remain unmeasured.

Compatibility constraints from actual source:

- StructuredType.Properties returns its stored slice directly. Signature public accessors clip capacity, but Checker.getSignaturesOfStructuredType returns slices without clipping.
- Anonymous-type resolution appends construct signatures to the stored signature list. Removing capacity changes reuse and can change alias-visible append behavior. A broad migration must audit consumers rather than assume all lists are immutable.
- setStructuredTypeMembers clips several lists, but alternate assignments do not uniformly establish this invariant. Pending-member materialization and base-member reuse assign property slices through additional paths.
- Nil and non-nil empty slices, existing backing-array identity, ordering, duplicates, and mutation remain observable. Packing lengths/capacities into uint32 needs a correct large-length path. Typed reachability cannot be replaced by integer-only addresses.

The current evidence does not justify a broad compact-slice migration as the next architectural optimization. No production code, performance table or accepted/rejected benchmark thresholds changed. Reproduce with `python3 -B benchmarks/profiles/semantic-header-audit/analyze.py`.
