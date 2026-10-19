# CPU budget for semantic sharing research

Offline attribution of preserved normal-build CPU profiles from retained production
source216d40c7/binary8fe4bd80. Every profile and pprof text hash is checked against
the earlier input manifest, and total CPU matches the earlier property budget.
Each sample enters one exclusive category combination; recursive frames and
nested matching families do not duplicate samples within a family or union.

| Workload | Signature construction + return union % | Symbol type resolution inclusive % | Instantiation inclusive % | Relation recursion inclusive % |
| --- | ---: | ---: | ---: | ---: |
| trpc | 4.569 | 9.137 | 10.660 | 18.274 |
| typeorm | 2.287 | 11.873 | 4.925 | 6.596 |
| vscode | 3.410 | 19.603 | 6.103 | 9.760 |
| sentry | 3.916 | 21.448 | 17.705 | 21.275 |

These inclusive families overlap. They include cache hits and callees and are not
estimates of duplicate, immutable, removable, or wall-clock work. Historical
sampling uncertainty applies; zero samples does not mean zero executed calls.
No timing or PERF row was added. Two parser tests cover overlapping/recursive
frames and rejection of undecodable locations.

Decision: signature-only sharing is below the analysis document's proposed 10%
CPU research gate even before identifying safe repeated work. Do not implement
that cache. Symbol-type resolution has a larger envelope, especially on the two
large workloads. Next instrument its actual cache misses, original declaration
provenance and checker ownership; distinguish ordinary declarations from
instantiated/synthetic/alias paths. Stable declaration identity alone is not
semantic equivalence. Context/inference/diagnostic effects and cyclic or unresolved
descriptors must remain unclassified. No shared semantic cache is authorized by
this attribution alone, and the 10x objective remains unmet.
