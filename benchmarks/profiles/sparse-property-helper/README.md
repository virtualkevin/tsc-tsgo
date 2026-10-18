# Sparse property filter in a wide-target helper

Separate experiment following the rejected filter screen. Code-generation evidence in `sparse-filter-codegen` showed the old candidate enlarged the common relation frame368→440bytes and initialized filter storage before checking target size. This is a static mechanism, not proof of the tRPC regression's cause.

The new caller retains the original final loop for property lists below256. Wide lists dispatch to `sparsePropertiesRelatedTo`, which holds filter storage and performs exactly the previous filtered traversal. The filter source and four focused tests are byte-identical to the rejected variant. Hash,256-bit size, source≤7/global≤32 eligibility, augmentation inclusion, target order, exclusions, and rebuild-after-real-lookup rules remain fixed. All earlier tuple paths that change the relation result return before reaching this dispatch, so the helper starts at TernaryTrue just as the original final loop does.

This trades common-caller frame/initialization overhead for a call and an additional frame on wide comparisons, and duplicates loop instructions. No benefit is assumed. Verify actual caller/helper assembly, full pinned conformance, root/race/checkptr,80native parity,12API/emit, and48wide-target cases against retained/pinned Go before promotion. Freeze the same9/5screen and two independent19/11confirmations; no pooling with the rejected experiment or placement tuning after failure.

Build and validation passed. Source e2b806c1578b85f998691163441813314bf3e84a295f17fe439115fba28dc0b2. Guarded restoration returned production source216d40c7/defaultbinary8fe4bd80. Performance screen recorded below.

## Generated code before timing

| Function | Entry stack reservation bytes | Encoded instruction bytes |
|---|---:|---:|
| Retained propertiesRelatedTo | 368 | 6318 |
| Rejected inline-filter propertiesRelatedTo | 440 | 6734 |
| Helper variant propertiesRelatedTo | 376 | 6414 |
| Helper variant sparsePropertiesRelatedTo | 208 | 1239 |

The common caller still grows8bytes; the wide path adds a helper frame and call. Filter storage/initialization is isolated in the helper. Combined static instruction footprint grows. These facts verify the intended structural change without establishing a speedup or explaining previous timing. `verify-codegen.py` reproduces the archived assembly and metrics against the pinned tool and binary hashes.

Initial build and race compilation failed due to disk exhaustion. Old disposable Go cache files were pruned with a recorded manifest; no source/binary/validation evidence was deleted. Failed reports are retained separately. A missing default provenance sidecar from the failed build was restored only after verifying the baseline binary/hash, then the build was retried. All validation passed: full14915configuration conformance(12789fully,8partial,2118unsupported,0failed), root2343records/119top-level/10packages, four focused race and four checkptr tests,80native cases,12API/emit cases,48wide-target cases across candidate/retained/pinned Go. Archived361raw files including disk-full failures and cache reclamation manifest. Restored-workspace preflight verifies four-file delta/5157candidate source files and identical build settings. Independent frozen screen completed and failed acceptance; production remains retained baseline.

## Screen decision: rejected

Capture dda3709 completed9pairs per small workload and5per large, identical physical inputs/clean diagnostics/matched RSS. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Median RSS baseline/candidate MiB |
|---|---:|---:|---:|
| TypeORM | 1.017024 | 1.023374 | 882.352 / 881.051 |
| tRPC | 0.950525 | 0.991025 | 245.375 / 242.875 |
| VS Code | 1.010121 | 0.992178 | 7876.227 / 7468.797 |
| Sentry | 0.995104 | 0.997488 | 5341.324 / 5448.898 |

Aggregate ratio-of-medians0.992851 and paired-median aggregate1.000931 both fail1.01. tRPC's ratio-of-medians fails0.98. RSS passes. No confirmations, extra samples or placement/hash/threshold tuning. All four PERF rows, raw paired measurements and execution copies are preserved in `benchmarks/results/sparse-property-helper-screen/`. Production stays216d40c7/8fe4bd80.

Reducing the common frame did not establish an accepted workload gain. The two independent rejected screens are not a direct inline-versus-helper comparison and must not be pooled or used to causally explain their differences. No native-relative progress is claimed.
