# Completed-fact census: source boundary audit

Source-only investigation during the first indexed-storage confirmation. No diagnostic compiler or new cache was built, no CPU budget was measured, and no sharing opportunity is established by this audit.

The next architectural question from OPTI_ANALYSIS_01.md is whether expensive completed work repeats across checker owners. Existing creation totals cannot answer that question. Record ownership and construction origin without calling semantic-ID allocators or new semantic queries.

## Boundaries and exclusions

- `getSignatureFromDeclaration` first checks `signatureLinks.resolvedSignature`. Misses construct parameter lists and signature flags, but also call contextual typing for untyped JavaScript functions, name resolution for parameter properties, paired-accessor resolution, and class/type-parameter resolution. A common declaration is only a shared origin, not a complete context key. `newSignature` is passed nil return type and type predicate: finishing this constructor does not make the signature an immutable, fully resolved fact. `Signature` retains mutable return/predicate, mapper, target and composite fields. Do not share the returned signature.
- `getDeclaredTypeOfClassOrInterface` publishes `links.declaredType` before resolving parameters and this-types. A non-nil link may therefore represent in-progress recursive construction. Its result owns checker-local type IDs, a this-type constraint cycle, and an instantiation map. Distinguish entry, publication, recursive observation and normal completion; none establishes immutable sharing eligibility.
- `getTypeOfFuncClassEnumModuleWorker` can resolve CommonJS exports, constructors, intersections and optional types. Symbol identity alone omits the checker-owned results and recursive work. Most non-class paths merely allocate a shallow anonymous type, so large call counts would not demonstrate large saved cost.
- `instantiateTypeWithAlias` performs depth/count checks before cache lookup, then uses active mapper scope and alias identity. Cache misses increment instantiation counters; popping a mapper clears its cache. Match mapper/inference generation and request mode before discussing reuse. Record budget/diagnostic involvement separately; a successful result cannot by itself justify bypassing future count/depth checks.

## Measurement design constraints

Each checker is accessed exclusively by its pool lock, so a diagnostic-only checker-local span stack can attribute nested measured work without inter-checker contention. This does not make a global event collector or shared production cache safe. Give instrumentation its own identities and leave unresolved/cyclic descriptors unclassified. Shared AST pointers can identify common origins within one process; filename/position/kind alone is insufficient identity for synthetic or cloned nodes across processes.

Do not use the existing `Tracing.Push` sampled events as a complete construction census. The implementation omits events that do not cross a 10ms boundary, skips sampled events entirely in deterministic mode, and clones entry arguments. Reusing it without accounting for those semantics would omit cheap events, bias duration totals, and miss completion metadata. Always-emitted events serialize through a global tracing mutex and allocate/format records; they can materially perturb the experiment.

A dedicated diagnostic census should report count coverage and instrumented exclusive elapsed time separately from sampled CPU. Exclusive wall duration includes scheduling and GC delays and cannot satisfy the analysis document's 10% non-overlapping CPU research gate. CPU labels/profile attribution, or another defensible CPU measurement, is still required before advancing a shared-fact prototype. A profile gathered with instrumentation also needs an uninstrumented control; instrumentation time is never a PERF.md speedup result.

Start with explicit cache misses at these boundaries, retaining completion/recursion/budget/diagnostic state and checker ownership. Preserve all unmatched origin groups rather than counting them as equivalent. Compare one/four-checker diagnostic runs only after the storage retention and direct-native milestone; preserve diagnostic equality and existing API/flow/inference/TS2589 regression coverage. The first useful output is a cost-ranked inventory with eligible, excluded and unclassified work, not a new production cache.

## Inspected source identities

- `packages/tsc-go/internal/checker/checker.go`: SHA256 `98199dd984bccc60528b6c24d83dd560f1c6c8416ebc60a1ad237f03c305a576`
- `packages/tsc-go/internal/checker/types.go`: SHA256 `9a39b928846926090a175d94773d5e3ab4b093b887061b0ef32cfa40548871f4`
- `packages/tsc-go/internal/checker/tracer.go`: SHA256 `7540e8090e865bc667836a9604e8e5e44a3933fb3f6b621f07ad6cda977d71b6`
- `packages/tsc-go/internal/tracing/tracing.go`: SHA256 `a2c7a2a3732e5f4239178943115da39c61283a305560a491f27d273f708b9ee2`
- `packages/tsc-go/internal/compiler/checkerpool.go`: SHA256 `d34f073cd1f9c7a888c2d3460ec219cc535c8f17ef2b22ff9e54be34367f4305`
