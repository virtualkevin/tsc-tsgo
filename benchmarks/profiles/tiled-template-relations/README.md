# Tiled template relation candidate (isolated)

Compiler integration of the standalone tiled-negative-relations prototype,
supported by template-relation-density measurements:3,579,148 Sentry plain
failure pairs occupied25,709 fixed16×16 tiles with no observation drops.

The candidate specializes only the measured template-key domain. Other keys
retain full128-bit hashing without a generic numeric-key interner. A tagged key
flows through every relation cache operation and the maybe stack/set. Plain
failures use bits, all other values preserve their full representation, and
logical cache size and relater control flow remain unchanged.

See CONTRACT.md for key-equivalence assumptions, operational invariants, risks
and required evidence. The new backend does not revive the rejected generic
numeric-map or prehashed-table variants unchanged. No compiler speedup or
whole-compiler proof is claimed. All four focused candidate tests and both retained semantic controls passed
normally, under race, and under checkptr. Full compiler/services/conformance and
CLI/API/emit validation passed, including80 CLI cases in each normal/race/checkptr
mode and12 API/emit cases. Independent raw-evidence verification passed. The normal
production build matched the tested binary exactly (fbe59ec1), with six changed
files and retained production restored. Workload timing is next. No production source
or default executable has been replaced, and no timing has started.
