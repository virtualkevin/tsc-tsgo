# Results and next experiment

All 12 baseline/observer-disabled/observer-enabled controls passed on pinned inputs
with four checker owners and empty diagnostics. Normal/race/checkptr each passed
four tests, including the real-checker history comparison. Five Python accounting
and aggregation tests pass. Independent verification and exact analysis
reproduction passed. No caps saturated; no keys were dropped.

| Workload | Queries | First keys | Completed repeats | Changed result ID/nil | Created instantiations/types/symbols |
| --- | ---: | ---: | ---: | ---: | --- |
| typeorm | 1344 | 334 | 1010 | 0 | 0 / 0 / 0 |
| trpc | 214 | 40 | 174 | 0 | 0 / 0 / 0 |
| vscode | 251592 | 16327 | 235265 | 0 | 0 / 0 / 0 |
| sentry | 11266463 | 129334 | 11137129 | 0 | 0 / 0 / 0 |

Assignable/subtype relation size growth was also zero for all observations.
These counters are incomplete effects; stable result IDs and zero counts are not
a purity proof. Timers in raw data include observer overhead and are not CPU or
wall-time performance. No PERF.md entry or speedup claim.

Sentry has 11,154,404 inactive-context kind-2 calls (JSX or ordinary object literal),
of which 11,054,661 repeat tracked keys. Two intersection-type flag cohorts alone
account for 11,113,418 kind-2 calls. VS Code has 118,246 inactive kind-1 calls,
133,256 inactive kind-2 calls, and 90 active kind-2 calls. Aggregate classifier
flags describe entry state, not immutable type ownership or context independence.

The evidence favors cheaper access to existing completed property results rather
than eliminating repeated instantiation. Existing mapped/instantiated symbol
helpers already cache resolved types. Do not add a broad type/name result cache
from this observation.

Next concrete experiment: fuse the already-resolved intersection property lookup
path, retaining the original `getTypeOfSymbol` call and its effects. A restricted
fast path can inspect the original type on each call and require all of:

- exact intersection type flags, no mapped-type dispatch;
- existing never-intersection computation says not-never;
- existing apparent type is exactly the input type;
- the existing non-augmented property cache contains the requested symbol;
- the symbol is not read-partial.

Under those guards, both original reductions and apparent conversion are already
resolved identities; the non-augmented property lookup returns that same symbol.
There is no new persistent cache or precomputation. Call `getTypeOfSymbol` normally
and fall back to the untouched original path on any guard failure. Guards must
be checked against current state, not remembered after semantic work. A focused
stateful differential must test stale/replaced cache entries, partial entries,
apparent-type changes, never flags and symbol type changes, plus original query
histories and required full compiler validation before performance screening.

This is a source-backed candidate contract, not implemented or proved here. Its
likely scope is limited; it is not an established route to 10×. It differs from
the rejected paired-property-cache layout: it retains both original maps, their
lookup priority, and their population rules.
