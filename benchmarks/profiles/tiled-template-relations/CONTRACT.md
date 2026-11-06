# Tiled template relation integration contract

## Representation

Each Relation remains checker-local and retains its pointer identity. A key is
canonical: nonzero packed means zero hash; otherwise the full original128-bit
hash is used. The packed domain is selected after the original identity ordering
and generic-detection expression, preserving their evaluation order. It requires
non-generic exact StringLiteral/TemplateLiteral source and TemplateLiteral target,
no reference object flags, nonzero IDs below2^30 and intersection state0..3.
All other cases keep original hashing and constrained-key behavior. There is no
generic hash interner, global registry, type pointer, skipped comparison, or new
semantic-result cache.

The packed value is sourceID<<32 | targetID<<2 | intersectionState. Its fixed
16×16 tile/lane decomposition is the standalone model already checked by Z3.
Only plain Failed values occupy bits. Other full-width result values occupy the
packed-value map. Hashed keys retain the original hash map. Overwrite transitions
remove the old representation; present zero entries still contribute to size.
Empty tiles are removed. The complete logical size feeds unchanged relation
complexity limits. Populated Relation/storage copying and concurrent mutation
are unsupported, as with existing checker-private mutable storage.

## Key-equivalence assumptions and limits

Type IDs identify types within a checker; the packed domain relies on their
identity and stable classification. Current writes to Type.flags outside
construction affect enum unions, boolean unions, or newly constructed regular
object types, not these string/template types. The classifier excludes enum
literal combinations. Identity sorting and intersection state are part of key
construction and cannot be discarded. All four key-construction sites and both
maybe-key containers use the tagged representation.

Original ordinary keys hash an encoding of the same IDs/state. Relating the new
exact IDs to the old128-bit hashes assumes no original hash collision involving
these live keys (including a collision with another domain). The new tags do not
preserve accidental aliasing from such a collision. This is an explicit boundary
of the equivalence argument, not a proved injectivity theorem for XXH3. Boundary
fixtures compare actual original hashes, and full compiler tests are required.
The standalone bitvector proof proves packing/storage-model properties only,
not this assumption or the Go compiler implementation.

## Operational invariants

- Original lookups and writes occur in the same order. No success/failure check,
  recursion, placeholder inference, constraint query or diagnostic is skipped.
- Original relationCount decrements and size-based starting budgets remain intact.
- ReportsUnmeasurable, ReportsUnreliable and both overflow bits survive reads and
  replacements exactly. Plain failure is only the exact value2, never a mask test.
- Ordinary failure diagnostic elaboration still reruns the full comparison.
- Maybe keys preserve tags through insertion, recursion checks, broadest generic
  checks, removal and success propagation; marked successes retain every bit.
- Whole-store resets clear both hash and packed storage while preserving the
  Relation object's pointer. The sole direct reset found is in the existing
  primitive-union test; it is migrated to assigning a zero Relation value.
- No change to keybuilder.go or declaration transformation is included.

## Validation scope

New focused tests cover mixed hash/packed histories against a map oracle, ID/state
boundaries and original hash comparisons, actual recursive failure/cache-hit
budget behavior, reliability/overflow replacements, reset, and mixed-key
maybe-stack success propagation. The semantic histories run on retained source
as well, with only the key container type mechanically changed.

Full compiler/services/conformance, CLI/API/emit and instrumented CLI checks remain
required, followed by a normal provenance-backed build. A/B screening and two
independent confirmations use the existing frozen protocol. Broader keys enlarge
the maybe-stack/set key from16 to24bytes and add dispatch branches; sparse tiles
and extra lookups may regress small workloads. Density evidence alone cannot
establish speed or justify promotion. Production remains unchanged throughout
the isolated overlay validation. The10× original-native objective remains unmet.
