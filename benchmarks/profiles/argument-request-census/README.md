# Argument request census

Diagnostic overlay against production source `216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd`, HEAD `8363e16`. No production edits, cache, or timing claim. This tests the repeated-work direction in the user’s OPTI_ANALYSIS_01.md after the argument-reuse-audit established contextual freshness and instantiation-budget effects.

| Workload | Call frames | Requests | Repeated tuple | Same result pointer | Different result pointer | Budget changed | Untracked |
|---|---:|---:|---:|---:|---:|---:|---:|
| TypeORM | 88,074 | 119,374 | 707 | 707 | 0 | 16,518 | 0 |
| tRPC | 3,226 | 3,284 | 6 | 6 | 0 | 1,312 | 0 |
| VS Code | 1,387,798 | 2,032,194 | 4,982 | 4,883 | 99 | 255,187 | 0 |
| Sentry | 457,877 | 498,596 | 1,587 | 1,557 | 30 | 104,401 | 0 |

Repeats are approximately 0.59%, 0.18%, 0.25%, and 0.32% of observed requests, respectively. These are counts, not weighted CPU costs or removable runtime. Defer implementing this partial-key cache: repetition is sparse and pointer identity is not stable for every repeated tuple. Differing pointers do not by themselves demonstrate differing semantic types or diagnostics; matching pointers do not prove immutable results or safe suppression of checking side effects. No conformance or performance promotion follows.

## Scope

One frame per `resolveCall`, shared across its ordinary candidate applicability checks. Key: argument pointer, contextual parameter type pointer, check mode, relation pointer, flow-loop depth, resolution start, and active mapper-cache depth **before** checking. These depths and pointers do not describe full flow/inference/resolution state. Counters compare each repeat against the first result for that key. They observe the instantiation counter before and after the call, not every reset or nested counter mutation.

Only direct ordinary argument expressions in `isSignatureApplicable` are covered. `this`, rest, JSX special handling, inference checks outside this site, and diagnostic-only applicability calls are excluded. Early exits and recursion execute normally. At most 4,096 keys are retained per call frame, not globally; recursive frames can coexist. No observed overflow. Borrowed semantic pointers live only with the frame; the process-wide registry holds checker-exclusive counters and is serialized after checking. This observer adds allocations and can extend object lifetimes within a call; it is not suitable for measuring normal runtime or heap use.

## Reproduction and validation

Run `python3 benchmarks/profiles/argument-request-census/prepare.py` from the repository. This creates ignored full-file overlays and `overlay.json`; the committed patch records modifications and the two census Go files supply added sources. Production source files are never written.

From `packages/tsc-go`, with the pinned Go 1.26.9 executable and `GOCACHE=/home/dev/.cache/go-build`:

```
go test -overlay /home/dev/tssss/tsc-tsgo/benchmarks/profiles/argument-request-census/overlay.json ./internal/checker -run '^TestArgumentRequestCensus$' -count=1 -json
go build -trimpath -overlay /home/dev/tssss/tsc-tsgo/benchmarks/profiles/argument-request-census/overlay.json -o /tmp/tsc-argument-request-census ./cmd/tsgo
```

Both commands exited zero. The focused test checks duplicates, changed result pointers, isolation, overflow, and disabled behavior. Then run `python3 benchmarks/profiles/argument-request-census/capture.py`. The controller requires unchanged production source, hashes the overlay sources and executable, verifies pinned input/configuration hashes before and after each workload, and requires clean output from baseline, observer-disabled, and observer-enabled runs. All 12 passed. This is narrow observer validation, not a new full compiler correctness suite.

The initial sandbox attempt failed during nested Git provenance capture (`EPERM`) before any workload; its stdout/stderr are retained separately. The same controller then completed with authorized elevated execution. `report.json` records hashes, commands, inputs, and counters. `build-info.txt` records embedded build settings; this custom overlay build does not have a normal build-system provenance sidecar. `evidence-manifest.json` hashes all committed evidence and verifies it by readback. The default compiler and its sidecar were preserved throughout. PERF.md has no entry because no optimization was timed.
