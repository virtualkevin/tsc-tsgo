# Frozen comparison policy

Candidate: unchanged compiler source built with pinned Go1.26.9 and the explicit
argument -gcflags=github.com/microsoft/typescript-go/...=-l=4. Retained uses normal
inlining. All other recorded build settings and all runtime settings must match.
This is an explicit compiler-policy difference, not identical build flags.
Retained baseline: node-pointer Go8fe4bd80/source216d40c7. Original native remains
the ultimate target, not a comparator to substitute during this Go/Go screen.

Before timing: candidate lifetime tests normal/race/checkptr,
full compiler/services/pinned conformance,80normal+80race+80checkptr CLI parity,
12API/emit integration cases, independent raw evidence readback, normal production
build provenance and restored retained workspace/default executable.

Fixed screen:9alternating pairs for TypeORM and tRPC;5for VS Code and Sentry;
1warmup;fresh processes, warm filesystem, default GC/checker/thread settings;
matched GNU-time peak RSS; identical pinned physical inputs/diagnostics. No other
builds, tests, profiles or development work during capture. Preserve every sample.

Acceptance requires both aggregate geometric means (ratios of medians and median
paired ratios)≥1.01; both summaries for every workload≥0.98; median peak RSS for
every workload≤1.05baseline. Failure rejects this candidate without rescue runs
or representation retuning to reinterpret the screen.

A passing screen requires two independent confirmations, each19small/11large
pairs, each meeting every gate separately. Reverse configured executable roles
in the second confirmation and normalize ratios. No pooling or favorable sample
selection. Only then consider promotion and a fresh direct original-native
milestone. Never multiply historical ratios or infer speed from smaller structs.
