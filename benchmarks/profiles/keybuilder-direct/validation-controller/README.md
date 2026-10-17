# Possible direct-writer validation: prepared only

This controller is a separate adaptation of `/tmp/tsc-small-keybuilder-validation/validate.py`. All previous controllers are untouched. Preparation ran only source reads/writes and a Python syntax parse; no build, test, workload, or controller execution was performed. Main was not modified. Root has not yet decided to apply or accept the draft.

Candidate draft: `/tmp/tsc-keybuilder-direct/direct-writers.patch`, SHA256 `6397d2b2cc8ca70ebf97663340ab70db734901ec5593d188a1c895217d12ddec`, based on319e931. Exact reviewed draft hashes:

- `keybuilder.go`: `67a96b9387677504cb07d0e3baac8f410e80b344555fd0638b03b1eb2d343725`.
- New `keybuilder_direct_test.go`: `05d375ffe42c718c1fe0f2b5c10c8939f3dab8dc32fa06eff46b760a072a3e30`.

Other exact file gates remain unchanged from the small-builder controller: checker.go, keybuilder_test.go, original relater.go, and retained relation_keys_api_test.go. Numeric relation-key production and the removed numeric unit test are rejected. The full captured source digest remains a required explicit argument supplied after future integration/build; no previous digest is silently accepted.

Only after parent applies the reviewed draft, supplies final source identity, freezes source/HEAD, and authorizes validation:

```sh
python3 /tmp/tsc-keybuilder-direct-validation/validate.py --output /tmp/keybuilder-direct-validation-main --expected-source PARENT_SUPPLIED_COMPLETE_SHA256
```

Output must be a fresh directory beneath /tmp, outside source. The controller does not apply patches, build release binaries, publish reports, or commit.

Sequence is strictly normal focused → race focused → checkptr focused → root npm test → full pinned TestSubmodule conformance. Focus is `-run '^(TestBuffered|TestRelationKeys)' -count=1`. Each focused run requires exactly ten named top-level tests and646 passing terminal test records, with no skips or failures. Static count from source: the existing255 records plus one new top-level test and390 direct boundary cases. The new test calls t.Run once for each of three widths (1/4/8) and each prefix0..129; slashes in the test name are not extra t.Run parent calls. Equivalently: ten top-level +240 existing mixed-write boundary subtests +390 new direct-write boundary subtests +four alias/type subtests +two cold-order subtests =646.

Root npm runs the unchanged ten-package alias with GOFLAGS='-json -count=1'. Full conformance uses -parallel4 -count=1 -timeout30m and separately reports fully checked, partially checked, unsupported and failed source/configuration cases. Pinned Go1.26.9 is untrimmed for fixture lookup. Normal/race/checkptr compile their own test binaries; a separately built production binary requires separate native validation.

The existing source-before/per-stage/source-after captures, source+HEAD immutability gates, fixed upstream revision checks, explicit runtime environment controls, exact commands/numeric exits/log hashes, JSON suite accounting, per-stage deadlines and process-group SIGTERM/SIGKILL cleanup remain. Any failed stage or scope/identity mismatch stops subsequent stages. No validation durations imply compiler performance. Fixture revisions are checked, but the external corpus tree is not independently content-hashed by this controller.
