# Initializer and call-resolution CPU budget

Offline attribution of preserved normal-build CPU samples from retained production.
The analyzer checks each original profile and decoded raw-text SHA256, reuses the
existing stack partitioner, and requires exact total CPU agreement with the earlier
property budget. It adds no compiler queries or instrumentation. Recursive frames
count once; exclusive combinations partition all samples. Two focused parser tests
pass for overlapping/recursive frames and rejection of unrecognized locations.

| Workload | Initializer CPU % | Quick-expression CPU % | Call-resolution CPU % | Object-literal CPU % |
|---|---:|---:|---:|---:|
| trpc | 4.061 | 0.508 | 12.183 | 4.569 |
| typeorm | 6.860 | 2.814 | 23.571 | 5.629 |
| vscode | 11.624 | 3.486 | 42.027 | 13.912 |
| sentry | 14.677 | 1.966 | 46.063 | 11.691 |

The categories overlap and include callees; they must not be summed. CPU is not
wall time. GC work without an initializer frame is not attributed to initializers,
and this does not measure marginal allocation or GC savings. Small-workload sample
resolution is coarse. These are historical normal profiles, not a fresh benchmark.

The uncapped variable-branch census establishes that initializers lead that resolver's
instrumented elapsed intervals. This CPU audit places that observation in context:
initializer checking covers 4.061–14.677% of total samples, not most compilation.
An initializer-only shortcut or sharing layer is therefore not an established route
to an order-of-magnitude improvement. No result reuse contract has been proved.

Call resolution has a broader footprint, especially on VS Code and Sentry, but
its inclusive footprint includes expression checking, inference, relations, and
instantiation. The source already caches signatures, preserves a resolving sentinel,
handles reentrant publication, and avoids caching transient flow-loop results.
`checkExpressionCachedEx` also resets flow state when computing a cached result.
A generic expression/signature cache cannot disregard those effects.

Decision: do not implement an origin-keyed initializer cache based on the census.
Use a broad semantic representation change, with explicit identity/ownership and
stateful replay, as the next implementation direction. These profiles neither prove
that representation changes will win nor establish a 10× mechanism. Retained source,
production defaults, and PERF.md are unchanged; no performance candidate is promoted.
