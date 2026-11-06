# Verified contextual JSX census

Capture atc0bc410 passed all12baseline/disabled/enabled controls. All configurations
used four checkers and exact pinned inputs with empty diagnostic output. The
source, binary, raw focused test logs, commands, counts and capture artifacts were
independently verified. Cohort analysis reproduces exactly. No caps saturated;
no request histories were dropped. Production remains unchanged.

TypeORM, tRPC and VS Code recorded zero eligible requests. This means zero calls
to this specific wrapper with JsxAttributes inputs in these workloads, not absence
of contextual expression checking generally or all conceivable JSX work.

| Sentry observation | Count |
| --- | ---: |
| Requests | 82,230 |
| First completed key requests | 80,625 |
| Repeated completed key requests | 1,605 |
| Repeats returning a different TypeID | 1,563 |
| Exclusive instantiations | 1,184,760 |
| Exclusive type constructions | 515,063 |
| Exclusive symbol constructions | 631,322 |
| Repeat-exclusive instantiations | 186 |
| Repeat-exclusive type constructions | 6,313 |
| Repeat-exclusive symbol constructions | 9,247 |
| Requests changing inference flags | 192 |

Recorded keys combine node identity, contextual TypeID, inference-context pointer,
requested check mode and nil-context distinction. Their repeats are1.952% of calls
and account for0.01570% of observed instantiations. First-key counts do not mean
unique AST nodes: another context or mode creates another key. Matching pointers
are not complete inference/flow state. All calls returned non-nil results.
Changed TypeID means identity differs, not a demonstrated semantic difference.

| Requested mode | Inference context | Calls | Repeats | Changed result IDs | Exclusive instantiations/types/symbols |
| --- | --- | ---: | ---: | ---: | --- |
| Normal | none | 67,788 | 1,240 | 1,198 | 713149 / 328651 / 447615 |
| Normal | present | 1,307 | 0 | 0 | 102339 / 11077 / 13845 |
| SkipContextSensitive | none | 1,815 | 350 | 350 | 104485 / 18970 / 58037 |
| SkipGenericFunctions | none | 173 | 15 | 15 | 5021 / 1226 / 1879 |
| SkipGenericFunctions | present | 9,431 | 0 | 0 | 208946 / 139690 / 89526 |
| Both skip flags | none | 19 | 0 | 0 | 549 / 189 / 291 |
| Both skip flags | present | 1,697 | 0 | 0 | 50271 / 15260 / 20129 |

Mode values are the incoming mode; the original helper adds Contextual and, when
applicable, Inferential. All rows have zero recorded active-instantiation context;
that coarse flag excludes many other kinds of mutable semantic state. Inference
site lengths were zero at both observed boundaries, which does not mean no sites
were created and consumed inside the helper. Flag changes occurred173times for
SkipGenericFunctions with inference and19times for both skip flags with inference.

The observer starts after its contextual parameter type has been computed. Work
in getEffectiveFirstArgumentForJsxSignature before entry, including managed-
attribute computation there, is excluded. These counts do not cover the complete
JSX applicability/inference delegation measured in the earlier CPU audit.

Net assignable+subtype relation growth was40,286entries, with zero on repeats.
Replacements, other caches and diagnostic effects are not captured by that metric.
Exclusive observed elapsed time was19.37seconds across checker intervals. It is
instrumented elapsed time, not CPU, wall-clock compilation, removable work or a
performance comparison. The observer retains AST/inference graphs and perturbs GC.

Decision: do not introduce a general exact-key JSX result cache from this evidence.
It would target few repeated requests, little observed repeated instantiation,
and commonly return an identity different from the original fresh result. It
would also need an effect-complete context contract that the current key lacks.
This does not rule out reuse between other descriptor classes or sharing proven
immutable facts; those are different hypotheses requiring evidence.

The remaining useful direction is reducing the cost of first recorded contextual
requests, including their type/property construction and underlying semantic
operations. Source inspection finds both contextual attribute checking and
LibraryManagedAttributes instantiation beneath the JSX path; their respective
costs are not separated by this census. Do not attribute all recorded work to
attribute-table allocation or assume a lazy map alone explains the earlier23.5%
CPU footprint. No production optimization, PERF row or10×claim follows here.
