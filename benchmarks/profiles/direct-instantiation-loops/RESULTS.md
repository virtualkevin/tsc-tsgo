# Direct instantiation loops: rejected screen

The fixed screen at `479b828` completed all 28 pairs. Recorder and independent
readback passed input/provenance/diagnostic/hash checks and recomputed every timing,
RSS, range, aggregate and gate. Capture success is not optimization acceptance.

Ratios are retained Go time / candidate time; values above one favor the candidate.
Both summaries are required by the policy fixed before timing.

| Workload | Ratio of medians | Median paired ratio | Paired range | Retained median RSS MiB | Candidate median RSS MiB |
| --- | ---: | ---: | --- | ---: | ---: |
| typeorm | 1.173391278 | 1.122560729 | 0.760022–1.659037 | 889.258 | 833.258 |
| trpc | 0.693761563 | 0.910919065 | 0.506046–1.243491 | 236.375 | 236.500 |
| vscode | 1.025243689 | 1.025243689 | 0.870679–1.209841 | 7740.043 | 7459.086 |
| sentry | 0.937923389 | 0.986773160 | 0.880565–1.089157 | 5349.703 | 5406.145 |

The aggregate ratio of medians is 0.940614978; the aggregate median paired ratio
is 1.008517683. Both fail the required 1.01. Both tRPC summaries and the Sentry
ratio of medians fail the per-workload 0.98 floor. All RSS gates pass.

Decision: reject without confirmation, rescue runs, or retuning to reinterpret
this screen. Broad paired variation limits causal slowdown estimates; this is a
failure to demonstrate the required gain. The generated-code result is still
valid: direct loops remove indirect callbacks, but that did not establish an
accepted end-to-end improvement. Full correctness success does not imply speed.

All raw observations, eleven execution files, and four table-only PERF rows are
preserved. Retained production source/default binary remain unchanged. No speedup
relative to original native tsc-ts is claimed; the 10× objective remains unmet.
