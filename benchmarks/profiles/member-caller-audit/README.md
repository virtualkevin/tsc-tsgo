# Member lookup caller audit

Offline analysis of retained normal CPU profiles, after the bounded miss-name census found Sentry misses spread across 25,851 names. No new timings or production changes. `source.json` identifies the inspected source and input archive; each raw profile is checked against the earlier capture hash before analysis.

Run `PYTHONDONTWRITEBYTECODE=1 python3 benchmarks/profiles/member-caller-audit/analyze.py` to reproduce the committed report exactly. Seven synthetic tests cover wrapper attribution, recursive counting, nested map callees, generic-map exclusion, denominator accounting, inline frames, inclusive operations and rejection of unparsed locations.

Each member-category sample is counted once, using its innermost `getResolvedMember`. Attribution walks outward past only `getPropertyOfObjectType`, `getPropertyOfTypeEx`, and `getPropertyOfType`. `memberPath` includes pending-member resolution and all other callees; it does not isolate materialized misses. `memberDirectStringMap` requires the nearest project caller above the innermost specialized string-map runtime entry point to be `getResolvedMember`. Generic map paths are excluded. Inclusive operation totals count each matching sample once even under recursion. Categories overlap and must not be added. None measures call frequency, hit/miss status, avoidable work, wall time, or a speedup.

| Workload | Member path CPU % | Direct member string-map CPU % | Inclusive propertiesRelatedTo CPU % |
|---|---:|---:|---:|
| tRPC | 1.015 | 0.508 | 12.690 |
| TypeORM | 2.111 | 0.704 | 5.189 |
| VS Code | 2.453 | 1.027 | 6.984 |
| Sentry | 3.488 | 2.221 | 10.325 |

For Sentry, direct member-map samples attributed to `propertiesRelatedTo` account for 1.325% of total CPU, versus 0.140% through `createUnionOrIntersectionProperty`. This changes the immediate investigation target from union-property construction to structural comparison. Samples do not prove which caller produced the census misses.

## Source inspection and next design boundary

`relater.go:4130` handles identity and tuples separately, then performs an unmatched-property pass and fresh-object checks before the final property comparison loop. The final loop traverses target properties in target order, applies exclusions/prototype/numeric/optional predicates, and calls `getPropertyOfType(source, name)`. Missing source properties cause no comparison. Wide optional targets against small source types are therefore a plausible source of sparse work, but their actual frequency and dimensions have not been measured.

A candidate sparse traversal must preserve target order (which affects recursive comparisons, diagnostics and limits), all preliminary checks, Object/Function augmentation, module type-only filtering, and on-demand inherited members. Simply reversing source/target iteration changes these semantics. `getPropertyOfTypeEx` also performs reduced/apparent-type resolution; fully materialized members alone do not prove that skipping calls is safe. Source/target tables can be published during resolution and shared by aliases.

Next useful evidence: count final-loop target candidates, actual source hits, and source/target sizes under precisely defined ordinary-object eligibility, without materializing additional types or retaining semantic objects. Only a substantial eligible sparse workload would justify building a target-order index and a proof of stable membership. No negative cache or special-name shortcut is proposed from these samples.
