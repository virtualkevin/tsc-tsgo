# Decision: rejected

The frozen screen at fa0c678 completed all 28 measurement pairs and passed input,
diagnostic, build-provenance and raw-evidence integrity checks. It failed performance
acceptance. Ratios above one favor the candidate.

| Workload | Ratio of medians | Median paired ratio | Median RSS baseline/candidate MiB |
| --- | ---: | ---: | ---: |
| typeorm | 1.058609 | 1.000010 | 887.102 / 888.699 |
| trpc | 1.042080 | 0.931221 | 232.625 / 232.625 |
| vscode | 1.086112 | 1.002973 | 7654.180 / 7781.883 |
| sentry | 0.985021 | 0.985021 | 5252.055 / 5110.652 |

Aggregate ratio of medians 1.042291; paired-median aggregate 0.979373. Both must be at least 1.01.
The paired aggregate fails. tRPC's paired median also fails the 0.98 per-workload
floor. All RSS gates pass. Favorable ratios of medians on three workloads do not
override those failures. All samples remain in the record; pair variation is large,
so these summaries do not establish a precise causal slowdown.

No confirmation runs, extra samples, placement/guard retuning to reinterpret this
screen, or promotion. Production remains retained source216d40c7/default8fe4bd80.
Four PERF.md rows and the exact execution scripts/configuration/supervisor evidence
are archived under benchmarks/results/fused-intersection-lookup-screen/.

The mechanism retained semantic operations and passed the required correctness
checks. However, stable repeated query results plus a shorter eligible path did
not establish an end-to-end gain. Static code shows the common lookup entry grows
from 116 to 331 encoded bytes; this is a potential cost, not a measured explanation
of the failed screen. Do not treat the 11M Sentry repeats as freely removable work
or assume the existing caches are missing. The 10× native-relative goal remains
unmet; no native-relative improvement is claimed.
