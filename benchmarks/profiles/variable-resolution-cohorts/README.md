# Variable/property origin cohorts

Offline breakdown of the verified symbol-resolution census, four checkers only.
Each raw census hash is checked, and recorded calls and exclusive elapsed totals
were reconciled with the prior independently verified per-kind summary. Kind names
come from the pinned generated Go enum's numeric consistency checks.

| Workload | Variable/property misses | Retained origin calls | Variable-declaration calls with zero recorded context | Their repeated-origin calls |
| --- | ---: | ---: | ---: | ---: |
| typeorm | 62,326 | 62,326 | 18,000 | 576 |
| trpc | 9,407 | 9,407 | 1,372 | 154 |
| vscode | 1,134,331 | 242,109 | 54,760 | 4,378 |
| sentry | 376,562 | 197,512 | 40,370 | 11,774 |

Variable declarations dominate recorded elapsed work in each workload. Parameters
repeat often but are not the dominant retained cost. These are instrumented
intervals, not CPU samples or removable work. Large-workload origins are capped
and first-seen, so no extrapolation or all-workload coverage claim is valid.
“Zero recorded context” means only zero instantiation depth and active mapper
count: it does not mean context-free. ErrorResults counts the checker error-type
sentinel, not emitted diagnostics. Matching origin keys still omit semantic
mapper/inference/flow/diagnostic state, and repeated totals include the first owner.

Source inspection of ranked origins found VS Code EditorOptions/codiconsLibrary
are large object initializers; Sentry Input/Prose are styled calls/tagged templates
with contextual callback inference. Those results are not plain immutable syntax
facts. In checker.go, variable/property resolution can push/pop cycle detection,
report circularity, infer initializer types, infer contextual parameter types,
and query constructor/static-block flow. Bypassing it with an origin-only cache
would require preserving all those observations, not only a final type.

Next targeted experiment: uncapped aggregate counts and observed cost by the actual
variable-like resolver branch (annotation, contextual parameter, initializer,
flow, binding, and special cases), with a separately bounded origin sample only
for the promising branch. Preserve query order and diagnostics; do not call helpers
merely to classify. The broad first-seen cap must not decide which branch appears
cheap. No shared result cache or production change is justified yet.
