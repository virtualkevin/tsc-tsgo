# Map callers in retained normal-flag CPU profiles

Offline reanalysis of `node-pointer-normal` profiles from retained binary8fe4bd80/source216d40c7. No new compiler run, production change, diagnostic flags or performance measurement. `inputs.json` links decoded data to the original profile hashes and exact pprof commands; `raw-profiles.tar.gz` preserves the decoded stacks. `verify.py` reproduces the report and checks original hashes against the retained capture manifest. Four synthetic tests cover nested-map deduplication, inline generic frames, runtime-only callers and unparsed sampled locations.

Each sample containing a builtin-map frame is assigned once to the nearest project caller after its innermost map frame. Costs include hash/allocation callees and are not lookup counts, isolated latency or removable work. Different callers sum to the map-path total; inclusive caller totals from other reports cannot be added to them. The small tRPC capture has coarse samples, so ranks are particularly uncertain.

| Workload | Map-path sampled CPU |
|---|---:|
| tRPC | 17.259% |
| TypeORM | 12.225% |
| VSCode | 18.767% |
| Sentry | 25.430% |

Sentry's largest individual map caller is Relation.get (5.306% of all sampled CPU); numeric and prehashed relation-storage experiments have already been rejected and this observation does not reverse those results. Resolved member lookup is2.221%, and union/intersection property cache lookup1.588%. VSCode is more distributed: reference-kind LinkStore1.287%, getMergedSymbol1.236%, Relation.get1.223%, resolved member lookup1.027%.

A distinct diagnostic lead is `getMergedSymbol` (VSCode1.236%,Sentry0.716%): source currently probes `c.mergedSymbols` for every nonnil symbol; all writes found in the checker go through `recordMergedSymbol`. No delete or reset exists beyond checker initialization. The profile does not reveal its hit/miss ratio or key cardinality. Before proposing a negative-lookup filter, measure those quantities and representative filter occupancy using checker-local instrumentation, preserve semantic results, and quantify observer effects. A filter must never have false negatives, must keep the authoritative map and its typed roots, and must not mutate shared symbol flags without a concurrency design. This is a bounded diagnostic lead, not a route to10× or a justified production change.

Run tests with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s benchmarks/profiles/normal-map-attribution -p test_analyze.py -v`, and reproduction with `PYTHONDONTWRITEBYTECODE=1 python3 benchmarks/profiles/normal-map-attribution/verify.py`.
