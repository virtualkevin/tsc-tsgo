# Symbol-table representation boundary

Source audit at retained production commit `870a62b`; no compiler change or new performance measurement. This investigates the indexed/compact semantic storage direction in the supplied analysis after the tagged AST payload failed its screen. It is a different mechanism from the rejected runtime small-string-map scan: a compiler-owned table could change allocation and eliminate hashing for bounded small tables, while that overlay retained Go's map representation and hashing.

## Reproduction and coverage

From `packages/tsc-go`, run:

```sh
/tmp/tsc-toolchains/go/bin/go run ../../benchmarks/profiles/symbol-table-storage-audit/inventory.go > /tmp/symbol-table-inventory.json
cmp ../../benchmarks/profiles/symbol-table-storage-audit/inventory.json /tmp/symbol-table-inventory.json
```

The tool uses the repository's pinned `golang.org/x/tools/go/packages` dependency to type-check current-platform non-test packages. It selects runtime expressions whose underlying type is `map[string]*ast.Symbol`, including unnamed maps with that shape. It excludes declaration identifiers, type expressions, and selector-name tokens. The report hashes all 494 loaded source files from 99 packages and contains 691 expression sites. These are **syntactic sites**, not dynamic counts, distinct tables, allocation savings, or a complete interprocedural alias analysis. Nested expressions can describe the same operation. Tests, other build configurations, and generic/unsafe conversions require additional review for a migration.

The first audit attempt failed when a declaration identifier reached the printer as a field. Excluding definitions fixed this; a subsequent review removed duplicate selector-name tokens. The completed report has count-conservation and source-hash checks, five manually checked representative operation sites, and an exact repeat-run comparison. No compiler test execution is claimed for this offline tooling.

## Findings that constrain a replacement

| Observed category | Sites | Required behavior |
|---|---:|---|
| Lookup | 111 | Preserve full byte-string equality, absent versus present-nil, and nil-table reads |
| Write | 67 | Copies/returned aliases must observe the same updates; replacing an entry must preserve table identity |
| Range | 42 | Preserve Go's allowed mutation-during-iteration behavior; changing storage cannot duplicate or silently omit surviving preexisting entries |
| Delete | 2 | Support scope rollback and removal of internal names |
| Length | 29 | Exact live-entry count, including present-nil entries |
| `maps.Clone` argument | 9 | Independent table storage with shared symbol pointers, preserving nil versus empty |
| `maps.Values` argument | 7 | Lazy iteration semantics need review, including mutations before/during consumption |
| Address-of table expression | 11 | Lazy initialization updates the owning slot and must remain visible to callers |
| Assignment | 184 | Includes both sides and nested expressions; not 184 distinct aliases |
| Return | 33 | A returned table can remain aliased to its owner |
| Nil comparison | 51 | Nil is used as a resolution/uninitialized state, not merely a zero entry count |

Specific source evidence (paths relative to `packages/tsc-go`):

- `internal/ast/symbol.go`: `SymbolTable` is a named map; `Symbol.Members` and `Exports` hold table values. Replacing it with a copied inline array would change map aliasing. A pointer to shared mutable storage is the straightforward compatibility boundary; allocation and size advantages remain unproven.
- `internal/ast/utilities.go:GetSymbolTable`: lazy allocation writes through `*SymbolTable`, then returns the same mutable map. Nil and allocated-empty states are distinguishable.
- `internal/binder/binder.go:declareSymbolEx`: insertion and replacement of constructor-created symbols happen through the caller's table alias. Ordinary name absence is tested by nil value, while other consumers use comma-ok; the replacement must support both.
- `internal/checker/checker.go:combineSymbolTables`: an empty-side fast path returns the other input directly. A new backend must not accidentally copy here. `mergeSymbolTable` writes into its supplied target.
- `internal/checker/checker.go:addInheritedMembers`: may allocate a nil table, then mutate entries by name. Member tables cannot be treated as globally frozen just because a pointer has been published.
- `internal/checker/nodebuilderscopes.go`: the returned undo closure deletes newly introduced locals and restores overwritten symbols on an existing scope. Append-only storage is insufficient.
- `internal/checker/services.go`: service code deletes the internal `this` entry from a constructed symbol table. CLI-only coverage would miss this path.
- `internal/checker/pending_members.go`: frozen name-position layouts already exist, but tables can be materialized and mutated during recursive base resolution. Replacing this mechanism with another per-instance index repeats a rejected experiment; it is not the proposed broad representation change.
- `internal/checker/symbolaccessibility.go`: `symbolTableID` encodes owner node/symbol IDs and a kind, not a map pointer. A representation change should retain these identity rules without adding another address-derived ID.

## Evidence and next decision

The retained normal profiles show substantial allocations at binder declaration and table creation sites, but flattened inclusive allocation percentages overlap and cannot be added into a speedup budget. The earlier string-map audit reports fast-string-map paths at 5.629–10.660% of sampled CPU across the workloads, including allocation/hash callees. The resolved-member census found many misses in size-4–7 materialized tables, but counts neither unique tables nor their mutation/iteration histories. These observations justify investigating storage; they do not demonstrate universal multiple-times headroom.

A candidate needs a shared mutable table state, exact string keys (including invalid UTF-8 internal names), nil-state preservation, clone independence, presence bits, and a large-table fallback. A local small-array copy or cached negative filter is not compatible with the observed boundary. The remaining design question is iteration: materializing a built-in map permanently on the first enumeration is simple and preserves mutation semantics, but could eliminate the small-table fast path before most checker lookups. Maintaining two mutable representations could instead increase memory and write costs. Establish which lifecycle applies to the hot tables before choosing a backend; do not assume that the small-table lookup counts establish eligibility for a never-enumerated representation.

This audit does not promote a candidate, change the fixed performance acceptance policy, or provide a route to the original-native 10× target. Production remains unchanged.
