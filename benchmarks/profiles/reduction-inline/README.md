# Inline temporary intersection-reduction symbol groups

Candidate prompted by the normal-flag retained-build profiles in `../node-pointer-normal/`. Sentry's sampled allocation profile attributes about 1.22 million objects to the per-name append/map-assignment line in `hasNeverReducedProperty`. Attribution combines operations and is not an exact allocation census or a removable runtime budget.

`candidate.patch` changes temporary storage only: keep the first symbol directly in the map value, allocate a slice only for additional distinct non-skipped symbols, and inspect the skipped constituent separately. Name order, symbol deduplication and first/rest/skipped short-circuit type resolution order are retained. Map values grow from a slice header to a pointer plus slice header; a workload benefit is not assumed.

`build.json` and `screen.json` identify the preserved candidate binary, exact source delta and unchanged build settings. `COMPARISON_POLICY.md` freezes the screening/confirmation rules before timing. The comparator is the retained node-pointer Go build, not original native tsc-ts. This candidate is not promoted by focused tests or screening alone.

Focused normal validation passes 176 test records across eight top-level tests. The new regressions cover repeated-symbol singleton non-resolution and all 24 four-constituent permutations for each combination of optional/conflicting tags, compared with eager property reduction. Full validation is tracked separately by the three `validate-*.py` controllers; their elapsed durations are not performance evidence.

Validation is complete: normal/race/checkptr focused suites each pass 176 records; root units pass 2,437 records across ten packages; pinned conformance passes 12,789 fully checked plus eight partially checked cases, with 2,118 unsupported skips and zero failures; native parity passes 80/80 and actual-Go API/emit/project suites 12/12. Raw evidence is in `validation.tar.gz`, indexed by `validation-archive.json`, with reports under `benchmarks/validation/reduction-inline-*.json`.

`restoration.json` proves production source/default executable were restored to the retained node-pointer build after validation. The candidate remains separately preserved. Screening preflight checks this restored workspace identity and both build sidecars; no promotion or speedup is established yet.
