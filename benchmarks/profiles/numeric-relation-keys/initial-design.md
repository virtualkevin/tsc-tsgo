# Numeric relation keys: isolated draft

Base: `c6f43f2`. No shared checkout edits. Draft is unbuilt and untested while the
GC/RSS sweep is active. Files are copied under `base/` and `draft/`; patch exported
as `relation-keys.patch`. This experiment is independent of pointer-link tables,
TypeData arenas, scheduler changes, and the reverted property-cache experiment.

## Evidence and scope

Native history separates three optimizations:

- `355eb96`: pack ordinary source/target Type IDs plus intersection state into a
  number; intern string-shaped exceptional keys per checker.
- `7483396`: replace generic key strings with collision-checked number-token
  interning. Native history mentions 133k string pieces on tRPC. Go does not build
  those strings, so that historical claim does not transfer directly.
- `8e85d67`: store relation results in a custom numeric open-addressing table.

Native `src/compiler/relations.ts` lines 801–945 holds packing/interning; lines
240–320 hold the custom table. The first behavior is the only proposed port;
generic serialization remains the existing Go 128-bit hash and Go maps remain.

Existing `/tmp/tsc-profiles/expansion-*/cpu-cum.txt` CPU summaries:

| Workload | getRelationKey cumulative | Relation.get cumulative | Relation.set cumulative |
| --- | ---: | ---: | ---: |
| TypeORM | 0.02s / 0.15% | 0.03s / 0.23% | 0.03s / 0.23% |
| tRPC | 0.01s / 0.48% | not sampled | 0.02s / 0.96% |
| VS Code | 0.72s / 0.44% | 1.79s / 1.09% | 0.39s / 0.24% |
| Sentry | 1.91s / 1.44% | 5.23s / 3.93% | 1.03s / 0.77% |

Sentry getRelationKey flat CPU was 0.50s / 0.38%; VS Code 0.17s / 0.10%.
Generic traversal alone was 0.02s Sentry / 0.03s VS Code. General keyBuilder and
xxh3 totals include other type caches and overlap these samples; do not add them.
These are older expansion CPU profiles, not current lazy timings or predicted
wall savings. Key packing can remove only part of relation work; 64-bit map keys
may reduce map overhead, but an A/B measurement is required. This is a modest
candidate, not a route to 10x by itself.

## Minimal representation

`RelationKey uint64`; for an ordinary comparison with IDs in `[1, 2^30)` and
intersection state in `[0,3]`:

```
(uint64(source.id) << 32) | (uint64(target.id) << 2) | uint64(state)
```

The packed domain fits in 62 bits. Bit 63 tags fallback IDs. A checker-owned lazy
`map[CacheHashKey]RelationKey` interns the unchanged full 128-bit hash; IDs start
at one and cannot wrap. Zero Type IDs, oversized IDs, future state bits and all
generic keys take this fallback. Zero RelationKey remains reserved, even though
Go maps do not need a sentinel. No hash truncation or new hash-bit partition is
introduced. Existing theoretical generic 128-bit hash collisions remain the
status quo; native exact token comparisons are deliberately not included.

The generic/oversized helper owns its hasher local, keeping its frame off the
common path at source level. Actual compiler inlining/frame behavior must be
inspected later; no codegen claim is made before a build.

## Consumers and invariants

Only four key creators exist, all in `internal/checker/relater.go`:

1. `isTypeRelatedTo` object-pair cache lookup (~219).
2. `checkTypeRelatedToEx` overflow-failure recording (~426).
3. `recursiveTypeRelatedTo` normal comparison (~3097).
4. Its constrained/broadest-equivalent recursion probe (~3128).

Consumers are `Relation.results`, `get/set/size`, `Relater.maybeKeys`,
`maybeKeysSet`, and `resetMaybeStack`. No external consumers, direct external map
accesses, or iteration-dependent relation behavior were found.

- Preserve identity source/target ID sorting before generic detection. Do not
  swap the intersection state when swapping identity operands: the old code does
  not do so.
