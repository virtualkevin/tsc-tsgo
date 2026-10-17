# Omitted default-argument mapper audit

Source-only: no main edits, patch, build, test, profile or workload execution. A real repeated-fill difference exists, but general per-mapper memoization is not yet justified by the source proof. A very narrow stable-primitive cache is defensible if explicit argument evaluation is preserved; it mostly saves vector/mapper setup, not the hypothesized repeated instantiateTypeWorker work. Attribution should precede a broader semantic cache.

## Exact callgraph and native delta

Go checker.go:17011 calls getInferredTypeParameterConstraint from getConstraintFromTypeParameter when an infer parameter has no declared constraint. For an infer node immediately inside a TypeReference (parentheses skipped), getInferredTypeParameterConstraint:17045–17067 resolves the referenced parameters, finds the corresponding declared constraint, constructs a DeferredTypeMapper, then instantiates that constraint. There is one callback per referenced parameter; each callback calls getEffectiveTypeArgumentAtIndex(parent,typeParameters,index).

mapper.go:194–209 stores callbacks without memoization and invokes the matching callback on EVERY Map. Explicit-index queries resolve that exact type node. Omitted-index queries invoke getEffectiveTypeArguments:21830, resolving ALL explicitly supplied nodes, then fillMissingTypeArguments:21851 fills the entire missing suffix. Each default invokes instantiateType with a newly constructed mapper over the same progressively populated result slice. Repeated missing indices can therefore repeat the full vector fill and mapper creation.

Native checker-inference.ts:2433 TypeArgumentMapper stores `filled`. Explicit-index queries still resolve their node each time. First omitted-index query resolves all provided nodes and fills; subsequent omitted queries reuse the whole array. Publication occurs only after fill returns. There is no explicit busy state, cycle sentinel or diagnostic check in that native cache. Recursive access before publication sees undefined and repeats the old fill; a nested call may publish before the outer call overwrites it. That code is a reference implementation, not proof that every result is context-independent.

The native call passes false for JavaScriptImplicitAny. Go passes ast.IsInJSFile(node). Native fillMissingTypeArguments also lacks Go's conversion of unknown/empty-object defaults to any under that flag. Both differences matter. Do not copy native's false or replace Go's fill with native logic. In Go minTypeArgumentCount is computed but the current fill implementation does not use it; removing/changing the shared helper is unrelated scope.

getInferredTypeParameterConstraint also serves declaration generation through nodebuilderimpl.go:3384, but that call passes omitTypeReferences=true and never constructs this particular mapper. Other consumers of getEffectiveTypeArguments/fillMissingTypeArguments are numerous and out of scope.

## What is stable and what can change

The callbacks capture a type-reference AST node, a parameter slice and per-callback index. The node and slice membership are stable within this checker/program; the parent-walking loop finishes before callbacks are constructed. These are not inference fixing callbacks directly. However, referenced Type objects have lazy mutable constraint/default/member state, and resolving provided nodes can reenter inference/default resolution. Stable AST ownership is insufficient to prove stable results or side effects.

fillMissingTypeArguments intentionally seeds missing positions with errorType before processing defaults left-to-right. Its ArrayTypeMapper keeps the target slice by reference (mapper.go:129–150), so later assignments update mappings already retained by lazily instantiated results. That mutability is deliberate: do not freeze/copy the vector midway, share a partially initialized vector, or compute defaults out of order. Once the fill finishes, the slice stops changing in this routine, but referenced Types may still resolve lazily.

Mapper lifetime is not simply the local call. getObjectTypeInstantiation:22201 maps outer parameters eagerly (a promising repeated-lookup point), then normally creates a new snapshot mapper. But its SingleSignatureType branch combines that mapper with the original mapper. Conditional creation stores mapper/combinedMapper (25172), deferred references store a mapper (25060), and instantiated parameters/signatures can retain combined mappers. Thus some source shapes consume missing indices promptly, while others can query the same deferred mapper after the creating call returns. A blanket activation-local cache may miss later reuse; a persistent native-style cache needs a stronger semantic argument.

## Reentrancy, errors and diagnostic hazards

getResolvedTypeParameterDefault:21904 has explicit resolvingDefaultType/circularConstraintType transitions. Recursive entry can permanently mark circular resolution. getDefaultFromTypeParameter hides noConstraint/circular by returning nil, which then becomes unknown in TS or any in JS. Do not cache such a fallback merely because it is not errorType; the resolution path and its effects are relevant.

Instantiation can produce/use errorType from invalid forward references or depth/count limits and report at c.currentNode. A superficially successful compound result can contain errors or deferred members that report later. Rejecting only `result==errorType` is not enough to prove a whole-vector cache safe. Alias type arguments can cause even primitive-looking types to enter instantiateTypeWithAlias. Depth/count and current diagnostic context can differ between later mapper queries. A cached successful vector can also bypass explicit-node resolutions that the current Go path repeats; those resolutions must be audited separately from defaults.

