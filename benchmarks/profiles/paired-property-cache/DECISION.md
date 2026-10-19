# Decision: reject paired property-cache storage

Capture `dd93178`, all 28 alternating pairs completed. Independent recording
verified inputs, clean diagnostics, normal build provenance, raw times/RSS and
summary calculations. Measurement integrity passed; performance acceptance failed.

| Workload | Baseline/candidate median ratio | Median paired ratio | Baseline RSS MiB | Candidate RSS MiB |
|---|---:|---:|---:|---:|
| typeorm | 0.983902 | 0.978931 | 884.254 | 884.465 |
| trpc | 0.989120 | 0.931753 | 241.125 | 243.500 |
| vscode | 0.972171 | 0.956157 | 7781.730 | 7850.418 |
| sentry | 1.018419 | 1.014134 | 5343.551 | 5247.938 |

Ratios above one favor the candidate. Aggregate ratio of medians is 0.990758 and
aggregate paired median is 0.969772; both miss the required 1.01. TypeORM and tRPC
fail the paired 0.98 floor; VS Code fails both workload floors. RSS gates pass.
Sentry's small gain does not override the other gates. No confirmations, extra
samples, pooling, or post-failure representation retuning are authorized by the
frozen experiment policy. The candidate is not promoted.

All correctness checks passed, including stateful cache identity/recursive updates,
full pinned conformance, CLI/API/emit and instrumented checks. The source and
separate candidate binary/provenance remain preserved. The retained default source
`216d40c7…` and binary `8fe4bd80…` stay in production.

The storage hypothesis was that sharing each name key between two independent
result slots would offset larger map values and reduce allocation. The workload
results do not support accepting that tradeoff. They do not isolate the cause of
regression: larger values, copies, hashing, locality and GC effects were not
causally separated. Do not infer that correctness tests or nominal header savings
establish a performance win. This experiment provides no native-relative speedup
and does not meet the 10× goal.

Raw reports: `benchmarks/results/paired-property-cache-screen/{small,large}.json`.
The execution archive was copied and hash-verified; four measured PERF.md rows
were appended. Complete pair samples and the rejection gates are preserved in
`recording/proposal.json`. Next research must use a distinct mechanism, not rescue
this layout based on the favorable Sentry subset.
