# Type-list storage: allocation and ownership audit

Offline evidence at retained production `50d78a7`. No compiler source change, new workload timing, or speedup claim. This is distinct from the rejected small-symbol-table representation: the question is whether pointer-heavy semantic lists can use existing type IDs without increasing object retention or breaking checker ownership.

## Conservative allocation attribution

`analyze.py` reuses the hash-checked raw heap profiles and parser from `ast-arena-audit`. It selects only samples whose **innermost** frame is an explicitly typed `[]*checker.Type` Insert/Clone/Grow helper, `instantiateList[*Type]`, or `AppendIfUnique[*Type]`. Allocations in a nested instantiator are not attributed to its outer list helper. Structs containing type pointers, maps and generic `*uint8` pointer shapes are excluded. Four classification/conservation tests pass and a second analysis run reproduces report.json exactly.

| Workload | Selected allocated objects / all sampled objects | Selected allocated bytes / all sampled bytes | Selected profile in-use bytes / all profile in-use bytes |
|---|---:|---:|---:|
| TypeORM | 3.584% | 0.280% | 0.000% |
| tRPC | 0.000% | 0.000% | 0.000% |
| VS Code | 1.824% | 0.134% | 0.025% |
| Sentry | 8.265% | 3.762% | 1.291% |

These are sampled allocation-site fractions, **not all type-list storage**. Zero means no selected sample, not no work. Generic shapes hide other list sites. In-use values are from the historical profile collection point, without a forced final GC; recent allocations may be omitted. They are neither maximum residency nor removable CPU or wall time. This narrow attribution does not justify a universal multiple-times gain or the requested original-native 10× target.

Reproduce from the repository root:

```sh
python3 -B benchmarks/profiles/type-list-storage-audit/test_analyze.py
python3 -B benchmarks/profiles/type-list-storage-audit/analyze.py
```

## Ownership boundary

- `checker/types.go` defines `TypeId` as uint32, and `Checker.TypeCount` is also uint32. `Checker.newType` increments the counter, assigns the ID, stores the owning checker pointer and records the type only when tracing is enabled. IDs are already narrow and are not program-global. There is no general decoder populated for every construction in this normal path.
- `api/session.go` **does** have a project registry of registered API types, and `api/proto.go:TypeHandle` uses `t.Id()`. Registration occurs through API responses/registration helpers, not unconditionally in every CLI `newType`. It cannot be treated as an existing free all-type ownership table for normal CLI checking.
- A dense strong decoder would add at least an eight-byte pointer per retained type slot on amd64, plus its own allocation/capacity costs, and retain every registered type's reachable graph. Reducing a pointer list entry from eight to four bytes only pays for that pointer-array storage when replaced entry count exceeds twice decoder slot count; this arithmetic ignores all other costs and is not a memory forecast. Sparse decoding or separate IDs changes this tradeoff and requires its own evidence.
- `Type.Types`, `UnionOrIntersectionType.Types`, `TemplateLiteralType.Types`, and alias type-argument accessors expose pointer slices. Returning decoded copies could add allocations and change aliasing. Internal callers and API adapters require a migration audit; replacing the field alone is insufficient.
- `instantiateList` already returns the input slice when all elements are unchanged and allocates only after the first changed element. An unconditional packed copy would lose that behavior. Alias identity, order, duplicates, nil values and checker ownership must remain explicit.
- Numeric IDs alone cannot preserve GC reachability. A weak decoder would allow a type referenced only by packed IDs to disappear, so it is unsuitable as the sole production owner. Unchecked pointer reconstruction is not part of this proposal.

## Next evidence needed

Before adding a strong decoder, measure whether completed CLI checking already retains all constructed types. A diagnostic-only checker-local weak-reference sample could observe reclaimable constructions after semantic checking, with checkers/program deliberately kept alive across a forced GC. It must not store strong `*Type` values in the ledger, must report its sampling denominator and construction owner, and must run outside any timing window. It should not derive final-GC liveness from the historical heap profile above.

The pinned Go weak-pointer implementation explicitly permits distinct interior-pointer offsets but does **not** guarantee that an unreachable object eventually yields nil. Therefore observed cleared references demonstrate reclamation; a surviving weak reference is not proof of semantic necessity. Diagnostic allocation/GC perturbation needs a baseline/disabled/enabled control, unchanged inputs and diagnostics, and no wall-time speedup claim. The sample must also avoid retaining types through a tracing recorder or API registry unintentionally. This diagnostic is not implemented in this checkpoint.

The immediate conclusion is a constraint, not a candidate: existing 32-bit IDs provide identity but not free reachability or decoding. The measured direct-list subset alone does not establish enough benefit to justify blindly retaining all types.
