| Revision / stage | Workload | Native tsc-ts median (ms) | Go median (ms) | Speedup | Runs | Correctness / evidence |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Initial Go (`c6c77d1`) | TypeORM source + tests; Node20 compatibility | 1420.04 | 2878.69 | 0.493× | 5 | Identical 3,572 inputs; clean diagnostics; [raw samples](benchmarks/results/initial-typeorm-trpc.json). Declaration ordering limitation outside no-emit workload. |
| Initial Go (`c6c77d1`) | tRPC server | 345.89 | 765.20 | 0.452× | 5 | Identical 942 inputs; clean diagnostics; [raw samples](benchmarks/results/initial-typeorm-trpc.json). Declaration ordering limitation outside no-emit workload. |
