# 512-probe Relation validation: prepared only

Separate adaptation of `/tmp/tsc-prehashed-relation-validation/validate.py`. Read `REVIEW.md` for independent source review and `metadata.json` for controller/patch hashes. No validation execution or main changes.

Only after explicit parent release on frozen main source/HEAD:

```sh
python3 /tmp/tsc-prehashed-relations-512-validation/validate.py --output /tmp/prehashed-relations-512-validation-main --expected-source PARENT_APPROVED_COMPLETE_SHA256
```

Fresh /tmp directory required. The parent supplies the complete source SHA after applying the512 patch; no old source SHA is reused. Exact pins cover final relater/cache/tests, retained public relation API and primitive-union tests, and retained saturated checker/keybuilder/test files. Numeric relation rollback checks remain active.

Stages remain sequential: focused normal, focused race with GORACE=halt_on_error=1, focused checkptr, uncached root npm ten-package tests, full pinned TestSubmodule. Each focused run requires11 named top-level tests and879 passing terminal records, no skips/failures, and exact subtest distribution. Cache tests contribute13 records; public API tests5; primitive-union matrix861. Rehash subtests are now entries512/entries513, not entries64/entries65. Normal/race/checkptr compile Go test binaries; release CLI/native validation is separate.

The controller captures sources/HEAD before, after each stage and at termination; records numeric exits/signals, commands, environment controls and log hashes; checks fixture revisions; separates full/partial/unsupported conformance cases; and stops on any failure or scope/identity mismatch. Test flags cover stored overflow values and capacity arithmetic, not deliberate end-to-end semantic complexity-overflow generation. Concurrent-read tests do not authorize concurrent writes. No duration is performance evidence. See the prior64 README for unchanged detailed coverage limitations.
