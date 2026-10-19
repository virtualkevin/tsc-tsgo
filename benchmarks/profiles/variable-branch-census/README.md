# Uncapped variable-like resolver branches

Diagnostic overlay on retained production. Observes all calls to
getTypeForVariableLikeDeclaration, not just symbol cache misses. Classifiers are
inserted at existing branch decisions and do not run additional semantic helpers.
The final selected branch receives the call's interval, including work spent on
preceding unsuccessful alternatives. These are not isolated helper timings.

Nineteen labels distinguish loops, binding, catches, annotations, auto types,
parameter special cases/contextual typing, initializers, instance/static flow or
base types, JSX booleans, and no inferred type. Unclassified is reserved for an
incomplete path and is rejected by successful-control validation. Declaration kind,
check mode, optionality request, and nonzero recorded context are extra dimensions.
Zero recorded context is not a claim of context independence.

There is no origin map, first-seen cap or retained AST/type graph. Every observed
call contributes to aggregate rows. Nested observed calls are subtracted for
exclusive elapsed/instantiation fields. Other nested work remains. Time is
instrumented elapsed time, not sampled CPU or a speedup estimate. NonNil counts
non-nil results; ErrorResults counts the checker error-type sentinel, not emitted
diagnostics. uint32 counter deltas cannot detect a full wrap within one call.

Production source and defaults are unchanged. All three focused tests passed in normal/race/checkptr modes, with independent
raw-log readback. All 24 baseline/disabled/enabled controls at one/four checkers passed with exact
inputs and empty diagnostic output. Independent verification passed. `audit_source.py` verifies that removing
only explicit observer additions restores byte-identical retained checker source;
this structural check is not a proof of observer noninterference. Output uses the existing pool locks after ordinary
CLI compilation. No semantic result sharing, optimization, or PERF row is claimed.


## Verified findings

Capture HEAD: `1a66583`. The initial capture was externally terminated after 14
completed controls; the signal audit records Codex PID 3841 as sender, with no
known reason. `report.json` preserves that failure. `report-resumed.json` preserves
the exact 14-run prefix and adds only the ten unfinished controls. `verify.py`
checks both reports/controllers, source/binary pins, input hashes, focused raw test
logs, all 24 outputs, and all eight census snapshots. `readback.json` records the
successful verification. `summary.json` reconciles both branch and full recorded
cohort totals; the original fixture failure remains preserved.

| Workload | Calls, 1 checker | Calls, 4 checkers | Initializer calls, 4 | Initializer exclusive instrumented seconds, 4 | Annotation exclusive instrumented seconds, 4 |
|---|---:|---:|---:|---:|---:|
| typeorm | 41648 | 65143 | 17889 | 1.018722 | 0.192010 |
| trpc | 6717 | 10258 | 1632 | 0.197553 | 0.059466 |
| vscode | 1023961 | 1335771 | 540794 | 19.009814 | 3.404676 |
| sentry | 444191 | 601490 | 212069 | 21.460903 | 3.734168 |

Initializer inference leads recorded elapsed work in all four workloads, at both
checker counts. Annotation calls are more numerous in four-checker runs but have
substantially less recorded elapsed work. Neither count differences nor elapsed
differences establish reusable results. In particular, zero recorded context
ignores inference and flow state and does not establish context independence.

`checkDeclarationInitializer` already uses `getQuickTypeOfExpression` followed by
contextual checking or `checkExpressionCachedEx`. It may pad parameter binding
patterns; widening may report implicit-any diagnostics for JavaScript. Thus an
origin-keyed initializer cache would skip existing semantic effects and cannot be
justified by these aggregates. The next implementation must address the expensive
expression/type construction beneath this path with a precise ownership and
stateful replay contract, rather than assuming an uncached declaration resolver.
These measurements do not establish a 10× mechanism or any production speedup.
