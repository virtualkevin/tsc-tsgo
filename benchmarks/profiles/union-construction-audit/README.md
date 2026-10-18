# Union construction budget audit

Offline investigation at `f4124a0`, after the rejected parser interner. No compiler changes or new timing samples. This investigates eliminating repeated sorted-list insertion, rather than compacting list entries or retaining all types in an ID decoder.

`analyze.py` checks the preserved normal CPU archive and individual profile hashes, checks the raw heap hashes from `ast-arena-audit`, and derives the following attribution. CPU is the rounded inclusive sample percentage of `addTypesToUnion`; recursive appearances are not summed. Heap samples are selected once by stack membership. Direct insertion requires the innermost frame to be `slices.Insert` and an outer union-construction frame.

| Workload | Union construction inclusive sampled CPU | Inclusive allocated bytes / all sampled allocated bytes | Direct insertion allocated bytes / all sampled allocated bytes |
|---|---:|---:|---:|
| TypeORM | 0.97% | 0.000% | 0.000% |
| tRPC | 1.02% | 0.000% | 0.000% |
| VS Code | 0.64% | 0.010% | 0.010% |
| Sentry | 2.87% | 2.946% | 2.946% |

Zero means no selected heap sample, not zero allocation. The heap profiles lack a forced final GC and may omit recent allocations. These figures are neither wall-time savings nor a complete account of indirect GC effects. They must not be added to overlapping profile categories or multiplied into historical speedup ratios.

## Source constraints and decision

`getUnionTypeWorker` starts with an owned empty slice; `addTypesToUnion` recursively flattens unions, ignores consecutive duplicate inputs, and tracks named unions. `addTypeToUnion` accumulates flags even for constituents later excluded by nullability rules, discards never types, and maintains a deduplicated sorted list by binary search and insertion. Subsequent reduction, canonical cache keys and named-origin handling require that exact order and include-mask behavior.

Batch collection followed by sorting could reduce repeated searches and movement, but could temporarily retain duplicate constituents and add sorting cost on already ordered small inputs. A merge of sorted union constituents must still preserve the existing comparator and all flags. `CompareTypes` uses names, declaration order, recursive mapper/type structure and final IDs; substituting numeric ID sorting would change ordering. The historical declaration-order regression makes that shortcut particularly inappropriate.

The measured direct construction budget is small on all four workloads. **Defer a batch-union implementation as a route to the requested architectural gain.** This is not proof that it cannot produce a local win; it is evidence against spending another full optimization cycle on this isolated mechanism while the native-relative gap remains much larger. No production candidate, PERF row or speedup claim is created.

Reproduce from the repository root with the pinned Go toolchain available:

```sh
python3 -B benchmarks/profiles/union-construction-audit/analyze.py
```

The script regenerates the decoded CPU reports and verifies the recorded numeric result. `report.json` records exact input hashes, source hashes, commands and unrounded heap counts. Preserved `.pb.gz` files are hash-checked copies from the existing archive. No network lookup or workload execution is needed.
