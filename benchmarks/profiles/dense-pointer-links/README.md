# Dense typed roots with numeric probe slots: declined pilot

CaptureHEAD079c033; production remains source216d40c7/defaultbinary8fe4bd80. This isolated core-package overlay tests the indexed-storage/GC direction of OPTI_ANALYSIS_01.md without changing AST/Symbol layouts, IDs, semantic queries or compiler integration. It is distinct from explicit symbol handles, owner interfaces and weak allocation-page lookup. No earlier rejected implementation is reinstated.

## Representation

The current PointerLinkStore has16-byte key/value pointer entries in every probe bucket onamd64. This prototype uses4-byte uint32 probe slots (dense index plus one, zero empty) and a separate typed key/value vector. At each table growth, the vector reserves precisely75%of bucket capacity, matching the existing load threshold. Nominal backing bytes are unchanged:4C+16(.75C)=16C. Typed pointer slots decrease from2C to1.5C. Slice headers, allocator rounding, transient growth allocations and the checker/store header are excluded; no heap-scan or GC-time reduction has been measured.

Every linked key and current value remains a typed root. Values use the retained ordinary arena; growth copies only entry pointers, never published values. DuplicateNew replaces with a fresh zero value while prior published values remain valid. Nil keys remain supported. Uint32index and native-int capacity growth have explicit overflow guards. Both guards are source-reviewed; impractically large allocations are not exercised by tests. Lookup now loads a numeric slot, checks the dense key and loads the dense value, adding dependence and bounds checks. Growth allocates two backing arrays. There is no deletion or key eviction.

The one-way address hash remains exactly the production helper, inheriting its pinned non-moving-heap assumption. No integer-to-pointer reconstruction, unsafe key owner encoding or shared metadata mutation. Writes require exclusive ownership; populated copies are read-only aliases, as with the original arena-backed store.

## Validation and bounded measurement

Validation71937 completed normally. Four tests each passed normal/race/checkptr=2: randomized differential operations against PointerLinkStore, old-value/key graph retention across GC and growth, completed concurrent reads, and nil/collision/growth handling. The differential test also checks cardinality, matched bucket capacity and nominalamd64layout arithmetic. These are storage-contract tests, not full compiler validation.

The normal-build lookup microbenchmark uses96-byte pointer-free keys and56-byte pointer-containing values. Both stores hold the same keys at once; a fixed coprime stride visits every key. Five200ms observations per case, fixed pointer-then-dense order. Allocation/setup excluded from timing. Go1.26.9/amd64, Intel Xeon Cascadelake, observed benchmarkGOMAXPROCS8. All observations report0B/lookup and0allocations/lookup.

| Keys | Pointer store median ns/lookup | Dense-root store median ns/lookup |
|---:|---:|---:|
|256|9.142|12.29|
|65536|81.93|94.55|

Decline compiler integration: no lookup advantage was observed, nominal backing storage did not shrink, and GC savings remain unmeasured. The fixed-order microbenchmark has noticeable variation and does not prove a compiler-wide regression or rule out GC benefits. The25%figure applies only to this table's reserved pointer slots, not the entire heap or runtime. No extra measurements, retuning, full-workload benchmark, promotion or PERF.md rows follow this pilot.

validate.py freezes source/controller hashes, saves rawGo test events and bounded benchmark output. verify.py independently checks source hashes, all expected tests and every raw lookup row and reproduces summary.json. Absolute overlay paths describe this workspace. Outputs are exclusive and cannot be silently overwritten. manifest.json hashes all archived files except itself. No new standalone dependencies were needed.
