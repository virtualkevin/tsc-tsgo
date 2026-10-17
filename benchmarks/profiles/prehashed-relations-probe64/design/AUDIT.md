# Conservative full-width prehashed Relation.results draft

Status: isolated source draft against main1633f6ac66404bad0f2d4bed42de02f8e7cda400. Formatted and apply-checked only. NO builds, tests, profiles, workloads or main edits. The source-only feasibility analysis remains `/tmp/tsc-prehashed-relation-audit/AUDIT.md`; this draft implements its bounded experiment, not an adoption decision.

## Scope and invariants

Only Relation.results storage changes: map becomes an optional pointer to a private relationResultCache. Relation objects and all five checker relation pointers retain their identity; enum relations, recursion maybeKeysSet, key generation,128-bit key equality, caller accounting and diagnostic paths are untouched. The pointer preserves existing nil-reset semantics in primitive_union_test.go: resetting results also discards count, arrays and fallback. There is one lazy cache-object allocation plus backing arrays; no claim that allocation object count falls.

The table holds separate full CacheHashKey keys, uint32 results, occupancy bitmap and exact count. Occupancy is independent of key/value bits: zero keys, explicit zero results and all32 result bits are supported. Missing get returns0; each distinct inserted key increments count once; replacement preserves size and replaces every result bit. Reads never allocate, mutate state, or reseed. No unsafe operations or stored pointers to table entries are introduced. Tables do not invoke semantic callbacks or hold references across checker recursion.

Capacity starts8 and doubles at75% occupancy. Existing-key lookup precedes the threshold check, so replacement never triggers growth. Capacity checking rejects invalid powers of two and doubling beyond maxInt/16, bounding the largest key backing allocation's byte arithmetic. The bitmap `(capacity+63)/64` arithmetic is also safe under this tighter bound. Runtime allocation failure/OOM remains possible as with Go maps; this is not a memory limit. New-table construction is private and receives either initial8 or the checked next capacity in production.

Probing uses low prehash bits for initial position and compares BOTH words for equality. Each insertion distance is below64 (or capacity when smaller). With no deletions, an empty slot or exhaustion of that same probe bound proves absence. Equal buckets/low words cannot alias distinct full keys. No per-entry truncated tag or value bit is used for occupancy. Deterministic low-bit hashing is not claimed to resist chosen inputs by itself.

If an insertion exceeds the probe budget, the relation permanently switches to Go's randomized full-key map. This bounds table-mode degeneration and avoids repeatedly growing a chosen collision chain. Fallback reconstructs every occupied old entry, applies the pending result, sets exact map length, and releases table backing references. Explicit zero-valued entries survive. Reads remain read-only in fallback too. A missing lookup over a64-entry chain performs at most64 slot comparisons; a65th colliding insertion triggers fallback.

Growth first creates a separate candidate table and reinserts all old entries, then the pending entry. Publishing `*store=next` happens only after complete success. Failure during old-entry reinsertion OR pending insertion rebuilds the map from the original table, never from partial next contents. Original backing arrays are not mutated. The helper can safely rebuild into other valid capacities, but production only doubles; tests deliberately request a smaller adequate capacity to force rehash failure branches. They do not claim those collision patterns naturally arise from doubling.

## Prepared tests (UNRUN)

Seven top-level tests cover:

- zero-value lazy reads, zero key/value, repeated full uint32 and overflow/reliability flags, exact count, five-store isolation and nil reset;
- deterministic differential updates/reads against a map across5000 operations each for ordinary and deliberately colliding keys, replacement and missing full-key reads;
- replacement at75% capacity without reallocating, followed by growth and value preservation;
- wrapped probe chains starting at the last bucket, a bounded miss without mutation, replacement at distance63 without growth/fallback, permanent fallback on the65th collision, release of arrays, fallback replacement and fallback-mode nil reset/reinsertion;
- both old-entry and pending-entry forced rehash failures, retaining all original values including zero, and unchanged original backing arrays;
- concurrent post-population reads in table and map modes (requires later race execution);
- checked power-of-two capacity growth through the architecture's arithmetic boundary without allocating huge tables.

Existing public API semantic regressions are unchanged. These storage tests do not exercise actual recursiveTypeRelatedTo complexity overflow/diagnostic replay end to end; parent must retain full checker/conformance/native gates before performance measurements.

## Performance and retention limits

No speed, memory or inlining claim. Nominal SoA payload20.125bytes/capacity slot at75% is26.83bytes/live versus the local Swiss group's theoretical28.57 at7/8, only a modest modeled difference before rounding, headers, actual occupancy and extra allocation objects. Cache object + three arrays add overhead for small relations. Every successful lookup still probes and compares a full key; the generic map's SIMD/control-byte machinery is gone, which may be a regression. Helper inlining and real caller assembly remain uninspected.

Monolithic growth temporarily retains old/new arrays and synchronously copies all entries, unlike Go's1024-slot table splits. Fallback may transiently retain original arrays, abandoned growth arrays and a new map. Collision fallback protects probe cost, not allocation peaks or OOM. The profile's Sentry Relation.get4.71% cumulative CPU and Relation.set289.38MiB/6.28% sampled allocation are exposure bounds, not removable totals; other workloads have substantially smaller allocation attribution. Reject if actual workload timings/RSS do not justify it. Do not broaden this draft to other maps or add numeric interning.
