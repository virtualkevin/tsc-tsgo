# Project-wide inlining confirmations

The preceding screen passed its fixed gates, with full correctness already
verified. This protocol runs 19 alternating pairs per small workload and 11 per
large workload, with one warmup and default runtime settings. The second run
reverses raw executable roles. Both normalize each pair to retained/inlined
before calculating summaries and must independently pass every gate in
../project-inlining/COMPARISON_POLICY.md. No pooling or rescue runs.

Same binaries/source as the screen; only the explicit project -l=4 build policy
differs. All other build metadata must match. Production stays unchanged until
both confirmations pass. This does not establish the original-native 10× goal.

The forward confirmation completed at 02a5a34: all 60 pairs, diagnostics and
provenance checks passed. Independent recomputation verified aggregates
1.017755 (ratios of medians) and 1.023989 (median paired ratios), with all
workload floors and RSS gates passing. Workload median ratios were TypeORM
1.045956, tRPC 1.002890, VS Code 0.988351, Sentry 1.034893. The gain remains
unconfirmed until the reversed-role run independently passes. All samples,
including wide pair variation, are preserved; no statistical certainty claimed.
