# Typed handle graph: standalone measurements

This experiment does not justify replacing compiler pointers with owner-local handles. All six timing cases have median paired pointer/compact ratios below 1. Compact records reduce allocation bytes, but decoding and public owner-carrying references cost time; a strong owner also keeps unreachable pages alive. No compiler source, default binary, or PERF.md change results from this experiment. The 10× compiler goal remains unmet.

## Method and correctness

The unchanged prototype in `../typed-handle-graph/prototype` is extended through `overlay.json`. `staged/storage_experiment_test.go` compares 32-byte integer-edge records with 48-byte pointer-edge records, each in typed 256-record pages. Both use deterministic identical values and four prior-node edges, including a full chain. Construction includes temporary external reference arrays: 16-byte owner-carrying references versus 8-byte pointers. It is not a pure allocator comparison; the compact public API also validates ownership. Internal traversal captures the owner once; public traversal reconstructs owner-carrying references through Read. Traversal setup is excluded from timing.

Seven tests passed in normal, race, and checkptr modes (21 passes), including full fixture equality through 262,144 records and pointer-page GC lifetime. These are model tests, not compiler conformance tests. Real compiler strings, maps, symbols, variable-arity data, and semantic effects are absent.

The fixed config uses nine alternating pairs per operation/size, fresh processes, 200ms Go benchmarks, and default runtime settings. All 108 timing observations are retained. Retention uses five alternating pairs per shape/size (40 fresh processes), two GCs before and after construction, and only the final root kept alive. No samples were selected or repeated. `capture.json` and `raw/` preserve evidence; `verify.py` independently reads raw output, validates hashes, identities, commands, order, counts, and retention arithmetic, and emits `readback.json`. The temporary binary and toolchain must still exist for its full pin check.

## Timing

Ratios are pointer time / compact time; greater than 1 favors compact. Paired ranges show substantial variability. These descriptive microbenchmarks do not pass a compiler promotion gate or establish compiler speedups.

| Records | Operation | Pointer median ns/op | Compact median ns/op | Ratio of medians | Median paired ratio | Paired range | Pointer B/op | Compact B/op |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4096 | construct | 780230 | 613683 | 1.2714 | 0.9110 | 0.5749–1.3838 | 258067 | 205126 |
| 4096 | internal | 32513 | 60571 | 0.5368 | 0.5271 | 0.4490–0.5484 | 0 | 0 |
| 4096 | public | 40723 | 389958 | 0.1044 | 0.0994 | 0.0840–0.1101 | 0 | 0 |
| 262144 | construct | 45408026 | 60600343 | 0.7493 | 0.8026 | 0.5960–0.8548 | 16001148 | 12624498 |
| 262144 | internal | 14671363 | 20141739 | 0.7284 | 0.7038 | 0.5419–0.9089 | 0 | 0 |
| 262144 | public | 15629564 | 64776813 | 0.2413 | 0.2587 | 0.2240–0.3450 | 0 | 0 |

Both traversal forms allocate zero bytes/objects per operation. Allocation counts for construction are preserved in readback.json. The small construction ratio of medians and paired median disagree; this is not evidence of a reliable construction win.

## Retention

These are median signed endpoint HeapAlloc differences in bytes, not peak RSS, exact object accounting, or timing. Runtime noise is retained. Linked graphs make every record reachable from the final root. Sparse graphs have no edges: the pointer baseline can release old pages, whereas a compact reference retains the entire owner.

| Records | Shape | Pointer HeapAlloc delta bytes | Compact HeapAlloc delta bytes |
| --- | --- | --- | --- |
| 4096 | linked | 222424 | 136568 |
| 4096 | sparse | 24224 | 131456 |
| 262144 | linked | 13914928 | 8411584 |
| 262144 | sparse | 29656 | 8411584 |

For 262,144 sparse records the compact endpoint is about 284× the pointer endpoint. Treat this as a warning about this ownership model, not a forecast for compiler memory. Any future handle experiment needs a concrete compiler lifetime boundary, a way to avoid repeated decoding on hot paths, and a measured end-to-end benefit. Shrinking record size alone is insufficient.
