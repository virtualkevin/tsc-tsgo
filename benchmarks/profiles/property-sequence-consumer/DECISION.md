# Rejected: ordered target-property sequence consumer

Correctness and normal build provenance passed. The completed nine-pair small
workloads fail the frozen 0.98 floor in both required summaries:

| Workload | Baseline median ms | Candidate median ms | Ratio of medians | Median paired ratio |
| --- | ---: | ---: | ---: | ---: |
| TypeORM | 2583.371807 | 2639.082598 | 0.978890092 | 0.967502570 |
| tRPC | 499.419030 | 521.555727 | 0.957556411 | 0.968237656 |

Both RSS gates pass, but they do not override timing failures. No confirmation,
extra samples, unchanged retry, or promotion is warranted.

The screen received SIGTERM during the large group. The supervisor recorded
sender PID 3841, UID 1000, process name codex; the cause is unknown. It forwarded
the signal, exited 143, and the runner reported zero leftover marked processes.
The VS Code console summary and partial large report remain raw evidence only;
no independently verified large-workload PERF row or four-workload aggregate is
claimed. Completed small-workload failures suffice for rejection under the
predeclared all-workloads rule.

The result does not establish why this representation is slower. Extra sequence
sorting, pending cache maps and dispatch are plausible costs, not measured causal
findings. Do not extrapolate component allocation savings into compiler gains.
Any next design needs broader coverage and a measured cost advantage, rather than
another unchanged screen of this candidate. Production remains the retained
node-pointer implementation. The 10x native-relative objective remains unmet.
