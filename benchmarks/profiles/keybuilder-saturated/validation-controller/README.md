# Saturated streaming length validation: prepared only

Separate adaptation of `/tmp/tsc-keybuilder-direct-validation/validate.py`. Previous controllers are unchanged. Preparation performed source reads/writes and a Python syntax parse only. No validation/controller execution, builds, tests, measurements or main changes.

Reviewed patch `/tmp/tsc-keybuilder-saturated/saturated-length.patch` SHA256 `2bf2c71a216d22733cc23ac65773cba99279e9759fbed203e90843043a13110a` updates exact pinned hashes:

- keybuilder.go: `6c50894e0b6c481c2878af208c31f575e15829025a594261cda3e9e10a16d13a`.
- keybuilder_direct_test.go: `e397e66d6cb2da4566e517ec75fdd00c2dcbe02eceea0915bba1ad1631dee3db`.

All other reviewed file gates remain unchanged: checker.go, keybuilder_test.go, original relater.go, retained relation_keys_api_test.go. Original128-bit relations are required; numeric relation residue is rejected. The parent must supply the final complete source digest after integration/build; no previous candidate digest is silently reused.

After parent explicitly authorizes validation with frozen source and HEAD:

```sh
python3 /tmp/tsc-keybuilder-saturated-validation/validate.py --output /tmp/keybuilder-saturated-validation-main --expected-source PARENT_SUPPLIED_COMPLETE_SHA256
```

Fresh /tmp output only. Strict sequential stages: normal focused → race focused → checkptr focused → root npm test → full pinned TestSubmodule. Focus `-run '^(TestBuffered|TestRelationKeys)' -count=1` requires exactly11 expected top-level tests and655 passing terminal records, with zero skips/failures. Count verified from source: previous646 + new TestBufferedKeyBuilderSaturatedStreamingLength parent1 + eight explicit prefix subtests =655. Total is11 parents +240 mixed-write boundaries +390 direct-write boundaries +8 saturated-streaming prefixes +4 alias/type +2 cold-order cases.

Root npm alias stays ten packages, uncached with GOFLAGS='-json -count=1'. Full conformance uses -parallel4 -count=1 -timeout30m and reports fully checked/partially checked/unsupported/failed cases separately. Go1.26.9 validation is untrimmed for fixture lookup. Release binary/native validation remains separate from these compiled test binaries.

Source/HEAD captures before, after each stage and at termination; explicit digest, reviewed file hashes, upstream pinned revisions, command/environment/exit/log hashes, strict package/test scope, deadlines and process-group cleanup are preserved. Failed stage or identity/scope gate prevents later stages. Runtime/profile controls are cleared without logging secret values. Conformance fixture revisions are checked before/after, while external corpus contents are not independently hashed. No reported duration is a performance measurement. Controller never applies patches, publishes reports, commits or builds production binaries.
