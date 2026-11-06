# Conditional spread override table: rejected

Correctness validation passed as recorded in README.md. The fixed screen at checkpoint eea55c6 completed (session 81226, exit 0); recorder 69204 exited 0. Capture success is not performance acceptance. Independent Python readback recomputed all 28 paired observations, timing/RSS medians, aggregates, copied execution hashes and appended PERF rows.

| Workload | Ratio of medians | Median paired ratio | Retained RSS MiB | Candidate RSS MiB |
| --- | --- | --- | --- | --- |
| typeorm | 0.928183 | 0.915512 | 881.336 | 878.988 |
| trpc | 0.770404 | 0.781213 | 244.125 | 234.000 |
| vscode | 0.967962 | 0.982187 | 7789.270 | 7825.402 |
| sentry | 1.035863 | 1.068297 | 5382.266 | 5423.312 |

Ratios above 1 favor the candidate. Aggregate geometric means are 0.920192 and 0.930744, both below 1.01. TypeORM and tRPC fail both workload floors; VS Code fails the ratio-of-medians floor. All median RSS ratios pass the 1.05 ceiling.

Reject without confirmation, rescue runs, or retuning this candidate. Broad paired variation prevents treating these as precise causal slowdown estimates. Removing unused bookkeeping did not yield an accepted workload improvement. This does not establish a native-relative speed change.

Four actual compiler workload rows were appended to PERF.md; frozen execution and samples are in ../../results/spread-override-table-screen. Production source and default binary remain retained. The 10× goal remains unmet.
