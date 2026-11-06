# Page-owned compact graph prototype

Standalone research after the current A/A calibration. This addresses the earlier
typed-handle-graph prototype's all-pages retention problem with a different
ownership graph. It is not a compiler integration, speedup, or substitute for the
native-relative 10x objective. Production and PERF.md are unchanged.

Each page owns 256 pointer-free records. A record has a stable uint32 identity,
uint32 kind, four uint32 edges and uint64 payload (32 bytes total). A published
Ref contains a typed page pointer and slot (16 bytes). The allocator roots only
its current page; an owner token prevents foreign references without pointing
back to the allocator or other pages. Old pages are reachable through published
Refs or the directed graph of live outgoing page references.

A local edge encodes slot+1 in nine bits. A remote edge also encodes a page-local
remote-table ordinal. Zero is nil. The remote table uses ordinary typed page
pointers and occurrence counts; a typed pointer-key map finds existing ordinals
when storing edges. A page has at most 1024 outgoing record edges. Removing the
last occurrence clears the table pointer and deletes its map entry. Internal
remote ordinals are reused only after no stored edge references them; published
record identities and page slots are never reused. There is no uintptr decoding,
weak production ownership, global decoder, manual reclamation or allocator reset.

Set validates all inputs before mutation. Under exclusive mutation, it removes
old edge counts, encodes new edges and publishes the record while retaining the
input Refs. No supported reader or user callback observes the intermediate state.
Completed reads may run concurrently with other reads. Independent mutation of
copied Graph values and concurrent read/write access are unsupported.

## Reviewed correspondence and limits

Map each logical record identity to its page/slot Ref. Every nonzero handle
selects that Ref directly within the source page or through a live remote entry.
For each remote target page, its occurrence count equals the number of stored
edges from the source page to that target. The map and remote table represent
exactly the nonzero counts; free slots hold no target pointer. Add/Set preserve
these conditions by removing all old occurrences and adding all new occurrences,
including duplicates. Whole-page cycles rely on ordinary Go GC, not on the
occurrence counts reaching zero globally. This is a reviewed argument with finite
tests, not a machine-checked Go/GC proof.

Coarse pages still retain otherwise unreachable sibling records and their outgoing
graphs. This resembles typed slab retention and can propagate across pages. It
does not prove equivalent reclamation to individual object allocation. Dynamic
remote tables/maps and slot reuse add allocation, branching and bookkeeping.
Actual amd64 layouts: record32, page including fixed records8264, remote entry16,
Ref16, Graph32 bytes. The page's backing slices/maps and runtime allocation size
classes are additional; smaller record fields do not establish smaller live heap
or faster execution. AllocatedSlots reports cumulative allocation, not live pages.

The payload remains only scalars and four edges. Real compiler strings, maps,
variable-arity lists, API pointer facades, identity translation, query effects and
cross-checker ownership are not implemented. No compiler counters or limits are
changed. A successful storage prototype would still need cost measurements and
an actual compiler-family mapping before any integration or workload claim.

## Validation

The first build failed because a test-local source variable used assignment
instead of declaration. failed-initial-build preserves the source and raw failure.
The corrected six-test suite passed normally, with race instrumentation and with
strict checkptr; six-test-checkpoint preserves that successful snapshot. An extra
cross-page cycle-collection regression was then added, without changing graph.go.
The final seven-test suite passed normally, with race instrumentation and strict
checkptr (session89489 exit0). Independent verify.py checked all21 final test
records and source/checkpoint hashes. validation.json and readback.json preserve
the results.

Coverage: 32768 deterministic add/mutate/read operations against an integer-ID
model; exact table/count/free-slot audits; final readback; foreign/invalid inputs
and failure atomicity; nil and uint32 capacity boundaries; 1024 distinct remote
pages and full-table reuse; 1024 duplicate edge occurrences; collection of old
unrelated pages while the allocator stays alive; live remote target retention and
collection after unlink; unreachable cross-page cycle collection; an escaped
4097-record chain after discarding its allocator; completed concurrent reads and
pointer-free record layout. Forced-GC observations cover these fixtures only.

Next: measure construction, internal traversal, public Ref adaptation and both
linked/sparse-root retention against a typed pointer-page baseline. Count remote
metadata and allocator size classes, preserve the baseline's ability to reclaim
old pages, and keep all synthetic results separate from PERF.md. Only evidence of
a useful cost/retention tradeoff would justify compiler integration research.
