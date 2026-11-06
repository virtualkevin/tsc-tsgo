# Decision: reject tiled template relations

The complete 28-pair screen at d66fc14 passed input, diagnostic and provenance checks but failed the frozen performance gates. No promotion, confirmation runs or rescue reruns.

| Workload | Baseline median ms | Candidate median ms | Ratio of medians | Median paired ratio | Baseline/candidate median RSS MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 3053.82 | 2902.81 | 1.052023 | 1.061783 | 880.96/883.59 |
| trpc | 603.28 | 602.75 | 1.000888 | 0.886423 | 239.75/235.00 |
| vscode | 49544.78 | 53330.49 | 0.929014 | 0.919124 | 7674.27/7800.94 |
| sentry | 39960.36 | 38127.78 | 1.048064 | 1.106876 | 5393.24/4969.45 |

Ratios above one favor the candidate. Aggregate geometric means are 1.006248 (ratios of medians) and 0.989208 (paired medians), both below 1.01. VS Code fails both 0.98 workload floors; tRPC fails the paired floor. All median RSS gates pass.

Sentry is faster in all five pairs and has 7.86% lower median peak RSS. This supports investigating the storage mechanism further, but does not override the failed acceptance rule or establish a confirmed speedup. Pair variation is substantial (TypeORM 0.353–1.294, tRPC 0.700–1.234); these samples do not establish a precise causal slowdown. Every sample is retained.

Candidate focused histories, retained semantic controls, full compiler/services/conformance, CLI/API/emit, race and checkptr checks passed. The normal provenance-backed build matched the tested overlay. These checks are not a whole-compiler equivalence proof; CONTRACT.md documents the key-equivalence assumptions. The recorder's `status: passed` means evidence integrity, while `qualifiesForConfirmation: false` is the performance decision.

The measured domain is dense on Sentry but sparse on VS Code. The tagged key expands every maybe-stack key from 16 to 24 bytes, and every relation lookup gains backend dispatch, including workloads with few eligible entries. These are source-level overhead hypotheses, not measured attribution. A future design must remove or independently justify costs imposed on the general path; merely retrying this layout or tuning tile size after seeing results is not a confirmation.

Retained production source (216d40c7) and default binary (8fe4bd80) remain unchanged. Candidate fbe59ec1 and all source, validation, timing, controller and supervisor evidence are preserved. No comparison against original native was performed in this screen, and the 10× native goal remains unmet.
