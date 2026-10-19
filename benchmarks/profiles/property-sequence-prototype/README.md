# Ordered pending target-property sequence prototype

This isolated overlay extends the rejected, snapshot-corrected property relation
view implementation. It is not enabled in production and has no performance
claim. The new sequence is not yet wired into a compiler consumer.

The sequence retains typed original-symbol roots, captures all active clone
nameType metadata before any consumer type query, and sorts visible properties
with the compiler comparator and declared-member-first partition. Reserved
members are excluded from visible order but included in metadata capture.
Identity consumers use the owner's current member representation, including
after Properties/Members enumeration retires the original pending state.

Whole-layout preflight excludes bases, resolving or materialized layouts,
duplicate names, non-property members, and already-instantiated sources before
creating cache entries. Existing frozen keep/clone decisions are preserved.
Source topology remains immutable under the existing checker contract; this is
not a concurrent mutation mechanism or a proof for arbitrary compiler histories.

Three new focused tests cover independent eager-reference ordering, zero symbol
allocation during sequence creation, post-enumeration/GC identity, nameType
snapshot timing, and fallback before cache effects. The inherited twelve tests
cover property-view metadata, types, and stateful histories. validate.py records
normal/race/checkptr results and exact overlay source hashes.

The initial fixture used the visible name __call instead of the internal reserved
call-signature constant. Both implementations agreed; the explicit expected list
was wrong. Its raw failed output and test source are retained separately.

Next: consume target metadata in unmatched-property checks, then in the following
relation loop so deferred symbol allocation is actually avoided. Full oracle and
CLI validation and a separately built normal binary are required before timing.
Do not infer a compiler speedup from sequence allocation behavior.
