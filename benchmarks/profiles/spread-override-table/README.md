# Conditional spread-override bookkeeping

Isolated two-file overlay on retained production at4e1070e. The existing computed-name prepass allocates a private override-diagnostic map only if a spread is present under strict null checking. No-spread literals avoid the map and its writes. The main property loop, result types, symbols and semantic queries are unchanged. See CONTRACT.md.

Exact source inverse audit passes. Retained21523 and candidate41948 focused normal/race/checkptr validation completed successfully with frozen source. Seven fixture shapes in two strict-null modes compare diagnostics, query identity, rendered types and semantic counters; verify-focused.py independently verified that all84 emitted histories agree. Full compiler/services/conformance87754 completed: root21176/14packages, services219, pinned14915cases(12789fully checked,8partially checked,2118unsupported skips,0failures). Independent full raw readback86540 passed. CLI30467 completed normal80, API/emit/project12, race80 and checkptr80. Complete independent raw-evidence readback50790 passed. All validation ran at HEAD4e1070e with fixed overlay sources.

Normal provenance build99009 passed: binary3b1f019d/source66a9d717,5155source files with exactlytwo changes. The retained production source/default executable were restored and verified. Duplicate raw logs were removed only after exact gzip readback; raw-compression.json records their identities. All correctness gates required for the fixed screen passed. The completed screen failed performance acceptance; see RESULTS.md.

Production remains unchanged. Four measured screen rows were appended to PERF.md. The candidate is rejected without confirmation or rescue runs. This bookkeeping optimization alone is not an established route to10×.
