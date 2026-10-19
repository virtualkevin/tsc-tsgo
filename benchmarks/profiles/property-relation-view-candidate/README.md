# Combined property presence and type-relation views

Isolated five-file candidate. The default compiler/source remain unchanged.
This combines the validated pending type-cache representation with two compiler
consumers: non-discriminant unmatched-property presence and source properties in
ordinary property relations. A presence-only version was previously rejected;
this candidate additionally carries views into type queries and their caches.

Lookup performs the original reduced-apparent-type/member-resolution prelude once.
Eligible positive own members can return a view; missing/unsupported members retain
module filtering and Object/Function/union/intersection lookup. Public enumeration
still materializes symbols through the original owner and ordering.

The relation consumer declines before type queries for diagnostics, strict subtype,
protected modifiers, kept symbols, and already materialized/retired views. Accepted
views preserve private declaration identity, target-before-source type evaluation,
any/unknown target shortcuts, source missingness removal and optionality rejection
after type relations. A temporary metadata symbol is read only by the declaration
modifier helper; it must never enter identity comparisons, caches or diagnostics.
The existing materialized relation path handles all declined cases.

The pending read-type cache follows the same source query and instantiateType
operations as an instantiated symbol, including their limits/effects. Reentrant
materialization transfers the cache and the completed outer query updates the
actual symbol. No cross-property, cross-checker or broader generic cache is added.

Focused validation includes nine view/history tests plus two relation differential
and fallback tests. Full pinned compiler/conformance, CLI/API parity, normal build
provenance and frozen four-workload performance gates remain required. No speedup
or whole-compiler proof is claimed from component tests. All map/metadata/callback
costs and retained roots count in eventual workload timing.
