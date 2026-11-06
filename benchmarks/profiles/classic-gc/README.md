# Alternative collector experiment

At 6063510, the pinned Go 1.26.9 source sets GreenTeaGC true in
internal/buildcfg/exp.go and exposes the GOEXPERIMENT override. This experiment
builds the unchanged retained compiler with GOEXPERIMENT=nogreenteagc into an
isolated temporary output. It does not change GC pacing, memory limits, checker
counts, thread defaults, source inputs, or compiler semantics intentionally.

The build checks the complete compiler source digest against retained216d40c7
and requires all recorded build settings to match the retained binary except
GOEXPERIMENT. It records the Go executable and inspected runtime-source hashes,
then publishes normal build provenance to the separate executable. The default
compiler is never overwritten. This records selected runtime files, not a complete
formal verification or hash of every toolchain/dependency source file.

budget.py reuses the tested historical CPU parser and verifies the raw archive,
individual inputs and earlier total sample counts. A second run reproduces its
report. It counts each sample containing background mark-worker or mutator-assist
frames once. These are not all GC work, wall-time fractions, removable work, or
predicted speedup from another collector.

| Workload | Historical mark-worker or assist CPU % |
| --- | ---: |
| tRPC | 14.721 |
| TypeORM | 18.118 |
| VS Code | 17.810 |
| Sentry | 17.367 |

This tests a different runtime mechanism from the rejected GOGC/memory tuning or
compact object layouts. It cannot establish the 10× native-relative goal by
itself. A collector implementation may trade scan cost, allocation overhead,
parallel efficiency and retention; no speed or memory improvement is assumed.

Before timing: require successful build/source/default preservation, compiler and
services tests, full pinned conformance, lifetime-focused race/checkptr tests,
normal/race/checkptr CLI parity, API/emit checks, and independent raw readback.
Record the explicit collector difference in comparison metadata. Keep default
runtime environment on both sides; the candidate's collector is selected at
build time. No diagnostic or build durations belong in PERF.md.

The isolated build completed successfully (binary 6940a08e, sidecar 8ca75452).
The retained default executable and sidecar remain unchanged. Validation
controllers cover ten existing lifetime tests in each of normal,
race and checkptr modes, the 21,175-test compiler suite, 219 services tests,
pinned conformance and CLI/API parity. No correctness or performance conclusion
is available at this build checkpoint.

The first validation controller stopped after a successful normal lifetime run
because its expected count was nine; the selector also matches
TestLinkStoreConcurrentExistingKeyReads in linkstore_split_race_test.go.
The original controller and failure report are retained. The continuation
verifies all ten exact test names and the raw log hash, reuses this successful
run without rerunning it, and proceeds with race/checkptr and full validation.

## Completed correctness gates

The isolated candidate passed 30 lifetime checks (ten each normal/race/checkptr),
21,175 compiler tests, 219 services tests and 14,915 pinned conformance
configurations (12,789 full, eight partial, 2,118 unsupported/skipped, zero
failures). CLI parity passed 80 cases in each of normal/race/checkptr modes;
API/emit integration passed 12. These are tested cases, not a whole-compiler
proof. Full raw streams are retained as hash-verified gzip archives.
No workload timing or speedup conclusion is available yet.

Independent final readback and benchmark preflight passed. screen.json records
the exact source/binary/sidecar hashes and the sole build-setting difference.
The fixed screen is prepared; no performance result at this checkpoint.
