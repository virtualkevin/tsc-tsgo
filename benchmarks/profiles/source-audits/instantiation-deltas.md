# Remaining native/Go instantiation differences: source-only audit

No main edits, Go commands, tests, builds, profiles or workloads. Local primary source and Git history were inspected. An isolated finite string/template guard draft was prepared only after parent authorization; it remains unrun.

## Evidence boundary

The historical single-checker evidence is benchmarks/profiles/lazy-large-single-checker-work/comparison.json, candidate source39b165a0/binary961e90a7 and original native525c0fe9. Sentry: native5,008,451 versus Go5,974,204 worker instantiations (+965,753;19.282%), but types1,792,408 versus1,798,696 (+0.351%). VSCode:4,208,367 versus4,217,548 (+0.218%) instantiations and slightly fewer Go types. These are earlier preserved lazy-candidate counts, not a fresh measurement of today's prehashed/saturated source. They count instantiateTypeWorker after active-cache miss, not total semantic work, cost, memory, or default-worker duplication. Nearly equal created-type counts suggest much extra work may return existing types, but that is an inference, not a measured attribution.

## Concrete differences

### 1. Missing relation entry rejection for impossible template texts

Native commit44b5440 (relations.ts452-472) rejects string literal sources whose text cannot match a template target's fixed ends. It also has a template-source clause with an explicit type-variable exclusion to retain unreliable-variance reporting. Go isTypeRelatedTo has no equivalent early guard. Go relater.go2446 already performs the finite-text rejection deeper in inferFromLiteralPartsToTemplateLiteral, and line3605 handles template comparability/variance deeper inside the relater. Existing template caches and literal union reduction do not supply the missing entry guard.

Smallest next behavior experiment: the finite string-source clause only. This has a local proof against the exact existing Go matcher predicate, does not inspect constraints or force placeholders, and leaves every template source on its old path. Avoid copying the broader template-source clause until its couldContainTypeVariables/variance ordering has a separate proof.

Authorized isolated draft: /tmp/tsc-template-entry-guard-draft/string-template-entry-guard.patch, initial SHAe782f3324d130e134daae3783b800478ec239406199364efe69459fec3a4b185. Detailed proof/tests/limits are in that directory's AUDIT.md. The patch is independent of the prehashed relation-store experiment. Three top-level tests plus120 subtests are drafted, including full-relater differential, explicit booleans, real marker variance callback and exact API diagnostic positions. They are not executed.

The entry guard mainly avoids relater/key/cache setup and a known failure traversal. It cannot automatically explain the worker-instantiation delta: the existing deep finite-text check already fails before placeholder work. Measure rejection frequency and exclusive avoided work before any claim.

### 2. Native lazy default-argument fill is shared per mapper; Go repeats it per missing-index query

Native checker-inference.ts TypeArgumentMapper (2423 onward, introduced in8d09d6c) keeps a `filled` array. Mapping an explicitly provided argument still resolves that exact type node on demand. The first missing-argument mapping resolves the argument list and calls fillMissingTypeArguments once; later missing indices return entries from that same array.

Go checker.go17030 getInferredTypeParameterConstraint uses newDeferredTypeMapper with one closure per formal parameter. Each closure calls getEffectiveTypeArgumentAtIndex. When the index is omitted, that calls getEffectiveTypeArguments (21830), which reconstructs/fills the whole argument vector every time. fillMissingTypeArguments (21851) creates a mapper and invokes instantiateType for each default. Thus a constraint repeatedly reading different omitted parameters can repeatedly instantiate the same defaults, even within one deferred mapper. The generic constraint/alias caches do not eliminate the first default-instantiation call themselves; an active mapper with a newly allocated identity may prevent temporary-cache reuse.

This is a concrete potential source of redundant worker calls, but no traffic count establishes significance. It is not a safe blind transplant:

- Go passes ast.IsInJSFile(node); native TypeArgumentMapper currently passes false. Keep Go's JS/default-any behavior.
- Preserve laziness for explicit and unused arguments. Do not eagerly fill at mapper construction.
- A mapper can be retained by a lazily instantiated object/type parameter; its lifetime is not necessarily this one call. Cached default results may have been produced under inference/circular-resolution state that later changes.
- Filling can reenter constraint/default resolution before publication. A shared in-progress cache must not expose a partially initialized vector or invent a circular sentinel with different behavior.
- Repeated filling may produce diagnostics at current use sites (including instantiation limits). Caching successful-looking types does not by itself prove diagnostic neutrality; errors and dependency state need examination.

