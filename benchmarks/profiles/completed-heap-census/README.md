# Completed-work heap census

Diagnostic overlay only; production is unchanged. After ordinary CLI compilation and emit/diagnostic processing, the observer writes an allocation profile, performs two forced GCs, and writes another allocation profile while keeping the existing Program alive. Each profile contains cumulative allocations and sampled in-use values. Default sampling remains unchanged. MemStats and profile rate are recorded. Tracing is rejected because it can retain extra semantic objects; existing output directories are rejected to preserve evidence.

This addresses the missing recent allocations in prior no-final-GC profiles and distinguishes retained sampled storage from total allocation at this endpoint. It does not prove semantic necessity, heap peaks, removable cost, or timing gains. Observer/profile serialization allocates and can trigger collections; before/after differences include that overhead. No observer duration belongs in PERF.md. Required next steps: focused normal/race/checkptr checks, isolated build, then baseline/observer-disabled/observer-enabled controls over all four exact pinned input sets, followed by hash-checked profile decoding.

Validation and collection completed: two focused tests passed normally, with race instrumentation, and strict checkptr. Separate observer binary ffdb71e5; all twelve baseline/disabled/enabled controls exited with clean diagnostics and identical pinned physical inputs. Independent verifier checked source, binary, controller and profile hashes at capture HEAD be0d34e. Eight profiles decoded with pinned Go1.26.9; two attribution tests passed and the full analysis reproduced exactly. Production source/default binary were unchanged.

| Workload | Before sampled cumulative MiB | After sampled cumulative MiB | After sampled in-use MiB | After MemStats HeapAlloc MiB | Interval TotalAlloc increase MiB |
|---|---:|---:|---:|---:|---:|
| typeorm | 509.30 | 1003.91 | 455.37 | 456.08 | 4.95 |
| trpc | 120.43 | 245.32 | 166.00 | 167.58 | 3.30 |
| vscode | 4747.46 | 8859.41 | 6538.82 | 6520.75 | 11.08 |
| sentry | 3844.98 | 7678.74 | 3896.09 | 3910.29 | 10.17 |

The large increase in published allocation samples, relative to the small interval TotalAlloc increase, supports the prior concern that no-final-GC captures omitted recent allocations. It is not newly executed semantic work or an optimization saving. Both profiles contain sampled allocation and in-use values; the table does not represent peak RSS. Source attribution is a disjoint partition by the first non-core/non-collections project frame, not exclusive object ownership.

After-GC leading sites include NewIdentifier/newObjectType/newSymbol/binder symbols on VS Code; checker symbols, relation result storage, object types, identifiers and instantiated-symbol links on Sentry. Existing rejected symbol-link, relation-table and type-layout candidates are not revived by this evidence. A new storage proposal must address multiple retained structures with a distinct access/lifetime design, and then pass full correctness and workload validation. The raw heap parser is preserved from ast-arena-audit/analyze.py; analysis.py uses only its parse function and constants.
