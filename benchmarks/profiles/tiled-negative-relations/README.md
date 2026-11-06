# Compact storage for plain failed relations — standalone prototype

This implements a different storage mechanism from the rejected generic numeric
relation map and prehashed table experiments. It is not integrated into the
compiler, and no previous rejected compiler variant is reinstated.

The motivation is the index-applicability census: Sentry issues millions of
mostly unsuccessful template-key comparisons. The prototype groups canonical
packed source/target IDs into 16×16 tiles, retaining intersection state in the
tile key. A plain Failed result occupies one bit. Successes, zero-valued entries,
reliability flags, overflow flags and arbitrary full-width results remain in a
regular map. Fallback-tagged and noncanonical keys also stay in that map.

Transitions remove the old representation before installing the new value.
Logical Size includes present zero entries and counts overwrites once. Empty
tiles are removed. No semantic computation, type/symbol pointer, global registry,
unsafe conversion or result reuse is introduced by this standalone backend.
Populated store copies and concurrent mutation are unsupported.

## Evidence

- **Tested:** three tests under normal, race and checkptr. Boundary histories
  exercise ID/tile/word boundaries, every intersection state, fallback and
  reserved key bits, maximum packed IDs, zero, reliability/overflow values, full
  uint32 results, replacements, reset and independent stores. Random histories
  compare 384000 operations per mode against a Go-map oracle. A dense-tile test
  checks 256 distinct cells, transitions and empty-tile removal.
- **Machine-checked model:** Z3 4.15.4 proves nine bitvector/one-key transition
  claims, including reconstruction and injectivity of tile/lane decomposition,
  distinct word/mask addresses, retention of intersection state, exclusion of
  tagged keys, exact result readback and size increments only on new keys.
- **Not proved:** the Go implementation against that model, Go runtime behavior,
  compiler key-generation equivalence, lifetime/concurrency beyond the stated
  ownership rule, semantic compiler equivalence, or performance. The proof
  records exact source hashes and is accompanied by independent Go differential
  tests; it is not a whole-compiler proof.

Reproduce with the pinned Go toolchain via validate.py (exclusive output files),
and prove.py using requirements.txt. verify.py independently reads test logs and
reruns the model proof. Existing output is retained rather than overwritten by a
new validation attempt.

## Integration requirements and decision

Do not promote or time this as a compiler optimization yet. First measure real
pair occupancy for the fixed 16×16 layout. Sparse tiles can cost more than map
entries; an extra lookup, allocations, and write barriers can outweigh compact
payloads. The previous bounded census did not export pair coordinates and cannot
establish occupancy. No tile-size tuning or speedup estimate follows from the
synthetic dense-tile test.

The backend accepts the prior numeric-key encoding as input; it does not produce
those keys. Before integration, establish how a domain-specific key travels
through all relation lookups, overflow writes, maybe-stack insertion/removal,
constraint-broadened keys, identity ordering, and successful propagation. Preserve
fallback full-hash equality and generic-detection side effects. Keep logical
relation size, relationCount decrements, diagnostic elaboration and every result
bit unchanged. Direct legacy resets of Relation.results also require an audit.
A pointer-free storage mechanism alone does not establish those obligations.

No production source, executable, or PERF.md is changed. The 10× native-relative
objective remains unmet. Next evidence needed: real template-key tile density,
followed by a compiler integration only if that storage budget is credible.
