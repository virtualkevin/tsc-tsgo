# Property-relation view with lookup-time metadata capture

Corrects the separately preserved property-relation-view-candidate. Its isolated
snapshot audit demonstrated that capturing nameType only at the first type query
can differ from the original clone created during presence lookup. This version
creates the pending metadata/cache entry at the first eligible logical lookup,
before subsequent semantic work, without querying the property type. Kept and
already materialized properties retain their original behavior. The first source
query and its result cache are still deferred. The regression joins the focused
suite. All allocation costs of earlier entry creation count in performance tests.

Production source/default remain unchanged. This corrected version requires fresh
validation; passing results from the earlier source do not validate this change.
No timing, promotion, or whole-compiler equivalence claim is made yet.

## Validation and build evidence

All12 focused tests passed normal/race/checkptr; root21,187, services219 and pinned
conformance14,915 configurations passed (12,789 full,8 partial,2,118 unsupported,
zero failures). NormalCLI80/API12 passed before SIGTERM interrupted the race build.
The failed report and raw interruption evidence remain preserved. Only unfinished
race/checkptr phases resumed; each passed80 CLI tests and the signal supervisor
exited0. verify.py checks both reports, raw archived logs, source hashes and exact
conformance coverage. No interrupted phase is represented as a completed test.

Normal production build79712 passed and matched validated overlay binary
0cee0116847b25ac1cc87ffc1613a77971659b8aa92fc7d3da8995d542439022.
Source52bd0f35d4c19b172be0bf1d9654cfeaff9d01fcad023827792bd4f137a2175b
has exactly five changed files and identical build settings to retained source.
Default source/binary/provenance were restored. Validation/build captureHEAD was
32c711f. Performance screening remains pending; these results do not imply speedup.
