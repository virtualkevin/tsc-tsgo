# Predeclared reversed-role tRPC confirmation

Preparation only while the original all-four-workload benchmark is active. No execution, syntax probe, compiler build, test or measurement performed. Original controllers/common modules remain unchanged.

After explicit root release:

`node /tmp/run-cjs-trpc-confirmation.mjs [NEW_RESULTS_DIRECTORY]`

Exactly nine alternating pairs plus one warmup, tRPC only. Baseline is NEW CJS guard a6da693db033a9c2a6a2d712efeb1f20507fc9dfc92ad7d02db0234116e2d80c; candidate is OLD PointerLinkStore b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322. The baseline/candidate ratio above1 favors the OLD binary, not the guard. The opening pair and warmup run the guard first; nine pairs yield five guard-first and four old-first pairs.

The original result reported by the coordinator favored old pointer in all seven tRPC pairs, with medians458.77ms old and493.04ms guard. This is the reason for one predeclared confirmation, not a request to repeat until favorable. That declaration is stored separately from measured confirmation evidence.

Both sides keep default GC, unset/default round-robin scheduling and default checkers, with GNU time RSS. Identical semantic arguments, exact pinned tRPC inputs, clean diagnostics, resource measurements, order and recalculated summaries are checked using a separate adapted common module. The known source delta is validated in OLD→NEW direction even though timing roles are reversed: one production guard plus one added JSX regression test, same build settings. Dynamic capture HEAD remains stable. All prior binaries/sidecars/controllers are preserved.

The selected-project assertion accepts the known tRPC subset of the complete pinned manifest and rejects unknown/duplicate selection. A new output directory is required. Process-owner cleanup and per-invocation180second timeout are retained; total confirmation deadline is five minutes. No adaptive workload or pair expansion exists.

After terminal completion:

`node /tmp/record-cjs-trpc-confirmation.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_EVIDENCE_DIRECTORY]`

Writes only confirmation.json and README.md beneath a new /tmp directory. It preserves raw report links/hashes, pair ordering/times/RSS, both clearly labeled ratios, old/new wins, and order-stratified paired ratios. It does not write or propose automatic PERF/NOTES entries and does not issue an acceptance decision. No statistical significance is inferred from the small confirmation sample. Wrapped results are not comparable with historical unwrapped data or the native target.
