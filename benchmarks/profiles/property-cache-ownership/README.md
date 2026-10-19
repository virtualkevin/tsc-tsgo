# Property-cache storage ownership boundary

Two stateful tests run as an overlay on unchanged retained compiler source. They
exercise cache publication, mutation of underlying members, later lookups through
another checker receiver, and distinct containing-type identities. They are focused
internal behavioral tests, not a claim that arbitrary cross-checker concurrent API
use is supported or that a pooling implementation is correct.

The proposed storage experiment would replace many per-type property-cache maps
with pooled maps keyed by exact containing-type identity and property name. This
is distinct from the previously rejected semantic sharing of augmented and
non-augmented entries: both namespaces and the original synthesis/update order
must remain intact. No pooled implementation has been applied yet.

Source constraints:

- `newType` assigns the creating checker and a checker-local TypeId. TypeId alone
  is not a globally unique key. Exact type identity and ownership must be retained.
- `getUnionOrIntersectionProperty` consults the cache stored on the input type
  before invoking receiver-local synthesis. A receiver-local pool would change
  this boundary when another receiver queries an already populated type.
- Missing properties remain uncached. Successful non-augmented complete results
  populate the augmented namespace only if it has no winner. Recursive synthesis
  may publish that winner before the outer operation completes.
- Pooling into the type owner's checker avoids conflating the receiver with the
  owner but changes synchronization granularity: previously independent type maps
  become one mutable map. Ownership/concurrency must be established before this
  approach is safe; these sequential tests do not establish it.
- Larger composite keys, additional hashing, shared retention, and locking can
  erase savings from fewer map allocations. Header-size arithmetic is not evidence
  of a compiler speedup. Public and internal escaped graph lifetimes need review.

Both focused tests passed in normal/race/checkptr modes; independent raw-log
readback confirms both tests passed without failures or skips in each mode. No performance result,
production modification, or 10× mechanism is claimed.
