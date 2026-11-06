# JSX work partition

Follow-up to the contextual request census, using preserved normal-build CPU
profiles. Production and PERF.md are unchanged. No new workload timings or speedup.

Every selected sample belongs to its nearest JSX inference/applicability handler,
inside its innermost call-resolution boundary. Handler source lines distinguish
parameter construction from contextual attribute checking and final comparison.
Nested ordinary calls and calls outside those boundaries are excluded. All unknown
handler lines remain `other`. Selected totals exactly reproduce the two JSX
source-line totals of call-resolution-partition for all four workloads.

| Sentry stage | Total sampled CPU % |
| --- | ---: |
| Contextual attribute checking | 12.126697 |
| Attribute compatibility relation | 5.668449 |
| Parameter type construction | 3.874949 |
| Type argument inference | 1.670095 |
| Inferred results | 0.106952 |
| Other | 0.016454 |
| Total selected JSX work | 23.463595 |

TypeORM, tRPC and VS Code have no samples in these selected JSX paths. This is not
a statement that they perform no ordinary contextual typing or discrimination.
These are disjoint CPU categories, not wall time or a removable-work estimate.
Inclusive function subrows in report.json overlap; do not add them.

Within contextual attributes, `checkJsxAttribute` includes 8.400% of total CPU and
`getContextualTypeForJsxAttribute` includes 6.294%. Within parameter construction,
`instantiateAliasOrInterfaceWithDefaults` includes 3.398%. Within the final
relation, `propertiesRelatedTo` includes 3.990%. These are descendants of their
respective stage, not additional budgets.

This rules out attributing all contextual JSX cost to fresh attribute symbol-table
construction. Avoid introducing a duplicate-table allocation optimization as an
explanation for that whole budget. The earlier exact-key census likewise does not
support a broad result cache. Parameter construction uses the existing alias
instantiation cache and must preserve depth/count diagnostic behavior, including
the known repeated-location LibraryManagedAttributes regression.

A source review also found the existing node/type cache in
`discriminateContextualTypeByJSXAttributes`, and cached discriminant flags in
`isDiscriminantProperty`. A new cache must not simply duplicate those caches or
precompute unqueried property types: property queries can materialize symbols,
instantiate types, and affect diagnostics. The next useful investigation is the
cost and query pattern of constituent property resolution during discrimination,
including the ordinary object/type callers shared with non-JSX workloads. Keep
actual query effects and property-augmentation modes separate before considering
a compact lookup plan. No candidate or architectural speedup is established here.

Validation: four ownership/source-line accounting tests; exact report reproduction;
raw profile, source, parser, archive and prior-report hashes. Tests cover nested
calls, nested handlers, recursive deduplication, unknown lines and out-of-scope
handlers. Existing parser tests are inherited, not replaced.

Reproduce:

```sh
python3 -B -m unittest discover -s benchmarks/profiles/jsx-work-partition
python3 -B benchmarks/profiles/jsx-work-partition/analyze.py
```
