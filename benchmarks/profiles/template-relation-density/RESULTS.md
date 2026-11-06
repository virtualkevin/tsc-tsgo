# Fixed tile density results

All three focused tests passed normally, with race and checkptr; all twelve
retained/disabled/enabled controls passed clean diagnostics and input checks.
Independent raw-log, hook and histogram readback passed. No checker reached the
131072-tile cap; no writes were dropped or unrepresentable in the selected domain.

| Workload | Domain ordinary failure writes | Plain distinct pairs | Tiles | Mean pairs/tile | Singleton tiles |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 69 | 69 | 32 | 2.156 | 25 |
| trpc | 0 | 0 | 0 | 0.000 | 0 |
| vscode | 9524 | 9524 | 699 | 13.625 | 303 |
| sentry | 3579152 | 3579148 | 25709 | 139.218 | 1542 |

Sentry had four non-plain failure writes, which were counted but excluded from
tile payloads. All recorded plain writes were distinct. Sentry had17826 tiles
with65–256 populated cells,2151 with17–64,2722 with5–16,1468 with2–4, and1542
singletons. The32-byte bitmap payload totals822688bytes for its25709 tiles,
before directory/allocation costs. This is not an RSS estimate or runtime gain.
TypeORM is sparse and tiny; tRPC did not exercise this selected failure domain.

These are *ever-written ordinary plain failures*. The hook does not establish
that every bit would remain live after later successful/overflow writes. All
result values, resets and overwrite transitions still need preservation.

## Observer-cost context

Single invocations in retained/disabled/enabled order; substantial timing
variation is visible. No statistical/performance claim or PERF.md row follows.

| Workload | Retained seconds | Disabled seconds | Enabled seconds |
| --- | ---: | ---: | ---: |
| typeorm | 3.900 | 3.582 | 4.084 |
| trpc | 0.791 | 0.780 | 0.827 |
| vscode | 60.626 | 76.374 | 52.885 |
| sentry | 41.104 | 42.510 | 41.238 |

## Decision

The measured density justifies an isolated compiler integration of the fixed
tiled-negative backend, particularly for Sentry. It does not justify skipping
comparisons or adding a semantic-result cache. Preserve the original query/write
sequence, relation-count budgets, maybe-stack handling, identity and intersection
state, generic key construction, overflow/reliability bits, and diagnostic replay.

The planned integration must specialize only the measured template-key domain;
other keys retain full128-bit hashes without the rejected generic numeric-key
interner. A tagged key must propagate through all four getRelationKey sites and
the maybe stack/set. The one direct test reset of assignableRelation.results must
reset the whole storage representation while preserving the Relation pointer.
Any hash-to-exact-ID key-equivalence argument must explicitly state its assumptions;
the standalone bit-layout theorem does not prove it.

Retained source/default executable and PERF.md are unchanged. Compiler integration,
full correctness validation, workload screening and confirmations are outstanding.
The10× original-native objective remains unmet.
