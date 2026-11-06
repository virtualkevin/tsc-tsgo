# Contextual JSX request census (diagnostic overlay)

Follows call-resolution-partition's23.463% Sentry sampled-CPU attribution to JSX
applicability/inference delegation. This observer is not an optimization, shared
semantic cache or performance candidate. Production remains unchanged.

The checkExpressionWithContextualType entry wrapper activates only when its input
is JsxAttributes. It performs no extra semantic query or lazy NodeID assignment;
all existing statements and return behavior remain. Contextual type ID and flags
are read directly. All requests enter aggregate rows by requested check mode,
contextual flags, inference-context presence and a coarse active-instantiation
indicator. The caller's mode is recorded before the helper adds contextual and
inferential bits. Direct fragment construction bypassing this helper is excluded.

Per checker, the first131072distinct(node pointer, contextual TypeID, nil-context
bit, inference-context pointer, check mode) requests receive completed-history
tracking. Known keys continue after the cap; later unknown requests are dropped
from history but remain in aggregate rows. Dropped counts and saturation are
explicit. This is biased early-request coverage, not a random/population estimate.
Keys deliberately retain AST and inference graphs during the diagnostic run;
results retain only TypeIDs. No memory or speed inference may use these captures.

Repeat means prior completed call, including inner-before-outer recursive
completion. A changed result means a different checker-local TypeID or nil state,
not a proved semantic difference. Matching keys/results do not prove equivalence:
inference contexts are mutable, and flow, diagnostics, constraints, mapper state,
and other caches are not fully represented. Do not implement a node-only cache.

Counters measure instantiations/types/symbols and net assignable+subtype relation
size growth. Child observed JSX intervals are subtracted for exclusive values;
other nested work remains included. Modulo uint32 deltas cannot detect a full
counter wrap inside a call. Net relation growth omits replacements and other
relations/caches. Inference-site lengths and flag changes are recorded at the
wrapper boundary; the original helper clears some inference sites before return.
These limited observations do not establish absence of semantic effects.
Instrumented elapsed time is neither CPU time nor a compiler speed benchmark.

The CLI exports after ordinary compilation under existing checker-pool locks,
without constructing checkers, querying types or forcing GC. Tracing is rejected;
output creation is exclusive. A source audit removes observer additions and
reproduces the two original production files. Its first inverse-hook attempt left
one extra blank line and failed; that script/error are preserved, and the corrected
audit passes without changing observer code. This is not a noninterference proof.

Four focused tests cover nested completion/counter partition, key separation/cap,
flag and relation effects/exclusive output, and a real JSX checker query/diagnostic
history compared with observer disabled. Normal/race/checkptr validation passed all four tests per mode. The isolated
diagnostic build passed (binary4e0f0c63), and focused raw logs/source identities
were independently read back. Five Python accounting/cohort-analysis tests pass.
All12baseline/disabled/enabled controls passed with exact pinned inputs and empty
diagnostic output. Independent raw-evidence verification and exact cohort-analysis
reproduction passed. See RESULTS.md for the measured repetition/effect counts. Source/HEAD remain fixed until runs complete.
No PERF row or10×claim. No subagents.
