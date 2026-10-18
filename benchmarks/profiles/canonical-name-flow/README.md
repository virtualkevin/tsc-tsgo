# Canonical name-flow boundary audit

Production remains source `216d40c7` at capture HEAD `2fb532c`. This is an offline source/layout investigation of the broader semantic-storage strategy in OPTI_ANALYSIS_01.md. No compiler change or performance measurement is included.

## Finding and next decision

A canonical name handle could replace string keys while retaining Go's built-in map aliasing, nil, clone, deletion, and mutation-during-range behavior. This differs from the rejected custom symbol-table backend and the rejected lazy identifier-map experiment. It would require carrying names through parsing, binding, symbol construction, and checker query interfaces. It must not implement a string-to-handle conversion at every existing lookup and assume hashing disappeared.

The audit supports investigating that full name flow, but **does not yet justify a compiler-wide migration**. The next gate is a workload census of name construction and distinct-name cardinality, including synthetic checker names. Canonical descriptors, cloned text, weak entries and cleanup can offset smaller node/key fields. A parser-only census would omit synthetic names. Static site counts cannot estimate how often a conversion boundary executes.

## Typed source inventory

`inventory.go` type-checks 99 current-platform non-test packages, hashes 494 source files, and records 1,205 sites. Tests, other platform configurations, reflection, and interprocedural dataflow are outside its coverage. Counts overlap between field and map sites and are not dynamic query counts.

| Direct key expression | Symbol-table reads | Writes |
|---|---:|---:|
| `Symbol.Name` field | 26 | 37 |
| Existing symbol-table range key | 9 | 5 |
| Constant | 37 | 7 |
| Function parameter | 18 | 5 |
| Other identifier | 14 | 9 |
| Call result | 7 | 2 |
| Other selector | 0 | 2 |
| Total | 111 | 67 |

The 35 reads from stored names/range keys and 37 constant reads are syntactically plausible handle-propagation sites, not proven optimized operations. Constants need a canonical, consistently initialized representation. The remaining 39 reads require tracing parameter/local/call-result origins; a parameter is not evidence of repeated string conversion. Representative boundaries include `NameResolver.Resolve`, `getResolvedMember`, `getUnionOrIntersectionProperty`, `getExportOfModule`, and binder declaration lookup. All five recorded examples were checked against source lines and type information.

There are also 330 direct `Symbol.Name` field uses, 27 direct `Identifier.Text` field uses, and 669 `Node.Text` method-value sites (all currently used as calls). `Node.Text` covers many non-identifier nodes; indiscriminately converting every text value into a name would change the scope substantially. The symbol field participates in comparisons, concatenation, indexing, slicing, returns, and calls. Text ordering, formatting, module-name tests and serialization must retain original byte-string behavior. A new handle type is not ordered, and a reflection-based serializer cannot be assumed to emit the old string representation.

## Ownership and cost constraints from the pinned Go implementation

The audit reads the installed Go 1.26.9 primary sources, whose hashes are recorded in `verification.json`:

- `unique/handle.go`: `Handle[T]` contains a typed `*T`; handles compare by canonical identity; `Make` and `Value` support concurrent use. `Value` dereferences the pointer, so a zero handle cannot be decoded directly. A wrapper must define one consistent representation for the existing empty-string/default-name state.
- `unique/canonmap.go`: canonical entries use weak pointers and runtime cleanup. A live handle keeps its canonical value reachable; reclamation/cleanup is not immediate or a fixed memory bound. This avoids inventing an unbounded strong process-global name table, but still introduces trie nodes, weak-reference machinery and synchronization.
- `unique/clone.go`: canonical string creation clones bytes to avoid retaining an arbitrarily large backing string. Those allocations belong in the cost model.
- `Make` still performs a type-map lookup and content hashing/trie lookup. Calling it at every symbol-table access merely moves work; a viable design must reuse carried handles through hot paths.

These are pointer-backed handles, **not pointer-free integer IDs**. A string and a handle each carry a pointer; a handle additionally reaches a canonical string header. Fewer bytes in an identifier do not prove fewer GC edges, cheaper scanning, or faster execution. Exact Go string equality includes invalid UTF-8, embedded NULs, escaped/private/internal names and empty strings; normalization must not be added. Shared ASTs and multiple programs require canonical identity to remain valid while any owning node/table/API handle retains a name. Internal raw-Go field changes and external CLI/API/emit behavior need separate review and validation.

## Layout probe

`layout.go` ran under the pinned amd64 toolchain using the actual AST base types and a proposed layout mirror:

| Item | Current bytes | Proposed mirror bytes |
|---|---:|---:|
| Name field | 16 | 8 |
| Identifier | 72 | 64 |
| Symbol | 96 | 88 |
| Raw key/value entry struct | 24 | 16 |

The entry struct is not a measurement of Go map groups, occupancy or allocated size classes. The mirror excludes all canonical objects, cloned strings, trie/cleanup state, and conversion/decoding costs. It is not a compiler candidate, heap/RSS result, or speedup forecast. The rejected tagged AST experiment already demonstrates why a nominally smaller structure is insufficient evidence.

## Reproduction and verification

From `packages/tsc-go`, run the inventory twice with the pinned toolchain and compare exact output:

```
GOCACHE=/home/dev/.cache/go-build /tmp/tsc-toolchains/go/bin/go run ../../benchmarks/profiles/canonical-name-flow/inventory.go > ../../benchmarks/profiles/canonical-name-flow/inventory.json 2> ../../benchmarks/profiles/canonical-name-flow/inventory.stderr
GOCACHE=/home/dev/.cache/go-build /tmp/tsc-toolchains/go/bin/go run ../../benchmarks/profiles/canonical-name-flow/inventory.go > /tmp/canonical-name-flow-repeat.json 2> /tmp/canonical-name-flow-repeat.stderr
```

For the layout probe, create a fresh `packages/tsc-go/_tmpcanonicalnameaudit` directory and copy `layout.go` into it as `main.go`. This temporary location allows Go's internal-package imports; the underscore prefix excludes it from `./...` inventory loading. From `packages/tsc-go`, run:

```
GOCACHE=/home/dev/.cache/go-build /tmp/tsc-toolchains/go/bin/go run ./_tmpcanonicalnameaudit > ../../benchmarks/profiles/canonical-name-flow/layout.json 2> ../../benchmarks/profiles/canonical-name-flow/layout.stderr
```

Run `verify.py` from this profile directory. It checks exact repeat output, all source hashes, category conservation, unique site identities, five manually reviewed cases, and layout results. It verifies then removes only its own temporary helper file/directory. Verification passed; the temporary helper is absent, and the production source hash still matches the retained compiler. No new PERF row or 10× claim follows.
