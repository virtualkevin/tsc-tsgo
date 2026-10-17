# Frozen indexed-storage comparison policy

Frozen after same-binary A/A calibration and before any handle-only or indexed-candidate workload timings. All candidate binaries and correctness evidence already exist. This is a practical experimental decision rule, not a statistical confidence claim or a redefinition of the10× objective.

## Calibration evidence

Identical saturated binaries produced ratios of medians1.007/1.066/0.992/1.021 for TypeORM/tRPC/VSCode/Sentry, but paired medians0.995/1.048/1.001/0.978. One Sentry pair reached0.812. All samples remain included. These finite data show that modest effects and disagreeing summaries are insufficient for promotion; they do not prove stationary or independent noise or identify its cause. RSS label medians differed by less than1% in this run, which is not a universal memory-noise bound.

## Screening

Run three separate paired comparisons: unchanged saturated baseline versus handle-only control; unchanged saturated baseline versus indexed candidate; handle-only control versus indexed candidate. Use9alternating pairs for TypeORM/tRPC and5for VSCode/Sentry, one warmup each, identical GNU time wrappers, default runtime/checker/GC settings and pinned inputs. Keep every sample. Screening comparisons diagnose allocation-handle cost, total effect, and indexed-lookup effect respectively. None alone promotes the candidate.

Report per-workload ratio of medians, median of within-pair time ratios, all paired ratios, and median peak RSS. Ratios are always normalized to unchanged/control time divided by indexed/handle time as appropriate. Report the unweighted geometric mean across all four workloads separately for each time summary. Do not pool raw durations across differently sized projects or choose a favorable summary after seeing results.

Proceed to confirmation only if the indexed-versus-unchanged screen satisfies both aggregate time summaries>=1.01, both per-workload time summaries>=0.98 for every workload, and indexed median peak RSS<=1.05times unchanged median peak RSS for every workload. A screen that misses a gate is not promoted. Its evidence may motivate a changed implementation or an untimed mechanism investigation, but not opportunistic extra samples of the same implementation to chase a passing result. The handle-only comparison is attribution evidence, not an adoption reference.

## Confirmation and retention

If screening qualifies, run exactly two fresh confirmation suites against the unchanged baseline, each with19pairs for TypeORM/tRPC and11pairs for VSCode/Sentry, plus one warmup. In the second suite swap executable roles in the existing harness, retaining its alternating order; normalize all results back to unchanged/indexed afterward. This counterbalances the extra first-position sample in odd-sized suites without changing the timing harness. Freeze the two configurations before either confirmation starts.

Each confirmation must independently meet the same aggregate>=1.01, per-workload>=0.98, and RSS<=1.05gates for both declared time summaries. Combined favorable pooling cannot rescue a failed confirmation. If either suite is inconclusive or fails a gate, restore the unchanged implementation and preserve all evidence. These finite empirical guards do not establish confidence intervals or universal performance. Report the individual workload tradeoffs even when retained.

## Integrity and target accounting

No concurrent builds, tests, profiles or other benchmark suites during timing. Preserve exact binary/sidecar/source/config/harness/HEAD identities and existing input/diagnostic/environment/wrapper/sample integrity gates. Infrastructure failures preserve partial evidence and require an identified fix before a separately named full retry; never merge a partial run with a retry or exclude slow observations. Do not tune runtime settings to rescue this storage experiment.

After the retention decision, compare the retained compiler directly with the pinned original native tsc-ts on all four workloads under matched wrappers/settings. Do not multiply historical Go/Go ratios. The10× target is achieved only with direct evidence meeting the original correctness and workload scope. No performance result here changes unsupported-conformance coverage or substitutes for compiler validation. No subagents are used.
