# Optional Symbol storage prototype

Isolated overlay on retained source at 42ed498, motivated by the independently
verified symbol-cold-field-census. Moves Members, Exports and ExportSymbol into a
lazy typed optional record. No checker-wide registry, integer handle, unsafe
pointer conversion, semantic result cache or altered slab policy is introduced.

The type-aware inventory loaded the module and tests using go/packages. It found
147 field uses in 23 files: 131 reads, 11 simple assignments and 5 address-taking
uses, no affected Symbol literals or complex assignments. migration.json records
exact source hashes and nonoverlapping byte edits; prepare.py writes only staged
files. Other AST node Members fields are untouched. Original production source
remains unchanged. Source-level access changes affect internal ast.Symbol; this
is not a claim of source compatibility for clients directly reading old fields.

Read methods return the same map/pointer without allocation. Setters preserve
other fields and avoid allocation for nil assignments to an untouched symbol.
The optional record is never replaced, so the typed slots used by existing lazy
map initialization remain stable. Maps still clone at the original clone sites.
No nil/empty normalization or ExportSymbol copying is added. A small Go probe
confirmed RHS execution before a nil-receiver field-write panic; setters have
the same order for the simple assignments in the inventory. This observation is
not a general proof for arbitrary Go assignments.

Expected amd64 sizes are 80 bytes for Symbol plus 24 bytes when optional fields
need storage, versus 96 bytes originally. The layout test measures the candidate.
Sparsity and nominal size do not prove a speedup: additional allocation, lookup
indirection, write barriers, GC scanning and slab retention may lose performance.
The existing frozen full-workload policy remains required before promotion.

Four focused tests cover 64 deterministic 256-operation mutation histories with
map/target identity checks; nil/empty distinctions; lazy maps and stable retained
slots; measured layout; and the actual checker clone path's independent map
backing and preservation of the existing omitted ExportSymbol behavior. GC tests
use typed roots and previously returned values. All four candidate tests passed under normal/race/checkptr; the
same clone history passed on retained source in all three modes. Full compiler, conformance, CLI/API/emit and normal build provenance
remain pending. No performance or whole-compiler equivalence claim is made.

See ../symbol-cold-field-census/LAYOUT_CONTRACT.md for the refinement obligations.

Initial focused run 65307 passed all three AST tests, including measured sizes
80/24 bytes, but the checker clone fixture panicked in recordMergedSymbol because
the minimal helper did not initialize mergedSymbols. The raw logs, controller,
initial test and full source hashes are preserved under failed-fixture/. The
fixture now initializes that existing map; production candidate code is unchanged.
Fresh validation runs all four candidate tests and the same clone history on
retained source, each normally and with race/checkptr. No failed run is relabeled.

Focused chain 25940 completed successfully. Full validation (root compiler,
services and pinned conformance) and CLI/API/emit/race/checkptr integration are
now running under separate signal supervisors. The source/HEAD remain frozen.
The candidate declaration transform is pinned to the exact audited one-read
substitution, SHA256 689bd2d2fdf56effc292e47b8bf96c1d8078253c193d262ddec1e75c334b7c8c.
No full-suite pass, production build, workload improvement or promotion is claimed.

A second type-aware audit (tool/copyaudit/main.go) found 23 Symbol value
expressions in the retained module/tests, all fresh composite literals; it found
no direct whole-Symbol copy expression in that loaded syntax. The existing generic
arena allocates new zeroed slabs without copying published objects. This is not a
proof about arbitrary generic code, reflection or future code. Raw locations and
expressions are preserved in value-expressions.json. Runtime identity and clone
tests remain necessary.

The first broader validation attempts did not complete: root reported build
failures, and the CLI linker explicitly reported no space left on device. Both
failed attempts, controllers and raw logs are preserved; failed-disk/failure.json
pins their hashes. Removing only hashed Go cache entries untouched for 12 hours
freed 52,765,782,721 bytes (8,341 files); source, evidence, retained executables and
recent cache entries were preserved. Retry controllers use separate output paths
and unchanged source/comparator pins. The failure is not relabeled as a pass.

Continuation: CLI/API/emit and race/checkptr CLI checks completed successfully. Root and services passed; conformance was interrupted by SIGTERM (supervisor records sender codex PID 3841, reason unknown). `validate-full-resumed.py` preserves that report and carries forward only completed phases, running conformance into separate outputs. An initial resume stopped before tests because the temporary Go toolchain was missing; the exact Go 1.26.9 toolchain was restored. No performance result yet.

All required correctness runs now completed and independently read back. The conformance continuation passed all 14,915 configurations (12,789 fully checked, 8 partially checked, 2,118 unsupported/skipped, zero failures). The normal production build matches the tested binary exactly; the retained source and default executable were restored. See readback.json and production-build.json. Performance screening is next; no promotion yet.
