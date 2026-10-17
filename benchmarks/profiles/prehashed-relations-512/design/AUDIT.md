# Separate512-probe full-width relation-cache draft

This is a new isolated draft against the restored saturated production baseline. The archived64-probe patch, production binary, validation and synthetic records remain untouched. No main edits, builds, tests, compiler workloads or profiles were run for this draft. Gofmt and apply-check only.

Production is byte-for-byte the reviewed64-probe implementation except `relationResultProbeLimit=512`; Relation integration is identical. Full128-bit equality, uint32 values including explicit zero, exact size/replacement, independent occupancy,75% load, transactional growth, nil reset and permanent Go-map fallback are unchanged. Numeric keys/interner and other caches remain out of scope.

The fixed probe budget now allows512 comparisons, including wraparound. A missing lookup stops at an empty slot or at512; every inserted table entry remains within this bound. In a same-home collision chain, distance511 replacement must find and overwrite the last admissible entry, while the513th distinct key falls back permanently. This is eight times the original maximum table-mode probe work. It is a deliberate worst-case latency tradeoff, not an unconditional safety/performance improvement.

The adaptive synthetic screen `/tmp/tsc-prehashed-relation-random-screen/comparison.json` observed early fallback on10/10 sequences at64 and128,1/10 at256, and0/10 before1million inserts at512. Those are reused fixed seeds selected adaptively, not independent validation or a probability bound. Actual compiler key distributions, cache sizes, updates, runtime and memory remain unknown. No performance measurement or production adoption is implied by this parameter choice.

Prepared tests adapt all bound-sensitive fixtures from the constant:

- Probe fallback inserts512 colliding full keys, checks missing-read bounds and distance511 overwrite, then triggers fallback with the513th; fallback-mode nil reset/reinsert coverage is retained.
- Differential pool is max(512,limit+64)=576, ensuring the colliding branch can exceed the new limit within5000 deterministic operations. Read-only concurrency population is max(256,limit+1)=513, so both table and fallback cases remain exercised.
- Forced rehash cases contain limit and limit+1 entries (512/513) in an old4*limit=2048-slot table, and rebuild into2*limit=1024 slots. Keys use increments2*limit, separating into two old buckets but collapsing into one destination bucket. The first case fails on the pending entry; the second fails while copying old entries. This uses controlled shrinking only to test transactional failure branches; production still only doubles.
- Zero/flags/count/isolation, overwrite-before-growth and arithmetic capacity tests remain unchanged.

Seven top-level tests, six child subtests, ten leaf cases are prepared but UNRUN. Child rehash names are now entries512 and entries513; the other child names remain collidefalse/collidetrue. Existing public semantic regressions must remain active. Their previous64-candidate pass does not validate this512 binary; new focused/race/full/native checks and compiler observation would be separate authorized work.

All prior memory risks remain: cache-object and three-array allocations, monolithic whole-table growth, transient old/new arrays and fallback-map peak, no Swiss SIMD control-byte filtering, and possible permanent fallback at larger/adverse distributions. The previous64 codegen is mechanism context only;512 codegen is not yet inspected. Reject or redesign if controlled actual workload evidence does not justify the change.
