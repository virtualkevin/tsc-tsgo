# Adaptive synthetic relation-table incidence screen

All executions are terminal. The exact production64-probe cache was copied with only `package checker` changed to `package main`; minimal full-width key and uint32 result definitions and a deterministic PCG driver are in main.go. Source/copy/driver/toolchain/binary hashes and exact commands are retained. No production source or compiler workload was changed/run.

Ten paired fixed PCG sequences each generated up to1million pseudorandom128-bit keys, stopping at the first fallback. Every stored result used the insertion count; an unexpected duplicate full key would fail rather than silently alter the count. The driver samples table mode only after set, without changing cache internals. GOMAXPROCS1 bounds resource use; durations were not collected as performance evidence.

| Probe bound | Sequences reaching1million in table mode | Fallbacks | First-fallback insertion range |
|---|---:|---:|---:|
| 64 | 0/10 | 10/10 | 376–10,313 |
| 128 | 0/10 | 10/10 | 5,868–746,283 |
| 256 | 9/10 | 1/10 | 765,996 |
| 512 | 10/10 | 0/10 | Not observed within limit |

The initial64-probe design fails early even on this synthetic distribution. Higher limits were selected ADAPTIVELY after inspecting preceding results, so these are calibration runs, not an independent evaluation or estimate of fallback probability. The same seeds are deliberately reused for comparability. Surviving1million inserts is right-censored evidence, not proof of continued survival at larger cache sizes or with compiler keys/updates.

The512 bound is eight times the initial worst-case table comparisons; a pathological missing read may now inspect512 slots before returning, and a513th same-bucket insertion triggers fallback. More tolerance may retain useful tables, but it can also increase worst-case latency. No compiler correctness, timing, RSS, allocation or improvement claim follows. Actual workloads may have very different distributions and sizes.

Each probe variant changes exactly the constant in relation_results.go; exact diffs, source/binary hashes, build stderr/stdout and raw records are preserved under probe-128, probe-256 and probe-512. The64 source/results remain unchanged. comparison.json includes all per-seed counts/capacities. The parent may build/test a separate512 draft; this screen is not production adoption.

The manifest deliberately excludes the four compiled screen executables (their hashes are in summaries). All source modules and controllers are included to reproduce them with the pinned toolchain. Do not treat test/build wall-clock output as a benchmark. Comparison is frozen after these four parameter settings.
