# Structured call-data storage prototype

Candidate at cda3026, source dfadc4329383b5acb32127c9bdf14295a5cd94e113894d4c9cbb34d32a12d3d9. Four production files and one test file differ from retained source216d40c7. This implements the analysis document's hot/cold-field separation hypothesis without type IDs or a global decoder. StructuredType moves its signatures, call count, index-info slice and abstract-constructor emit cache into one lazily allocated typed record owned by the structured type. Existing nil and non-nil-empty slices remain distinct; public clipping and internal un-clipped views are preserved. Setting members does not clear the independent emit cache. No semantic caches, budgets, resolution order, or hash keys are intentionally changed.

Expected amd64 field storage: replace64bytes by8byte pointer, plus64bytes per populated record. This is layout arithmetic, not measured total heap/RSS. Savings depend on population, allocator size classes, lifetime, and pointer-access costs. Callable/indexed types gain an allocation, so end-to-end regressions are possible. No strong all-type decoder and no unchecked pointer conversion are introduced.

## Validation

All validation is complete for source `dfadc4329383b5acb32127c9bdf14295a5cd94e113894d4c9cbb34d32a12d3d9` at HEAD cda3026. Normal candidate binary SHA256 `d93225f34a386e3b990005f49d309fbeef9ae3c1fcf909214c700491baf3c2cf`, sidecar `180fe99caab15dad03db3968cd91529be548d7508478a501cde4db905f132a07`.

- Focused normal/race/checkptr: three tests each; covers member resets, slice aliases/capacities, nil/empty distinctions, independent emit cache state, and GC reachability.
- Core suite: 2,342 passing test records across ten packages.
- Full pinned conformance: 14,915 configurations; 12,789 fully checked, eight partially checked, 2,118 explicitly unsupported, zero failures.
- Services: 219 passing test records, 60 top-level tests, six tested packages and one explicitly verified no-test-files package.
- Normal CLI parity: 80 passed; API/emit/project integration: 12 passed.
- Race and checkptr CLI parity: 80 passed each, no skipped or failed tests.

`validation.tar.gz` preserves 25 raw files, including logs and controller reports. `validation-archive.json` records their SHA256 hashes and the archive hash; every member was read back and verified. These tests do not prove universal correctness or performance. Controllers preserve exact source, binary and pinned-reference identities.

## Ownership and code generation

The typed copy inventory spans 234 loaded package variants and 4,954 deduplicated syntax files, including dependency syntax exposed by the loader. All 29 by-value expressions containing StructuredType are fresh composite literals: 25 addressed constructions and four Sizeof test operands. Two test literals initialize declaredMembers while leaving the embedded StructuredType zero. No populated-value copy was found in this build configuration. `copies.json`, `audit-copies.go`, and `copy-review.json` preserve evidence and limits; this is not a universal proof about reflection, external callers or other build tags.

Measured amd64 sizes: StructuredType112, ObjectType136, TypeReference168, UnionType224, optional record64 bytes. Static disassembly shows newObjectType unchanged at411 encoded bytes, getSignaturesOfStructuredType191→280, and setStructuredTypeMembers712→799. These are body sizes, not executed instruction counts or speedups. Extra nil checks and allocations must be weighed against reduced object size in actual workloads.

## Performance status

The completed screen is rejected; see `../../results/structured-call-data-screen/README.md` for all workload summaries and `recording/proposal.json` for the gates. The frozen policy uses nine alternating pairs for TypeORM/tRPC and five for VS Code/Sentry, one warmup each, matched GNU time RSS, fresh processes and identical inputs. Passing requires both aggregate ratios≥1.01, every workload summary≥0.98, and median RSS≤1.05×baseline; two independent confirmations are then required before promotion. No layout or accessor retuning after a failed screen.

`restoration.json` verifies production source restored to216d40c7 and default binary8fe4bd80 before timing. The candidate is preserved separately, with its patch and added test file. Restored preflight passes matching build settings and the exact five-file candidate delta. No promotion or native-relative speedup claim; the10×goal remains unmet.
