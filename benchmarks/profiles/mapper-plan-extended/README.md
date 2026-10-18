# Mapper plan nested histories and cost envelope

This extends the isolated prototype from9abc12d without changing its implementation or production. The prior deep-chain result excludes construction and does not establish workload benefit. No candidate is promoted.

Added deterministic histories use128seeds, up to five nested merged/composite levels, and24queries per independent execution. Leaves observe changing step/call state, return input or other fixture types, and panic on each17thcall. The independent recursive control-flow evaluator and compiled plan must produce the same ordered leaf/instantiate trace, result identity labels, panic sequence, and subsequent-query behavior. Compilation must execute no leaves. This is finite component testing, not a pinned-upstream API replay or formal proof.

The prepared mechanism benchmark measures1/2/4/8/32leaf chains, separate recursive evaluation, plan evaluation, and compilation over an existing graph. Five fixed-order100ms observations each; no workload speedup claim. Compilation allocations include discarded growth buffers, so B/op is not retained plan size. It excludes graph construction and remains sensitive to fixed-order and host effects. It must finish before interpreting the cost envelope or changing the plan.

Normal/race/checkptr validation is running. Next: run costs only after validation, independently read raw logs/source hashes, and decide how to integrate only where amortization and representation costs warrant it. Full compiler correctness and workload performance gates remain required.

## Completed validation and decision

Validation58719 terminal0: all five tests passed normal/race/checkptr. Benchmark61460 terminal0; verify.py independently checked exact source hashes, raw test coverage and all75observations.

| Leaves | Recursive ns | Plan ns | Compile ns | Compile bytes allocated | Idealized reuse to repay compile |
|---:|---:|---:|---:|---:|---:|
|1|1.931|8.105|155.2|64|no evaluation gain|
|2|6.604|11.22|338.8|128|no evaluation gain|
|4|12.52|15.2|735.1|256|no evaluation gain|
|8|28.07|24.55|1326.0|512|377|
|32|268.0|103.6|9781.0|4296|60|

Decision: do not integrate blanket plan compilation. Shallow chains regress; deep-chain benefit requires enough reuse and ignores added GC/memory cost. Continue the reusable-plan design by specializing immutable simple-substitution spans, preserving effectful leaves and their order. This is a new representation change to validate, not a performance claim or a request to relax workload gates. No production source, baseline, or PERF rows changed.
