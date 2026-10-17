# Saturated buffered-keybuilder A/B: prepared, awaiting release

Separate /tmp controller/common/recorder adapted from the reviewed direct-writer scripts. Earlier scripts are unchanged. Node syntax checks and read-only common capture verification passed; no compiler builds, tests, workloads or main edits occurred. The corrected recorder sorts both actual and expected controller filenames.

After validation, candidate commit and explicit quiet-window release:

```sh
node /tmp/run-keybuilder-saturated-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/keybuilder-saturated-default-rss
```

Fresh output directory required. Dynamic launch HEAD is frozen across reports and all captures. Both sides use default GC, default/unset round-robin scheduler and default checker count, identical explicit libraries and runtime/profile environment clearing, without candidate-only overrides. GNU time wraps both sides. Seven alternating pairs per TypeORM/tRPC and three per VS Code/Sentry, one warmup each; ratio above one favors candidate. Existing exact input/content, argument/environment, clean diagnostic, exit, order, cgroup/RSS and recomputed-median gates and bounded cleanup remain.

Preserved reference: pointer-linkstore binary `b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322`, source `6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d`, sidecar `97d330f15385fa956d521349254195da088c60ee6bec2717ac4757efc43156f2`.

Preserved candidate: `packages/tsc-go/dist/tsc-go-keybuilder-saturated`, binary `2bdcca53f630535846054eada84cae8afaa32b4faab21de029eca41c79e26303`, source `78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337` (5,153 files), sidecar `c398c606655dcc0a59c8f0167014380bbf77a836866ef1bad81422516d08de8d`, build base `23a5f1ba45e446c4a013edd9980f76e86f616e82` dirty.

Complete six-file delta is enforced with exact hashes: checker.go modified; keybuilder.go and keybuilder_test.go/keybuilder_direct_test.go plus relation_keys_api_test.go and JSX diagnostic regression added versus pointer. Updated builder SHA6c50894e… and direct-test SHAe397e66d… are pinned. relater.go and declaration transform.go remain byte-identical originals. Full build settings match Go1.26.9 normal linux/amd64 v1 CGO1 -trimpath without PGO or extra flags.

This measures combined128-byte buffering, direct primitive writers and saturated streaming length against pointer. It does not isolate any incremental optimization, and no speed or memory improvement is assumed. Relation keys/storage remain128-bit; serialized key and overflow hash semantics are preserved.

After successful measurement:

```sh
node /tmp/record-keybuilder-saturated-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/keybuilder-saturated-default-rss /tmp/keybuilder-saturated-ab-proposal
```

Recorder revalidates evidence and writes proposed four PERF rows, one NOTES entry and proposal.json only below a new /tmp directory, never main. Duplicate labels are rejected; build provenance is distinguished from capture HEAD.

Direct Go/Go comparison only, not native target or proof of10×. Wrapped timing cannot compare with historical unwrapped timings. RSS is command peak resident memory, not Go heap or aggregate process-tree memory. Raw timed diagnostic text is not retained per sample; the hashed runner enforces parity. Timing gates do not replace compiler validation, and provenance does not independently hash external module-cache/toolchain contents.
