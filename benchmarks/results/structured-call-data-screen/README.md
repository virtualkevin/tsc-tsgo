# Structured call-data screen: rejected

Capture `124cd42`. All 28 alternating pairs and raw resource measurements are preserved. Input, diagnostics, build, source, binary, wrapper and sample integrity checks passed; that does not imply performance acceptance. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Baseline / candidate median RSS MiB |
|---|---:|---:|---:|
| typeorm | 0.972971 | 0.957609 | 878.207 / 873.398 |
| trpc | 1.002496 | 1.018032 | 238.500 / 238.000 |
| vscode | 1.012392 | 1.012392 | 7791.066 / 7781.531 |
| sentry | 0.995109 | 1.013315 | 5422.586 / 5276.816 |

Aggregate ratios are 0.995636 and 1.000025; both fail the required1.01. Both TypeORM summaries fail0.98. All RSS gates pass. The candidate is rejected under the predeclared policy: no confirmations, extra samples or layout/accessor/grouping retuning. The smaller layout did not establish a net workload speed improvement. This does not identify the cause of the outcome or imply that all hot/cold storage designs fail.

Production stays at retained source216d40c7 and binary8fe4bd80. No original-native improvement is claimed; the10×target remains unmet. Execution files and actual stdout/stderr are archived with SHA256 hashes under `execution/`.
