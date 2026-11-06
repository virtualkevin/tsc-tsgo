# Fused completed intersection lookup

Isolated candidate following the discriminant-query census at 399a553. That census
observed 11.14M repeated Sentry property-query keys, mostly intersections, with no
counted instantiation/type/symbol construction. It supports investigating cheaper
existing-result access, not adding a broad semantic result cache.

The candidate recognizes a completed identity path through type reduction,
apparent-type conversion, and the non-augmented property cache. It uses the same
current symbol and calls the original symbol-type resolver. Everything else
follows the unchanged original path. See CONTRACT.md for exact guards, state
assumptions and observable correspondence. Both existing property maps and all
population rules remain unchanged.

This adds guard reads to every getTypeOfPropertyOfType call and may regress other
workloads. No speedup is assumed. The established four-workload acceptance policy
applies; production and PERF.md remain unchanged until measured acceptance.

Candidate and retained each passed 11 focused tests in normal/race/checkptr modes.
Full validation passed 21,179 root test records across 14 packages, 219 services
records, and all 14,915 pinned conformance configurations (12,789 fully checked,
8 partially checked, 2,118 unsupported/skipped, zero failures). Normal/race/checkptr
CLI parity each passed 80 cases; API/emit integration passed 12. Independent raw
archive verification passed. These are tested domains, not a whole-compiler proof.
The normal production build passed with exactly three changed/new files and
5,156 candidate source files; its executable matches the tested normal overlay.
Retained source/default executable restoration and benchmark preflight passed.
The performance screen has not run yet. Source audit
proves exact original fallback restoration and correspondence of candidate/baseline
helper and tests.

Static assembly capture (exact reproduction passed) confirms the candidate entry
contains direct map lookup and no call to a standalone guard helper. The retained
entry is 116 encoded bytes/34 instructions; candidate is 331 bytes/86 instructions.
The larger footprint is a cost, not an executed-instruction count or performance
result. Original fallback and symbol-type calls remain in the candidate code.
The optional objdump utility was absent from the installed toolchain and archive;
initial failures are preserved. Building cmd/objdump from installed Go 1.26.9 source
into a separate temporary directory enabled inspection without changing compiler
sources or the installed toolchain. See codegen-tool-discovery.json and codegen.json.
