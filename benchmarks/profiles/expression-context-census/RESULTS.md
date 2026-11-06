# Completed ordinary contextual expression census

Validation43094 exited0: four tests each normal/race/checkptr. Build51090 exited0, binary451d1f27042e47405d3993f516e1dce9c56492ceae051ff70976b2e905fbd57e. Capture2089 exited0: all twelve retained/disabled/enabled controls had clean diagnostics, four checker owners, and identical pinned physical inputs. Independent raw verification and analysis/reproduction83067 passed; four Python accounting tests passed. Production is unchanged.

| Workload | Calls | Tracked first | Tracked repeats | Changed result identity | Dropped requests | Saturated owners | Exclusive instantiations/types/symbols | Repeat exclusive instantiations/types/symbols |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| typeorm | 150857 | 149909 | 948 | 40 | 0 | 0 | 174259/105519/110652 | 0/84/94 |
| trpc | 4789 | 4759 | 30 | 8 | 0 | 0 | 30701/14795/10556 | 0/14/20 |
| vscode | 2414062 | 524288 | 3248 | 153 | 1886526 | 4 | 2684051/2395138/2204249 | 138/344/620 |
| sentry | 648441 | 524288 | 2181 | 166 | 121972 | 4 | 1978122/873738/871209 | 6120/6754/6978 |

TypeORM and tRPC have complete recorded histories in this capture. Both large projects saturate all four owners, censoring later histories; do not interpret their tracked repeats/calls as a full-workload recurrence rate. Uncapped aggregate calls and construction counters cover all observed requests. Repeat counters cover tracked keys only. Changed identities are not automatically different TypeScript meaning, but they invalidate an assumption of stable identity for indiscriminate result reuse.

The small projects show no instantiation increments on completed repeats; this does not mean those requests are effect-free or costless. VS Code records six net relation entries on repeats. Inference flags change on 37/1137/501 calls for tRPC/VS Code/Sentry respectively. Boundary inference-site counts are zero, which does not exclude internal inference effects. Instrumented elapsed times are excluded from PERF.md.

Decision: do not implement a broad contextual result cache from these keys. For the large projects, repeat coverage is insufficient to reject every narrower cache; a bounded rotating history would be needed for that question. The uncapped expression-kind cohorts in analysis.json instead identify construction-heavy families without assuming recurrence. Investigate their source operations and allocation contracts before proposing a representation or work-elimination change. No compiler speedup or route to 10× has been established.
