# Saturated key-builder length: production codegen and allocation

All three primitive writers now inline in the inspected production binary. The previous direct-writer candidate emitted calls to these helpers; the saturated candidate emits direct byte/integer stores in callers, retaining cold overflow calls. This establishes the intended code-generation change, not a compiler speedup.

Baseline is preserved `tsc-go-keybuilder-direct` SHA61313d4e…; candidate is `tsc-go-keybuilder-saturated` SHA2bdcca53…, source78b76607…. Exact binary, sidecar and source hashes, toolchain settings, commands and assembly hashes are in `capture.json`. Their source manifests differ only in production `keybuilder.go` and updated `keybuilder_direct_test.go`. Build settings match: Go1.26.9, Linux/amd64 v1, trimpath, no PGO or extra flags. Main was not changed; this inspection did not rebuild either compiler.

## Inlining and remaining checks

The tiny exact-source package reports inline cost76 for each primitive writer, below budget80. Production confirms the result independently: writeByte/writeUint32/writeUint64 no longer have emitted symbols, while overflow methods remain. `getIndexedAccessKey` contains direct MOVL stores; `getRelationKey` has inline byte and uint32 writes; `writeTypes` has inline uint64 length serialization with a direct MOVQ store. `candidate-nested-writers.asm` captures the latter, plus alias-writing behavior. The selected hot caller `instantiateTypeWithAlias` includes inline keybuilder operations in `candidate-caller.asm`.

Bounds checks are only partially eliminated. The first two fixed-offset uint32 writes in `getIndexedAccessKey` become direct stores without capacity or bounds branches. The third still loads n, checks capacity with a signed comparison, and performs a bounds check before the store. General relation and nested writer paths similarly retain guards and panicBounds branches. No claim is made that all bounds checks vanish or every helper call in key construction is gone; alias/type-list helpers, hash calls and cold overflow calls remain.

Frames excluding saved BP are unchanged between these two versions: getTypeListKey176, getIndexedAccessKey160, getConditionalTypeKey176, getRelationKey200 and instantiateTypeWithAlias640 bytes. The144-byte builder and its zeroing remain. Inlining increases some code sizes: getRelationKey367→684, indexed key237→285, conditional key244→298, and instantiateTypeWithAlias2263→2277 bytes. Stream grows165→179 bytes to saturate n after prefix copying. These tradeoffs require workload measurement; eligibility/inlining alone do not establish benefit.

## Exact-source allocation screen

The isolated module copies candidate `keybuilder.go` byte-for-byte (SHA6c50894e…), verified against its production manifest. Its51 cases and commands are recorded in `allocation-summary.json`; input setup is outside each1000-iteration AllocsPerRun closure. String, byte-slice and bytewise lengths0,5,13,64,127,128 allocate zero; lengths129,256,1089,4096 allocate once. Prepared hash-only cases, the13-byte indexed-key existing-map hit and the embedded-streaming reference allocate zero. Counts are identical to the previous direct and buffered screens.

Package-local escape output reports no escape of the builder receiver or input strings/byte slices through short helpers; the allocated overflow hasher escapes. The screen does not measure whole-compiler allocations, all possible real cache-hit paths, runtime speed, GC, memory retention or workload key-length distribution. AllocsPerRun temporarily uses one P. No timing conclusion is drawn from the test runtime.

## Safety boundary and reproducibility

The patch copies buf[:old n] into a newly created stream before setting n=128. This preserves serialized bytes while making every streaming state fail the primitive inline-capacity guard. Exact-fit inline128, empty writes, hash continuation and stable stream identity retain their prior behavior. Builder copying after a first write or explicit stream creation remains prohibited. No hash truncation, relation interner, alias/ID order or mutable shared buffer is introduced.

`inspect.py` captures the primary helpers/caller; `capture.json` also records the two targeted nested-writer objdump commands. `allocation-summary.json` records both screen commands, with raw results in allocation.log and escape.log. Parent-owned correctness suites are outside this artifact's claims. All inspection and allocation processes are terminal; no active work remains. `manifest.json` hashes the small evidence files and test module, excluding itself.
