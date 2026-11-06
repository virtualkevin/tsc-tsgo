# Current retained-Go A/A calibration

Both configured labels execute the exact same retained node-pointer Go binary,
source and provenance sidecar. No candidate implementation is involved. The
purpose is to observe finite-sample label variation under the current harness,
not to estimate an optimization, subtract a noise correction, reopen a rejected
candidate or infer a universal noise/confidence bound.

Freeze before capture: nine alternating pairs each for TypeORM/tRPC and five
for VS Code/Sentry; one warmup; fresh processes, warm filesystem, default
runtime/checker settings, matched GNU-time peak RSS and pinned physical inputs.
Both labels use identical arguments and environments. Keep every observation;
failures preserve partial evidence and stop the stage without selective retries.
No builds, tests, source edits, profiling or Git work during timing.

Report ratios of medians, medians and ranges of paired ratios, absolute-log
median deviations, RSS summaries and order. The labels have no true compiler
implementation difference, so non-unit ratios do not represent a compiler
speedup. Dependence, drift and external host effects remain possible. Historical
A/A evidence and prior screens stay separate. Do not pool or rescale their data.

This calibration does not change any existing candidate acceptance thresholds
or justify a retrospective rescue run. Any future protocol change requires its
own prospective rationale and a new frozen design. The original native 10x
performance target remains unchanged and unmet. Four measured compiler rows may
be recorded in PERF.md only with explicit calibration-only labels.
