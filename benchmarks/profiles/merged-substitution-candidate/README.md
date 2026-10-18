# Geometric merged-substitution candidate

Integrated isolated compiler overlay at a5c9426; production remains source216d40c7/defaultbinary8fe4bd80. Correctness oracle remains pinned upstream2bd066d8/binaryb7b9a434; original native525c0fe9 is the performance target. No production or baseline replacement has occurred.

Pure trees contain only SimpleTypeMapper and MergedTypeMapper nodes. Each merged constructor records a saturated weight; eligible exact leaf counts16,32,64,128,256 build a typed source-to-final-result map. Other merged nodes evaluate their original children, which may contain eligible descendants. Ineligible effectful/array/composite/inference nodes propagate zero eligibility. Counts above256 saturate257; no wraparound. Thresholds are frozen before workload measurement, not tuned on results.

This is a bounded implementation of reusable substitution plans, not result memoization. Simple mapper source/target fields are constructor-owned and unchanged afterward. Composition repeats the original ordered pointer substitutions for every distinct source; absent sources remain unchanged. Nil keys/results use comma-ok lookup. Constructors execute no semantic queries or callbacks. Original child pointers, kind, structural ordering and roots are preserved. Completed maps publish with construction and support concurrent reads. No lazy publication, synchronization protocol, inference sharing, diagnostics suppression, or counter replay is introduced.

Representation cost: MergedTypeMapper gains one map pointer and a uint16 weight (including alignment cost); all merged allocations pay this, even when ineligible. Compilation allocates an intermediate leaf list and result map; ancestors may compose at geometric sizes. These costs must be included in whole-workload measurements. The prior13.4×deep-chain mechanism result is not a prediction for this candidate.

Focused tests:6561four-substitution prefixes embedded in16leaf trees, nil/duplicate/cycle/absent behavior against recursive evaluator bypassing compiled maps; eligibility through300leaf ancestors and live effectful/array behavior; concurrent read-only evaluation; original intermediate-root survival across GC. Fullroot/services/pinnedconformance and normal/APIemit/raceCLI/checkptrCLI are required before timing. Existing stateful prototype histories are supporting component evidence, not a full upstream API replay.

Validation42429 is running against frozen overlay/source/HEAD. CLI controller prepared separately. No promotion or workload speedup claim. Full standard build provenance, workload screen and independent confirmations remain required. PERF contains no diagnostic/mechanism rows.

## Completed validation and preflight

Original controllers42429/75717 were interrupted bySIGTERM; their failed reports and empty partial logs are preserved. Completed focused4tests eachnormal/race/checkptr and normalCLI80/APIemit12 remain valid. Resumed51909 passedroot21179/services219/full14915conformance (12789full/8partial/2118unsupported/0failed). Resumed32670 passedrace80/checkptr80; supervisors recordedcleanexit. Independentreadback35739 passed allsource/patch/binary/comparator andraw/archive checks.

Normalbuild99211 passed: source04c8543327a74557b352d80769d25b642136c1074c733254ccc0316306682d16 (5156files), binaryd234c3c6e9e08a2863c7886ce0a98acb44340186ea97801df57ce5599cb976f5, sidecar7cafd9d842f3c61f475cb6ba45ae9d8f54197882455fac0fb30dd597c49f3507. Baseline216d40c7/8fe4bd80 restored. Benchmarkpreflight passed with exactly3changedfiles/identicalbuildsettings. Candidate notpromoted; workloadperformance unmeasured.

Compressed test logs are committed; raw decompressed logs remain local and ignored. The verifier is captureHEAD-bound and was run before commit. Reconstruct raw logs from their corresponding .gz files when inspecting archived evidence; do not reinterpret a laterHEAD mismatch as a test failure.
