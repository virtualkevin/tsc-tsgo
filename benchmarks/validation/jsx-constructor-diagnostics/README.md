# JSX per-use instantiation error regression

This package preserves a confirmed diagnostic difference and the standalone regression as originally prepared, plus its later focused validation. It does not contain the proposed JSX constructor cache or any production modification.

| Compiler | Exit | TS2589 positions (one-based line,column) |
| --- | ---: | --- |
| Preserved lazy Go | 1 | (7,15), (8,16) |
| Pinned upstream Go oracle | 1 | (7,15), (8,16) |
| Original native tsc-ts | 1 | (7,15) |
| Official JS TypeScript 5.9.3 | 0 | none |

The regression contract is the two-position behavior shared by the Go baselines. The JS5.9.3 comparator is a different labeled version and is not treated as the pinned compiler oracle. The faithful native constructor canonicalization draft remains deferred because reusing constructor identity can reuse failed managed-attributes instantiations and suppress a later diagnostic.

## Contents and provenance

- `recursive-managed-attributes.tsx`: exact reproduced fixture, including its original line layout.
- `repro-report.json`: untouched original report with exact commands/semantic options, binary SHA256s, explicit library input hashes, raw output hashes, and before/after immutability checks. Absolute paths describe the original run; copied raw files are mapped in manifest.json.
- `raw/`: complete unmodified stdout/stderr from all four compilers, including empty logs.
- `REPAIR-AUDIT.md`: why top-level error checks or diagnostic-count changes do not establish safe cache admission for delayed/member/API work.
- `jsx_managed_attributes_errors_api_test.go`: standalone public-checker API regression, package checker_test. It has no dependency on private representation, new constructor helpers, internal cache entries or synthetic identity assumptions.
- `regression-test.patch`: additive patch targeting `packages/tsc-go/internal/checker/jsx_managed_attributes_errors_api_test.go` only.
- `manifest.json`: fixture/log integrity verification, test/patch hashes, and library identities.

The historical upstream-Go binary has no build-time sidecar. Its exact binary hash and repository upstream pin/build-oracle path are recorded; no retroactive verified source digest is claimed. No timings are performance evidence, since unrelated validation/builds were active.

## Test scope and later validation

The test copies the three pinned bundled libraries into a virtual filesystem and uses explicit files plus noLib, strict, target es2022, jsx preserve, noEmit and pretty false, preserving the reproduction's semantic inputs. One public checker is obtained directly, corresponding to the Go/native reproduction's --checkers1 scheduling choice. Virtual file paths differ, but library and source contents are preserved. It queries diagnostics twice and requires exactly TS2589 at both JSX-use offsets, without depending on diagnostic ordering.

The original draft was applied unchanged to the repository and the focused Go test passed: one test, no failures or skips. Exact command, test hash, source digest and scope are in [the validation report](../jsx-managed-attributes-errors.json); copied execution logs are `applied-regression.jsonl` and `applied-regression.stderr`. The manifest’s draft status describes preparation time. No production compiler change or broad test rerun is attributed to this test-only addition.

Reproduce from `packages/tsc-go` with an untrimmed test build:

`go test ./internal/checker -run '^TestJsxManagedAttributesReportsInstantiationDepthAtEachUse$' -count=1`

The test uses bundled.TestingLibPath and the pinned bundled library fixture links. It does not require the native compiler or original temporary reproduction directory. Full library files and compiler binaries are not copied here; exact identities remain in the original report and manifest.
