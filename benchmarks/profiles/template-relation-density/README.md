# Template relation failure tile density

Isolated diagnostic overlay on retained source216d40c7. It observes the ordinary
failure cache write in recursiveTypeRelatedTo *after* the original write, without
changing any relation lookup, key generation, decrement, diagnostic or result.
A checker-local observer and post-check export are the only other hooks. The
three-file mechanical source audit preserves all original code around them.

The selected domain is an exact TemplateLiteral target and exact StringLiteral
or TemplateLiteral source. Only plain Failed values enter the tile histogram;
reliability-marked failures are counted separately. Numeric type IDs must be
nonzero and below2^30, intersection state at most3, and neither type may have
ObjectFlagsReference. Identity relations order IDs as the original key builder
does. Relation kind and intersection state remain part of each tile's identity.

The layout is fixed at16×16, matching the standalone tiled-negative-relations
prototype. Each checker retains at most131072 tiles. Known tiles continue to
accept writes after saturation; writes to new tiles are explicitly dropped.
Dropped writes are not unique keys and a capped histogram cannot be extrapolated.
No Type pointers are retained and no semantic queries are added.

This records unique pairs *ever written as ordinary plain failures*, not current
cache entries. Successful propagation, explicit overflow writes and later value
replacement are outside this hook. Repeated writes count occurrences, not saved
CPU. Histogram payload arithmetic excludes map headers, bucket slack, pointers,
allocator classes, GC work and access latency; it is not RSS or speedup evidence.

Three focused tests validate full tiles, snapshot stability, cap accounting,
known-tile writes after saturation, marked/unsupported cases, identity ordering,
relation separation and domain exclusion. Normal/race/checkptr validation and a
separate diagnostic CLI build are required before workload capture. Four Python
checks reject corrupt accounting and duplicate owners. Baseline, observer-disabled
and enabled controls require identical pinned physical inputs and clean diagnostics.
Single invocation durations are observer-cost context only and never enter PERF.md.

No production optimization is integrated. A dense histogram would justify
further integration work, not promotion or a claim that this mechanism can meet
the10× native-relative goal on its own.

Completed all validation/control/readback checks. RESULTS.md records uncapped observed density and the decision to proceed to an isolated compiler integration; no production promotion or speedup is established.
