# PointerLinkStore scheduler experiment

Prepared under /tmp only. No benchmarks/builds/tests launched. Existing PointerLinkStore comparison scripts remain unchanged.

Launch only after coordinator approval of a quiet window:

`node /tmp/run-pointer-scheduler-ab.mjs [NEW_RESULTS_DIRECTORY]`

The default output is a new timestamped benchmarks/results/pointer-scheduler-ab-rss-* directory. Existing directories/reports are rejected. The exact same preserved PointerLinkStore849d873 binary is used on both sides: SHA256 b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322, source6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d.

A saved manifest overlay adds --checkers4 symmetrically, leaving all pinned project configuration and semantic inputs intact. Baseline clears TSC_GO_SCHEDULER, which the preserved source implements as round-robin. Candidate sets only --candidate-env TSC_GO_SCHEDULER=dependency after the common --unset-env removal. Default GC is shared. Both sides use GNU time and the same explicit library directory. All four projects run in TypeORM, tRPC, VS Code, Sentry order, with three alternating pairs and one warmup each. Ratios above1favor dependency scheduling.

The source snapshot /tmp/pointer-scheduler-checkerpool.go is checked against the preserved binary's source manifest before running and copied into the report directory. The controller asserts both accepted dependency scheduling and default round-robin implementation rather than assuming the current working tree is the preserved source.

The independent common module /tmp/pointer-scheduler-ab-common.mjs retains the reviewed binary/sidecar/Node/wrapper/harness/manifest snapshots, exact compiler and wrapper arguments, environment controls, input-content hashes, clean diagnostics, alternating order, warmup/pair counts and RSS/median recomputation gates. It validates candidate-only dependency scheduling explicitly. Existing quiet-window cancellation and unique process-owner cleanup are retained without changes:180-second invocation timeout,30-minute overall deadline, signal forwarding,5-second fallback and terminal /proc owner scans; no periodic /proc scanning during measurement. No new process-management framework or source instrumentation was added.

Recorder, after terminal success:

`node /tmp/record-pointer-scheduler-ab.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_PROPOSAL_DIRECTORY]`

It repeats the gates, reconstructs the overlay from the pinned original manifest to rule out other input changes, verifies identical binary provenance and copied scheduler source, rejects duplicate PERF/NOTES stages, and creates only proposed PERF.rows.md, NOTES.entry.md and proposal.json in a new directory under /tmp. No repository documentation is modified. Links outside benchmarks/ need relocation before commit.

This is a same-binary scheduler A/B, not a native tsc-ts comparison or proof of the10× target. Wrapped timing is not comparable with historical unwrapped values. RSS is command peak resident memory, not Go heap or aggregate process-tree memory. Compiler conformance remains a separate gate. Per-sample diagnostic/exit checks occur in the hashed runner; the report records their validated outcome rather than retaining all timed stdout text. Ordinary environment variables such as locale/PATH remain inherited; only recorded runtime/profile controls are cleared, with no secret values logged.
