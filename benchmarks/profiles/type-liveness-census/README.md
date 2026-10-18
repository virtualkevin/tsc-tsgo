# Diagnostic type-construction liveness census

This is an observer, not a production optimization or timing candidate. Source `390c3a036035aaf1d8a1e8d7f60bdf6376df172f1ed6905b2413e1235caecf90`, 5,157 files, based on retained main `686a0c7`. Two tracked files change and three diagnostic/test files are added. `source.json`, `instrumentation.patch`, and copied added files preserve the source.

Each checker records weak references at construction ordinals 1,65,..., capped at 65,536 samples. The ledger stores creation flags and semantic ID but no strong type pointer. Reports include total constructions, eligible/sample/overflow counts, available/cleared weak references, kind totals, and checker identity mismatch checks. The CLI reports after ordinary emit/diagnostic work; it holds existing checker locks, performs two forced GCs while keeping the program/checkers alive, and writes JSON. It does not construct extra checkers or issue semantic queries. Empty uninitialized lock slots are skipped. Tracing-enabled captures are rejected to avoid tracing retention bias.

Cleared references demonstrate reclamation in the diagnostic run; available references do not prove semantic necessity. Sampling is deterministic and bounded, not an unbiased estimate or retained-byte measurement. Weak-reference bookkeeping and forced GC perturb execution. No capture elapsed time is a compiler performance result.

Validation completed: three focused tests pass normally, under the race detector, and with checkptr=2. The core suite passes 2,342 test records across ten packages. All twelve baseline/observer-disabled/observer-enabled captures exit cleanly against identical pinned physical inputs. Source and HEAD were held fixed; all four captures have four checker owners, conserved counters, zero identity mismatches, and no sampling overflow. Raw logs and counts are preserved in `evidence.tar.gz`; `evidence-manifest.json` hashes every member and the archive, and the archive was read back and verified. `summary.json` contains derived counts. The initial sandboxed launch failed at Git provenance before any workload ran; its empty output directory was removed before the authorized capture.

| Workload | Types constructed | Sampled | Available | Cleared | Cleared / sampled |
|---|---:|---:|---:|---:|---:|
| typeorm | 257,912 | 4,032 | 3,773 | 259 | 6.424% |
| trpc | 79,462 | 1,243 | 1,229 | 14 | 1.126% |
| vscode | 4,277,160 | 66,832 | 61,756 | 5,076 | 7.595% |
| sentry | 2,725,687 | 42,590 | 35,327 | 7,263 | 17.053% |

This establishes a concrete retention tradeoff for an unconditional strong all-type ID decoder: some constructed types can currently become unreachable even while their checker and program remain alive. It does not establish the byte cost, population reclamation rate, or net performance of such a decoder. A weak decoder alone cannot preserve types reachable only through integer IDs. Any compact representation still needs a reachability-preserving ownership design; a permanent decoder is not a free replacement for pointer edges.

The separate type-list audit finds a small explicitly attributable slice-byte subset, with ambiguous generic allocations excluded. Combined with this census, the evidence does not justify a broad pointer-list-to-ID rewrite yet. A future proposal should identify a bounded owner that already retains its targets and measure both decoder cost and removed pointer storage, rather than assume all semantic types already live for the entire checker lifetime.

`restoration.json` verifies production source restored to `216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd` and default binary to `8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f`. Instrumentation is retained only as the patch and copied files here. No production optimization, PERF row, or speedup claim; the 10× native-relative target remains unmet.
