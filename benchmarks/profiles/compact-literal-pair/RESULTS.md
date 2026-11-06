# Compact literal-pair screen: rejected

All required correctness gates passed, including paired representation histories, normal/race/checkptr focused tests, root compiler tests, services, pinned conformance, CLI parity and API/emit/project integration. Independent raw evidence readback passed. The provenance-backed candidate is binaryd9252a12/source35b57efd; retained production remains binary8fe4bd80/source216d40c7.

The fixed screen completed at checkpoint0e1ee45 (session14722 exit0); recorder54378 exit0 verified the protocol, input hashes, diagnostics, timing/RSS observations and frozen identities. Capture success means the experiment completed, not that the candidate passed the acceptance gates. All28pairs were preserved.

| Workload | Ratio of medians | Median paired ratio | Paired range | Retained median RSS MiB | Candidate median RSS MiB |
| --- | --- | --- | --- | --- | --- |
| typeorm | 0.968201 | 0.984527 | 0.874369–1.228085 | 878.777 | 883.660 |
| trpc | 1.014670 | 0.965928 | 0.523282–1.605513 | 241.875 | 231.750 |
| vscode | 0.963792 | 1.007682 | 0.879193–1.084137 | 7428.246 | 7795.586 |
| sentry | 0.937460 | 0.940630 | 0.856462–1.065735 | 5396.117 | 5268.230 |

Ratios greater than1favor the candidate. Aggregate geometric means are0.970636(ratios of medians) and0.974381(paired medians), both below the required1.01. The workload floor also fails: TypeORM/VS Code ratios of medians, tRPC paired median, and both Sentry summaries are below0.98. All median-RSS ratios pass the1.05ceiling (VS Code is close to that ceiling).

Reject the candidate with no confirmation, rescue run, or post-result representation retuning. Struct size fell from88to80bytes, but that did not translate to an accepted end-to-end improvement. Small-workload paired ranges are broad; these observations are not precise causal slowdown estimates. This experiment does not disprove all literal-storage approaches or establish a native-relative speed change.

Four measured compiler rows were appended to PERF.md. Raw sample reports, frozen protocol and copied execution files are in ../../results/compact-literal-pair-screen. Production source and default binary remain retained. The10×native-relative goal is unmet.
