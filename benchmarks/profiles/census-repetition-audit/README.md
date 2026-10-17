# Raw-key repetition in the saved tRPC census

This offline audit uses the existing detailed, insertion-order-capped census. It does not run the compiler or measure a new optimization. `inputs.json` identifies exact archive members and SHA256 hashes. Run `python3 benchmarks/profiles/census-repetition-audit/reproduce.py` from the repository to verify the archived inputs and reproduce `report.json`; run `python3 -m unittest discover -s benchmarks/profiles/census-repetition-audit -p test_analyze.py -v` for six synthetic analyzer tests.

| Historical capture | Recorded calls | Unclassified overflow calls | Nonnested raw-key reentries | CPU labeled by records having those reentries | All sampled CPU | Overflow-labeled CPU |
|---|---:|---:|---:|---:|---:|---:|
| One checker | 57,462 | 92,722 | 7,462 | 10 ms (0.383%) | 2,610 ms | 270 ms |
| Four checkers | 210,398 | 21,587 | 33,132 | 60 ms (1.439%) | 4,170 ms | 60 ms |

All observed nonnested raw-key reentries belong to type-instantiation misses. The recorded signature-construction, class/interface-construction and resolved-signature misses have one call per raw key. None of the repeated records has the observer's error, deferred-result, diagnostic-span or abnormal-return flags. These are observations of retained records only, not a claim about overflow or other workloads.

`Calls - 1 - NestedSameRawKeyEntries` counts entries after the first that did not begin while that same record was active. The archived `beginCensus` implementation increments the nested counter when the record's active count is nonzero. The analyzer never applies this formula to overflow, where different keys share a record. Record IDs are checker-local, so every profile join uses both checker and record ID. Sample categories are disjoint and sum to total sampled CPU.

CPU assigned to a repeated record includes its first call, subsequent calls and any inherited goroutine labels. It is **not** repeated-call CPU, inclusive repeated-subtree CPU, or a removable-work budget. Descendant census spans replace parent labels. A record with zero sampled CPU can still execute substantial work; these are coarse samples. Counts cannot be converted into speedups.

The observer retained pointer keys, capped each checker at 50,000 records in insertion order, and materially perturbed execution. Different checker counts change both work and coverage. Raw pointer keys and stack-depth fields do not capture inference generations or all mutable state; equal keys do not prove equivalent results. The capture did not record returned-result identity. No cache extension is supported by this evidence alone.

Decision: do not infer a large redundant-work opportunity from the much larger family-level resolved-signature CPU fraction. If pursuing instantiation caching, the next diagnostic must distinguish completed results, context/inference invalidation and first versus later calls, use bounded sampling across the whole execution rather than first-key truncation, and quantify observer overhead. Alias-free results alone are not sufficient to establish safe reuse. Production remains the retained node-pointer implementation; no PERF row is appropriate for this offline analysis.
