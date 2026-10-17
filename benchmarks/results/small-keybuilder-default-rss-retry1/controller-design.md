# Buffered small-keybuilder A/B: prepared, awaiting release

These separate /tmp scripts preserve all previous numeric/CJS/pointer controllers. No compiler, test, workload or benchmark was launched, and no main files were changed. All three scripts passed `node --check`; importing the common module and calling `capture()` passed actual preserved binary/sidecar hash, complete source-delta and identical build-setting checks.

After correctness gates finish, their evidence is committed, and the parent releases a quiet window:

```sh
node /tmp/run-small-keybuilder-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/small-keybuilder-default-rss
```

The results directory must not exist. The launch captures repository HEAD dynamically and requires that HEAD throughout both groups, including matching HEADs recorded by the runner. Scripts, wrapper, Node, harness, manifest, binary and sidecar identities are frozen in the capture. Both compiler sides use default GC, unset/default round-robin scheduler and default checker count, with all experimental/runtime/profile knobs cleared and the same explicit library path. No asymmetric compiler environment or checker override is allowed. GNU time wraps both sides. TypeORM and tRPC each get seven alternating pairs; VS Code and Sentry each get three; all have one warmup. Ratios above one favor the buffered candidate. Inputs, actual args/env, diagnostic cleanliness, exits, alternating order, cgroup counters, RSS resources and recomputed medians are validated. Cleanup/deadline behavior is inherited from the reviewed pointer/numeric controller.

Reference: preserved pointer-linkstore binary SHA256 `b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322`, source `6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d`, sidecar `97d330f15385fa956d521349254195da088c60ee6bec2717ac4757efc43156f2` (reference label849d873; actual build-time revision retained separately in sidecar).

Candidate: preserved `packages/tsc-go/dist/tsc-go-small-keybuilder`, binary SHA256 `9d87e9195e65a2113fec862d702faa313b51749c171cf92ddc6756eda0719b85`, source `4937cfc277515b8b566162d078dd493524d406de94ced593a78f38bbd6c7aa5d` (5,152 files), sidecar `a69df92a3a587b5f36e7823159c73cc57175b37176d7a91c5e5fadd2fa982e0c`, build base `f1551e0dd417880cd007ae18353fa9c2d386f63d` dirty.

The full source-manifest difference is enforced with exact file content hashes: modified checker.go, added keybuilder.go, added keybuilder_test.go, retained relation_keys_api_test.go, and added jsx_managed_attributes_errors_api_test.go. relater.go is byte-identical original 128-bit relation storage; the declaration transformer also matches the baseline (CJS guard reverted). Production changes only extract the key builder and replace streaming short-key hashing with a local 128-byte buffer and one-shot xxh3, preserving streaming overflow behavior. Settings match exactly: normal Go1.26.9 linux/amd64 v1, CGO1, `build -trimpath`, no PGO/extra flags. No performance benefit is assumed.

After measurement, validate and create documentation proposals ONLY under a new /tmp directory:

```sh
node /tmp/record-small-keybuilder-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/small-keybuilder-default-rss /tmp/small-keybuilder-ab-proposal
```

Recorder writes four proposed eight-column PERF rows, one NOTES entry and proposal.json; it never changes main documentation. It rechecks all evidence, source/settings deltas and script hashes, rejects duplicate documentation labels, and distinguishes capture HEAD from build provenance.

This is a direct Go/Go experiment, not the original native target comparison. Wrapped times cannot compare with historical unwrapped times. RSS is command peak resident memory, not Go heap or aggregate tree memory. Timings do not replace separate compiler correctness validation and do not establish the user's10× target. Build provenance is not a hermetic attestation of external module-cache or toolchain bytes. Raw timed diagnostic text is not separately retained per sample; the hashed runner enforces parity during invocation.
