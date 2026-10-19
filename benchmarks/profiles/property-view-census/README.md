# Property-view coverage and materialization census

Diagnostic observer of the rejected property-relation-view-snapshot candidate.
Production source/default remain unchanged. This is not another performance run
of the rejected candidate and cannot rescue its failed tRPC floor.

Per-checker scalar counters record existing lookup, entry preparation, type-query,
relation and clone/materialization events. Reporting runs after CLI checking under
the existing checker-pool locks, without constructing checkers, forcing queries,
retaining extra symbol/type roots, or forcing GC. Counter arrays themselves and
branches change cost; observer timings are not performance evidence.

Cache-entry-prepared counts every successful prepare request, including creation;
it is not a reuse-only count. Entry-materialized counts transfer of an existing
entry into a newly created symbol. Created-minus-materialized at report time
includes both potentially unreachable and retained entries; it is not a liveness
measurement or a claim of permanent savings. Relation fallback categories are
ordered and partition attempts together with accepted relations. Private rejection
is a subset of accepted relations. Query counts include recursive write-to-read
queries and can exceed hits/misses/delegated/kept totals.

Controls compare the exact uninstrumented rejected candidate (0cee0116), observer
disabled, and observer enabled on the pinned physical inputs for all four projects.
The retained workspace source remains216d40c7. All controls must have clean matching
output and unchanged input hashes. No native-relative gain is inferred. Diagnostic
coverage can guide a structurally different design; gates must not be retuned.

## Verified diagnostic result

All14 focused tests passed normal/race/checkptr, all12 workload controls passed,
and independent readback verified exact inputs, artifacts and counter invariants.

| Workload | Lookups | Returned views | Kept views | Entries created | Later materialized | Entries not materialized at report | Clone constructors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| typeorm | 390699 | 2710 | 1862 | 486 | 287 | 199 | 176326 |
| trpc | 37861 | 3470 | 1308 | 1240 | 839 | 401 | 37073 |
| vscode | 8468315 | 35841 | 21800 | 6642 | 4772 | 1870 | 1857832 |
| sentry | 33052864 | 20748 | 10042 | 5155 | 3501 | 1654 | 1686429 |

The current consumer reaches only0.69%/9.17%/0.42%/0.063% of lookup calls on
TypeORM/tRPC/VSCode/Sentry, including kept originals. Most newly created entries
later materialize. This supports investigating earlier bulk enumeration and view
eligibility boundaries before tuning the lookup cache. It does not identify which
exclusion dominates, prove enumeration is the sole cause, or estimate CPU savings.
The rejected candidate remains rejected; no new PERF.md rows are appropriate.
