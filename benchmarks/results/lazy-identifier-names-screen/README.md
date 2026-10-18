# Lazy identifier names screen: rejected

Capture `6d9585b`. All 28 alternating pairs and raw resource measurements are retained. Input, diagnostic, build, source, binary, wrapper and sample-integrity checks passed. Performance acceptance failed. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Baseline / candidate median RSS MiB |
|---|---:|---:|---:|
| TypeORM | 1.008834 | 1.009959 | 879.008 / 878.492 |
| tRPC | 0.964049 | 0.969155 | 242.500 / 236.375 |
| VS Code | 0.997220 | 0.996893 | 7885.500 / 7741.422 |
| Sentry | 1.007440 | 1.004359 | 5354.281 / 5418.957 |

Both aggregate summaries fail the required 1.01 gate: ratio-of-medians geometric mean 0.9942193135750945 and paired-median geometric mean 0.9949671037231864. Both tRPC summaries also fail the per-workload 0.98 gate. All median RSS ratios pass the 1.05 ceiling. No confirmations, extra samples, or eager/lazy threshold, lookup, replay or storage retuning will follow this rejected screen.

Deferring identifier-name maps passed correctness validation but did not establish a net workload improvement. This experiment jointly changes eager canonicalization and demand-driven map materialization; its results do not isolate a cause or prove that every form of deferred parser work will fail. RSS is total command peak memory, not the size of the map alone.

Production remains source `216d40c7`, default executable `8fe4bd80`. No original-native speedup is established, and the 10× target remains unmet. `execution/` preserves the exact frozen harness/configuration files, recorder, and actual stdout/stderr with a readback-verified hash manifest. `recording/proposal.json` distinguishes measurement integrity from the failed performance gates.
