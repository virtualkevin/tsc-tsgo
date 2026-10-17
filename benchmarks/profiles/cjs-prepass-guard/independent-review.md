# Independent review: guard only the CommonJS export-assignment prepass

Read-only source review; no compiler runs/tests/builds or main edits. Reviewed packages/tsc-go/internal/transformers/declarations/transform.go transformSourceFile, visitCJSExportAssignments, setupDiagnosticContext; ast/visitor.go; ast/utilities.go GetAssignmentDeclarationKind; printer/emitcontext.go visitor hooks.

Conclusion: no correctness blocker found for wrapping only cjsExportAssignmentVisitor.VisitNode(node.AsNode()) in `if node.CommonJSModuleIndicator != nil`. state.currentSourceFile is assigned the identical node before transformSourceFile, so this is the same condition already protecting every semantic effect in the callback. Keep expressionVisitor unconditional, actual declaration transformation and declaration diagnostics unchanged. Do not substitute IsExternalModule, compiler module setting, or filename suffix for this precise bound-source-file flag.

When the indicator is nil, the callback only (a) establishes a diagnostic-selection closure/context, (b) reads assignment kind, and (c) visits children. The only transformExportAssignment call is already guarded false. setupDiagnosticContext installs getSymbolAccessibilityDiagnostic, suppressNewDiagnosticContexts, and saves errorNameNode; defer restores all three on return. It does not issue a diagnostic or resolve a type on its own. Any AST modifier-flag queries used in selector creation are ordinary read/caching helpers, not required semantic state for later transformation.

NodeVisitor has EmitContext hooks, so calling it is not merely a raw read walk. However, VisitVariableEnvironment/VisitParameters/VisitFunctionBody and iteration hooks enter/leave fresh scopes, and the nil-indicator visitor calls no hoisting or initialization APIs. No generated declarations can arise; parameter relocation conditional on variablesHoistedInParameters stays false. Child visitor nodes remain identical, so update factories normally return the input. Embedded NotEmittedStatement handling could allocate a discarded replacement in a synthetic input tree, but it neither becomes the real output nor carries necessary declaration state. The prepass return value is ignored. No consumed lexical declarations, retained generated names, or resolver side effects were found that the skipped nil-indicator walk is required to produce.

The existing second expressionVisitor pass is semantically necessary even for TS/ESM files: it collects function/property expandos. It must remain unconditional. CommonJS files still require the first prepass over nested functions/blocks so module.exports assignment is discovered before exports-member/expando processing, regardless of textual order.

## Meaningful validation strategy

Use existing pinned compiler baseline cases to compare diagnostics and declaration text, not a mock counting visitor calls. In particular:

- declarationEmitExpandoWithGenericConstraint.ts: ordinary TS source compiled with module commonjs, but no CommonJSModuleIndicator; generic function/object expando declaration remains.
- declarationEmitLateBoundAssignments.ts: ordinary exported TS function properties with symbol/string/numeric names; guards against accidentally gating expressionVisitor.
- declarationEmitExpandoPropertyPrivateName.ts and isolatedDeclarationErrorsExpandoFunctions.ts: retain declaration diagnostics and contextual error attribution.
- jsDeclarationEmitExportAssignedFunctionWithExtraTypedefsMembers.ts and jsDeclarationEmitExportAssignedArray.ts: actual JS CommonJS positive branch including exported members.
- declarationEmitBindingPatterns.ts / declarationEmitDestructuringWithOptionalBindingParameters.ts: exercise parameter/body hooks and lexical contexts on skipped files.

A small new actual-program regression can combine two sources but must assert their bound CommonJSModuleIndicator states, proving the intended branches: (1) TS export function with generic/default/destructured parameter and late property assignments, expected .d.ts namespace/function output; (2) JS nested module.exports assignment plus an exports/member assignment textually before it, expected export-equals/member output. Include a declaration-only diagnostic case whose semantic checker diagnostics are empty, to prove declaration checks remain active under noEmit+declaration. Pin exact error code/location using the preserved baseline before creating expectations; do not bless whatever the modified compiler prints. Existing fixtures may make a new diagnostics case unnecessary.

Native parity alone is insufficient if the native already has the same guard. Pinned oracle baselines or original preserved Go output provide independent expectations. Targeted declaration suite is enough to start; full conformance before publishing a production optimization remains the parent's decision. No claim about runtime speed is made by this source audit.
