# Discriminant constituent property-query census

Diagnostic overlay only. No production change, proposed cache, benchmark speedup,
or PERF.md entry. Follows the JSX partition at fc52708: investigate query work
before constructing a property lookup plan or changing semantic operation order.

The single original `getTypeOfPropertyOrIndexSignatureOfType` call inside
`discriminateTypeByDiscriminableItems` routes through an observer. The observer
calls the original helper exactly once with the same type/name. Other callers of
the property helper are excluded. Query ordering, discriminant matching, candidate
elimination, union creation, and original helper implementation are unchanged.

Rows classify concrete discriminator (1 TypeDiscriminator, 2
ObjectLiteralDiscriminator, 0 unknown), incoming type/object flags and coarse
active-instantiation context. Kind 2 includes both JSX and ordinary object literal
callers; do not label it JSX-only. All row totals are uncapped.

First 131072 distinct `(checker-local TypeID, property name)` keys per checker are
tracked. Known keys remain tracked at the cap; later unknown keys are explicitly
dropped. The key deliberately omits mutable state and caller. Repeat means an
earlier completed query, including nested completion order. Track changed returned
TypeID and nil separately; do not infer equivalence from stable IDs. The observer
retains property-name strings but no new Type/AST/inference pointer roots.

Count instantiations, created types/symbols, assignable+subtype relation size growth,
and instrumented elapsed time, both inclusive and excluding nested observed
queries. Also report repeat-exclusive work. Relation size omits replacements and
other relations; zero growth/counters does not establish purity. Observer elapsed
time and CLI invocation durations are not CPU or workload performance results.

Seven-file overlay: three production files with removable hooks, observer,
post-CLI exporter, internal accounting tests, and external real-checker differential
test. Export locks existing owners; no checker construction, GC, or semantic query.
Exclusive output prevents overwriting an existing report. Source audit removes
all hooks and reproduces original files exactly.

Focused tests cover nested completion/exclusive accounting, cap/key/name/nil
identity, output exclusivity/disabled state, and a TSX plus object-union program
with query-before-diagnostics, repeat identity, rendered types and counters compared
enabled versus disabled. Normal/race/checkptr each passed all four focused tests; diagnostic build passed.
Five Python accounting/aggregation tests pass. All twelve pinned workload controls
and independent readback passed. See RESULTS.md for counts and the next candidate
contract; production remains unchanged.
