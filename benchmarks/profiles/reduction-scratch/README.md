# Temporary reduction grouping reuse prototype

Distinct from rejected inline-first-symbol and small-pair grouping changes:
retain map[string][]T and insertion-order names, but reuse cleared backing
storage between operations. This standalone generic module is not integrated
with the compiler and caches no types or semantic results.

Ownership contract: one exclusive owner per pool; Acquire removes its sole idle
frame before publication, so recursive calls cannot reuse an active frame.
Release clears every occupied group's entire capacity, map entries and name
slots before retaining at most one idle frame. Frames with more than1024 names
are discarded; group buffers with capacity above64 are discarded. Published
borrows must not survive Release. No concurrent shared-pool contract, unsafe
pointers, resets of published compiler objects, or process-wide pool.

Normal/race/checkptr each passed two tests. 4096 seeded construction histories
compare name order, symbol identity, deduplication and nested reuse against the
original grouping algorithm. Tests inspect cleared backing references, large
frame/group rejection, and pointer lifetime across forced GC. These are finite
prototype tests, not compiler equivalence or a formal proof.

Five fixed-order 200ms microbenchmark observations per case used two passes of
the same symbols (duplicate-hit workload). Baseline/reuse median ns were
1853/1063 at8 names,29804/11269 at64,354114/73175 at512. Median allocations were
12/0,80/0,537/0; median bytes304/0,12984/0,115097/38. Fractional amortized reuse
allocations can round to0. The retained pool holds backing storage: this is not
zero memory usage. These are synthetic hot reuse results, not independent
alternating workload pairs, cold/recursive behavior or end-to-end speedups.

Next candidate integration must preserve original construction/consumption and
skipped-constituent resolution order, singleton non-resolution, repeated names,
recursive effects and early returns. Check cleanup through panic/early return
and compiler object lifetime. Keep normal/race/checkptr, full pinned oracle,
API/emit and fixed workload/RSS gates before adoption. No PERF rows yet.
