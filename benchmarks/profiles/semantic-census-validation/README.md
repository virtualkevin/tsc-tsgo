# Diagnostic construction census validation

This is an isolated diagnostic tool, not a production optimization. `semantic-census.patch` and `source/` contain the exact final four-file delta against commit8e2561e. Production source and default executable have been restored; the separately preserved executable is `packages/tsc-go/dist/tsc-go-semantic-census`.

`validation.tar.gz` contains raw test output, fixture sources, executed controllers, both the initial failed CLI setup and corrected complete run, provenance and discovery manifests. Extract with `tar -xzf validation.tar.gz` into a fresh directory. Absolute paths in evidence describe the original execution environment. `benchmarks/validation/semantic-census.json` summarizes the checks and hashes archived artifacts; `semantic-census-restoration.json` proves the production restoration.

Seven focused tests pass normally, with race detection and checkptr; six observer-enabled API regressions and the ten-package root suite pass. Eight CLI comparisons match diagnostics/exit status and semantic counters across one/four checkers and label modes. The first fixture setup failure is retained, not excluded silently.

No workload profiling, full conformance run for the diagnostic build, sharing proof, or speedup is claimed. Raw pointer/context matches do not establish immutable equivalent results. Elapsed nested accounting is not CPU time; allocation counters are inclusive. Record caps and label inheritance must be assessed on real workloads before interpretation. The separate diagnostic executable retains pointer keys and changes memory lifetimes.
