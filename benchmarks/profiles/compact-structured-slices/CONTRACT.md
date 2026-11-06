# Structured-type slice representation contract

Baseline: retained source216d40c7/defaultbinary8fe4bd80. Correctness oracle remains
pinned upstream Go2bd066d8. Performance target remains original native525c0fe9,
not the retained Go build. The previous tiled template relation candidate stays
rejected; this candidate has no relation-cache changes.

Only StructuredType.properties, signatures and indexInfos change representation.
Every original read reconstructs the same ordinary slice header; every assignment
stores the computed header. No element copy, capacity clipping beyond existing
sites, changed semantic query, new memoization, ordering change, or ID assignment.
Original aliases remain aliases, and copied headers retain independent lengths
and capacities. Public Properties remains un-clipped; public signature methods
retain their existing Clip calls. Internal signature slicing remains un-clipped.
The anonymous-type append and all pending-member publication sites retain their
original evaluation order and allocation/reuse decisions.

The storage invariant is specified in ../compact-slice-header/README.md. Direct
shape stores exact uint32 length/capacity and a GC-visible pointer into the original
array; indirect shape owns an immutable ordinary header. Both decoding paths
convert back to the original pointer type. No uintptr representation or pointer
arithmetic. The ordinary path must allocate zero headers, including when inlining
is unavailable. No concurrently mutable header API is introduced. Retaining a
copy retains the same backing graph as a slice copy, including original capacity.

Source adaptation: six existing files, storage implementation and focused test
file. changes.json records all35 selector/write line adaptations; source-audit.py
replays them plus three field declarations, verifies the storage implementation
matches the tested prototype modulo names/package, and verifies corresponding
baseline test histories. Textual reproduction is not proof of semantic coverage;
compiler typechecking, pending-member tests, full conformance and API/emit parity
remain required. CompositeSignature.signatures and inheritedPendingMembers.properties
remain ordinary slices because they are distinct representations.

Assurance: standalone eight tests each normal/race/checkptr, seeded header
histories, actual large zero-sized slices, ordinary/indirect graph retention and
zero-allocation regression passed. Five SMT packing-model claims passed; no proof
of the Go frontend/runtime/GC or compiler equivalence is claimed. Tests exercise
selected histories rather than all possible client operations. Do not weaken
oracle checks, limits, diagnostics, identity or lifecycle requirements.

Potential benefit:24nominal header bytes removed per StructuredType on amd64,
including its embedding object types. Actual allocator size classes, transient
versus retained object populations and workload effect are not established by
this arithmetic. Element pointer arrays are unchanged. Added decoding/bounds
checks and rare fallback allocation can offset footprint savings. No speedup is
claimed before pinned correctness, normal production build provenance and frozen
four-workload performance/memory gates pass.
