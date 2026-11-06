# Index-applicability census (isolated diagnostic overlay)

Investigates the Sentry-heavy relation work identified by index-applicability-budget.
No production optimization or semantic cache is introduced. The overlay adds a
checker-local observer to the original isApplicableIndexType entry/return and a
post-checking snapshot export. It preserves the original boolean expression,
query order, and all original semantic calls. When disabled, a nil observer is
checked; this branch/layout cost is measured separately from the enabled observer.

The observer records uncapped aggregate rows by source/target flags and whether
instantiationDepth or activeMappers is nonzero. It tracks the first 131072 distinct
ordered numeric type-ID pairs per checker; known pairs continue to be observed
after the cap, while untracked pair calls are counted as dropped. IDs are existing
construction IDs; no GetSymbolId, new semantic query, or strong type root is added.
The cap biases coverage toward early construction pairs. Counts are not a uniform
sample, source-origin equivalence, or cross-checker sharing estimate.

A repeated pair means a prior completion in that checker. Recursive calls finish
before their outer calls, so this is deliberately completion-history accounting.
ChangedResult compares adjacent completed results for a tracked pair. A stable
boolean is not an effects-equivalence proof. Aggregated instantiation and relation
size deltas include both first and repeated calls; separate repeat-exclusive
fields isolate the measured deltas on completed repeats. Neither measures CPU.
Exclusive deltas subtract directly nested observed calls; inclusive deltas can
overlap. Map-size growth misses replacements, diagnostics, cache transitions,
identity changes and other semantic effects; zero growth is not purity evidence.
ActiveContext is a coarse flag, not a context-complete cache key.

Validation covers nested accounting, cap overflow/continued known-pair tracking,
and original primitive behavior with the observer enabled/disabled, in normal,
race and checkptr builds. The four-workload capture will compare retained binary,
observer-disabled binary and observer-enabled binary on identical pinned inputs,
four checkers, clean diagnostics and sanitized environments. Single invocation
elapsed values give observer-cost context only, not benchmark speedups. No timing
from this diagnostic belongs in PERF.md.

The initial attempted build failed before tests because prepare.py used the same
staged basename for a checker file and a compiler file. failed-staging preserves
that controller, overlay and raw logs. Distinct staged paths correct this tooling
failure; the retained compiler source was never modified.

The next compile caught a named-type mismatch: type IDs use TypeId, not uint32. failed-id-type preserves that failed compile and observer source. The corrected numeric key uses TypeId directly. Repeat-exclusive effect counters were added before the fresh validation run.

Completed: all focused modes, diagnostic build, 12 controls, and independent readback passed. See RESULTS.md for observations, saturation limits, observer timings, and the next storage question. No candidate is promoted.
