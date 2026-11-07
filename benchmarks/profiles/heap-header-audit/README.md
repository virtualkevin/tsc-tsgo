# Allocation header attribution

Tested hypothesis: fixed-size typed arrays could avoid dynamic bitmap setup
performed by the current Arena's slices.Grow allocation. Source inspection
rejects that mechanism. In pinned Go 1.26.9, heapSetTypeSmallHeader writes one
type pointer at runtime/mbitmap.go:737. There is no bitmap reconstruction loop.
The small scanned-object allocator in runtime/malloc.go zeros memory when
required, then calls this helper for the header. A fixed pointer-bearing array
of the same allocation class would still require a header.

Verified profiles attribute all flat samples in this helper to that store:
TypeORM 3.69 CPU seconds, tRPC 1.70, VS Code 44.25, Sentry 10.19. These are
sampled CPU attribution, not wall time, removable costs or identified hardware
stalls. VS Code's overall lostProfileEvent share is 1.62%. Source line attribution
cannot distinguish cache/TLB misses, faults, scheduling perturbation, or sample
skid. Hardware counters were previously unavailable; do not infer a cause.

The first interactive pprof command lacked source_path and reported that trimmed
runtime/mbitmap.go was unavailable. The reproducible capture supplies the pinned
runtime source path, rejects missing-source output, checks all input profile
hashes, and records runtime source/toolchain/output hashes. Four captures passed.

Decision: do not implement the proposed fixed-array replacement on the premise
of avoiding bitmap reconstruction. Reducing actual allocation volume or pointer
scanning still merits investigation, but the current AST arena already allocates
typed stable pages, and prior slab/compact-node experiments must be considered.
No production change, new performance measurement, or PERF row.
