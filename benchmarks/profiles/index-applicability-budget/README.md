# Index applicability: cost and effect audit

Offline analysis of the preserved normal-build CPU samples for retained Go
binary 8fe4bd80 / source 216d40c7. This is a diagnostic investigation, not a new
workload timing, implementation optimization, or proof of redundant work.

`analyze.py` reads the archived raw stacks from normal-map-attribution, checks
raw hashes against inputs.json and original profile hashes against the retained
capture manifest, then reuses the existing stack partition parser. Each sample
is counted once per inclusive category, including recursive/inlined frames.
Exclusive buckets partition the entire profile. `--verify` reproduces the report
and checks current checker/relater source hashes. No missing temporary profile
files are needed and no profile data is silently regenerated.

| Workload | Index lookup inclusive CPU % | Lookup outside relation entry % | Lookup with full relation checking % |
| --- | ---: | ---: | ---: |
| tRPC | 0.508 | 0.508 | 0.000 |
| TypeORM | 0.264 | 0.176 | 0.000 |
| VS Code | 0.177 | 0.133 | 0.019 |
| Sentry | 6.631 | 0.271 | 6.072 |

Categories overlap. Outside-relation samples still include other callees;
they are not exact local instruction counts. No sample means no observed cost,
not absence of execution. The tRPC capture is particularly coarse. Historical
sampled CPU cannot be substituted for current wall time or an Amdahl forecast.

## Source-linked compatibility findings

- `checker.go:findApplicableIndexInfo` processes every non-string index in input
  order through `isApplicableIndexType`; only afterward does it use a string
  fallback. With multiple applicable entries it creates a synthetic IndexInfo
  and intersects the value types. Readonly/value fields are read after the
  relation queries. Moving those reads earlier would need a reentrancy argument.
- `relater.go:isTypeRelatedTo` already normalizes literal freshness, checks
  identity and primitive cases, and consults relation storage for object pairs.
  A new cache cannot assume all existing invocations perform uncached work.
- `checkTypeRelatedToEx` derives its relation budget from relation.size(), records
  overflow failures, and can report an overflow at c.currentNode even when
  errorNode is nil. Returning a cached boolean is therefore not sufficient to
  establish identical effects, diagnostic history or limit behavior.
- A multiple-match result allocates a new IndexInfo at the current call site.
  Reusing that object introduces an identity change that needs an explicit
  observable-contract audit; equal printed types do not settle it.
- Template matching is not the main measured explanation: all template-matching
  samples combined are only 0.362% of Sentry CPU and 0.019% of VS Code CPU.
  The existing unexecuted template-entry-guard draft is not thereby validated.

## Decision

Do not implement a broad index-applicability memoization cache from this evidence.
It provides neither a context-complete key nor an effects/identity contract.
Do not pursue the lookup's small scratch-list allocation as an order-of-magnitude
strategy: the observed cost is concentrated in semantic relation callees, and
this family is tiny on three workloads. Existing rejected numeric/prehashed
relation-table experiments remain rejected; these samples do not justify
rerunning them unchanged.

The remaining concrete diagnostic question is which relation source/target
forms account for Sentry's index-related work, whether they repeat, and which
state transitions they cause. Any future census must preserve call order,
avoid extra semantic queries, distinguish construction identities from stable
source origins, and measure observer effects before proposing shared results.
No production source, runtime settings, or PERF rows change in this audit.
The 10× native-relative objective remains unmet.