- Generic detection may resolve type arguments. Preserve its left-to-right,
  short-circuit ordering and keep the same type-owned constraint-resolution calls.
- Preserve source/target-shared type-parameter positions, depth-four recursion,
  nested delimiters, constrained IDs and ignoreConstraints normalization. Ordinary
  keys ignore that boolean exactly as before.
- The constrained result is a local return value, not checker scratch state;
  recursive constraint resolution cannot overwrite it.
- Checker-local IDs were already the cache identity. Keep fallback interning and
  cached relations local to the owning checker, not source/target.checker or a
  global registry. Do not extend this to cross-checker cache sharing.
- Relation size counts successful/failed cache entries, not interner probes;
  `(16_000_000 - relation.size()) / 8` complexity budgets stay unchanged.
- Preserve all success/failure, reliability and stack/complexity-overflow flags.
  Maybe-stack membership, partial commits and pooled-relater cleanup retain their
  existing behavior.
- Fallback interning retains probe-only exceptional keys for checker lifetime,
  even if no result is cached. This is an extra memory/lookup cost to measure.
- TypeId is uint32; crossing 2^30 uses existing full-ID hashing. Existing TypeId
  wrap beyond uint32 is not solved or made worse by this port. Interner exhaustion
  explicitly panics instead of aliasing an existing key (unreachable in practical
  memory limits).

## Draft tests; not run

- Ordinary boundary matrix: zero, small IDs, 2^30 boundary, high uint32 IDs;
  all valid states and future bits; both identity and constraint flags. Compares
  key-equivalence classes against the original hashed implementation and checks
  identity/state behavior explicitly.
- Generic matrix uses established `lazyPropertyTestChecker`, initialized cached
  constraints and resolved reference arguments. Covers alpha-equivalent and
  distinct occurrence positions, target identities, same-constraint/different
  parameters, broadest recursion keys, and nested references through depth six.
- Full 128-bit fallback distinctions, stable IDs, lazy allocation, per-checker
  lifetime, reserved zero/tag domains and exhaustion.
- Maybe-stack partial commits/discards, reliability/overflow flags, overwrite
  accounting and pooled relater reset.
- Public checker fixture: mutually recursive generic assignments, repeated
  expected diagnostics, distinct unconstrained/constrained parameters,
  intersection direction and generic signature identity.

After the quiet window, build/test in an isolated module or approved main batch:

```
/tmp/tsc-toolchains/go/bin/go test ./internal/checker -run '^TestRelationKeys?' -count=1
```

Use the normal untrimmed test build because existing public API fixtures resolve
repository fixtures from source paths. Then run compiler/checker units, race tests,
full pinned conformance and native parity/API gates before any performance claim.
The current draft has not passed any of these gates.


## Follow-up static review

Independent read-only review by port_audit found no production semantic blocker:
packing ranges are disjoint, all four consumers are converted, generic detection
ordering remains intact, and the complete fallback hash is interned only after
local constraint/key construction, so nested key creation cannot overwrite outer
scratch state. The relation count remains independent of interner growth.

The synthetic reference helper now uses `newObjectType(ObjectFlagsReference,
nil)` followed by assigning its target/resolved arguments. It does not depend on
the private `newType` signature, and is compatible with the separate proposed
TypeData constructor representation.

Added a public cold-constraint fixture adapted from pinned upstream
`signatureInstantiationWithRecursiveConstraints.ts` (#17148), with recursive
constraints on generic methods and generic Box return references. Each direction
runs first on a fresh checker before diagnostics are collected, then repeats
warm queries and checks distinct required-property failures/diagnostics. It tests
cold versus cached recursive-constraint behavior; it does not instrument or prove
an exact count of nested getRelationKey calls. The source-level reentrancy proof
is that source/target/state/hash builder/constrained result remain local, and
fallback IDs are looked up/assigned only after the complete hash is produced.
The new fixture, like the rest of the patch, is still unbuilt and untested.
