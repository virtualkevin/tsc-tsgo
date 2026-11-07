# Reduction scratch integration contract

Isolated Go overlay on current production; no default source/binary changes.
The Checker gains one pointer to an idle scratch frame. Active frames are
removed from that slot before use, including before any recursive property
queries. At most one completed frame remains idle; a nested completed frame
may displace its caller's reuse opportunity without sharing live storage.

Original algorithm remains in place. Only map/names initialization and the
first-symbol buffer source change. Name insertion order, identity deduplication,
constituent traversal, costliest constituent selection, skipped apparent-type
query, skipped property lookup, singleton non-resolution, literal/private
short-circuit, and synthetic combined-property query stay in the same order.
Original byName values and scratch buffers are private temporary slices. The
only consumer of the gathered symbols iterates them; no slice is published.
The skipped-constituent append remains local exactly as before. If it reuses
the map slice backing, full-capacity clearing removes that extra reference;
if it reallocates, that independent temporary is not retained by the pool.

A defer receives the final local names slice and clears map keys, name slots,
and full capacities of all live symbol buffers. Old buffers displaced by
append are dropped when their frame slot is replaced. Groups above capacity64
are not retained. Frames above1024 names are not retained. This is a bound on
logical entries, not exact backing bytes: Go growth can overallocate capacity.
All previously retained buffers were cleared on the prior release. No symbols,
types, source strings, or semantic results are intentionally cached in idle
storage. Scratch ownership follows existing exclusive Checker usage, not a new
same-checker concurrency guarantee.

Costs: cleanup writes, defer/frame overhead, map clearing, retained map/slice
capacity, and recursive reuse misses may offset saved allocations. The standalone
warm microbenchmark is insufficient for adoption. Full oracle/API/emit checks
and fixed matched workload/RSS comparisons remain necessary.

Focused tests reuse the frozen original algorithm and cover widths0/1/2/8/9/16/
65/1025, duplicate names, optional/conflicting literals, repeated reduction,
shared-symbol singleton behavior, recursive frame ownership and explicit panic
unwind cleanup. A controlled unwind is a lifecycle test, not a proof covering
all production panic sites. Existing lazy-property and lifetime tests also run
under normal/race/checkptr with adopted project inlining.
