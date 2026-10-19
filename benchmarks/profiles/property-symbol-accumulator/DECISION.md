# Decision: reject property-symbol accumulator

Capture `306e97a`; all 28 alternating pairs completed without interruption.
Independent readback verified frozen inputs, clean diagnostics, normal build
provenance, raw elapsed times/RSS, and summary calculations. Measurement integrity
passed; performance acceptance failed.

| Workload | Baseline/candidate median ratio | Median paired ratio | Baseline RSS MiB | Candidate RSS MiB |
|---|---:|---:|---:|---:|
| typeorm | 0.984406 | 0.984406 | 883.625 | 887.781 |
| trpc | 0.969118 | 0.992810 | 242.250 | 240.125 |
| vscode | 1.034357 | 1.036015 | 7849.359 | 7816.781 |
| sentry | 1.012711 | 1.025708 | 5318.555 | 5313.512 |

Ratios above one favor the candidate. Aggregate ratio of medians is 0.999831;
aggregate paired median is 1.009503. Both miss 1.01. tRPC's ratio of medians
0.969118 fails the 0.98 workload floor. All RSS limits pass. Improvements on
VS Code and Sentry do not override failed gates. No confirmations, extra samples,
pooling, or post-failure threshold retuning will be used to rescue this candidate.

The append-only local accumulator was intended to avoid allocating a map for
small property-symbol collections using the checker's existing threshold of 16.
It preserved pointer identity and first-occurrence order, with full correctness
checks and explicit stateful query-order fixtures passing. The workload results
do not support retaining the change. They do not causally isolate linear search,
map allocation, locality, or GC costs; nominal allocation reduction is not an
established end-to-end gain.

Retained source `216d40c7…` and default binary `8fe4bd80…` remain unchanged.
The isolated candidate and its validation/provenance are preserved. Complete raw
samples are in `benchmarks/results/property-symbol-accumulator-screen`; the eleven
execution files were copied and hash-verified, and four PERF.md rows were appended.
This is not a native-relative improvement and does not achieve the 10× objective.
Further work needs a distinct mechanism, not rescue of this failed screen.
