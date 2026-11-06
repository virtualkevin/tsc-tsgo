# Decision: reject compact structured slices

The complete 28-pair screen at8f050ea passed input, diagnostic and provenance
integrity checks but failed the frozen performance gates. No promotion,
confirmation runs or rescue reruns.

| Workload | Baseline median ms | Candidate median ms | Ratio of medians | Median paired ratio | Baseline/candidate median RSS MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| typeorm | 3707.31 | 3481.45 | 1.064875 | 1.054102 | 883.10/876.74 |
| trpc | 723.91 | 699.17 | 1.035383 | 1.064203 | 239.62/242.38 |
| vscode | 54865.05 | 53975.45 | 1.016482 | 0.980639 | 7754.93/7640.88 |
| sentry | 40468.05 | 40502.28 | 0.999155 | 0.923815 | 5426.89/5352.04 |

Ratios above one favor the candidate. The ratio-of-medians geometric mean is
1.028687, but the paired-median geometric mean is1.004038, below the required1.01.
Sentry's paired median0.923815 misses the0.98workload floor. VS Code's paired
median0.980639 narrowly clears that floor. All median peak RSS gates pass.

Pair variation is substantial, particularly tRPC0.923–2.020 and
Sentry0.888–1.233. These data establish failure of the predetermined acceptance
rule, not a precise causal slowdown or statistical-confidence interval. No
favorable samples were selected, and no historical ratios were compounded.
The recorder's status:passed means evidence integrity; its
qualifiesForConfirmation:false records performance rejection.

The24-byte nominal StructuredType reduction is real layout evidence, and median
RSS was lower on TypeORM, VS Code and Sentry in this screen. It does not establish
an acceptable runtime gain. Added reconstruction/bounds checks remain a possible
cost, not a measured causal attribution. Do not repeat this same representation
or tune it after observing the screen to seek a favorable confirmation.

Standalone storage tests and packing-model checks, actual-checker stateful
histories and retained controls, full compiler/services/conformance, normal CLI,
API/emit, race and checkptr validation all passed. Independent raw-evidence
verification and the normal provenance-backed build passed. These are not a
whole-compiler equivalence proof; representation assumptions remain in CONTRACT.md.

Retained production source216d40c7/defaultbinary8fe4bd80 remain unchanged.
Candidatea2974b77/source3a16fa1b/sidecar8fd4282a and all source, failed attempts,
validation, controller, supervisor and timing evidence are preserved. This is
Go-versus-Go evidence, not a direct original-native comparison. The10×native
goal remains unmet.
