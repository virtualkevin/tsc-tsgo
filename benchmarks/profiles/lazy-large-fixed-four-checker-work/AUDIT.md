# Fixed-four checker creation counts

This is an untimed architecture probe against the preserved lazy Go compiler and original native compiler, using the same binary hashes, pinned project inputs, libraries, runtime controls, and options as `../lazy-large-single-checker-work/comparison.json`, except `--checkers 1` becomes `--checkers 4`. Root compiler changes after that preserved binary was built do not affect this comparison.

Go defaults to four checkers. Native defaults to automatic parallelism, with CPU/memory/library adjustments, and is explicitly fixed to four in this probe. The collector records the actual native worker indices rather than assuming the request cannot be reduced.

## Count coverage

Go `Program.TypeCount` and `Program.InstantiationCount` in `internal/compiler/program.go` call `ForEachCheckerParallel` and atomically sum each checker's counters. `checkerpool.go` visits every pool slot under its lock. This covers all checker-created Types and counted instantiation-worker calls, including checker initialization. The uint32 aggregation is not near overflow for these workloads.

Native `parallel-check.ts` includes final Type and instantiation counts in each `CheckerResult.stats`, and `record` prints every returned generation. Recycling can reuse a worker index, so the collector sums all records rather than deduplicating indices. It checks the final completion marker, absence of worker failure messages, and equality of summed checked-file counts with the planned file count. The worker records alone do not include the native reporting-main checker: `mainThreadChecks(shared)` returns false for the native shared-graph runtime.

Native `tsc-compile.ts::statisticsOf` reports `compilerProgram.checked.checker.typeCount`, which is that separate reporting checker, not the workers. Therefore total native Types equals all worker Type counts plus the extended-diagnostics Types value. Parallel `compileInParallel` does not call `traceSingleChecker`, and statisticsOf does not populate Instantiations, so reporting-main instantiations are unavailable. The report retains worker-only instantiations, marks total native Instantiations unavailable, and does not calculate a native all-checker instantiation ratio. No zero value is assumed from the placeholder extended-diagnostics Instantiations row.

With no emit and incremental/composite disabled, the worker trace is taken after file semantic checks and worker-global diagnostics. Input counters Files/Lines/Identifiers are checked against the earlier single-checker sample. Binary and complete listed input hashes are verified before and after each project. A 180-second overall collector budget bounds the experiment; incomplete runs preserve partial logs and do not extrapolate counters.

## Interpretation

The four/single ratios cover creation counts only. Extra Type allocations can include repeated initialization, repeated dependent-type work, different traversal/cache behavior, and scheduling effects. They do not identify duplicate semantic identities, equal-cost work, or an achievable time saving. Native work stealing and retirement can vary the counts between runs; this report contains one sample per workload/compiler. Concurrent validation makes elapsed time unsuitable for performance comparison. Raw stdout/stderr retain compiler-produced time and memory fields solely for trace completeness; they are not measurement results.

A higher Go creation ratio than native would motivate further static dependency-affinity or sharing experiments, but would not prove either safe. Cross-checker semantic caches depend on checker ownership, mutable inference state, diagnostics, and lifetime. Single-checker execution also trades away parallelism, so lower creation counts alone do not establish that it is faster.

## Collected results

All four compiler invocations completed successfully within the overall budget. Each native run produced exactly four worker generations, indices 0–3; no retirement or failure appeared. Worker file totals matched the plans: Sentry 9,634 and VS Code 10,408.

| Workload | Compiler          | Counter        | One checker | Four checkers | Four / one |
| -------- | ----------------- | -------------- | ----------: | ------------: | ---------: |
| sentry   | Original native   | Types          |   1,792,408 |     2,525,760 |     1.409× |
| sentry   | Preserved lazy Go | Types          |   1,798,696 |     2,725,687 |     1.515× |
| sentry   | Preserved lazy Go | Instantiations |   5,974,204 |    11,722,854 |     1.962× |
| vscode   | Original native   | Types          |   3,270,735 |     4,030,100 |     1.232× |
| vscode   | Preserved lazy Go | Types          |   3,267,740 |     4,277,160 |     1.309× |
| vscode   | Preserved lazy Go | Instantiations |   4,217,548 |     5,915,965 |     1.403× |

Native worker-only Instantiations were 7,920,617 for Sentry and 5,522,185 for VS Code; their reporting-main contributions remain unavailable. No total native Instantiations ratio is reported. Reporting-main Types were 83 and 85, respectively, and are included in the table.

The clearest measured creation-count growth is Go Sentry instantiations (1.962×); Go Type growth is 1.515× for Sentry and 1.309× for VS Code. Native Type growth is 1.409× and 1.232×. This supports a bounded checker-count/assignment experiment, especially on Sentry, without establishing that fewer checkers or sharing mutable semantic state would improve elapsed time. It does not isolate exact duplicate identities.
