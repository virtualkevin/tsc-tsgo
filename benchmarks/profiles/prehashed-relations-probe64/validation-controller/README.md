# Prehashed Relation validation controller: prepared only

Adapted from `/tmp/tsc-keybuilder-saturated-validation/validate.py` (SHA256 `925bbb03a8dc75718db004035563b4fb6cc42c3a924fb9fa78b78559cf15da81`). Preparation only read source, wrote files under /tmp, and parsed Python syntax with ast.parse. No controller execution, Go command, compiler build, test, workload run, or main edit.

The author confirmed final patch `/tmp/tsc-prehashed-relation-draft/prehashed-relation.patch`, SHA256 `96999bd26b5a9443bb5e1546f13fb94a19dbb91a7015b5e20d27dbdbeaa7d60e`. Exact final relater.go, relation_results.go and relation_results_test.go hashes are pinned in the controller, along with retained relation_keys_api_test.go and primitive_union_test.go. Parent then confirmed the saturated keybuilder remains; its four unchanged checker/builder/test hashes are also pinned. Numeric relation representation residue is rejected. The final complete captureGoSources hash must still be explicitly supplied by parent after integration; no historical full-source digest is assumed.

Only after the parent releases validation on frozen source and HEAD:

```sh
python3 /tmp/tsc-prehashed-relation-validation/validate.py --output /tmp/prehashed-relation-validation-main --expected-source PARENT_APPROVED_COMPLETE_SHA256
```

The output directory must be fresh, strictly below /tmp, and outside repository sources. Strict sequential stages are normal focused → race focused → checkptr focused → root npm test → full pinned TestSubmodule. Stop at the first failure, incomplete test selection, changed source/HEAD, or other integrity error. The controller never applies patches, builds a production binary, publishes reports, or commits.

## Focused scope

Regexp: `^(TestRelationResults|TestRelationKeys|TestPrimitiveUnionRelationsMatchFullRelater$)`.

Each normal/race/checkptr run must have exactly 11 named passing top-level tests, 879 total passing records, zero skips/failures and exactly the checker package. The expected nested distribution and cache/API subtest names are enforced separately, not only the total.

- Seven RelationResults tests: zero/replacement/isolation, differential table/map behavior, overwrite before growth, bounded probes/fallback/reset, transactional rehash fallback, read-only concurrency, checked arithmetic capacity. Six nested tests: differential collidefalse/collidetrue; rehash entries64/entries65; concurrent reads collidefalse/collidetrue. Total 13 records. Distance63 overwrite and fallback nil-reset/reinsert are assertions within ProbeFallback, not additional named tests.
- Three retained RelationKeys public API tests: recursive generic assignments and exact diagnostics, two cold recursion-order cases, and repeated failure diagnostics preserving distinct use positions. Total 5 records. Despite their historical name these tests do not require the rejected numeric-key representation.
- One primitive-union test with 860 nested cases: 23 sources × 7 targets × 5 relation kinds = 805, plus 11 explicit semantic cases × 5 relations = 55. Total 861 records. It also verifies actual relation-cache population, reuse and direct nil reset through the checker. Both shortcut and full engine share the candidate storage, so only the explicit expectations provide an independent semantic oracle; storage differential tests use a separate Go map.

Total 13 + 5 + 861 = 879. These are terminal records including parents, not 879 independent top-level tests. Buffer/keybuilder tests are retained and pinned but are outside this focused selection; the later root checker suite includes them.

Race uses `GORACE=halt_on_error=1` and includes deliberate concurrent post-population reads in table and fallback modes. Neither the storage nor the tests support concurrent writes. checkptr is a separate all-packages-in-build instrumentation mode; the storage draft introduces no unsafe operation. Flag-value tests do not establish actual end-to-end recursion complexity-overflow generation. Arithmetic checks reach the machine-int boundary without allocating huge tables; no cross-architecture build is claimed here.

## Evidence and limits

Go 1.26.9 is required. Source/HEAD are captured before, after every stage, and at termination. Reports include full reviewed file hashes, expected source, exact commands, environment controls, numeric exits/signals, log hashes, package/test counts, fixture revisions and explicit incomplete status. Deadlines and process-group cleanup prevent abandoned compiler/test descendants after failure or interruption. Controller reports remain in /tmp for parent review before any selective repository publication.

Root npm test must report the expected ten packages, no skips, and no cached package results; `GOFLAGS=-json -count=1` forces fresh execution. Full conformance uses `-parallel 4 -count=1 -timeout 30m`, separately counts fully checked, partially checked, unsupported and failed cases, and verifies pinned Go/TypeScript fixture revisions before/after. External fixture content is not independently hashed. Actual full-corpus counts are reported, not substituted with historical numbers.

Normal/race/checkptr binaries compiled by Go test are distinct from the release CLI; parent owns native 80-case parity and 12 API/emit/project checks and their binary provenance separately. No duration recorded by this controller is a performance measurement.
