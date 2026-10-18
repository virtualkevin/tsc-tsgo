# Primitive-property clone coverage

Diagnostic overlay only. At actual newInstantiatedSymbolWithLinks entries, count ordered exclusions and a strict syntactic candidate subset: an ordinary Property (optionally Optional), zero checker metadata, exactly one matching value declaration, TypeScript PropertySignature under an interface or type literal, no initializer, and a direct any/unknown/string/number/bigint/boolean/symbol/object/void/undefined/never annotation. No clone is removed. Scalar per-checker counters do not retain semantic objects, allocate per request, or invoke semantic queries.

The existing isThisless helper is insufficient: it admits generic type references without this parameters. The direct keywords instead map to checker intrinsic types in getTypeFromTypeNodeWorker. Variable-like declarations obtain that type and then apply optionality; instantiated read/write symbols currently resolve the original and instantiate it. These source observations motivate measurement, not a complete proof that returning the original earlier preserves all identity, error, recursive and API behavior.

The hook runs at clone construction, which can follow a frozen pending-member decision. It is not a census of all calls to instantiateSymbol, nor does it measure saved CPU. Cases already reused by the existing resolved-type or this-only checks do not reach it. A future optimization must be placed at the original decision boundary, preserve frozen decisions, and pass full conformance/API/emit/race validation and unchanged performance gates. No PERF rows for diagnostic durations.

All twelve controls completed with clean diagnostics and exact pinned physical inputs. Three focused Go tests passed in normal, race and strict-checkptr modes, and three count-validator tests passed. Independent verification of raw category totals, source, binaries and controllers passed before archival.

| Workload | Actual clone entries | Strict syntactic candidates | Coverage |
|---|---:|---:|---:|
| typeorm | 176525 | 520 | 0.295% |
| trpc | 37474 | 604 | 1.612% |
| vscode | 1859702 | 4167 | 0.224% |
| sentry | 1688083 | 30818 | 1.826% |

Decision: do not implement this strict shortcut. Coverage of the selected construction path is small, especially on VS Code and TypeORM, and adding the predicate to every instantiation decision has no measured cost justification. Counts are not a performance bound: requests differ in downstream costs, and neither avoided allocations nor end-to-end savings were measured. A broader rule would be a separate hypothesis requiring semantic proof and evidence, not an unmeasured extension of these counts.

Most exclusions are in the first category (non-plain-property); the ordered classification does not identify the distribution of specific rejected flags or make their cases eligible. It must not be read as evidence that every excluded clone is necessary. TypeORM constructor totals differ by four from the separate weak-reference census (176525 versus 176521); both controls were clean, but this comparison does not establish why the counts differ or prove observer neutrality. Do not pool the two runs. No compiler optimization or PERF row.
