# Parser interner screen: rejected

Capture `70f98c6`. All 28 alternating pairs and raw resource measurements are preserved. Input, diagnostics, build, source, binary, wrapper and sample integrity checks passed; performance acceptance failed. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Baseline / candidate median RSS MiB |
|---|---:|---:|---:|
| TypeORM | 1.026772 | 1.016210 | 885.141 / 879.398 |
| tRPC | 0.987750 | 1.020406 | 241.625 / 239.250 |
| VS Code | 1.002656 | 1.002656 | 7746.996 / 7796.668 |
| Sentry | 0.997040 | 1.000948 | 5342.379 / 5343.309 |

Aggregate ratio of medians is 1.0034515476321384, below the required 1.01. The paired aggregate is 1.0100197445208616 and passes. All workload summaries meet 0.98 and all median RSS ratios meet 1.05. Both aggregate checks must pass, so this candidate is rejected. No confirmations, extra samples or hash/load/probe/layout retuning follow this failed screen. These data do not establish the cause of the outcome.

Production remains source `216d40c7` and binary `8fe4bd80`. No original-native improvement is claimed; the 10× target remains unmet. Execution files and actual stdout/stderr are archived with verified SHA256 hashes under `execution/`. The stdout's inherited “Compact-symbol-table experiment passed” label refers to controller integrity completion, not this experiment's name or performance acceptance; the separate recorder establishes rejection.
