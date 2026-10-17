# Current PointerLinkStore CPU audit and next experiment

Source-only analysis of all four completed current CPU summaries. No compiler build, test, new profile, network access or main-source edit. Capture: /tmp/tsc-pointer-current-profiles/capture.json; text derivation: summary-evidence.json. Preserved binary SHA256b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322, source6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d. Default GC, RR, explicit4checkers. Per-workload sampled metrics are recorded in summary.json. Every percentage is aggregate sampled CPU, not elapsed time; nested cumulative categories overlap. Top300 tables omit smaller entries. tRPC total2.26CPU seconds over489ms gives particularly noisy individual-function fractions.

## Recommended first experiment: eliminate the inert non-CJS declaration prepass

Current TypeORM spends0.76s/6.74% CPU in DeclarationTransformer.visitCJSExportAssignments. transform.go348 scans every file even when CommonJSModuleIndicator is nil, while callback2645 can perform its only semantic action only when that same indicator is nonnil. Native declarations.ts already guards the entire ModuleExports walk. This is actual work elimination with a narrow syntactic bound, unlike declaring a wrapper's complete recursive cumulative cost removable. A minimal isolated patch and detailed callback/diagnostic/visitor-hook proof are /tmp/tsc-cjs-prepass-guard/{cjs-prepass-guard.patch,AUDIT.md}. No builds/tests yet. Required declaration diagnostics, TypeScript expandos and the second traversal remain intact.

TypeORM setupDiagnosticContext8.33% and Node.VisitEachChild13.39% overlap this and other passes. They cannot be added to6.74%. tRPC's CJS walk2.21% is onlyfive10ms samples; VSCode/Sentry entries are absent from top300. Do not claim broad benefit or predict6.74% wall-time savings. This is primarily a TypeORM-targeted opportunity, with a direct no-op elimination proof. Current CPU gives a stronger basis than the old general declaration-allocation observations.

## Current larger workloads: where costs remain

| Sampled CPU frame/category | VSCode | Sentry | Interpretation |
| --- | ---: | ---: | --- |
| background GC |19.92%|16.61%| Independent GC worker cost; allocators/assists elsewhere overlap when considered separately |
| instantiateTypeWorker inclusive |5.71%|18.73%| Recursive instantiation remains largest Sentry algorithmic area; not all repeated or cacheable |
| getConditionalTypeInstantiation inclusive |3.57%|8.56%| Nested under instantiation, already caches by mapped outer arguments/alias/constraint mode |
| getConditionalType inclusive |3.11%|7.61%| Error location/depth/inference/reentrancy constrain additional caching |
| resolveStructuredTypeMembers inclusive |5.20%|13.43%| Actual member resolution below wrapper remains necessary; queued wrapper fast path saves only repeated dispatch/checks |
| union construction getUnionTypeEx inclusive |3.61%|7.29%| Potential normalization algorithm work, discussed below |
| PointerLinkStore.slot inclusive |2.81%|3.33%| All lookup/insertion/rehash callers combined; flat2.78%/3.27% |
| PointerLinkStore.Get inclusive |4.07%|3.59%| Includes miss insertion/growth, not just hits |
| PointerLinkStore.grow inclusive |2.26%|belowtop300| Rehash/allocation can offset lookup gains; not additive to Get/slot |
| pending materialize inclusive |1.49%|3.02%| Direct-properties draft already queued; avoid quoting older8.95% allocation as CPU |

There is no novel safe persistent mapper/conditional cache established by this profile. getConditionalTypeInstantiation already maps outer parameters, constructs a complete key and caches results; bypassing mapper evaluation can omit side effects from function/inference mappers, and error results have source-position behavior. The JSX reproduction shows that even changing input identity can suppress TS2589 diagnostics. Cumulative18.73% cannot be translated into a cache opportunity without eligible hit/miss attribution. No new such instrumentation is authorized or performed here.

## Secondary new algorithm idea: union normalization strategy, bounded by current exposure

Current Sentry addTypeToUnion costs3.48s/2.82% inclusive; compareTypesWithOrder3.28s/2.65% inclusive,1.37s/1.11% flat. These overlap and compareTypes is used outside union construction. checker.go25743 recursively flattens constituents, then every retained nonunion uses BinarySearchFunc and slices.Insert. For long unsorted lists, repeated insertion entails quadratic pointer movement and repeated rich comparisons. Existing two-input union-of-union memoization already removes many common repeated combinations.

A separate normalization strategy could collect flattened eligible constituents in original visitation order, preserve includes flags/never/strictNullChecks rules, then sort/deduplicate once for sufficiently long lists; or merge already sorted union constituent lists. Preserve CompareTypes, not TypeId ordering: it compares named/aliased objects, literals, reference arguments, deferred source locations and mapper shapes, ultimately IDs. Aliases/origin retention and literal/subtype reductions remain downstream. Mutable type fields and any comparison side effects need proof before reordering comparisons; nested named unions can contain recursive references. No universal hash set/sort shortcut is proposed.

Allocation agent notes current Sentry slices.Insert121.90MiB/2.65% flat is not all proven union-attributed; getUnionTypeWorker54.90MiB/1.19%. Temporary scratch arrays cannot escape into canonical UnionType, origin or subtypeReductionCache (removeSubtypes retains successful lists). A first experiment would need length/order distributions or call-site attribution; current CPU bounds suggest a smaller targeted optimization, not elimination of7.29%. No patch drafted and no duplicate work with allocation agent.

## Other findings and exclusions

Remaining Go map costs are broad: ctrlGroup.matchH2 flat6.94%VS/7.74%Sentry, mapaccess1_fast64 cum8.72%VS/5.05%Sentry, faststr3.68%VS/5.47%Sentry. These mix many caches. The current SymbolNodeLinks.Get alone is3.21%VS,2.39%TypeORM; SignatureLinks.Get1.48%VS. Extending the pointer store would be another store-specific measured experiment, not a justified wholesale map replacement, especially given current grow cost. Numeric relation keys already queued address a different subset; current Sentry getRelationKey is1.80% inclusive, only0.60%flat.

GC and allocation are broad but typed concrete arenas/direct-properties are already assigned. Program-lifetime or shared semantic storage would impose ownership/reentrancy/lifetime constraints not solved by profile evidence. The scheduler experiment already found mixed results, so no automatic switch follows from fixed-checker duplication counts.

Compared descriptively with expansion profiles, Sentry getReducedType cumulative fraction is now4.73% rather than10.60%; current hasNeverReducedProperty4.44% shows the already-ported selective reduction path. Captures have different source, sampled totals and runtime timing; this difference is not an isolated speedup result. It does invalidate treating old reduction or union-property allocation fractions as current untouched opportunities. Current PointerLinkStore profiles likewise cannot isolate table benefit by comparing percentages with old LinkStore; the controlled benchmark is the effect evidence.

Conclude with the narrow CJS whole-pass guard first. It targets observed and provably inert work, has bounded correctness scope and is independent of queued semantic cache/layout experiments. Broader prepass context/traversal changes remain a separate investigation because ancestor suppression and EmitContext lexical hooks matter. No10x prediction is supported.