Next step is separate observational counters, not a production patch: count omitted-index calls per mapper, actual whole-vector fills, default positions visited, recursive worker-call deltas within each fill, and later calls after mapper escape/inference-cache invalidation. This identifies whether repetition is material and whether a narrower nonescaping stable-default scope exists. Do not combine with the template guard.

### 3. Native broad conditional-inference skip remains intentionally absent, for correctness

Native checker-type-operators.ts2045/2140 isFalseForEveryInference uses failed permissive assignability to skip inference for a broad class of object extends targets. Go checker.go24205 has only hasInferenceIndependentTagMismatch: a required directly written literal tag mismatch with carefully checked declarations/optionalness. The broad native heuristic had already failed pinned inferTInParentheses and callable/variadic wrapper cases in this project; wildcard substitution can alter tuple shape. Current Go regression fixtures document these cases.

This is a credible unmeasured source of extra Go inference/instantiation, especially in utility-type-heavy workloads. It is not an optimization available for copying: native speed obtained by an unsound rejection cannot satisfy correctness. The existing Go tag-only proof already captures a safe subset. Any extension needs a new semantic proof (for example a strictly inference-independent structural contradiction) and independent expected-type regressions, not just native agreement.

A useful diagnostic-only comparison can count how often a *read-only syntactic* eligibility classification falls outside the Go tag case; do not run the native permissive predicate as a shadow test on the Go checker because that itself resolves/instantiates types and changes work/state. If deeper eligibility comparison is needed, use separate instrumented processes and preserve the original semantic path.

## Large optimizations checked and already present / not explanations

- Template instantiation memoization b95d9ab/466d847 is present in Go checker.go28941, keyed by template identity plus instantiated argument IDs; error products are not cached so diagnostics repeat. Conditional root instantiations include alias and forConstraint state in both implementations. Object instantiations reduce outer parameters, share by mapped arguments and propagate containment flags in both.
- Lazy instantiated members63ae946, name layouts d7b26e9, lazy intersection never reduction0d43400 and unmatched-property inference pruning e419e41 are present in Go pending_members.go/lazy_properties.go. The discriminant-aware unrelatedness change8c591de is also present in inference.go1168. These should not be proposed again as absent algorithms.
- Variance inference laziness6ca738b and the conservative conditional fast path are already ported; no missing broad cache lifetime was established here.
- Type-variable constraint relations try the uninstantiated constraint before a costly this-instantiation in both (Go relater.go3695, native relations.ts2178). Permissive/restrictive instantiation caches and restrictive-result self entries exist in both (Go24419/24433; native instantiation.ts838).
- Active mapper caches have the same semantic lifetime in both: keyed by mapper identity; only active nested instantiations retained; caches cleared after fixing an inference. Native437c852 splits alias-free TypeId and alias-bearing caches and allocates lazily; the analogous Go experiment was already measured and reverted. It changes representation/lookup cost, not an established opportunity to eliminate965k worker calls. Do not keep caches across inference changes.
- Native8275803 moves already-resolved member/apparent-type tests into inline entry functions; Go still uses some larger entry functions and getReducedApparentType always calls the second reduction. This is call overhead/redundant flag testing, not proof of repeated instantiation: reduction state is already memoized. It may be a later code-generation experiment, not a large algorithmic explanation.
- Composite mapper semantics agree: map with m1, instantiate changed result through m2, otherwise map with m2. `instantiateTypes` maps each element once and preserves the original list when unchanged in both. No missing same-result shortcut was found there.

## Smallest attribution experiment before more speculative caches

Use separate untimed instrumented native/Go builds on the same pinned single-checker Sentry and VSCode inputs. Attribute actual instantiateTypeWorker entries by input flag kind and current call-site category: conditional inference/extends, omitted default fill, mapper composition, member/return type resolution, and ordinary instantiated type arguments. Track cache hit/miss and returned-input/returned-existing/new-type outcomes; retain only bounded aggregate counts. Distinguish root mapper calls from nested calls and use exclusive counters to avoid adding recursive inclusive totals. Do not allocate new AST/Symbol IDs, force constraints/member resolution, or call prospective optimizers merely to classify.

These counters would separate a correct-but-more-conservative conditional path from repeated default fills and representation overhead. Publish actual source/binary hashes and instrumentation scope; the historical19.282% count ratio is neither a current timing ratio nor a removable-cost estimate. No source-only finding here establishes a path to10×.
