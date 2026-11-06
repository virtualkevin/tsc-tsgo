# Current retained-Go same-binary control

The latest storage screens show broad paired variation and changes in the
unchanged baseline's absolute times. context.py verifies twelve retained summaries
across the compact-literal-pair, spread-override-table and coallocated-symbol
screens: the binary and per-workload input manifests, arguments, configs and
lockfiles match. VS Code baseline medians range from 39.3 to 63.2 seconds. Those
cross-run observations do not identify a cause or isolate measurement noise from
other run conditions. baseline-context.json preserves the exact report hashes.

An older A/A run exists at ../../results/indexed-symbol-aa. Its identical binary
labels produced non-unit summaries (including tRPC median ratio 1.066 and Sentry
paired ratio 0.978). That is historical calibration using a different preserved
baseline, not evidence of the current noise distribution.

This experiment runs retained binary 8fe4bd80/source216d40c7 under both labels,
with the same executable path, sidecar, build settings and environments. No
compiler change or correctness rerun is needed. The current validated capture
controller is reused with additional explicit same-artifact and empty-source-
difference assertions. Standard input, clean-diagnostic, wrapper, sample-count,
order, provenance and post-capture integrity checks remain intact.

COMPARISON_POLICY.md freezes nine small-workload and five large-workload pairs,
one warmup, default settings and matched RSS. All four workloads are included.
The recorder reports variation only; no candidate promotion or speedup can
follow. Rejected candidates remain rejected. Capture44244 and recorder71874
completed successfully; independent readback verified all28pairs and copied
execution hashes. See RESULTS.md for the observations and their limits. Four
explicitly calibration-only rows were appended to PERF.md. The original
native-relative 10x goal remains unmet.
