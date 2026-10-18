# Compact symbol-table representation prototype

Isolated implementation following the type-checked symbol-table boundary audit at `c40c808`. This code is **not integrated into the compiler**, is not a promoted optimization, and has no workload timing result. It resolves the earlier design question of whether enumeration must permanently materialize a Go map.

`Table[V]` is a pointer alias to shared mutable storage. Up to eight entries use exact string comparisons and presence bits; the ninth distinct entry promotes the shared state to a Go map. Promotion clears the inline entries to release their duplicate references. Table copies retain aliasing; clone copies storage but preserves value identities. Nil reads, length, deletion, iteration and cloning are supported; nil writes panic. Allocated-empty remains distinguishable from nil. Negative runtime capacity hints behave as zero, matching the pinned Go runtime. Larger hints allocate a fallback map immediately.

Small-table iteration snapshots at most eight original keys **when consumed**, then looks up their current values before yielding. A deletion before visitation suppresses the entry, replacement returns the current value, and new keys may be omitted. This is within Go map iteration's allowed mutation behavior. Slot reuse does not change the snapshot, and promotion during a callback is observed through shared storage. Large-table iteration uses native map iteration. Neither iterator is safe for concurrent writes; the compiler must preserve its existing ownership and synchronization boundaries. This design makes no promise of a stable cross-backend iteration order.

The prototype uses typed Go pointers and storage only. It does not add name interning, global IDs, pointer reconstruction, shared semantic caches, or an unsafe map-header dependency. `unsafe.Sizeof` is used only by the layout diagnostic in the tests.

## Verification

From the repository root, with pinned Go 1.26.9:

```sh
/tmp/tsc-toolchains/go/bin/go test -json benchmarks/profiles/compact-symbol-table-prototype/table.go benchmarks/profiles/compact-symbol-table-prototype/table_test.go
/tmp/tsc-toolchains/go/bin/go test -race -json benchmarks/profiles/compact-symbol-table-prototype/table.go benchmarks/profiles/compact-symbol-table-prototype/table_test.go
/tmp/tsc-toolchains/go/bin/go test -gcflags=all=-d=checkptr=2 -json benchmarks/profiles/compact-symbol-table-prototype/table.go benchmarks/profiles/compact-symbol-table-prototype/table_test.go
```

Seven top-level tests cover nil/empty/present-nil, invalid UTF-8 and empty keys, aliasing through promotion, clone storage independence and value identity, deletion and replacement during iteration, early termination, clear, slot reuse, nested/lazy iterators, and a deterministic 40,000-operation differential sequence against native maps. Normal, race and strict-checkptr logs are archived. The race run is instrumented validation of these tests, not a proof of compiler concurrency correctness. Layout evidence on this amd64 toolchain: pointer-valued storage 208 bytes; entry 24 bytes. That size is not allocation or RSS evidence.

## Integration risks and next step

The 208-byte inline state is allocated even for empty tables and remains present after promotion. Large or empty-heavy populations may therefore regress memory. Linear comparisons, iterator key snapshots, generic code generation, and extra method boundaries may also cost more than the current runtime. No performance gain is inferred from removing hashing on the small path.

Next, integrate through the audited expression sites with type-directed rewrites and explicit handling for nil checks, comma-ok reads, clone, iterator calls, map literals, address-of initialization and API adapters. Repeat the inventory with tests included so test-only map literals and helpers are covered. The original inventory did not cover other platforms or tests and is not itself a complete migration script. An integrated candidate must pass full compiler conformance, native/API/emit/project parity, focused semantic regressions, and race/checkptr validation before the frozen four-workload screen. Production source and the retained binary are unchanged at this checkpoint.
