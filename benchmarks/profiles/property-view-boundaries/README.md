# Property-view lookup boundaries and bulk callers

Diagnostic extension of property-view-census on the rejected0cee0116 candidate.
Production source/default remain unchanged. This is not a benchmark or rescue run.

An ordered classification partitions every propertyViewOrSymbol lookup into twelve
categories: nonobject, module, no pending state, already materialized name layout,
resolving, bases, missing source, duplicate names, missing/skipped entry, name/kind
mismatch, already-instantiated source, and eligible. Classification only reads
existing fields and maps; it does not resolve types, create symbols, or modify
eligibility. Eligible counts must equal actual returned-view counts. Categories
are ordered exclusions, not independent overlapping opportunities.

At actual pending-table materialization, exact scalar counters record events and
source slots. Every256th event per checker, starting with the first, samples up to
12 caller PCs and records symbolic stack strings plus sampled slot counts. This is
systematic sampling, not a random unbiased estimator; do not multiply by256 or
interpret slots as clones, live objects, CPU time, or saved cost. Truncated stacks
are marked. No semantic symbol/type pointers are retained by the observer.

All previous view/counter tests remain, with added boundary and sample-lifecycle
checks. Three workload controls per project compare the uninstrumented rejected
candidate against observer disabled/enabled, with pinned inputs and clean output.
Counter and sample invariants, raw files and source/binary/controller hashes must
be verified before drawing conclusions. No PERF.md rows are appropriate.

## Verified results

All16 focused Go tests passed normal/race/checkptr, all12 workload controls passed,
and independent readback verified source/input hashes and counter/sample invariants.

| Workload | No pending state | Materialized layout | Bases | Bulk materializations | Sampled unmatched-property calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 66.73% | 15.17% | 8.47% | 10767 | 34 |
| trpc | 24.14% | 31.64% | 23.77% | 3618 | 13 |
| vscode | 75.90% | 14.06% | 7.17% | 103103 | 206 |
| sentry | 95.22% | 2.60% | 0.40% | 121244 | 156 |

getUnmatchedPropertiesWorker is the leading sampled non-dispatch caller on every
workload. Source inspection confirms its target getPropertiesOfType call forces
full enumeration before presence checking. Other sampled consumers include union
property enumeration, subtype reduction, identity relations, key extraction and
never-reduction. These samples locate architectural boundaries; they do not measure
the fraction of CPU time or clones that a lazy target sequence could eliminate.

Next implementation target: ordered metadata-only target property sequences, with
first-lookup metadata snapshot semantics and materialized identity preserved. To
avoid merely moving allocation to the next loop, eventual ordinary relations need
to consume target views too. Preserve declared-before-inherited/name ordering and
fall back before effects for unsupported source layouts, aliases and base handling.
