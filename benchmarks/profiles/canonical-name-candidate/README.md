# Carried canonical-name candidate — integration checkpoint

## Latest validated staging checkpoint

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
