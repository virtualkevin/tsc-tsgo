# Current retained-Go A/A results

Capture at checkpoint 0f22191 completed successfully (session 44244, exit 0). Recorder 71874 exited 0 after checking frozen artifacts, physical inputs, diagnostics and protocol. The same retained executable, path, source and sidecar ran under both labels. Independent verify-screen.py recomputed all 28 pair orders, timing/RSS summaries, ranges, log deviations and archived execution hashes.

| Workload | Ratio of label medians A/B | Median paired A/B | Paired range | Label A median RSS MiB | Label B median RSS MiB |
| --- | --- | --- | --- | --- | --- |
| typeorm | 1.012812 | 0.989157 | 0.852403–1.181623 | 879.648 | 858.754 |
| trpc | 1.014833 | 1.000342 | 0.872517–1.264041 | 242.625 | 244.125 |
| vscode | 0.956315 | 1.022731 | 0.882378–1.071114 | 7642.145 | 7686.367 |
| sentry | 0.987691 | 0.963332 | 0.841164–1.102657 | 5399.109 | 5434.148 |

There is no implementation difference to explain these ratios. TypeORM and VS Code summaries point in opposite directions depending on whether medians or paired ratios are used. Sentry’s paired ratio is 0.963332. The VS Code ratio of medians and Sentry paired median would cross the existing 0.98 workload floor despite identical executables. RSS label medians differ too; none exceeds a 1.05 ratio in this finite sample.

This demonstrates that small screen effects can occur without a code change. It does not estimate a universal noise bound, prove independent samples or stationarity, identify the external cause, or prove that a rejected candidate would help. The historical different-binary screens cannot be corrected by subtracting these differences or dividing by these ratios. No samples were removed, no previous candidate was reopened and no acceptance policy was retroactively changed.

Keep prior rejections as conservative non-promotion decisions, without treating their small differences as precise causal slowdown estimates. Future research needs a mechanism affecting a substantial share of execution and a fresh matched comparison; accumulating historical micro-optimization ratios is not a route to the original native-relative target. A/A calibration supplies measurement context, not progress in compiler speed.

Four explicitly calibration-only compiler workload rows were appended to PERF.md. All samples and copied execution files are in ../../results/retained-aa-current-screen. Production remains retained node-pointer Go; the 10× objective remains unmet.
