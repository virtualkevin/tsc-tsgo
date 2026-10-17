# Direct primitive writes for the small keyBuilder

Source-only follow-up against319e931. Patch direct-writers.patch and exact source hashes are recorded in metadata.json. Main is untouched. Gofmt and git apply --check pass. No build, tests, codegen inspection, profiles, allocation screen or workloads have been run for this draft during the quiet window.

## Motivation and bounded change

The accepted-for-measurement128-byte builder's actual codegen shows uint32/uint64 wrappers inline, but each calls the generic writeBytes helper, which then calls runtime.memmove on the short path. writeByte itself remains out-of-line. This draft puts binary.LittleEndian.PutUint32/PutUint64 directly in the short branches and moves temporary arrays and streaming writes into width-specific overflow helpers. writeByte's overflow array construction likewise moves to a separate helper.

No buffer capacity, key grammar, hash algorithm, cache policy, structure layout, retention rule or caller changes. writeBytes/writeString/hash/stream are byte-for-byte unchanged. The existing tests are unchanged; one new boundary test addresses the new width-specific fit predicates.

The fast methods contain only a fit check, endian store and length update, with one overflow call in the other branch. This reduces syntactic work in the byte writer and removes generic copying from integer short branches. It does not establish that Go's inliner accepts them: the uint writers now also contain branch/store work, and a cold helper call still counts against the static budget. They might remain out-of-line. Even then the source no longer routes a short integer through writeBytes/memmove, but actual lowering, bounds-check elimination, frame sizes and speed require a future build. No //go:noinline, linkname, unsafe, assembly or compiler flag is introduced to force a result.

## Transition proof

Valid builder state satisfies0<=n<=128. Existing byte/string methods retain this invariant; overflow does not increment n. For a widthW in{4,8}, `overflow==nil && n<=128-W` means the complete integer fits. LittleEndian.PutUintW writes exactlyW bytes into buf[n:], then n increases byW, remaining<=128. Guards subtract a small constant from capacity rather than add to n, so there is no new arithmetic-overflow hazard. Go bounds checks remain the safety mechanism; the source does not rely on unaligned machine stores or host endianness.

If n is125 for width4 or121 for width8, the whole write goes to overflow. The draft does not partially fill remaining inline bytes. stream initializes once, writes the exact old prefix buf[:n], and the overflow helper writes the same little-endian temporary bytes the old writeBytes path would have received. This preserves both hash bytes and the old prefix-length bookkeeping. At the exact-fit boundaries124/120, the entire value stays inline; the next nonempty write crosses normally.

When overflow already exists, all three primitive methods route there regardless of remaining inline capacity; stream returns the same hasher without replaying the prefix. A previously queried hash remains nonfinal and can be extended. The byte helper writes exactly one byte. Empty writes elsewhere, zero-valued integers, maximal integer values, and signed-int conversion in unchanged callers retain their old behavior.

Builder instances remain independent. There is no global scratch, pooling, builder copying, deferred ID assignment, new semantic callback or hash truncation. Existing no-copy-after-first-write contract remains. Node/Symbol ID arguments are still evaluated before primitive writer entry at the original caller sites. Overflow payload arrays are local; actual escape behavior must be reconfirmed rather than assumed from the previous version.

## Focused test addition

Existing keybuilder_test.go is unchanged. Its mixed-integer test first overflows through a uint32 write, so it does not directly isolate a uint64 first spill at121 bytes. New TestBufferedDirectIntegerBoundaryTransitions tests widths1/4/8 at every prefix length0..129 (390 subcases): all alignments, last fitting offset, first nonfitting offset, exact full buffer and already-existing stream. It queries the hash before the primitive write, compares independently encoded bytes/full hashes through the existing streaming oracle, checks whether overflow should exist, then appends another uint64 and verifies continuation. No implementation-shaped allocation assertion or performance claim is added.

## Future gate, only after release

Run focused buffered-key tests, then inspect actual production primitive methods and callers. Confirm whether the three writers inline, whether short integer paths contain direct stores instead of CALLwriteBytes/CALLmemmove, whether bounds checks remain, and whether the short builder stays on stack. Repeat the exact-source allocation screen: <=128 bytes should remain0 allocations, spill should remain one; do not assume zero from source inspection. Full conformance/native parity remain necessary before timing. Compare against the preserved319e931 binary using identical workloads/runtime controls; current ongoing timings do not measure this draft and must not be used as evidence for it.
