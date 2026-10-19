# Pending property view — identity boundary prototype

At7e593fc, production remains unchanged. This adds an isolated view over existing pending own-property state; no production relation/lookup consumer calls it yet. The preceding profile audit motivates the subsystem, not a projected speedup.

A view retains the structured owner, original source and captured keep/clone decision. Metadata can be read without allocating a clone or querying its type. Materialization always resolves through the owner's existing pending/table cache; it never creates a parallel symbol cache. This matters because Properties/ Members can retire and clear the saved pending state. Once a symbol already exists, metadata reads use that symbol. The original transient/check flag transformation is mirrored only for not-yet-materialized, non-instantiated source properties.

Eligibility is limited to own members with no bases or reentrant resolution, unique source names, property flags and no already-instantiated source. Unsupported cases return before effects. Enumeration and inherited lookup remain on the old path. Missing own properties are distinguished from unsupported state. The view is checker-owned, not safe for arbitrary concurrent mutation. Original/source/owner structural mutation beyond existing supported pending transitions is outside this prototype's contract.

Four focused tests cover metadata without clone allocation, stable published identity, frozen keep/clone decisions after later type resolution, retention through GC and pending retirement, fallback before effects, and independent materialization/enumeration histories. This is a local component correspondence, not a full pinned-oracle API replay or proof. Node/private-origin metadata is carried, but comprehensive nominal-origin fixtures, aliases, repeated diagnostic budgets, type-query effects and reentrant histories remain outstanding.

No type-query or relation fast path is implemented yet. A later consumer must preserve effect order and public identity; removing clone allocation alone must not bypass instantiation or diagnostics. Materializing the same view repeatedly is identity-stable. Retaining views also retains source roots, which may increase memory; benchmark that cost when integrated. Validation is running; no performance claim or PERF rows.

## Completed component validation

Session89512 exited0: all four tests passed normal/race/checkptr. verify.py independently checked exact overlay hashes and raw test coverage. No workload or compiler-wide validation follows from these tests. Next candidate boundary is non-discriminant own-property presence, preserving apparent reduction/resolution and falling back for augmentation/modules/unsupported pending states; type comparison remains materialized.
