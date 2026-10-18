# Name construction census

This diagnostic overlay implements the cardinality gate from the canonical-name-flow audit. Production source remains `216d40c7` at capture HEAD `cc36c1f`. The retained compiler is unchanged. This is evidence for evaluating the semantic-storage strategy in OPTI_ANALYSIS_01.md, not a performance candidate.

## Results

| Workload | Identifier constructor events | Binder symbol events | Checker symbol events | Distinct names across categories | Distinct byte length | Untracked events |
|---|---:|---:|---:|---:|---:|---:|
| typeorm | 453,869 | 186,223 | 275,370 | 20,689 | 666,469 | 0 |
| trpc | 204,655 | 127,787 | 59,115 | 26,772 | 501,374 | 0 |
| vscode | 7,465,145 | 2,923,596 | 3,922,589 | 272,860 | 5,974,029 | 0 |
| sentry | 2,667,723 | 1,454,672 | 3,578,157 | 155,727 | 3,988,296 | 0 |

All 12 controls (retained binary, observer binary with collection disabled, and collection enabled on each workload) exited zero with empty stdout/stderr. Physical input/config hashes were checked before and after each workload. Underlying source, HEAD, both binary hashes, retained provenance sidecar and six overlay sources stayed fixed. The original native implementation was not timed here.

The repeated construction events and relatively small distinct-name sets support prototyping canonical name propagation. They do not show how often `unique.Make` would execute, how many objects remain live, what fraction of names is already canonicalized by the parser, or how much CPU/heap/RSS could be saved. Each constructor call may create a temporary/speculative/repeated object. Event-byte totals are not allocation totals. Do not multiply event counts by a proposed field-size reduction and report that as memory saved.

Next implementation decision: carry a canonical name through identifier/symbol storage and the checker/binder query interfaces; preserve built-in map semantics. Trace the remaining query boundaries before replacing their key type. A conversion at every map access would retain hashing and add canonical-table work. Canonical weak descriptors, cloned strings and cleanup costs must be measured in the complete candidate. This capture is not a reason to retune rejected parser-interner or lazy-identifier-name candidates.

## Observer scope and correctness

`NodeFactory.NewIdentifier`, `Binder.newSymbol` and `Checker.newSymbol` record exact byte strings under one mutex. A shared dictionary caps tracked names at 1,048,576 keys and 64 MiB of distinct name bytes. No capture reached either cap. The dictionary clones each first-seen key and never replaces it on category updates, avoiding backing-source retention; a separate membership slice stores category bits. It retains no AST or Symbol pointers and serializes no name text. Shared synchronization and cloned-name retention perturb execution, so capture durations are intentionally not performance measurements.

Membership masks use bit 0 for identifier construction, bit 1 for binder symbols, bit 2 for checker symbols. Length histograms use `bits.Len(byte length)`; empty names occupy bucket zero. Counts include synthetic checker names, but exclude direct Symbol.Name rewrites, keyed initializers, direct struct copies, other literal/private-identifier constructors, and query conversions. No semantic identities are merged.

Four focused tests passed both normally and with `-race`: category membership/exact bytes including NUL and invalid UTF-8, both caps and overflow accounting, concurrent updates, and cloned-key ownership across updates. Test-only unsafe pointer inspection checks key ownership; the observer uses no unsafe operations. These tests validate the observer, not full compiler conformance. `verify.py` checks the saved raw outputs, tests, build/capture links, reference commands and counter conservation; `verification.json` records its result.

## Reproduction

At this production source, run `python3 benchmarks/profiles/name-construction-census/prepare.py` from the repository root to regenerate ignored overlay sources and overlay.json. The generated patch and observer sources are archived. Run `validate.py` for focused normal/race tests. Build from packages/tsc-go with the pinned Go 1.26.9 toolchain, `-trimpath -overlay <absolute profile>/overlay.json -o /tmp/tsc-name-construction-census ./cmd/tsgo`; the exact command and resulting binary hash are in build.json, and toolchain build settings in build-info.txt. build.json is post-build diagnostic metadata, not a production build-system sidecar. `capture.py` requires that metadata and source/test hashes to match before running the 12 controls. A new build must record its own metadata before capture; do not relabel archived evidence.

Run `python3 benchmarks/profiles/name-construction-census/verify.py` for offline evidence readback. `manifest.json` covers archived files other than itself and the regenerated overlay. No PERF row follows because no performance comparison was made. The 10× original-native goal remains unmet.
