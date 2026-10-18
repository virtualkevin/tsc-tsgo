# Compact mutable symbol-table candidate: validated, unpromoted

This candidate replaces the compiler's `ast.SymbolTable` maps with shared mutable storage containing up to eight exact-string entries and a built-in map fallback. Nil state, present-nil values, aliases, clones, deletion, and mutation during iteration are preserved at the migrated consumers. Small-table enumeration snapshots original keys and reads current values, so iteration alone does not force map materialization. See the earlier isolated prototype and type-checked storage audit for design evidence and limitations.

The candidate's 208-byte inline state remains allocated for empty and promoted tables. Linear comparisons, iterator snapshots and method dispatch can also cost more than the baseline. Correctness results and static sizes do not establish a performance improvement.

## Preserved identities

- Candidate source: `67bdc271aedf37c03f0746414a8b67e0072dfe9c79f9aee15af8bd14b9cb4155` (5,156 files), based on `2680e2c` with 31 changed/added package files.
- Candidate executable: `packages/tsc-go/dist/tsc-go-compact-symbol-table`, SHA256 `be58977c37d393f9e6232e06415211ce6e4cb9c6c6d18787592ef6c4ea22192b`.
- Candidate sidecar: `0d130b4e7d32f3f31003850f9e9c0798ec1a40fb1dee562b85ca133bce9f5f96`.
- Retained baseline source: `216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd` (5,154 files); executable `8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f`.

Production source and the default executable are restored to that exact retained baseline. The candidate remains separately preserved. `candidate.patch` covers the 29 tracked changes and applies cleanly to the restored workspace; `compact_table.go` and `compact_table_test.go` preserve the two added collection files. `candidate-source.json` records their complete source manifest. The one-shot `rewrite.go` updates typed production/test expression sites; manual constructor, exported storage signature and map-search-helper adaptations are included in the final patch. Normal build settings match the baseline exactly. The declaration transform changes only one lookup, one constructor and one assignment; its existing prepass behavior is preserved and its reviewed hash is checked explicitly.

## Validation completed

| Check | Evidence |
|---|---|
| All Go packages including test packages compile | compile4 stdout/stderr, successful terminal session69312 |
| Root unit suites | 2,357 records, 130 top-level tests, 12 packages; no failures/skips |
| Focused race and strict checkptr | 9 records / 7 top-level tests each, including nested iteration cases |
| Pinned conformance | 14,915 configurations: 12,789 fully checked, 8 partial, 2,118 unsupported skips, zero failures |
| API/language-service Go suites | 219 test records, 60 top-level tests, six packages with tests; all pass |
| Normal CLI parity | 80/80 |
| API/emit/project CLI integration | 12/12 |
| Race-instrumented CLI parity | 80/80 |
| Checkptr-instrumented CLI parity | 80/80 |
| Archive | 26 raw evidence files, every archived member hash verified |
| Restoration/preflight | Exact baseline source/default executable restored; candidate and build settings verified |

The original service controller reported failure solely because `internal/ls/change` has no test files and Go emits a package-level skip. `record-services.py` checks the original log hashes, confirms all actual test records passed, verifies the package has no tests, and records the distinction without rerunning. Both the original report and corrected verification remain archived. Initial compile failures (recursive generic alias importer deadlock, a constructor rewrite typo, and the map-specific helper) are preserved; none is counted as a successful correctness run.

`validation.tar.gz` and `validation-archive.json` preserve raw logs and hashes; summary reports are also under `benchmarks/validation/compact-symbol-table-*.json`. `generic-boundary-review.json` reviews the 16 previously identified generic/callback argument sites; it is not a general interface-escape proof. `codegen.json` and assembly files show static tradeoffs: `getSymbol` grows from 268 to 472 encoded instruction bytes and stack reservation 48 to 56; the candidate retains a separate 301-byte `getResolvedMember` body while the baseline has no matching retained body; `propertiesRelatedTo` stays 6,318 bytes/frame 368. These are not execution-cost measurements.

## Performance status

No workload timing has run at this checkpoint. `COMPARISON_POLICY.md` freezes nine alternating pairs for TypeORM/tRPC and five for VSCode/Sentry, default settings, identical inputs and matched GNU-time RSS. Both aggregate summaries must reach 1.01, every workload summary must reach 0.98, and each median RSS must remain within 1.05 of baseline. Passing requires two further independent confirmations before promotion; no layout/capacity/dispatch retuning or opportunistic samples after a failed screen. A fresh original-native comparison is required after an accepted change. The requested 10× target remains unmet.
