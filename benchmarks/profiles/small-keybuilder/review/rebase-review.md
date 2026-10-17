# Small keyBuilder rebase and native-controller review

Source-only review; no execution, Go commands, builds, tests, or main source edits.

## Rebased patch

Approved patch d3a9248bb3f7874b3271023f2845637a9d0fbce943d612dc8ae14149bf0626e1. New keybuilder.go and keybuilder_test.go diff sections are byte-identical to previously reviewed6291b284 draft. checker.go context is restored full128-bit relation hashing; only its old explicit uint32 state write changes to the byte-equivalent buffered writer. Numeric representation-test hunk is removed. No numeric interner or64-bit RelationKey representation remains. Current preapply checker SHA5f4ea48686c739b07e5b9c54551cd35783884c26f047bcaba8209480776d2eb1 and relater SHA5e4638c881b4371c828a4a71cd1b2204a90c0aa4b1da8c9a5c1759f0b4c58aae match rollback; corrected public API test SHAe32a99d280fc626e4812705d21fe3f856ca9a7688777b91368d1c96a1dbae5ec remains unchanged. Earlier serialization/reentrancy/no-copy review and escape/spill cost caveats apply. Indexed-access grammar is13bytes with nil alias (4+4+4+1), not12.

## Native controller

Reviewed /tmp/run-small-keybuilder-native.mjs SHA e628deff5a45225a9253e52cd14047c89ea82573a46ce0cb41f6313494525e90 after parent corrections. Approved for the intended two normal native suites, not proof of full compiler correctness or race-instrumented CLI behavior.

The controller verifies sidecar integrity and binary hash, then requires complete captured Go source digest to match the build. It records all three actual comparator binaries. Exact80 differential cases plus12 API/emit/project tests must pass with0failed/skipped/cancelled/todo and exit0; missing summary fields or errors fail closed. It stops after failed suite, hashes logs, and rechecks source/candidate/comparators/sidecar before declaring success. Child runs use explicit candidate/baseline env; project filtering and checker/scheduler overrides are cleared. Toolchain and default-versus-instrumented limitations are stated.

Found and resolved before launch: api.test.mjs's report helper truncates failures using SHOW_FAILURES, so inherited0 or NaN could mask differential mismatches while reporting passed tests. Parent added SHOW_FAILURES to unsetEnvironment. This is a preventive controller fix; there is no evidence previous runs inherited such a value, so no retrospective failed-validation claim is warranted. Parent also checks exactly one @scriptc/cli-* package named cli-linux-x64-gnu, ensuring the hardcoded comparator hash matches toolchain.mjs's discovered oracle.

Scope limits: captureGoSources covers Go build sources, not every external pinned library, JS harness or fixture file; those auxiliary inputs are not independently before/after hashed by this controller. This does not invalidate the immutable compiler-source claim but should remain explicit. Child duration is not benchmark evidence, CLI is not race-instrumented, and full Go conformance/units are separate. Optional nonblocking provenance improvement: record actual process.execPath/process.version rather than generic node, and result.signal alongside null exit/error for terminated children. No extra workload runs required by this review.
