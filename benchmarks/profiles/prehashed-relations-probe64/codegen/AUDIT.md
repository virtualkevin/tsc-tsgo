# Prehashed relation cache: bounded production inspection

The table-mode lookup avoids runtime rehashing of the already-hashed key, but it retains an out-of-line cache call, scalar probing, separate array loads and bounds checks. This is actual generated-code evidence, not a runtime benefit or allocation measurement. All inspection processes are terminal; no build, test, workload, profile or main edit was performed.

Candidate is preserved `tsc-go-prehashed-relations` SHA4b7a58ba…, sourcef5e6e441…, compared with preserved saturated key-builder baseline2bdcca53…. Exact hashes, commands and settings are in capture.json. Complete provenance manifests differ only in relater.go, new relation_results.go and new relation_results_test.go; build settings match (Go1.26.9, Linux/amd64 v1, trimpath, no PGO/extra flags). See source-comparison.json. There is no numeric relation interner or semantic key rewrite.

## Lookup and write paths

Relation.get/set wrappers inline into actual semantic callers, while relationResultCache.get/set/rebuild have standalone symbols and calls. The compiler inlines find, hasSlot and writeSlot into the latter methods: no extra call for every probe. In cache.get, low-bit starting-index masking uses ANDQ, occupied-bit selection uses BTQ, and full-key equality uses two distinct64-bit loads/CMPQ. A matching slot then loads its uint32 result. Bitmap/key/value slice bounds checks and panicBounds branches remain. The table branch has no runtime key-hasher/map-access call; fallback retains runtime.mapaccess1. Other maps in recursiveTypeRelatedTo remain unchanged and must not be attributed to this table.

Actual isTypeRelatedTo and recursiveTypeRelatedTo call cache.get. Failure recording and resetMaybeStack call cache.set. The candidate emits resetMaybeStack out of line; its baseline body was inlined at the inspected recursive caller. Thus a smaller caller is not necessarily less work: some code moved to additional function boundaries.

Set emits three makeslice calls for initial key/value/bitmap arrays. Rebuild likewise emits three, then reinsert loops. Relation allocation remains a separate runtime.newobject in callers. Pointer-bearing cache-header assignments retain write-barrier paths (wbMove, wbZero, gcWriteBarrier); key/value backing arrays contain no pointers. Fallback construction uses runtime.makemap and mapassign. No allocation quantities, escape rates or hot-path allocation guarantees are inferred solely from assembly.

The compiler inlines useFallback into both failure paths of set and both failure paths of rebuild, duplicating map reconstruction code in cold branches. Emitted code sizes are get345, set1917 and rebuild2329 bytes. These code-size and cache-pressure tradeoffs remain unmeasured.

| Function | Baseline stack bytes | Candidate stack bytes |
|---|---:|---:|
| Checker.isTypeRelatedTo | 120 | 104 |
| Relater.recursiveTypeRelatedTo | 616 | 552 |
| Relater.resetMaybeStack | inlined | 88 |
| relationResultCache.get | absent | 24 |
| relationResultCache.set | absent | 216 |
| relationResultCache.rebuild | absent | 296 |

Frames exclude saved BP and cannot be summed into a compiler-wide stack claim. Caller code sizes change1208→1168 and4311→3581 respectively, plus the new421-byte reset helper and cache helpers. Exact values/calls are in summary.json. Baseline result lookups called runtime.mapaccess1 directly; candidate table lookup replaces that call with cache.get, while fallback goes through cache.get and then the runtime map.

## What this does not show

No actual table residency, fallback frequency, probe distribution, live memory, allocated bytes, workload duration or performance improvement was measured. The64-probe policy may cause ordinary large tables to fall back permanently; FALLBACK-OBSERVATION.md proposes a separate untimed cold-event diagnostic variant. The production artifact remains unchanged. Monolithic growth/RSS and cold-code duplication remain risks, not reasons to claim an improvement before measurement.

inspect.py reproduces the bounded helper/caller extraction. Helpers are complete; caller excerpts retain relevant calls/source operations and prologues, omitting unrelated instructions. capture.json records exact commands; summary.json records observed frames/code sizes/calls; manifest.json hashes all evidence except itself. Parent correctness validation is separate and is not claimed by this artifact.
