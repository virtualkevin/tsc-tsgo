# Owned symbol links screen: rejected

Capture `f2527e0`. All28 alternating pairs and raw resource measurements are preserved. Input, diagnostics, build, source, binary, wrapper and sample integrity checks passed; performance acceptance failed. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Baseline / candidate median RSS MiB |
|---|---:|---:|---:|
| TypeORM | 1.029347 | 1.014386 | 880.324 / 883.875 |
| tRPC | 1.035052 | 1.002545 | 243.000 / 246.496 |
| VS Code | 0.992113 | 0.989868 | 7738.512 / 7858.832 |
| Sentry | 1.029017 | 0.999025 | 5424.629 / 5494.078 |

Aggregate ratio of medians1.0212380255629596 passes1.01; paired aggregate1.0014176655303098 fails. Both are required. All workload summaries meet0.98, and all median RSS ratios stay within1.05. This candidate is rejected under the frozen policy: no confirmations, extra samples or payload/layout/owner-check retuning. The apparent improvement in the ratio-of-medians summary was not reproduced by the required paired summary. These results do not establish a cause or prove that every direct semantic-storage design will fail.

Production remains source216d40c7/defaultbinary8fe4bd80. The larger symbol records and explicit key roots passed correctness validation but did not establish the required net workload improvement. No original-native improvement is claimed; the10×target remains unmet. Exact execution files and actual stdout/stderr are preserved with readback-verified SHA256 hashes under `execution/`.
