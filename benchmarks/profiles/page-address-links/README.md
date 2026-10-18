# Allocation-page symbol link prototype: declined before integration

At capture HEAD80508d4, implemented an isolated Go-overlay storage prototype for the indexed semantic-access strategy in OPTI_ANALYSIS_01.md. Production source and binaries remain unchanged. No compiler workload timing or acceptance claim; PERF.md is unchanged.

The previous indexed-symbol design enlarged every Symbol, while the owned-symbol-links design added an interface and direct metadata. This experiment adds no fields to keys and does not reuse the lazily assigned, process-global Symbol ID. Neither earlier rejected design is revived.

## Mechanism and constraints

Allocate owned keys in typed arrays of256 elements. A directory indexed by address shifted16bits registers every region overlapped by each array. Each directory record contains a weak typed array reference and the integer base address. Lookup range-checks the scalar offset, upgrades the weak reference, and checks the resulting typed element pointer against the supplied key. Integer addresses never become pointers; runtime.KeepAlive preserves the supplied key throughout lookup. This inherits PointerLinkStore's pinned non-moving-heap assumption.

Foreign, nil and zero-sized keys use PointerLinkStore. Owned links remain absent until requested. Lazy per-page pointer slots refer to ordinary arena values; New replaces a value without invalidating published old pointers. A typed vector roots each linked owned key once. Unlinked displaced pages have only weak references. Keys do not contain links or directory pointers, so keeping a key alive does not itself retain its links/store. The current key page remains rooted, as with the original arena. Completed read-only access does not mutate the directory.

Costs include a builtin map lookup, weak-reference upgrade, range/divisibility and pointer checks, extra dependent loads, and lazy256-pointer arrays. Fixed-size pages overallocate initial key capacity relative to Arena's geometric growth. Directory records for dead pages are pruned only when registering a new page in the same region; otherwise dead metadata can accumulate for the store's lifetime. This prototype has no bounded-address-space memory guarantee. These costs would require end-to-end memory and timing assessment if the mechanism were promising.

## Evidence and decision

Five focused tests passed normally, with race instrumentation, and with checkptr=2: randomized differential operations against PointerLinkStore (including nil/foreign keys and replacement), displaced unlinked-key collection, linked-key and published old-value retention, concurrent read-only copied stores, and region-spanning/zero-sized cases. These are storage-contract tests, not full compiler correctness validation. No compiler integration was performed.

A normal-build mechanism microbenchmark uses96-byte pointer-free keys and56-byte pointer-containing values, approximating Symbol/ValueSymbolLinks sizes without pretending to reproduce their object graphs. Both stores hold the same keys simultaneously; a fixed coprime stride visits all keys. Five200ms observations per case, fixed pointer-then-page order, allocations excluded from lookup timing. CPU Intel Xeon Cascadelake, Go1.26.9, amd64, observed Go benchmark GOMAXPROCS8. This is not the controlled four-workload benchmark contract and gives no end-to-end speed ratio.

| Keys | Pointer store median ns/lookup | Page directory median ns/lookup |
|---:|---:|---:|
|256|8.966|21.71|
|65536|96.86|162.5|

Every observation reports zero allocations per lookup. With no observed lookup advantage and added metadata/allocation costs, decline compiler integration. Do not infer that all indexed designs are slower, or that this proves a full compiler regression. No extra samples or tuning were used to rescue this prototype. Future work needs a distinct mechanism that avoids both per-symbol size growth and this directory/weak-reference lookup overhead.

`validate.py` freezes source/controller hashes, records normal/race/checkptr test events, and runs the bounded microbenchmark. Output files are exclusive; it intentionally refuses to overwrite evidence. `python3 benchmarks/profiles/page-address-links/verify.py` independently reads raw events, validates expected tests and source hashes, and reproduces summary.json. Absolute overlay paths describe this workspace. manifest.json hashes all archived files except itself.
