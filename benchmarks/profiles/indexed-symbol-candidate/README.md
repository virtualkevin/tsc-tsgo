# Indexed ValueSymbolLinks candidate

Variant3 of the indexed-symbol pilot is now built and compiler-validated, but has no workload performance results and is not yet promoted. It adds sparse typed indexed links to the identical allocation handles used by the preserved handle-only control. Only ValueSymbolLinks changes storage. No semantic IDs are forced and no checker-owned values are published on shared symbols.

The original combined implementation is ../indexed-symbol-pilot/indexed-combined.patch. The additional wrapper integration fixture is now internal/ast/symbol_links_test.go in the compiler source. indexed-build.json records the exact five-file delta against the handle-only control and nine-file delta against the saturated baseline, with identical build settings across all three. The normal executable is preserved locally as packages/tsc-go/dist/tsc-go-symbol-indexed with its provenance sidecar.

## Validation

Nine focused tests pass under each of normal, race and checkptr. This includes allocator exhaustion and concurrency, sparse index boundaries, fallback identity, readonly access, typed GC roots, wrapper domain/reset behavior, and existing actual checker graph-retention/replacement tests. Root units pass2345records in ten packages, without skips. Full pinned conformance passes12789fully checked and8partially checked cases with2118unsupported skips and no failures.

Native parity passes80tests, and actual-Go API/parallel-emit/project integration passes12, without skips. The separately built race-instrumented CLI passes all three parallel-emit tests, covering ten compiler invocations across single-threaded and2/3/4checker configurations. This does not establish safety for arbitrary concurrent mutation of a checker.

Reports: ../../validation/indexed-symbol-candidate-{conformance,native,race-cli}.json. Focused/native/race-CLI raw logs and executed controllers are archived here. Large root/conformance logs remain in /tmp/tsc-indexed-integration/indexed; the report records hashes. Source/HEAD/pins and normal/comparator binary identities are checked by their respective controllers; the race controller separately checks source, instrumented executable and sidecar identity. External dependency contents are not fully hermetically hashed. Correctness runs overlapped; elapsed times are not performance evidence.

Controllers retain their original absolute paths. validate-indexed.py imports the earlier prehashed-relations validator solely for root/conformance summarization, disables bytecode-cache writes, and adds interruption handling. Its cache-specific checks are not executed. Native and race controllers require the preserved indexed-build.json identity. Reruns require fresh output locations.

## Layout and generated code

The executable layout report measures Symbol104bytes versus96baseline; Binder296versus288; Checker6832versus4760handle-only and4752baseline. The indexed store adds2072bytes to the control Checker, largely its inline radix root. These are type sizes, not allocation size classes or RSS; sparse page occupancy remains unmeasured.

The real indexed Get contains shifted/masked indices and dependent pointer loads, with nil and identity checks. Indexed hits avoid pointer hashing/probing. Its entry walk is inlined, but Get itself remains out of line. No panicIndex call appears in the inspected Get. Unindexed and colliding handles retain PointerLinkStore fallback. In the sampled getTypeOfInstantiatedSymbol caller the wrapper/handle load inline; caller size grows180to197bytes while the40-byte stack reservation is unchanged. Getter sizes cannot alone compare the complete lookup code footprint because the control calls a separate slot routine. See codegen/report.json and hashed assembly. No speed conclusion follows.

## Remaining performance gates

Preserve the saturated baseline and handle-only control. Calibrate same-binary A/A variability, then compare all three builds on the four pinned workloads with identical wrappers, environments and peak RSS. Overall adoption must beat the unchanged baseline, not just the handle-only control. Measure page occupancy/fallback use if needed to explain costs. Run a fresh original-native comparison for goal accounting; do not multiply historical Go/Go ratios. The10× target remains unmet.