Native-style `filled=nil` until completion preserves lack of partial publication, but does not itself settle recursion. A `busy` guard must fall back to the original computation, not return an invented sentinel or half-built vector. If considering a broader cache, any reentrancy should invalidate publication for that attempt, and nested publication must not accidentally be overwritten without a deliberate policy. None of this proves inference/error-context independence; it only avoids obvious implementation hazards.

## Narrow defensible proposal

Do not cache arbitrary defaults yet. If evidence warrants a small allocation experiment, limit eligibility to a missing suffix whose parameter default fields are ALREADY resolved to stable closed intrinsic/literal types (or the already-final no-default sentinel). Inspect existing fields without forcing resolution. Exclude unresolved/resolving/circular defaults, error types, aliases, enums, type parameters, objects, references, unions/intersections, conditionals, templates and other instantiable forms. Require every omitted default to meet the rule, not only the requested index, because the old fill visits the entire suffix.

For that narrow set, instantiateType returns before its depth/count checks and creates no dependent mapped type; no omitted default references supplied arguments or another parameter. JS base defaults remain any, and already-resolved unknown defaults still convert to any using the existing Go behavior. Empty-object defaults remain excluded, so they take the unchanged path. A lazy shared completed suffix may be cached per deferred mapper, preserving explicit-index mapping exactly.

Crucially, an omitted cache hit must STILL resolve every explicitly supplied node in the original order, even though the cached suffix does not depend on those values. The current Go path performs those calls on every omitted-index query; skipping them would broaden the proof to node-resolution side effects. A first miss uses the original getEffectiveTypeArguments; only then publish the completed safe suffix. Unknown eligibility falls back permanently or is reevaluated read-only; no global/per-node cache and no shared cache across mapper instances.

This rule is narrow enough to preserve effects, but instantiateTypeWorker was never entered for these alias-free closed defaults anyway. It could save repeated vector allocation and mapper setup; it is NOT a demonstrated explanation of the historical Sentry worker-instantiation excess. Current pointer Sentry alloc-space summary attributes about1MiB flat/5.02MiB cumulative to fillMissingTypeArguments (~0.022%/~0.11%). Absence from top300 CPU rows does not prove zero cost, but provides no large direct profile justification. A broader cache may be more valuable, yet currently lacks the required lifetime/diagnostic proof.

## Fixtures and observational plan

Useful parsed TS shape to drive this callsite:

```ts
type Holder<T extends { left: U; right: V; again: U }, U = { value: string }, V = U> = T;
type ExtractHolder<X> = X extends Holder<infer T> ? T : never;
```

This is a proposed fixture, not executed evidence. Pair it with omitted independent primitive defaults, explicitly supplied overrides, interdependent object/default parameters, repeated property reads in opposite orders, callable/single-signature constraints, generic conditional/deferred constraints, and aliases carrying unused type arguments. Verify exact resulting property types with both valid and invalid assignments, not only agreement with native.

For TS/JS behavior, use parsed JSDoc generics and conditional infer expressions with omitted defaults where Go chooses any for no default/unknown/empty-object; compare unoptimized Go, not native's false flag. Include malformed forward defaults and circular defaults, two distinct use sites that should retain both errors, and repeated/later mapper access after initial constraint resolution. Existing pinned baselines `inferTypeParameterConstraints`, `inferTypeConstraintInstantiationCircularity` and `typeArgumentDefaultUsesConstraintOnCircularDefault` identify relevant conformance cases; preserve their declared diagnostics/types. Ensure a fixture actually reaches this mapper before counting it as coverage.

A separate untimed diagnostic variant can assign a local ID to each mapper created ONLY at17059, recording provided/omitted counts and a closed creation phase. Aggregate missing-index callback calls, whole-vector fills, distinct indices, synchronous reentry, and calls before/after the original constraint-instantiation returns. Capture input/default flag categories by direct fields only; do not force defaults, constraints or IDs merely to classify. A stack of these fill scopes can attribute instantiateTypeWorker increments exclusively to the innermost active fill, avoiding double-counted inclusive deltas. Preserve cold/warm/error/circular categories and JS status. No per-query payload logging or shared cache should affect the semantic path.

Pinned single-checker Sentry is the first useful attribution target, with VSCode as contrast; this is a future authorization, not a run performed here. If most repeated fills are closed primitives, only allocation/setup savings are supported. If complex omitted defaults dominate worker calls, design and prove their stable subset from actual shapes before introducing persistent caching. Keep this experiment separate from the template-entry guard, relation-cache representation and rejected broad conditional-inference shortcut.
