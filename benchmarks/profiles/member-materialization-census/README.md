# Pending-member materialization census

Diagnostic-only Go overlay on retained source216d40c7. Production source/default binary are unchanged. `prepare.py` adds scalar observer calls to pending_members.go and writes the completed counters from the CLI exit path. A separate executable is built under /tmp; it is not a performance candidate.

Nine rows distinguish starts without bases, starts with bases, recursive starts, two reasons a table cannot be discarded, new versus reused name layouts, and immediate versus later reconstruction of a mutable table. Columns are events, entries, and auxiliary totals. For starts, entries are source entries and auxiliary is the number of already collected bases. For retained-table failures, entries are map length and auxiliary is property count. For new/reused layouts, entries are properties and auxiliary is base count. For table reconstruction, entries are properties and auxiliary is zero. Base totals do not reveal the distribution of bases across events. Immediate means Members() entered before a name layout existed; later means it entered with a completed layout, not necessarily a long time afterward.

Counters contain no semantic pointers, names or per-instance identity, have fixed space, and use atomics for concurrent checkers. The disabled observer returns without recording. Output uses exclusive creation to preserve existing evidence. Atomic hooks perturb execution; counts are neither cost-weighted requests nor allocations, live objects, safe optimization eligibility or speedup estimates. They aggregate all checkers without identifying duplicate semantic work. Counters are read at CLI completion; the capture checks conservation across completed runs.

Focused tests cover concurrent accumulation, exclusive valid output and actual pending-member lifecycle with shared layout reuse plus immediate/later table demand. Normal and race validation each passed three focused tests; the separate diagnostic build passed. All 12 retained/disabled/enabled controls passed on the four pinned workloads, with clean diagnostics and matching inputs. `verification.json` records independent raw-output/input/hash/conservation readback. Before using census results, require those checks to pass and run all four pinned workloads with retained, observer-disabled and observer-enabled binaries, clean diagnostics and input/source/hash guards. Keep these diagnostic runs out of PERF.md.

## Completed observations

| Workload | Materializations | Reused layouts | Reuse fraction | Immediate / later table reconstruction |
|---|---:|---:|---:|---:|
| typeorm | 10767 | 8562 | 79.52% | 0 / 0 |
| trpc | 3618 | 2944 | 81.37% | 0 / 0 |
| vscode | 103103 | 89527 | 86.83% | 1503 / 4 |
| sentry | 121244 | 114814 | 94.70% | 0 / 0 |

No recursive-start or retained-table-failure event occurred in these four diagnostic captures. All VS Code table-reconstruction events had zero entries; the other workloads had none. This observation does not remove API, emit or recursive-resolution requirements. Base-count auxiliary totals show inherited materialization is represented, but do not classify each reused-layout event by base count. Layout reuse is observed after construction, so it is not proof a preconstruction shortcut would be valid.

Decision: prototype direct construction into an existing name layout with inherited-member merging, exact own-symbol creation/overwrite order, current classification/sorting, and conversion to an ordinary map whenever the layout cannot represent the actual result. Recursive resolution keeps its eager mutable path. Publication and fallback must not repeat symbol construction or eagerly resolve bases. This targets transient map construction, distinct from the rejected sparse pending-member cache indexing experiment. Full correctness and frozen performance gates remain mandatory; no speedup has been measured.
