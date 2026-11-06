# Capacity-preserving compact slice header prototype

A distinct follow-up to semantic-header-audit: retain capacity and backing-array
identity while reducing a three-word slice header to two words on amd64. This is
standalone storage code, not yet a production optimization or performance claim.

The ordinary shape packs uint32 length and capacity into a uint64. A GC-visible
unsafe.Pointer retains the original backing allocation, including an interior
slice offset. No uintptr addresses, pointer arithmetic, decoder table, global
roots, semantic cache, element copying or pooling. Nil and non-nil empty slices
remain distinct. Values reconstructs exactly the original length and capacity;
append, three-index slicing and header copies retain ordinary slice behavior.

If capacity exceeds uint32 or both length and capacity equal uint32 maximum,
all-ones shape identifies an immutable ordinary slice header allocated by a cold
helper. That fallback preserves all representable Go slice sizes. Tests use real
zero-sized-element slices at and beyond the boundary, without forged headers or
huge backing allocations. The sentinel pointer always converts back to *[]T;
ordinary pointers always convert back to *T. Invalid hand-built representations
are outside the private constructor contract. Concurrent header/element mutation
requires ordinary slice synchronization; only published read sharing is tested.

Initial six tests passed normal/race/checkptr. Escape analysis then exposed an
ordinary-path allocation caused by the fallback taking the parameter's address.
An added regression reproduced one allocation per conversion. The initial source,
validation and failing allocation test are preserved under initial/. Separating
allocation into a noinline cold helper fixes that regression: final eight tests
pass in each mode, including zero ordinary conversion allocations, 131,072 seeded
header operations, backing aliases/append, copies across GC, indirect graph
retention and concurrent reads. The first archive command used the wrong cwd and
failed before changing any files; rerunning from the repository root succeeded.

Five Z3 4.15.4 bitvector claims prove packing round trips, injectivity, sentinel
exclusion and zero-shape identity; a false extraction rule returns sat. These are
model results, not a verified translation of Go, GC proof or compiler equivalence.
The implementation/source hash is recorded explicitly. The local Go 1.26.9
unsafe.go contract and https://pkg.go.dev/unsafe#SliceData were reviewed.

Next integration target is only StructuredType's properties, signatures and
indexInfos headers. Preserve all publication sites, append capacities, pending
materialization, public identity and nil/empty behavior. Three headers nominally
save 24 bytes per StructuredType on amd64, not 24 bytes per every Type allocation.
Allocator classes, fallback allocations, extra decode instructions and GC effects
must be measured; backing pointer arrays are unchanged. Existing historical type
counts do not establish retained bytes or an end-to-end gain. Full correctness,
normal-build provenance and frozen workload gates are still required. Production
remains retained; PERF.md has no new rows, and the 10× native goal is unmet.
