# Coallocated instantiated-symbol screen: rejected

All planned correctness gates passed, including paired constructor histories, store and graph-lifetime tests, compiler/services/pinned conformance, normal/race/checkptr CLI parity and API/emit/project integration. The normal provenance build matches the tested executable. Production remains retained binary 8fe4bd80 / source 216d40c7.

The frozen screen at checkpoint 13e26d7 completed (session 95341, exit 0); recorder 13151, exit 0 verified the protocol, inputs, diagnostics and identities. Capture success does not mean performance acceptance. Independent verify-screen.py recomputed all 28 pairs, order, timing and RSS medians, paired ranges, aggregates, gates and archived execution hashes.

| Workload | Ratio of medians | Median paired ratio | Paired range | Retained median RSS MiB | Candidate median RSS MiB |
| --- | --- | --- | --- | --- | --- |
| typeorm | 0.955822 | 0.977001 | 0.744198–1.674596 | 867.414 | 872.738 |
| trpc | 0.883461 | 0.918438 | 0.765160–1.400856 | 243.125 | 241.375 |
| vscode | 1.124459 | 1.032370 | 0.884801–1.249151 | 7699.863 | 7565.605 |
| sentry | 0.989713 | 0.960134 | 0.941746–1.252594 | 5407.586 | 5167.949 |

Ratios above 1 favor the candidate. Aggregate geometric means 0.984587 and 0.971131 both fail the 1.01 threshold. TypeORM and tRPC fail both 0.98 workload floors; Sentry fails its paired floor. All median RSS ratios pass the 1.05 ceiling.

Reject this candidate without confirmation, rescue runs or post-result representation tuning. The VS Code improvement does not override the frozen aggregate and regression gates. Pair ranges are broad, so these observations are not precise causal slowdown estimates. This Go/Go screen establishes no original-native-relative improvement.

The coallocated record keeps the same 152 bytes of payload and introduces stronger symbol-to-links retention. These results do not justify that tradeoff for production. They do not rule out every ownership or storage redesign. Four measured compiler rows were appended to PERF.md; all samples and copied execution files are retained under ../../results/coallocated-instantiated-symbol-screen. The 10× goal remains unmet.
