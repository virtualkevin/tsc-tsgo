# Property presence consumer experiment

This isolated overlay integrates the pending-property view into non-discriminant
`isUnmatchedProperty` checks. Production source and the default executable remain
unchanged. This is an implementation experiment, not a demonstrated speedup.

The consumer performs the original reduced-apparent-type and structured-member
resolution before consulting the view. A supported, present, value-bearing own
property of a non-module object can answer true without creating a symbol.
Missing and unsupported views use the original property lookup, including module
filtering, union/intersection handling and Object/Function augmentation. The
fallback reuses the semantic prelude rather than repeating it. Discriminant checks
still obtain materialized symbols and query types in their original order.

The view retains the original frozen keep/clone decision. Later symbol queries
use the owning member cache. Enumeration and garbage collection must preserve
that materialized identity. Symbol allocation and its timing intentionally differ
for presence-only requests; whether this affects observable downstream behavior
requires full compiler and pinned-oracle validation.

Focused tests exercise metadata, identity, unsupported views, independent lookup
histories, allocation-free positive presence, deferred materialization, and missing
own-property augmentation. They do not constitute a whole-compiler proof. Full conformance and CLI/API oracle validation have now passed; controlled
workload timing remains required before promotion. No PERF.md rows are warranted before workload timing.

## Completed validation

Six focused tests passed normal/race/checkptr; 21,181 root tests and 219 service
tests passed. Pinned conformance matched 12,789 fully checked, 8 partially checked
and 2,118 unsupported configurations, with zero failures. CLI parity passed 80
tests each normal/race/checkptr; API/emit integration passed 12. `verify.py` reads
the captured raw evidence and checks source/log hashes.

The normal production build matched the overlay binary
`dded877d210b88f1724e8890ccf7521453c17f8822b163e99aeb690564bb99ce`.
Its provenance identifies source
`e773bc7b61a1c575a1c598a4801502cc91ddc8e73e2b994152aa829f304636e1`,
with exactly the four overlay source changes. Retained source/default artifacts
were restored. Validation/build capture HEAD was `4d23435`; subsequent commits
archive that evidence and must not be substituted for its capture HEAD.
