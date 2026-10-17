# Direct primitive key writers: generated code and allocation screen

The candidate replaces generic byte-copy calls on short integer writes with direct stores, but the three dedicated primitive writers do **not** inline. This is mechanism evidence, not a compiler performance result. All inspection and screen processes are terminal; this audit did not rebuild the compiler or change repository sources.

`capture.json` binds the actual production binaries, commands and assembly hashes. Baseline is the previous buffered implementation (`9d87e919…`); candidate is the direct-writer implementation (`61313d4e…`, source `1511f3d0…`). Both use Go1.26.9, Linux/amd64 v1, trimpath, no PGO and no extra flags. Their complete source manifests differ only in production `keybuilder.go` and added `keybuilder_direct_test.go`; see `source-comparison.json`. There is no numeric relation interner change in this comparison.

## Actual generated code

The production integer writer short branches contain direct MOVL/MOVQ stores. They no longer call generic `writeBytes` and `runtime.memmove`; caller-to-writer CALLs remain. The previous integer wrappers inlined into callers but then called `writeBytes`. The candidate's `writeBytes` method has no emitted production symbol; its source remains and the primitive screen still exercises it. `writeString` retains its existing memmove path. Overflow methods remain separate calls and use the same streaming hasher.

The exact-source tiny-package diagnostic reports cost81 versus budget80 for each of `writeByte`, `writeUint32` and `writeUint64`. Production assembly independently confirms they remain out of line. Go's inlining visitor disables early budget termination under `-m=2` (`compiler-budget-excerpt.txt`), so the screen's cost is completed accounting. This is not a prediction that removing one syntax node will produce inlining: costs and caller heuristics are compiler decisions.

Observed stack allocations, excluding saved BP, are:

| Caller | Previous buffer bytes | Direct writer bytes |
|---|---:|---:|
| getTypeListKey | 176 | 176 |
| getIndexedAccessKey | 192 | 160 |
| getConditionalTypeKey | 176 | 176 |
| getRelationKey | 208 | 200 |
| instantiateTypeWithAlias | 648 | 640 |

Both versions retain a144-byte keyBuilder; this experiment does not repeat the earlier1184-to144-byte representation change. Symbol code sizes and exact frames are captured in `summary.json`; smaller code or frames are not runtime measurements. Caller assembly is deliberately filtered to retain relevant prologue, key operations and calls; the helper assembly is complete for the selected symbols.

## Allocation evidence and limits

`allocation-screen/keybuilder.go` is byte-identical to the candidate source and its provenance manifest (`67a96b93…`). `allocation-summary.json` records exact commands and all51 passing subcases, each using1000 `testing.AllocsPerRun` iterations with input setup outside the measured closure. String, byte-slice and bytewise keys through128 bytes allocate zero;129,256,1089 and4096-byte keys allocate once. Prepared hash-only cases and the13-byte indexed-key generation plus existing-map hit allocate zero. The older embedded-streaming reference allocates zero for all screen lengths. These counts match the previous buffered implementation's same screen.

The bounded package escape log reports that the builder receiver, byte data and strings do not escape through the short helpers; the newly allocated streaming hasher escapes. The screen does not establish whole-compiler allocation counts, all real cache-hit behavior, long-key frequency, memory retention, GC cost or a speedup. The one overflow allocation is a real tradeoff versus the original embedded hasher, and the direct writers preserve it. AllocsPerRun temporarily uses one P; this was an untimed screen outside a quiet benchmark window.

Hash identity, write ordering, alias/ID side effects, independent builder reentrancy and the existing noncopy-after-write requirement are unchanged by this direct-writer delta. Boundary regression tests belong to the parent's correctness validation; this artifact contains codegen and allocation evidence, not a claim that those broader suites have passed.

Reproduce inspection with `inspect.py` while the preserved binaries exist; allocation commands are in `allocation-summary.json`. `manifest.json` hashes the compact artifacts and tiny source module, excluding itself. No compiled test binary is included.
