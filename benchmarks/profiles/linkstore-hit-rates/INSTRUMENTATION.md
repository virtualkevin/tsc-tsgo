Exploratory instrumentation draft; no shared source edits, builds, or tests.

Apply separately from the cache patch. Set TSC_GO_LINKSTORE_PROFILE to an absolute output prefix; each process writes PREFIX.PID.json for one compiler command. It counts each store instance by Key/Value concrete types and registration ID; IDs are not stable across runs because checker startup may interleave. Aggregate by valueType to compare LinkStore families.

Predicted Get cache-hit ratio = lastInsertedMatches/getCalls. Also record lastInsertedMatches/mapHits to distinguish misses from older existing entries. Expected invariants at normal command completion: lastInsertedMatches <= mapHits <= getCalls; insertions == newCalls + getCalls - mapHits. Empty/unaccessed stores do not register.

The actual map lookup remains in place; no cache shortcut changes semantic results. Counters use atomics so published existing-entry reads do not race with one another; original map insertions still require the existing exclusivity. Last-insert key state is only written where the original map already mutated. Current production does not copy initialized stores; a read-only copy would intentionally share the profile pointer and thus aggregate counters, which should be documented if any caller is introduced.

runMain defers output until the CLI, API, or LSP command returns. All production cmd/tsgo os.Exit paths route through an explicit flush wrapper, including worker restart, parent-death watchdog and fatal filesystem errors; sync.Once prevents duplicate flushes. SIGKILL cannot flush, and abrupt signal termination can lose the final sample. Separate PID paths avoid supervisor/worker clobber. No finalizer or periodic sampling is installed.

This build adds atomics, reflection during registration, a global registry and extra fields. It is unsuitable for timing or allocation comparisons. Do not interpret its wall time as the cache experiment's performance. After measuring hit rate, remove this patch and build the isolated actual cache patch for benchmark comparison.
