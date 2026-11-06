# Decision: reject optional symbol storage

The complete 28-pair screen at adddc6a passed input/provenance/diagnostic integrity checks but failed the frozen performance acceptance gates. No promotion or confirmation runs.

| Workload | Baseline median ms | Candidate median ms | Ratio of medians | Median paired ratio | Baseline/candidate median RSS MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 2412.43 | 2579.84 | 0.935106 | 1.028331 | 883.42/882.20 |
| trpc | 467.21 | 480.89 | 0.971556 | 0.971556 | 243.25/239.62 |
| vscode | 53095.18 | 57171.05 | 0.928707 | 0.999291 | 7726.15/7590.03 |
| sentry | 43146.33 | 43130.30 | 1.000372 | 1.025305 | 5422.27/5112.63 |

Ratios above one favor the candidate. Aggregate ratio-of-medians geometric mean is 0.958500; paired-median geometric mean is 1.005857, both below the required 1.01. TypeORM, tRPC and VS Code miss the 0.98 ratio-of-medians floor; tRPC also misses the paired-median floor. All RSS gates pass.

Pair variation is substantial, and paired summaries differ from ratio-of-medians summaries. These results do not establish a precise causal slowdown or a statistical confidence interval. They do establish failure of the predetermined acceptance rule. Reduced RSS, especially Sentry, does not compensate for that failure. No favorable samples were selected and no historical ratios were compounded.

Focused stateful storage/clone tests, compiler/services/conformance, and CLI/API/emit/race/checkptr checks passed. The normal provenance-backed build matched the tested overlay binary. Tests do not constitute a whole-compiler equivalence proof.

Retained production source and default compiler remain unchanged. This experiment provides no progress claim toward 10× original native performance. The additional allocation/indirection is a possible explanation, not a measured attribution. Preserve this experiment as a rejected layout; do not promote or repeat unchanged to seek a favorable run.
