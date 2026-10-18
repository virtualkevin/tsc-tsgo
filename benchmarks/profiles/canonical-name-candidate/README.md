# Carried canonical-name candidate — integration checkpoint

## Performance decision: rejected

The matched screen at `c0d7357` completed successfully as a measurement, but failed both speed gates. Retained Go / candidate ratios of medians were TypeORM 0.971941, tRPC 0.918940, VS Code 0.913058, and Sentry 0.845896. The aggregate ratio of medians was 0.911351; the aggregate median paired ratio was 0.906158. All four workload paired medians also fell below 0.98. Median peak RSS fell modestly on all four workloads, but this did not compensate for slower execution.

The baseline remains installed. No confirmation or promotion is warranted, and this candidate will not be retuned to rescue the failed screen. Full raw samples, execution scripts, environment/build/input hashes and gate calculations are archived under `benchmarks/results/canonical-name-candidate-screen/`; four measured rows are in PERF.md. This is a Go-to-Go comparison, not evidence of progress toward the original-native 10× performance target. Reduced memory use does not establish the cause of the runtime regression.

## Current 70-file candidate

`candidate-final.patch` and `final-freeze.json` define the completed staged integration: 67 Go files plus package commands and two generation-support files. The boundary follow-up and generator support described below are now integrated in this version. Exact patch reconstruction and local generation checks passed (`final-reconstruction.json`). The exact patch was applied temporarily for a normal production build after validation, then all 70 paths were restored and the baseline source hash verified.

All six Go-side phases passed: focused normal/race/checkptr, root, services, and pinned conformance. Conformance comprises 12,789 fully checked, eight partially checked, and 2,118 unsupported cases, with zero failures. `final-tests.json` records scope and skips; `final-tests-readback.json` verifies the 12 compressed/raw logs. Normal CLI 80, API/emit integration 12, race CLI 80, and pointer-checking CLI 80 passed. `final-cli.json` records all four completed phases; `final-cli-readback.json` verifies six archived logs.

The separate overlay executable is diagnostic evidence, not the production-provenance benchmark binary. `build-production.py` requires matching completed validation and an already-applied exact candidate. The normal production build passed; its binary SHA256 matches the validated overlay executable. It preserves and restores the retained default binary and sidecar. Source application passed automatic approval after full validation. Normal build provenance verifies the exact 70-file delta and identical build settings; `restoration.json` and `preflight-restored.json` verify the restored baseline. The candidate executable is retained separately with the completed screen evidence. `COMPARISON_POLICY.md` freezes the screen and two confirmation gates. The screen results above reject promotion; the original-native 10× goal is unmet.

The compile-05 failure was an unused local after a lookup became entirely key-based; its exact patch/logs are preserved. Removing that binding produced the successful final diagnostic build. Earlier checkpoint evidence below applies only to its named sources.

## Earlier 66-file staging checkpoint

The current staged source is **candidate-next-02.patch**, with 66 files hashed in refinement-freeze-02.json. Declaration keys, 43 cached constant names and 148 typed call-site refinements extend the initial checkpoint below. Normal, race and checkptr focused runs each passed 19 records/17 top-level tests across four packages. The broader run passed 21,181 records/253 top-level tests across 14 packages, with no failures or skips. Controller 54229 finished successfully at HEAD 24fc106; source remained frozen throughout. Compressed raw logs, readback verification and exact corrected-patch reconstruction are archived. These results do not cover full conformance or the complete CLI/API/emit/services suites.

The first refinement introduced a real bug: the automated pass rewrote Node.NameKey's non-identifier fallback into self-recursion. Literal-name tests caught the stack overflow. refinement-failure-01 preserves the exact failed source and logs. The correction changed only that Go file; the refinement generator now excludes the primitive. No performance measurement was taken on either version.

The generation-support helper reproduces three generated files exactly from copies of the baseline layouts, is idempotent, and rejects unknown layouts without writes. It is a local post-generation adapter, not a rerun of the upstream generators; final package integration and provenance comments remain pending.

**boundary-proposal.patch is a separate, unapplied seven-file follow-up**, not part of those successful tests. It carries keys through additional local/synthetic/export indexes, restores string-keyed module-reference lookup and cleans comments displaced by the first migration tool. Its source copies are ignored; the patch, generator and source hashes are archived for review. Applying it requires a new source freeze and validation. The production compiler remains unchanged, and 10× original-native speedup is unproven.

## Initial checkpoint history

This is an incomplete staged compiler candidate on main, based on production source `216d40c7` at HEAD `b7fe783`. Production files and the retained executable are unchanged. No performance measurement or promotion is claimed.

The candidate stores `ast.Name` in Identifier and Symbol and uses built-in `map[Name]*Symbol` tables. It carries names through property/union/intersection lookup, pending-member layouts and positions, symbol constructors, and name-resolution scope traversal. String-facing wrappers preserve existing entry points. Parser interning now reuses Name values; an internal factory accepts an existing Name, including clone paths. SourceFile identifier membership remains available to the printer. API encoder and text-facing uses explicitly decode strings. Pending-member ordering still compares original string bytes.

`candidate.patch` is the authoritative checkpoint, including 64 staged source/test files. `checkpoint.json` hashes every reconstructed file. `archive.py` applied the patch to copies of baseline files in a private reconstruction directory, compared every resulting file to staging, then removed only that reconstruction. The ignored `staged/` tree and `overlay.json` remain available locally. Reconstruct the patch into staging copies for continued work; do not apply it to production before the remaining work and review.

Validation completed:

- Initial storage migration compiled all current-platform packages (`compile-01`, exact initial storage.patch).
- First propagation compile failed at two JSDoc string-to-Name call sites (`compile-02.stderr`); these were corrected without adding JSDoc identifier-map entries.
- Corrected carried-name version compiled all current-platform packages (`compile-03`, exact compile-03.patch and source hashes).
- Focused AST/parser/checker run passed 18 test records, 16 top-level tests, three packages, zero failures/skips. It covers canonical-name basics, factory/clone accounting, escaped-identifier parsing/interner reuse, and existing pending-member identity/order/private/static behavior. Raw logs and checkpoint counts are archived. This is not full compiler conformance, race, checkptr or CLI/API/emit validation.

The first propagation tool invocation ran from the wrong module directory and failed before source generation; its error is retained separately. Generator scripts document mechanical steps, but the final patch also includes reviewed boundary edits. Generated Go comments/layout still need final diff review. Local AST and API encoder generation support must be updated before promotion.

Remaining work includes constants and syntax/API boundary propagation, declaration-name flow, avoiding avoidable decode/recanonicalize paths, separating string-domain module/path indexes where appropriate, final source review, full compatibility gates, and the existing frozen performance screening/confirmation policy. The 10× original-native target remains unmet. Do not benchmark or promote this partial checkpoint as a completed architecture change.

Automatic approval review rejected the original proposed in-place bulk rewrite, citing broad production-file disruption risk. No production files were modified by that attempt. The subsequent authorized safer workflow generated into staging, compiled through a Go overlay, and reviewed/reconstructed the patch without applying it. A future application must use the concrete reviewed/validated diff and must not bypass that rejection.
