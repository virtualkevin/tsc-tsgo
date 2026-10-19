# Symbol resolution diagnostic census

Isolated overlay on retained production, not the rejected property-view candidate.
The nine existing resolver paths record hits at their existing resolvedType check.
Misses record declaration origin, checker ownership, context depth/active-mapper
count, completion/cache state, elapsed intervals and instantiation counter deltas.
The original resolver body and queries retain their order. No compiler IDs or
additional semantic queries are requested by the observer.

Origins serialize the full ordered declaration location list and symbol name/flags,
not just a hash. Missing/cyclic/unrooted declaration ancestry is explicitly marked
unresolved, with bounded traversal. Descriptors are diagnostic grouping keys only:
mapper identity, inference generation, diagnostics, flow context and semantic result
equivalence are NOT established. Matching declarations across checkers does not
justify sharing Type objects or skipping work. Unresolved groups must never be
counted as equivalent computations.

Nested observed resolver intervals and instantiation deltas are subtracted from
parents' exclusive values. Time is instrumented elapsed wall time, not sampled CPU
or a savings forecast. Observer overhead perturbs it; unobserved nested work stays
inside the enclosing interval. uint32 instantiation subtraction follows the existing
counter width and cannot distinguish an entire wrap within one observed call.
Origin records cap at 100,000 per checker, with dropped miss events reported.
All event totals still include dropped records. Maps retain strings and scalar
records, not semantic result pointers. The frame stack is checker-local and is
read only after checking under existing pool locks.

Scope: ordinary one-shot CLI compilation with built-in checker pool. Build/watch
modes are not instrumented by the export hook. The observer is opt-in through
TSC_GO_SYMBOL_RESOLUTION_CENSUS; snapshots must use a new path. No performance
candidate or PERF row may be produced from this instrumented binary.

Focused validation passed three tests in each normal/race/checkptr mode; raw
logs were independently read back. Two count-validator and three analyzer tests
passed. All 24 workload controls passed: baseline/disabled/enabled at one/four
checkers, with exact pinned input hashes and clean diagnostic output. The original
capture was interrupted by SIGTERM after 13 controls; its failed report and logs
remain intact. Only the 11 unfinished controls were resumed under identical pins.
Both supervisor logs are retained. Sender was process codex; cause unknown.

Independent verification checked source/binary/controller pins, unchanged completed
prefix, all 24 outputs, counters, and eight deterministic gzip archives against raw
hashes and bytes. Capture HEAD f49f9c0; production source remained 216d40c7.

| Workload | Misses, one checker | Misses, four checkers | Recorded-origin coverage, one | Recorded-origin coverage, four |
| --- | ---: | ---: | ---: | ---: |
| typeorm | 137,355 | 198,484 | 100.00% | 100.00% |
| trpc | 27,535 | 42,671 | 100.00% | 100.00% |
| vscode | 2,284,046 | 3,055,256 | 34.70% | 45.33% |
| sentry | 1,205,042 | 1,996,474 | 59.89% | 77.90% |

Instantiated symbols lead miss counts; ordinary variable/property resolution also
has substantial counts and recorded elapsed work. Repeated instantiated origins
omit mapper equivalence and cannot support sharing. Origin cap losses on both
large workloads are substantial; the retained first-seen records are not random
samples, so do not extrapolate their cost or repetition percentages.

Next investigate ordinary variable/property misses and classify contextual typing,
flow, annotations and diagnostic effects before any shared-fact design. This census
is a diagnostic lead, not proof of equivalent completed computations, a CPU saving,
or a speedup. No PERF entries or production changes result from this experiment.
