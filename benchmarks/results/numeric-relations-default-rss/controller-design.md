# Numeric relation-key A/B — corrected candidate verified, awaiting launch release

Separate /tmp-only adapted controller/common/recorder; all previous controllers remain unchanged. No compiler builds, tests, benchmarks or main edits were performed. All three scripts passed syntax checks; the common capture function ran successfully to verify binary hashes, sidecars, the complete source delta and identical build settings.

Do not launch until the coordinating agent releases the quiet benchmark window. Final preserved candidate SHA256 is17436c0cc37d89adb39f10ca6fdbf734c67f407fc82dc68eb23302506c796f2b; corrected source digest ba28763bee00738fc90a7f7c61dc87949860ba92d02e0dc9350bd1351b0a6f95, with5,151 files, build base7437132b3f96a0d0bb7f3edcab01968074edaa86 dirty. Sidecar SHA256 c6517f968888c5c35f871d26b94186db4804095c3e0ee1fdfc4b273d7a44ab78. Corrected relation API test SHA256 e32a99d280fc626e4812705d21fe3f856ca9a7688777b91368d1c96a1dbae5ec is pinned. The initially failed245f0f0a source is not accepted. Production file hashes remain the reviewed checker/relater hashes; only the API regression expectation changed during correction.

After final identity verification and an authorized quiet window:

`node /tmp/run-numeric-relations-ab.mjs [NEW_RESULTS_DIRECTORY]`

Reference is preserved PointerLinkStore849d873 binaryb1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322. Candidate is preserved dist/tsc-go-numeric-relations. Default GC, round-robin scheduler and checker count are symmetric, without candidate-only controls. GNU time RSS wraps both sides. Seven alternating pairs each for TypeORM/tRPC, three each for VS Code/Sentry, one warmup each. Dynamic launch HEAD and runner HEADs must remain consistent throughout measurement. Existing strict input/diagnostic/provenance/order/RSS gates and bounded process cleanup are retained.

The complete source-manifest difference must contain only checker.go and relater.go production changes, two new relation regression files, and the previously added JSX diagnostic regression versus the old PointerLinkStore build. The CommonJS guard must be reverted: transform.go equals original hash3642d191e79150264e99afdadf9a832930c6f4ab2a39257d313e65498e9aa072 on both sides. Exact final per-file hashes are checked, not just filename allowlists. Full build settings must match, using normal Go1.26.9 linux/amd64 v1 -trimpath build without PGO or extra flags.

The measured scope is numeric relation-key construction/storage: ordinary keys use direct packing, while generic/oversize keys preserve128-bit fallback hashing and are interned per checker. Narrower relation-result keys may reduce map storage, but the fallback interner retains additional state. No speed or memory improvement is assumed, and process RSS cannot isolate interner cost.

After completed measurement, `/tmp/record-numeric-relations-ab.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_PROPOSAL_DIRECTORY]` validates the reports and writes only proposed four PERF rows, one NOTES entry and proposal.json below /tmp. It reports capture HEAD separately from build-time provenance and describes the scoped production/test changes truthfully. Separate correctness gates are not inferred from timings.

This is direct Go/Go evidence, not the original native target comparison. Wrapped timing cannot compare with historical unwrapped results. RSS is command peak resident memory, not Go heap or aggregate process-tree memory. Final identities are verified; measurement still awaits the parent release after correctness validation.
