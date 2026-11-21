# Where the Go compiler spends CPU

The semantic checker accounts for 73% of Sentry's sampled CPU and 64% of VS Code's. tRPC spends 35% in the checker and 31% parsing, scanning and binding. These are full, fresh-process type checks of the four pinned projects with shipping compiler e1eeaab. Each run verified the input files, completed with exit zero and produced clean diagnostics.

| Project | Profile interval | Sampled CPU | Checker | GC marking | Parse and scan | Bind | Other |
|---|---:|---:|---:|---:|---:|---:|---:|
| VS Code | 46.11 s | 203.66 s | 64.0% | 16.9% | 10.6% | 4.8% | 3.6% |
| Sentry | 47.97 s | 201.98 s | 73.3% | 15.0% | 3.9% | 3.0% | 4.8% |
| TypeORM | 3.45 s | 16.57 s | 47.5% | 17.7% | 8.9% | 4.9% | 20.9% |
| tRPC | 0.58 s | 2.85 s | 35.1% | 18.6% | 17.9% | 13.0% | 15.4% |

CPU seconds sum work across threads. The first table assigns each sample to one category, giving precedence to GC marking, then checker, binder and parser/scanner frames. Other includes samples outside those families. Percentages are rounded. The tRPC profile has 285 samples and correspondingly less precision.

| Operation present on the sampled stack | VS Code | Sentry | TypeORM | tRPC |
|---|---:|---:|---:|---:|
| Resolving symbol types | 19.1% | 22.1% | 12.0% | 9.8% |
| Comparing types for compatibility or identity | 11.6% | 23.4% | 7.5% | 9.8% |
| Instantiating generic types | 5.8% | 17.9% | 3.9% | 9.5% |
| Normalizing union types | 3.4% | 6.1% | 1.8% | 0.7% |
| Go map operations | 18.2% | 24.9% | 11.6% | 17.2% |
| Pointer-keyed checker tables | 8.3% | 6.4% | 4.6% | 4.9% |
| Go heap allocation | 9.3% | 8.9% | 11.8% | 12.3% |

The second table gives shares of total sampled CPU. A type comparison can instantiate a type and read a map, so its sample can appear in all three rows. On Sentry the relation-result map read alone accounts for 4.46% of CPU and its write for 0.94%. On VS Code the largest ordinary map call site is the generic LinkStore lookup at 2.34%. These figures motivate reducing repeated semantic requests along with their table accesses and allocations.

The [raw attribution](costs.json) records the matching rules and overlap counts. The [manifest](manifest.json) identifies the compiler, project revisions and profile hashes. To explore a call tree interactively with the Go toolchain, run the following from the repository root, substituting the desired project name for sentry.

```sh
go tool pprof -http=localhost:0 benchmarks/profiles/shipped-cpu-costs/sentry-cpu.pb.gz
```

## Optimization targets

1. **Start with overload selection inside declaration initializers.** The entire initializer path accounts for 15.41% of all sampled CPU on Sentry, 11.46% on VS Code, 7.18% on TypeORM and 4.56% on tRPC. Within it, overload selection accounts for 9.51%, 6.42%, 4.71% and 3.86% respectively. At the outermost overload choice inside an initializer, the first generic argument inference pass alone accounts for 4.01% on Sentry and 3.57% on VS Code. The first general applicability check accounts for another 3.00% and 0.99%. Measure repeated checking of the same argument against equivalent parameter types across candidate signatures here. Any reuse must account for contextual typing, check mode and mutable inference state.
2. **Target structural property comparison on the two large projects.** Samples assigned to the innermost propertiesRelatedTo or propertyRelatedTo branch account for 7.86% of Sentry and 4.65% of VS Code CPU. Inspect demand for member types on each side of a comparison and whether name/optionality checks can establish the outcome earlier while preserving diagnostic order. Sentry also spends 6.15% in generic instantiation initiated by type alias instantiation and 4.15% initiated by the mapped-member resolver's closure. These figures are inclusive and can overlap property comparison.
3. **Short union normalization has measurable reuse.** A checker-local 4,096-slot simulation found 1,569,337 resident matches across 1,962,083 eligible ordered inputs on VS Code, and 988,222 across 1,208,542 on Sentry. All actual computations still ran. Union normalization covers 3.38% and 6.06% of total CPU respectively, including ineligible cases. A bounded cache for the plain literal/intrinsic subset is a concrete experiment. A simulated match alone does not prove that skipping the computation preserves diagnostics or saves wall time.

An independent observer tested the quick initializer path on the same projects. Full resolution checked the same callee again 65,202 times on VS Code and 24,600 times on Sentry. The second check returned a different type pointer in 34 and eight cases respectively. Those two evaluations occur in different contexts; reusing the first result unconditionally would change actual compiler state. Even the broader source line that evaluates callees during full resolution inside initializers accounts for only 0.98% and 1.14% of total CPU. The larger opportunity is generic argument inference and candidate applicability. [Observer results](../initializer-call-demand/counts.json)

### Argument checks across overload candidates

The first argument-expression check during generic inference is the largest sampled inference source line on every project. It reaches 3.42% of all CPU on VS Code and 3.86% on Sentry. Within that line, nested calls lead VS Code at 2.32%. On Sentry, function expressions and object literal methods account for 1.68%, object literals for 0.99% and array literals for 0.70%. These are descendant CPU costs. A repeated argument-result cache was tested observationally on both inference and applicability paths.

Within one resolution, the observer compared each check to the most recent check of the exact argument node and parameter type. In VS Code, only 157 of 363,683 observed inference checks repeated that pair under a different signature. Sentry had 239 of 143,578. Neither project had an inference repeat with both the same check mode and inference-context pointer. Applicability did repeat under those stricter conditions, but the resulting type pointer changed on 1,494 of 14,283 such checks on VS Code and 141 of 2,530 on Sentry. Across all four projects the public CLI comparison fixtures and options remained frozen and the diagnostic Go build completed each check cleanly. [Raw probe counts](../overload-argument-reuse/counts.json)

This moves cross-candidate caching down the priority list. On VS Code, inspect the nested-call signature resolver's existing cache, specifically whether expensive misses are first visits, in-progress resolutions or deliberately uncached checks under flow analysis. On Sentry, target the construction and contextual typing of function and object arguments in the first pass. Any sharing must preserve parameter assignments, diagnostics and inference effects.
