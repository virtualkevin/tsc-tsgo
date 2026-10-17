# JSX constructor-cache repair audit: defer the general cache

Read-only investigation after the recursive managed-attributes reproduction. No compiler build, test, profile, source edit, or workaround was performed. The regression contract remains TS2589 at both (7,15) and (8,16), matching preserved lazy Go and pinned upstream Go. Original native emits only the first.

## Conclusion

There is no existing checker-wide completed-instantiation status or persistent failure epoch that makes a small general-purpose eviction repair sound. Checking only the managed result for errorType would repair the direct Loop<C> reproduction but would not establish safety for lazy members, cached failures, or queries that do not emit diagnostics. Defer the canonicalization candidate rather than ship that partial fix.

## Existing mechanisms inspected

All references are under `packages/tsc-go/internal/checker` in the current worktree.

| Mechanism | Source | Why it is insufficient for cache admission |
| --- | --- | --- |
| `errorType` and `isErrorType` | checker.go:26589; instantiateTypeWithAlias:22041; getConditionalType:24281 | Explicit top-level failure is detectable, including alias error types. A non-error object may contain uninstantiated members that fail later. A returned non-error type is not a completed semantic result. |
| `instantiationDepth` | checker.go:22048–22079 | Depth is decremented when the worker returns; before/after equality does not show a nested failure. Limit checks run before cache lookup, so caller depth/budget can also change the outcome of previously successful work. |
| `instantiationCount` / `TotalInstantiationCount` | checker.go:22048–22072; reset at2237,2500,7543 | Counts measure work, not failures; per-expression counts reset. They cannot distinguish completed work, cached failure, or conditional tail recursion failure. |
| Conditional `tailCount` | checker.go:24281–24298 | Local counter emits TS2589 at1000 and returns errorType; no persistent failure state survives. |
| Type-resolution cycle results | checker.go:18666–18688 | Marks currently active stack frames false, then pop clears them. Not a completed-result taint marker, and separate from instantiation limit failures. |
| Relation overflow flags | relater.go:72–75,424–427,3090–3115 | Persisted with relation entries and can regenerate comparison-overflow diagnostics for a later reporting query. This is a useful example of explicit failure status, but only for relation comparison; it does not cover instantiation or alias caches. |
| `reliabilityFlags` | checker.go:739,1141–1148 | Variance/unmeasurability bookkeeping, not a universal error or completion status. |
| `wasCanceled` | checker.go:616,2218,13890 | Cancellation signal only, not recursion/semantic failure. |
| Diagnostic collection / deferred callbacks | checker.go:13901–13932; checkSourceFile:2186–2206 | Adds can be suppressed by serialization depth; callbacks may be ignored when not saving diagnostics, or executed after the instantiation scope. Existing diagnostics unrelated to this pair provide no causal information. Even a new-error counter would miss a cached failed result and future lazy failures. |

## Why wrapper-level eviction is not enough

`getTypeAliasInstantiation` (checker.go:23581) caches the return from instantiateTypeWithAlias unconditionally. `getConditionalTypeInstantiation` (22423) likewise records its result without distinguishing error/completed/deferred states. There are multiple nested caches, not only the new constructor map.

More importantly, `instantiateAnonymousType` (22396) creates an object with target+mapper and returns it without resolving members. `getTypeOfInstantiatedSymbol` (16444) later resolves and caches a property's type. The JSX managed wrapper (jsx.go:1022) returns that lazy result before contextual attribute checking and assignability consume its properties (jsx.go:549 and following). Thus a candidate may publish a constructor as successful, with the failure appearing outside its observed instantiation scope.

A diagnostic-count delta around getJsxManagedAttributesFromLocatedAttributes cannot cover that lifetime. Moving the scope to the full JSX check still does not prove completion: API queries can request only some members, later contexts may explore others, and outstanding deferred work is not tied to a particular synthetic constructor by the existing data structures. The diagnostic callback list demonstrates that checker work need not report synchronously, although this audit does not claim every callback category is reachable from this particular helper.

Evicting the constructor after a directly observed failure would avoid reuse of that particular identity on a later fresh request, but it cannot undo reuse that already happened while the entry was published. Cached derived types may already hold the identity and failure; error-cache hits do not necessarily execute an error-producing branch again. Replaying stored diagnostic objects is incorrect because they retain the earlier source location, and because the original failure may have been suppressed, deferred, or never represented as a stored diagnostic.

## What a principled repair would require

A broader design could carry explicit failed/incomplete status through instantiation results and every cache that can return one, update that status at the actual failure sites independently of diagnostics emission, and preserve dependency/ownership information for deferred member evaluation. Constructor admission would need a demonstrated completed dependency closure, or cache-hit semantics capable of reproducing the required per-use failure behavior without stale positions. Recursive requests must not see an entry as completed before that proof exists.

A new monotonic failure epoch at the two TS2589 producers can detect freshly executed instantiation-limit failures even under diagnostic suppression. It would be useful instrumentation, but **not a sufficient production fix**: existing failed cache hits, delayed property evaluation, other abort paths, and depth/budget-dependent success need separate handling. No such partial epoch change is proposed here.

An alternative conservative admission rule could allow only fully resolved, demonstrably context-independent result shapes. That needs a separate proof of the entire reachable type graph and diagnostic behavior. Merely checking ObjectFlagsMembersResolved, absence of type variables, or a top-level primitive flag does not show all earlier work completed without failure; forcing the graph eagerly would change traversal/error order and cost. This would also exclude the ordinary object-shaped React props that motivate the optimization, so its useful hit rate is unknown.

Given the old-profile local CPU ceiling (~1.056x if the whole managed-attributes frame vanished), this general cache does not justify introducing cross-cutting failure tracking speculatively. Preserve the regression fixture and measured native diagnostic discrepancy, leave the draft unbuilt, and prioritize independent candidates unless a narrow semantic completion proof emerges.
