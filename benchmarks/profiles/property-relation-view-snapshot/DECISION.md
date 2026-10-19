# Rejected on completed workload regression

The screen at capture HEAD32d8218 was interrupted by SIGTERM during the large
workload group. Signal auditing recorded sender PID3841 UID1000 comm codex; the
reason for that signal is unknown. It was forwarded immediately, the supervisor
exited143, and benchmark cleanup reported zero leftover marked processes.

Independent raw-input/provenance/pair verification of the completed nine-pair
small group confirms tRPC failed both required0.98 workload floors:

| Workload | Baseline ms | Candidate ms | Ratio of medians | Median paired ratio |
| --- | ---: | ---: | ---: | ---: |
| TypeORM | 2460.792515 | 2413.626815 | 1.019541422 | 1.020287482 |
| tRPC | 444.114781 | 456.927425 | 0.971959127 | 0.972207952 |

This completed floor failure suffices to reject under the frozen all-workloads
policy. No replacement screen, confirmation, extra samples, retuning or promotion
is warranted. Retained production source/default remain unchanged. No speedup
against the original native target is inferred.

The VS Code console result and partial large JSON remain raw evidence, not an
independently credited complete large-group result. No four-workload aggregate or
large-workload PERF rows are produced. The two completed verified workloads,
interruption details, execution-file copies and hashes are preserved under
benchmarks/results/property-relation-view-snapshot-screen/.
