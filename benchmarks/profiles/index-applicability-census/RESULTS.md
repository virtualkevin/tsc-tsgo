# Results and next decision

All three focused tests passed normally, under race, and under checkptr. All 12
retained/disabled/enabled workload controls completed with identical pinned inputs
and empty diagnostics. The independent raw-log/count verifier passed. This is a
validated observer, not a production optimization or whole-compiler proof.

| Workload | Calls | Tracked pairs | Completed repeats | Untracked calls after cap | Changed tracked results |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 71110 | 2519 | 68591 | 0 | 0 |
| trpc | 4911 | 878 | 4033 | 0 | 0 |
| vscode | 988516 | 31138 | 957378 | 0 | 0 |
| sentry | 18652240 | 524288 | 3462157 | 14665795 | 0 |

Sentry saturated all four 131072-pair tables. The other workloads did not saturate.
Sentry's 14665795 dropped calls are not known unique pairs; they may repeat one
another. The census cannot extrapolate tracked-repeat behavior to that population.
All tracked-repeat exclusive instantiation and relation-size-growth counters were
zero. This is narrower than an effects-purity result: replacements, reliability
flags, diagnostics and other mutable state were not observed.

Sentry made 15416416 template-to-template calls (8998888 with the coarse active
context flag, 6417528 without). Their aggregate 2571337 instantiations accounted
for all observed instantiations in applicability calls. Sentry also made 1748100
string-literal-to-template calls without active context; these grew the relation
cache by 869137 entries. These are logical size deltas, not allocation bytes or
CPU savings. Template calls can be cheap cached repeats; call counts alone do not
rank their cost.

## Observer controls

Single invocation seconds, in baseline/disabled/enabled execution order. These
are diagnostic overhead context, not matched repeated performance measurements,
confidence intervals or speedup claims. No values are added to PERF.md.

| Workload | Retained seconds | Observer disabled seconds | Observer enabled seconds |
| --- | ---: | ---: | ---: |
| typeorm | 2.857 | 2.798 | 2.586 |
| trpc | 0.470 | 0.524 | 0.569 |
| vscode | 42.456 | 39.527 | 41.706 |
| sentry | 32.245 | 30.058 | 35.052 |

## Decision

The new evidence identifies a specific domain for further work: template-key
relation storage and traversal in Sentry, not generic index-list scratch space.
Do not add an applicability-result cache from stable booleans alone. The full
relater propagates reliability bits, counts cache entries against complexity
limits, records overflow failures, and reruns ordinary failures for diagnostic
elaboration. The earlier finite-string entry guard also changes relation-cache
population; its draft tests do not establish preservation of all those effects.

A storage experiment should keep all original semantic queries, cache writes,
logical size accounting, result/reliability/overflow bits, and diagnostic replay.
A compact representation specialized to these source/target forms would need
actual pair-density/occupancy evidence, exact key equivalence across intersection
states and identity ordering, and preservation of maybe-stack keys. The current
census does not measure that density and does not justify a block size or layout.
Previously rejected generic numeric/prehashed relation tables remain rejected;
this is not authorization to repeat those unchanged experiments.

Production source and default binary are unchanged. No 10× speedup is established.
