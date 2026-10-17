# Saturated streaming length draft

This isolated patch makes a streaming builder's `n` equal128 after copying its existing prefix to the hasher. Primitive writers can then test the remaining inline capacity without separately loading/testing `overflow`. No main source was changed, and no build, test, profile or workload was run. Only formatting and `git apply --check` were performed. Inlining and runtime effects remain unmeasured.

## State proof

The zero value has `n=0`, `overflow=nil`. While inline, every writer increments `n` only when the complete payload fits, so `0<=n<=128`; empty writes preserve it. `hash` never changes state. The first `stream` call allocates the hasher and writes exactly `buf[:old n]` BEFORE saturating `n=128`. A subsequent `stream` call returns the same hasher without copying any prefix again. Thus after every completed method call, `overflow!=nil` implies `n==128`.

For width1,4,8, the guards `n<128`, `n<=124`, `n<=120` exclude every streaming state. In inline states, they are exactly the previous predicates because `overflow` is nil. On failure, the existing overflow helpers call `stream` then append precisely the same encoded payload. Exact-fit `n=128,overflow=nil` remains legal: hashing still uses the complete inline buffer; the next nonempty primitive spills. No negative/greater-than128 sentinel is introduced, so existing slice bounds remain valid.

The byte-slice/string writers and hash retain their pointer checks. An empty slice/string at an inline full buffer stays inline; in streaming mode it writes an empty payload to the hasher. A first spill from a partial prefix neither includes unused buffer bytes nor loses the prefix. A long first write copies zero prefix bytes before saturating; later primitive writes cannot accidentally append into the inline buffer. Repeat hashes remain nonfinal and continuations preserve the same stream.

There are no external callbacks between prefix copying and saturation. The existing xxh3 byte writes do not return an error; allocation failure is fatal as before. Concurrent mutation of one builder and copying a builder after its first write or explicit stream creation are unsupported. Normal zero-value construction and all existing helpers honor the invariant; fabricated private-field mutations would not, and are not a supported API.

## Tests and scope

The existing direct-writer boundary cases are unchanged: they cover each width at prefixes0..129, exact fits, first/existing overflow, and continuation. Existing string/byte/mixed/hash equivalence tests also remain unchanged.

The added eight-subcase test explicitly forces streaming at zero, partial and full prefixes. It asserts saturated length and stable hasher identity, checks hash equality against independent streaming and one-shot oracles before and after empty writes, then exercises byte, uint32 and uint64 continuations. This specifically catches saturating before prefix copying, repeated prefix copying, and forgetting to reroute primitive writes after an explicit partial-prefix transition. These tests are prepared but UNRUN.

Production scope is one assignment and three guard simplifications plus an invariant comment in `keybuilder.go`; only `keybuilder_direct_test.go` gains tests. No hash/key serialization, ID evaluation order, allocation strategy, map key type or caller changes. The previous candidate's out-of-line cost81 observation motivates the draft but does not establish that this variant will inline or run faster.
