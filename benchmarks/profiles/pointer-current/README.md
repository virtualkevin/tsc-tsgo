# Current PointerLinkStore profile evidence

Captured preserved PointerLinkStore `849d873` with explicit four checkers, default GC and unset/default round-robin scheduling. All four full pinned workload checks exited zero, consumed the verified benchmark inputs, and emitted only the expected CPU/Memory profile announcements. These are instrumented profiling runs, not performance measurements.

| Workload | Inputs | Sampled CPU | Estimated allocated space | Estimated allocated objects |
| --- | ---: | ---: | ---: | ---: |
| typeorm | 3,572 | 11.28s | 559.45MB | 2,943,695 |
| trpc | 942 | 2.26s | 98.81MB | 313,288 |
| vscode | 11,563 | 152.30s | 5125.36MB | 19,060,504 |
| sentry | 13,290 | 123.57s | 4606.09MB | 23,994,046 |

All eight raw profiles decoded successfully with pinned Go 1.26.9. Each workload directory contains cpu-flat.txt, cpu-cum.txt, alloc-space-flat.txt, alloc-space-cum.txt, and alloc-objects-flat.txt, plus raw profiles and command logs. Each text table retains at most 300 nodes with node/edge fraction filtering disabled; omitted tail nodes remain in the raw profiles.

profile-evidence.json is the compact index; capture.json retains exact input hashes/build provenance/commands; summary-evidence.json retains all pprof commands, exits, raw before/after hashes and summary hashes. Original capture, profiles, binary and sidecar remained unchanged. Preservation-plan.json describes a proposed copy only: no repository files have been written.

CPU percentages are sampled and cumulative caller/callee percentages overlap; they cannot be summed into a speedup prediction. alloc_space and alloc_objects estimate cumulative allocation, not live heap or peak RSS. No timings here are comparable to wrapped benchmark medians. The separate same-binary scheduler experiment does not change this capture’s round-robin policy.

Original report absolute paths describe the capture machine. The preservation plan supplies repository-relative destinations. The preserved binary is identified by SHA256; it is not included in the copy plan.
