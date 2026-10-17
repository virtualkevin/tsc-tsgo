# Small keyBuilder: code generation and allocation screen

All work is terminal. No compiler rebuild, workload profile, or benchmark was performed by this audit. Parent-built candidate: dist/tsc-go-small-keybuilder, SHA9d87e9195e65a2113fec862d702faa313b51749c171cf92ddc6756eda0719b85, source4937cfc277515b8b566162d078dd493524d406de94ced593a78f38bbd6c7aa5d (5152 files). Baseline is preserved pointer binary b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322.

summary.json records exact commands/hashes/build metadata. source-comparison.json verifies equal Go1.26.9 linux/amd64/v1 trimpath/no-PGO build settings. Only checker.go and the added keybuilder.go differ in production; three test files are added (keybuilder, relation API, JSX managed-attributes error regression). The CommonJS transformer is identical.

## Actual production code

| Function | Baseline frame bytes | Candidate frame bytes |
| --- | ---: | ---: |
| getTypeListKey | 1216 | 176 |
| getIndexedAccessKey | 1208 | 192 |
| getConditionalTypeKey | 1224 | 176 |
| getRelationKey | 1240 | 208 |
| instantiateTypeWithAlias | 1680 | 648 |

These are explicit SUBQ reservations from targeted objdump, not peak stack usage, RSS or speed measurements. In the inspected builders, the old1184-byte zeroing loop becomes nine16-byte stores (144 bytes). Production callers pass stack addresses for their local builder; there is no runtime.newobject for that builder. The overflow helper alone allocates a Hasher using runtime.newobject and publishes its pointer with a write-barrier path. Existing semantic work within callers can still allocate independently.

The candidate's hash (98 code bytes), stream (165), writeBytes (234), writeString (218) and writeByte (133) remain out-of-line functions. Integer writers have no standalone symbols and their operations appear inline at callers, followed by a CALL to writeBytes. The short writeBytes/writeString branches call runtime.memmove; the byte writer uses a direct store but remains a CALL boundary. Therefore the smaller zeroing/frame is accompanied by real helper-call/copy overhead, not a fully inlined fast path.

The hash helper branches on overflow: the short branch calls xxh3.hashAny128 directly after a bounds check; the long branch calls Hasher.Sum128. Stream calls Hasher.updateString once for the prefix, and each subsequent overflow write uses streaming updateString. There is no numeric relation interner, key truncation, or changed relation-map representation.

## Exact-source allocation screen

allocation-screen/keybuilder.go is byte-for-byte the production file and its sidecar hash, verified before/after. The screen adds only a CacheHashKey type alias, pinned dependency module and tests. Inputs/maps are prepared outside each AllocsPerRun call. Two authorized small-package test commands passed; the second requested -m=2 solely for this tiny package. It did not rebuild the compiler or emit checker-wide diagnostics. Exact commands/toolchain/environment/results are in allocation-summary.json; raw logs are allocation.log and escape.log.

51 subcases,1000 measured calls each:

- String, byte-slice and bytewise modes at lengths0,5,13,64,127,128:0 allocations per call.
- The same modes at lengths129,256,1089,4096:1 allocation per call.
- Repeated hash-only queries after builder setup:0 allocations for all lengths.
- A13-byte indexed-key construction plus existing map lookup:0 allocations and the expected cached value.
- Legacy embedded streaming Hasher screen:0 allocations for all tested lengths. Thus overflow introduces an observed allocation, not just a theoretical escape concern.

The small-package escape log explicitly reports builder/data/string parameters do not escape; new(xxh3.Hasher) escapes. The stream receiver's contained pointer leaks to its return (dereference level1), not the receiver object itself. Hash/stream/writeBytes/writeString/writeByte exceed the inlining budget, while uint32/uint64 writers inline. These screen findings agree with actual production symbol/call/frame evidence; they do not prove every compiler caller has zero allocations or establish workload spill frequency.

AllocsPerRun measures allocation counts only; no ns/op or throughput benchmark was requested. It temporarily sets GOMAXPROCS to1 internally, and ran outside a quiet benchmark window. Long allocations contain a nominal1184-byte Hasher; allocator rounding/actual bytes were not measured. No compiler speed, aggregate heap/RSS, GC savings or peak-stack claim follows from this screen. Full conformance/native validation and paired workloads remain the parent's separate acceptance gates.
