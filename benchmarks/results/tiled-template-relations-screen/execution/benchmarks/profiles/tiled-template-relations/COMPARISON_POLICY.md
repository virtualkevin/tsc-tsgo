# Frozen before timing

Compare retained node-pointer Go baseline8fe4bd80/source216d40c7 with the validated
tiled-template-relations candidate. Same pinned physical inputs/libraries, fresh
processes, default runtime/checker settings, alternating order and matched GNU-time
RSS wrappers. No builds, tests, profiles or Git work during timing.

Screen with9 pairs each for TypeORM/tRPC and5 each for VS Code/Sentry, one warmup.
Both aggregate geometric means (ratio of medians and median paired ratios) must
reach1.01. Both summaries of every workload must reach0.98. Candidate median RSS
must be at most1.05×baseline. A passing screen requires two independent confirmations,
each19 small-workload pairs and11 large-workload pairs; reverse executable roles
in the second and normalize pairs. Each must independently pass all gates. No
pooling, opportunistic additional samples, or threshold/representation changes
to rescue failure. All four workloads are mandatory.

Before timing require complete focused and retained semantic controls, root and
services tests, full pinned conformance, normal/race/checkptr CLI parity and API/
emit checks, independent raw-evidence readback, and normal production-build
provenance matching the tested binary. Restore retained production source/default
artifacts. After an accepted change remeasure directly against original native;
never multiply historical Go-to-Go ratios.

Mechanism: canonical tagged keys specialize only eligible string/template-to-
template comparisons. Plain failures use fixed16×16 ID tiles; other result bits
and full-hash keys preserve exact values and logical size. All semantic queries,
cache writes, budget decrements and diagnostic paths remain. The maybe-stack key
grows from16 to24bytes, and sparse tiles, exceptions, dispatch and directory
lookups may cost more. These costs count against the candidate. No generic hash
interner or semantic-result memoization is introduced. keybuilder.go and the
entire declaration transform stay unchanged; specialized key construction and
fallback equivalence are explicitly audited in CONTRACT.md/source-audit.json.
