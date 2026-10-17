# CJS assignment prepass guard A/B draft

Prepared only; no measurements launched. All files are separate copies under /tmp; frozen PointerLinkStore/scheduler controllers remain unchanged. Syntax-only node --check passed for the three new scripts.

Launch after validation finishes and the coordinator releases a quiet window:

`node /tmp/run-cjs-prepass-ab.mjs [NEW_RESULTS_DIRECTORY]`

The controller captures repository HEAD dynamically at launch, requires it to remain stable through both report groups, and requires both runner reports to carry that same HEAD. This operational HEAD is separate from the binary's recorded build-time revision/dirty state.

Reference: preserved PointerLinkStore849d873, binary SHA256 b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322, source6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d.

Candidate: dist/tsc-go-cjs-prepass, binary SHA256 a6da693db033a9c2a6a2d712efeb1f20507fc9dfc92ad7d02db0234116e2d80c, source02093082d3baa33b0e2d3f2f77b916a7fe01907c96d894b6805eeeab0648c014. Its sidecar records build revision8291ee5c9dc14ee2a2c244a4ec56b5c4128a0568 with dirty transform.go.

The controller compares the complete source manifests and permits exactly:

- Added checker/jsx_managed_attributes_errors_api_test.go, hash9db62d8a8fd00af674034a59a86d7d34b76e95d00766a986e9ac13802a929e99. This is a test-only addition.
- declarations/transform.go, hash3642d191e79150264e99afdadf9a832930c6f4ab2a39257d313e65498e9aa072 →224a1e3a2727790ba4fdfcbd27b9f826b8ff53d8272ca76815577c5a3bd5e625. The sole production change guards the module.exports assignment visitor with CommonJSModuleIndicator != nil. The expando expression visitor remains unconditional.

Both source manifests have the same build/toolchain settings: normal Go1.26.9 linux/amd64 v1 -trimpath build, no extra flags and no PGO profile. The complete settings objects must match; exact binary/source hashes and verified sidecars remain mandatory. As documented by build provenance, external module-cache contents/toolchain files were not originally content-hashed; matching settings do not remove that provenance limitation.

Runtime policy is symmetric: default GC, unset/default round-robin scheduler, default checker count, no candidate-only overrides. GNU time wraps both sides. TypeORM/tRPC use seven alternating pairs each; VS Code/Sentry use three; all use one warmup. Reports preserve exact args/env/inputs/diagnostics/order/resources, validate clean checks, and recompute medians/RSS. Existing reviewed cancellation, deadlines and process-owner cleanup are retained. New output directories are mandatory.

After terminal completion:

`node /tmp/record-cjs-prepass-ab.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_PROPOSAL_DIRECTORY]`

Recorder writes only proposed four PERF rows, one NOTES entry and proposal.json under a new /tmp directory. It captures the launch HEAD truthfully as capture metadata rather than inventing a candidate commit. It records the precise guard scope and distinguishes test-only source changes. Separate conformance/native/API/race validation is not inferred from benchmark passes.

This compares two preserved Go binaries; it does not directly measure the original native target. Wrapped timing cannot compare with historical unwrapped timing. RSS means command peak resident memory, not Go heap or aggregate tree peak. No performance improvement is assumed in the draft or recorder.
