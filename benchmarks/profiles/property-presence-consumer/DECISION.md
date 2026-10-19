# Rejected after complete workload screen

The complete frozen screen at capture HEAD `3dd098a` passed measurement-integrity
validation but failed performance acceptance. Ratio-of-medians geometric mean was
1.0048200118442163; paired-median geometric mean was 1.0167448471127103. Both had to
reach 1.01. All per-workload summary floors and RSS gates passed.

| Workload | Baseline / candidate median | Median paired ratio |
| --- | ---: | ---: |
| TypeORM | 1.0191916072603433 | 1.0353923899667374 |
| tRPC | 1.0208588455041976 | 0.9824377345704466 |
| VS Code | 0.9804223670745089 | 1.0481618392577876 |
| Sentry | 0.9993517051357859 | 1.0023273305863059 |

No confirmation, extra samples, threshold changes or promotion are warranted.
The retained source/default binary remain unchanged. Raw paired data, physical
inputs, executable provenance and frozen execution files are preserved under
`benchmarks/results/property-presence-consumer-screen/`; PERF.md contains the four
measured rows. This is a Go-to-Go screen, not evidence of progress to 10× native.

This result rejects this specific presence-only consumer as a performance change.
It does not measure a broader replacement of materialized property relations.
The validated view's identity/lifetime contract remains useful experimental
infrastructure, but its narrow consumer did not meet the predeclared gate.
