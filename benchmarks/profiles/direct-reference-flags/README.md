# Direct symbol-reference flags: validated candidate

Capture HEADc83b57c; production source216d40c7/defaultbinary8fe4bd80 unchanged. This is an unpromoted two-file compiler overlay plus focused tests. It applies the semantic-storage direction from OPTI_ANALYSIS_01.md to a scalar-only links family; no full-workload speed claim is made.

The existing SymbolReferenceLinks contains only SymbolFlags. Its pointer is never published outside the seven checker access sites: two monotonic OR writes and five reads. Replacing LinkStore[*Symbol,SymbolReferenceLinks] with map[*Symbol]SymbolFlags removes the value arena and dependent value-pointer load. Both writes use symbolReferenced, which lazily initializes the checker-local map and ORs meanings. All five reads use ordinary map lookup, with zero for absent keys. No query, ID assignment, diagnostics, recursive work, or evaluation order is deliberately changed.

An intentional lifetime difference: reading an absent symbol no longer inserts a zero-valued entry or retains that key in this map. Written keys, including zero-meaning writes and nil keys, remain typed map roots. There is no published SymbolReferenceLinks identity to preserve; symbol pointers remain unchanged. Whole-compiler validation still needs to establish behavior, including unused-variable/parameter/private-member diagnostics, merged symbols, API query order and emit. Completed reads are safe concurrently; writes remain checker-exclusive as before.

Costs may increase: a flag write now does a map read and map assignment rather than mutating a pointed-to value after one lookup. This is a representation experiment, not a justified speedup. The retained normal profile attributes1.287% of VSCode sampled CPU to the reference-kind LinkStore map path; that is neither total cost nor removable runtime, and cannot explain10× by itself. A successful pilot could motivate examining other scalar-only state families; it does not authorize changing them without evidence.

Four focused tests cover randomized differential flags against the old LinkStore representation, nil/zero/read-before-write/checker isolation, retention of written keys, and concurrent completed reads. validate.py runs normal/race/checkptr, expanded root tests, services, and full pinned conformance. It freezes HEAD, original source hashes, overlay hashes, pinned fixtures and default executable. CLI/oracle/API/emit/instrumented parity and controlled workload measurement remain separate required work before promotion.

prepare.py recreates ignored staged source and the overlay from the production files. candidate.patch records the exact modifications; direct_reference_flags_test.go is the added test source. Do not regenerate staged files or alter source/HEAD/controller while validation session37612 is active. Test logs and partial validation.json record completed phases. No benchmark has been launched.

## Interrupted services phase

Original validation37612 completed normal/race/checkptr (4tests each) and root21179tests across14packages, then receivedSIGTERM during services. validation.json intentionally remains failed/incomplete with KeyboardInterrupt('15'). No failure event was present in the interrupted services stream; interrupted-services.json and compressed raw streams preserve it. This is not accepted services evidence. New controller validate-remaining.py runs only a complete fresh services phase and conformance, retaining the identical source/HEAD/pins. Supervisor records any signal sender; no signal suppression or automatic retry. CLI87518 continues independently and has passed normal80case parity. No timing or promotion.

## Completed validation and normal build

Four focused tests each passed normal/race/checkptr; expanded units21179records/14packages, services219records, conformance14915configurations (12789full,8partial,2118unsupported,0failures), CLI80normal/80race/80checkptr, API/emit12. Independent readback55872 passed raw/archive hashes, exact patch, source identities and coverage. Interrupted services evidence stays separate.

Normal production build20146 passed: source3958f79a (5155files), binary25f46474092282b85f14f85a3eb70e097978401c86d5d6dca0a5c00bbc888777, sidecar256447ca8c8e0cc6d5f2792e6429e314bf807407b087109145e1cf4686791281. The executable matches the validated overlay. Exactly checker.go/types.go and the added test differ. Baseline source216d40c7 (5154files), default binary8fe4bd80 and sidecar76e6c4f0 were restored. Preflight92791 passed identical build settings and exact3file source delta.

Performance remains unmeasured. Frozen screen policy requires9small/5large pairs, both aggregate ratios>=1.01, both workload summaries>=.98 and median RSS<=1.05baseline, followed by two independent19/11confirmations. This does not establish10xoriginal-native performance. No production promotion.

Validation controllers/readback pin captureHEADc83b57c and intentionally refuse rerunning unchanged after commit. Raw large event streams are workspace-only; exact compressed archives are committed. prepare.py regenerates ignored staged source. manifest.json hashes all committed profile files except itself.

## Completed screen: qualifies for confirmation

Capture0473c3d/session33859 completed exit0 without a signal; independent recorder45751 passed exact inputs, source/binary/controller checks and all gates. Ratios of medians/paired medians: TypeORM1.026488/1.032241; tRPC1.013730/1.036124; VSCode1.001262/.995469; Sentry1.010668/1.009808. Aggregates1.012996793/1.018274439, all workload floors and RSS pass. Four measured rows added to PERF.md. Raw reports and11readback-verified execution files reside in ../../results/direct-reference-flags-screen. Two separate confirmations remain required; no promotion or native-relative gain claim.
