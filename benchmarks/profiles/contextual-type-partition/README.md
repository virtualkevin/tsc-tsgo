# Contextual-type CPU partition

Offline analysis at 367d331 of the retained normal compiler profiles. No compiler
change, new workload timing, or PERF row. Six tests check recursive ownership,
unclassified/outside samples, distinct flat and inclusive accounting, source-line
partitioning, exact current callsites and rejection of negative samples. A second
analysis reproduces the complete report exactly. Raw archive, individual profile
text, input manifest, parser and current checker source are hash checked against
the existing call-resolution evidence.

Each selected sample belongs to the innermost getContextualType frame. Its source
line identifies the delegated operation; unknown lines remain explicit. Stage and
flat rows partition selected samples. Inclusive descendant rows overlap and must
not be summed. Source-line attribution can include compiler-assigned adjacent
instructions; it is not an exact helper instruction budget. Recursive contexts
are not counted again. Samples are historical CPU, not wall time, call counts,
repeated requests, purity or removable work.

| Workload | All contextual queries CPU % | Object-literal element stage % | JSX attribute stage % |
| --- | ---: | ---: | ---: |
| tRPC | 1.523 | 1.015 | 0 sampled |
| TypeORM | 1.143 | 0.616 | 0 sampled |
| VS Code | 2.706 | 1.813 | 0 sampled |
| Sentry | 10.358 | 3.332 | 6.425 |

The contextual stack lookup callsite is only 0.038% of total VS Code CPU and
0.025% of Sentry CPU. Replacing its linear scan cannot address the broader query
cost. Zero samples on small workloads do not establish zero execution.

Within Sentry's JSX-attribute stage, 5.356% of all CPU is beneath
`discriminateContextualTypeByJSXAttributes`; 3.233% is beneath
`discriminateTypeByDiscriminableItems`. These overlap. Discrimination already has
an exact node-ID/type-ID result cache, and discriminant properties already carry
cached flags. A second generic result cache would duplicate those mechanisms or
need a broader equivalence argument; stable printed types do not supply it.

Within Sentry's object-literal stage, 2.435% of all CPU is beneath
`resolveMappedTypeMembers`, with 2.155% beneath `findApplicableIndexInfo`.
These also overlap. This is eager mapped-type construction, distinct from the
previous rejected direct materialization of ordinary pending instantiations.
However, construction publishes an empty object before resolving dependencies,
enumerates keys in order, instantiates remapped names, combines colliding names,
queries modifiers and index applicability, and publishes properties/index info.
Replacing it with an on-demand single-property lookup could change recursion,
query effects, diagnostics and identities. No such shortcut is justified by
these CPU samples.

Next useful investigation: quantify mapped construction's name-remapping,
modifier lookup and index-resolution costs across the whole workload, preserving
key order and all semantic effects. This can distinguish representation work
from relation evaluation before attempting a mapped-member execution plan.
The existing rejected index-applicability/result-cache and relation-table
experiments are not reopened. This partition alone is not a 10× mechanism.

Development correction: the initial source-extraction guard expected 28 calls;
it failed before producing a report and printed the actual 25 source callsites.
The pinned-source list was reviewed and the guard corrected to 25. No compiler
execution or measurement was affected.

Reproduce with `python3 -B -m unittest discover -s benchmarks/profiles/contextual-type-partition`
and `python3 -B benchmarks/profiles/contextual-type-partition/analyze.py`.
