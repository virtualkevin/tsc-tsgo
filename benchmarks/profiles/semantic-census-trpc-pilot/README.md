# tRPC diagnostic census pilot

Six profiled compilations compare the unchanged production baseline with observation disabled/enabled CPU labels, for one and four checkers. This is single-sample diagnostic evidence, not an optimization benchmark. Output and semantic counters match, and joint CPU label references validate against the census.

The record cap overflows substantially; the observer increases runtime and retains pointers. Detailed records are insertion-order bounded, not a representative statistical sample. No duplicated result is established as equivalent or shareable. Larger-workload interpretation is deferred until collection overhead and coverage improve.

`evidence.tar.gz` preserves discovery manifests, stdout/stderr, JSONL census dumps, CPU/allocation profiles and decoded CPU profiles. `summary.json` records commands and integrity checks; `analysis.json` records sampled label coverage. Controllers are included. Profile decoding used the pinned Go1.26.9 `go tool pprof -raw`. All measurements include profiling; wall elapsed additionally includes census serialization and profiler shutdown. Production source was not changed.
