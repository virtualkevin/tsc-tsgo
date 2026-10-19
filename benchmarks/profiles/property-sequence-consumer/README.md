# Ordered property sequences in relation consumers

Experimental isolated overlay; not promoted and not timed. Extends the ordered
sequence prototype by consuming pending target properties in both non-discriminant
unmatched-property checks and the following propertiesRelatedTo loop.

propertyRef represents an actual symbol or a pending view. Identity compares
actual symbols or the same owner/name; metadata temporaries never escape into
identity/caches. Type comparisons retain target-before-source evaluation, the
any/unknown shortcut, and optionality rejection after type relation. Diagnostics,
strict subtype comparisons, and protected overrides use materialized fallback.
Discriminant matching keeps the original path. Existing sequence exclusions and
snapshot contracts still apply, including immutable source topology.

18 focused tests include independent eager/deferred dual-reference histories,
reentrant enumeration and GC during target type computation, optional rejection,
source-query short circuit, final cache and instantiation-count equality,
identity before/after publication, and fallback before type queries. Inherited
prototype tests also remain. These component tests do not prove whole-compiler
correctness or performance; full pinned conformance and CLI gates are separate.

The source-property helper from the preceding prototype remains for its inherited
component tests; the actual relation loop now uses propertyRefsRelatedTo.

Validation pins HEAD and source hashes. Do not edit overlays or change HEAD while
those controllers run. No PERF row is warranted until a normal build has passed
correctness/provenance gates and matched workload timing has been recorded.

Validation completed at HEAD 8ae8db8: 18 focused tests each normal/race/checkptr,
21,193 root tests, 219 service tests, all 14,915 pinned conformance configurations
(12,789 fully checked, 8 partial, 2,118 unsupported, zero failures), 80 CLI parity
tests each normal/race/checkptr, and 12 API/emit integration tests. Independent
raw-evidence readback passed. Normal production build matched the validated binary
c08f624c, with exact nine-file source delta and unchanged build settings. Baseline
source/default executable and sidecar were restored. These results authorize the
frozen performance screen, not promotion or a performance claim.
