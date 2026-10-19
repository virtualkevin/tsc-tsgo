# Independent property type-view histories

Extends the isolated property type-cache prototype without changing its production
mechanism. No compiler consumer or workload speedup is claimed.

The materialized reference and view implementation run in separately initialized
checker instances. Sixty-four deterministic seeds each drive 24 read/write,
Properties/Members enumeration, active-mapper-cache-clear and GC operations.
Observations include type categories, mapper callback counts, instantiation counts,
depth, active-mapper depth and final symbol allocation/identity relationships.
Exact optional-property handling makes write/read ordering observable: the mapped
missing type remains the read result while the write result is never.

Separate histories exercise nested queries with and without reentrant enumeration:
the inner result is visible during evaluation and the outer assignment subsequently
wins, including after cache transfer. A mapper-panic history compares the original
failure residue and verifies no failed result was cached. The tests intentionally
do not invent cleanup absent from the original path.

These are component histories, not a pinned whole-compiler oracle or proof of all
reachable histories. Nominal/alias/API traces and full compiler validation remain
necessary for actual consumers. Initial test compilation failed because uint32
depth values lacked explicit int conversions; raw failure logs are preserved in
`initial-build-failure/`. No candidate semantic change was needed for that fix.

## Integration finding

`propertiesRelatedTo` calls `getUnmatchedProperty` before traversing target
properties. The unmatched-property path materializes required source properties;
a type-view relation consumer alone would therefore miss those allocations. A
broader candidate must carry views through both presence and type-relation stages.
The rejected presence-only candidate is not evidence that such a combined design
will pass. Preserve target-before-source type-query order, private declaration
identity, protected-override behavior, strict-subtype readonly checks, optionality
checks after type relations, and diagnostic replay. Unsupported cases must fall
back before new semantic effects. Public property enumeration still requires its
original ordering and materialized symbol identities.
