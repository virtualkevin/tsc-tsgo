# Native worker boundary: source-only audit

Inspected during the direct native-versus-restored-Go milestone. No native instrumentation, new compiler execution, worker-count experiment or CPU-utilization measurement was performed for this audit.

`parallel-check.ts` uses automatic native checker selection by default: available parallelism, a memory estimate, bounds, and a small-program single-thread path participate. Explicit fixed policy uses four. The Go pool defaults to four, with explicit single-threaded/Checkers overrides. Therefore the current default-versus-default milestone must not be described as a controlled equal-worker comparison. Its input/options/wrapper equality checks remain valid; the actual native worker count has not been traced in this run. Do not infer it from Node's reported parallelism or a comment alone.

Native `packsResults` is enabled when the scriptc runtime shares published graphs and TSC_TS_REGION is not zero. Its documented boundary is packed diagnostics/declaration diagnostics/emit metadata returned from a worker, permitting the runtime to discard that worker's heap when it ends. `PackedResult` is not a cache of completed semantic Type/Signature graphs shared between checker owners. It therefore supplies a lifetime-boundary lead, not evidence that mutable Go checker results can be shared safely. Recycling defaults to zero; no periodic recycling behavior is assumed.

The native Type/Signature side-state experiment is opt-in through TSC_TS_SIDE_STATE=1, so it must not be attributed to this default-settings measurement. The ordinary native Type still has mutable computed fields. Any Go region/owner redesign would need to preserve escaped API objects, typed reachability, checker-local mutable overlays and program lifetimes. Source comments about scriptc heap disposal do not establish Go arena safety or a speedup magnitude.

Current GNU-time benchmark resource records contain peak RSS and exit status, not per-command user/system CPU time. Cgroup CPU counters are broader contextual observations, not automatically exclusive compiler CPU. Do not estimate worker utilization by dividing an unrelated historical CPU profile total by this run's wall duration. The diagnostic census and uninstrumented controls remain the next measurement step; no production optimization follows from this audit alone.

## Inspected files

- `packages/tsc-ts/src/compiler/parallel-check.ts` SHA256 `31e378fb176134847a9c244b7f6c4910698ea216ccba929bddd1ed820220b8ed`
- `packages/tsc-ts/src/compiler/checker-types.ts` SHA256 `9ed00bcc174d4d1af153a5b3169922bc98c7bd9055ddc719f36953155284c696`
- `packages/tsc-go/internal/compiler/checkerpool.go` SHA256 `d34f073cd1f9c7a888c2d3460ec219cc535c8f17ef2b22ff9e54be34367f4305`
- `benchmarks/resource-run.mjs` SHA256 `67461dce38a48c8cb29d9a28fb41ac10cf2636f9fab9bf80df6d5d7172198c80`
