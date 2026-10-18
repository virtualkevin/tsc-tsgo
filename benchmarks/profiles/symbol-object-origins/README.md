# Origins of completed-work symbol and object allocations

Offline reanalysis of the verified after-GC heap captures in completed-heap-census, with no new compiler execution or source change. Each sample is assigned once to its innermost selected constructor (newSymbol or newObjectType), then its nearest outer checker caller after explicitly listed constructor/instantiation wrappers. The report preserves all sampled totals, selected totals, and every caller group. This is allocation attribution, not the number of semantic requests, proof of redundant construction, exclusive ownership or a removable runtime budget. In particular, symbol arenas allocate slabs; sampled allocated-object counts must not be interpreted as symbol counts. Two tests cover nested-constructor deduplication and conservation, and the complete report reproduces exactly.

The VS Code retained samples include approximately 134 MiB from anonymous-type instantiation, 127.5 MiB from type-reference construction, and 112.4 MiB from symbol creation beneath object-literal checking. Sentry includes 97 MiB of symbol storage beneath object-property materialization and 88.5 MiB of anonymous-type instantiation. These are disjoint selected allocation groups, but they exclude backing maps, member arrays and links allocated elsewhere. They cannot be added to inclusive totals from unrelated reports.

Source constraints before proposing reuse:

- createTypeReferenceEx already computes a type-list key and consults the target interface's instantiations map. Allocation on that path follows a cache miss; the profile does not identify missed equivalent keys or redundant work.
- instantiateAnonymousType sets target and mapper on the new result, can instantiate aliases, and for mapped types deliberately clones a fresh type parameter and composes its mapper. Sharing by original type alone would be incorrect.
- instantiateSymbol already returns the original when its existing resolved read/write types prove it unaffected, including special handling for setters and this-only mappings. Otherwise it constructs a new transient symbol and checker-owned links. A repeated target or mapper pointer alone would not establish safe sharing: mutable resolution, flags, result identity, and consumer writes remain relevant.
- checkObjectLiteral depends on check mode, contextual type, const context, computed properties and spreads. Its cloned property symbols cannot be replaced wholesale with binder symbols merely because declaration pointers match.

A focused follow-up should measure request descriptors and mutation boundaries for the selected instantiation families, preserving unknown/ineligible cases, before introducing any cache or shared result. The allocation profiles do not answer that repeated-request question. Previously rejected owned-symbol-link, pending-member, direct-member and semantic-slab experiments remain rejected.

Run `python3 -B benchmarks/profiles/symbol-object-origins/analyze.py` to reproduce the report. No PERF row or performance claim.
