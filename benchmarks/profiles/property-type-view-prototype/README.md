# Pending property type-cache prototype

Isolated representation experiment; no production consumer or performance claim.
The earlier presence-only consumer failed its performance gate and is not revived.

A supported pending property clone owns a small cache entry before allocating its
symbol. Read queries use the same original-symbol query and `instantiateType`
sequence as `getTypeOfInstantiatedSymbol`; repeat queries use that one clone's
resolved-type cache. This is not broader generic memoization. Name-type metadata
is captured before the source query, at the point the original clone would have
captured it. Ordinary property write queries remove missingness after the read
query, matching the original property dispatch.

Materialization transfers the cache and captured name type to actual symbol links
and publishes the symbol into the entry. Actual symbol links become authoritative.
An in-flight query retains the entry through reentrant enumeration/GC and writes
its final result to the materialized symbol, matching the original outer assignment.
Retiring the pending table releases its cache map; an active query still roots its
entry and eventual symbol. No integer pointer reconstruction or new concurrent
mutation contract is introduced.

Eligibility and metadata semantics inherit the original property-view prototype:
no bases, pending resolution, duplicate source names, or already instantiated
sources. Kept originals and retired/materialized views use existing symbol queries.
The existing pending-member materialization path remains responsible for identity.

Focused tests include type-cache transfer, captured name metadata, repeated reads,
reentrant enumeration and GC, plus the four earlier view metadata/identity tests.
These are component checks, not a whole-compiler proof. Additional independent
stateful histories (write/read order, nested query effects, exceptions, nominal and
alias observations), actual compiler consumers, pinned-oracle validation and full
performance gates remain required before promotion. Constructor/map allocation,
retained roots and cache transfer costs must count in workload measurement.
