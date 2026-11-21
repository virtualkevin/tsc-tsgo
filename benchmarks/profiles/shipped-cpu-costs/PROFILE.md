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
