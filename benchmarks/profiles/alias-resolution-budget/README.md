# Alias resolution feasibility

Offline attribution of the preserved normal-build CPU profiles. Every source
profile and decoded raw profile hash is checked, and total sampled CPU reconciles
with the earlier property-work audit. The unchanged tested stack parser counts
recursive matches once and partitions samples into exclusive category combinations.
Inclusive columns overlap and include callees; do not sum them or treat them as
removable wall time. Sampling resolution is coarse on the small workloads.

| Workload | Alias resolution CPU % | Alias-target dispatch CPU % | Entity-name resolution CPU % | Module exports CPU % |
|---|---:|---:|---:|---:|
| trpc | 2.538 | 2.538 | 2.538 | 1.523 |
| typeorm | 0.792 | 0.967 | 0.616 | 0.176 |
| vscode | 1.610 | 1.939 | 1.711 | 0.254 |
| sentry | 1.440 | 1.958 | 1.226 | 0.247 |

Source review of retained checker.go:

- resolveAlias uses checker-local AliasSymbolLinks, pushes/pops the type-resolution
  stack, returns the checker-local unknownSymbol sentinel on unresolved/cyclic
  requests, and emits a circular-definition diagnostic after a failed pop.
- resolveIndirectionAlias obtains the merged target and propagates the target's
  typeOnlyDeclaration into source links. A target pointer alone omits this effect.
- getTargetOfAliasDeclaration dispatches across import/export forms and JS alias-like
  expressions; it is not merely a syntax-only module table lookup.
- The older symbol-type census's alias category observes resolved type requests,
  not this complete alias-target protocol. It cannot establish effect-free target
  sharing or safe cross-checker symbol identity.

Decision: do not implement a standalone shared alias-target cache from this
hypothesis. The measured direct footprint is small and the required effects are
not captured by a pointer-only value. This does not prove no local improvement is
possible, nor rule out alias handling as part of a larger immutable semantic model.
It does rule out treating this as an established order-of-magnitude mechanism.

The existing union-construction audit was also checked before proposing another
batch-insertion experiment: its direct CPU budget was already recorded as small.
Neither deferred path is reinstated. Production and PERF.md remain unchanged.
