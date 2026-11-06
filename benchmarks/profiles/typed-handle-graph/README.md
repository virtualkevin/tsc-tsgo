# Pointer-free typed-page graph prototype

Standalone architectural experiment after fused-intersection-lookup rejection
8a1c781. No compiler integration, workload timing, PERF.md row or speedup claim.
This changes graph-edge representation and ownership, rather than another header,
map layout or guarded compiler shortcut. It is not a substitute for the 10× goal.

A graph owns typed pages of 256 fixed records. Records contain a uint32 kind,
four uint32 edge handles and a uint64 scalar payload. A handle is a one-based
slot index; zero means nil. Decode uses a checked slice index and page offset.
There is no uintptr address reconstruction, hidden Go pointer or weak ownership.
A record cannot own pointer-bearing payloads; strings, symbols, maps, variable
arity and actual compiler type variants are not represented by this prototype.

Published `Ref` values carry the graph owner and handle. Equality distinguishes
owners even when local IDs coincide. All edge admission checks reject foreign or
invalid references before mutation. Reading an edge reconstructs a reference
with the same owner. Growth never relocates existing pages. There is no deletion,
reset or handle reuse. Exclusive mutation is required; concurrent completed reads
are supported only without concurrent mutation.

The lifetime tradeoff is deliberate and unresolved: one published reference
retains every allocated page, including unreachable records. Existing compiler
arenas can release old slabs when no pointer reaches them; this representation
can lose that behavior. Earlier lifetime and heap censuses remain relevant.
This prototype is **not** authorization to retain every compiler type indefinitely.
It establishes a concrete alternative whose retention cost can be measured, rather
than treating existing TypeIDs as a free decoder or storing integer-only roots.

Measured on the pinned amd64 toolchain: record32bytes, page8192bytes, published
Ref16bytes, Graph32bytes, plus the owner slice's pointer entries/capacity. The
record-field reflection check verifies only integer fields/arrays. Public Ref
is larger than one pointer and Read returns four owner-carrying references;
these costs matter. The core owner-scoped handle traversal and public adapter
must be measured separately. Smaller records do not establish faster execution.

Validation passed five tests each normally, with race instrumentation and strict
checkptr. Coverage includes65,536 seeded add/mutate/read operations against an
independent integer-indexed graph model, final full graph readback, identity,
cycles, failed-operation atomicity, cross-owner/invalid references, zero capacity,
actual uint32 full-boundary rejection, page boundaries, growth/GC retention with
only a published root remaining, and concurrent reads after mutation completes.
The synthetic full-boundary sentinel tests only rejection before any slot access;
it does not allocate billions of records. Tests are not a universal proof.

Z3 verifies six32-bit arithmetic lemmas by unsatisfiable counterexample queries,
plus a satisfiable broken-mask negative control. Source text checks and hashes
bind the modeled constants/expressions, but the proof is limited to arithmetic:
no Go semantics, GC, owner lifetime or compiler-equivalence theorem is claimed.

Next experiments, before compiler integration:

1. Compare owner-scoped handle traversal with stable typed pointer-page traversal
   on identical graphs, retaining all reachable nodes in both representations.
   Separate construction, internal traversal and public reference adaptation.
2. Measure sparse-root retention separately. The baseline must be allowed to
   reclaim unreachable old pages; do not make it retain everything to manufacture
   equality. Record retained allocation and GC cost, not just nominal struct size.
3. Map an actual compiler payload/edge family and all exposed pointer/identity
   surfaces to this representation. Shared ownership, variable lists, cold payloads,
   type creation order, limits and escaping API objects remain open obligations.

A standalone win would justify only that next investigation. Production changes
still require the full oracle/API/conformance and pinned workload gates.
