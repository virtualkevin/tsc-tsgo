# Project-wide inline call-cost experiment

Candidate: unchanged retained source 216d40c7, pinned Go1.26.9, with the explicit
build argument `-gcflags=github.com/microsoft/typescript-go/...=-l=4`. Standard
library/runtime packages keep normal compiler settings; runtime GC/checker/thread
settings remain default. This is a build-policy experiment, not the rejected
classic collector or profile-guided optimization experiment.

Pinned compiler source cmd/compile/internal/inline/inl.go defines the normal
extra call cost as 57 and selects cost 1 when LowerL is 4. This changes inlining
heuristics, not source-language operations intentionally. It may expose helper
chains to further optimization, but code growth, register pressure, compilation
cost and instruction-cache effects may offset any benefit. No speedup is assumed.

The isolated build preserves normal provenance and requires the complete source
digest and all recorded build settings to match retained Go after removing only
the explicit project-package gcflags argument. The default executable is never
overwritten. Selected compiler implementation files and the Go executable are
hashed; this is not a hermetic or formally verified toolchain claim.

Next inspect actual generated code and binary size against retained Go before
proceeding to correctness validation and a frozen workload comparison. No
microbenchmark or build duration belongs in PERF.md. The native-relative 10×
goal remains unmet.

## Build and bounded code-generation evidence

The build passed at cd866b0: binary861bb976, sidecar80b2cddf, retained source
216d40c7. Default executable and sidecar remained unchanged. Actual executable
file size increased from38,952,698 to43,949,926 bytes (+12.829%). This includes
metadata/debug information and is not a text-section or resident-memory measure.

Selected getTypeOfInstantiatedSymbol instruction bytes increased180→309, with
PointerLinkStore.Get calls replaced by slot/insertAt calls and lookup logic in
the caller. getTypeOfSymbol increased246→683; instantiateType remained66 bytes.
The four selected PointerLinkStore.slot instantiations remained218 bytes each.
Get and newType no longer occur among the selected emitted symbols; absence alone
does not prove every call inlines. Do not compare summed selected bytes as total
code-size reduction when the selected symbol sets differ.

The first disassembly parser truncated generic names at spaces. Its script,
failure record and raw archive are preserved; the corrected parser reads through
the (SB) delimiter and reused the retained assembly. Independent reproduction
matched both complete selected disassemblies and verified the caller transition.

This is enough mechanism evidence to proceed to full correctness and a fixed
workload screen, not enough to claim a speedup. Code growth could offset reduced
call overhead. No production default change or PERF row at this checkpoint.

## Validation flag contract

Validation uses the candidate's project-package -l=4 and -trimpath settings.
For checkptr, the command first sets all=-d=checkptr=2, then sets the project
pattern to BOTH -l=4 and -d=checkptr=2. Pinned cmd/go/internal/load/flag.go
selects the last matching rule; it does not merge those rule values. Race builds
likewise retain the project -l=4 rule. This keeps instrumentation from silently
replacing the policy being tested. Full and CLI controllers record commands;
the independent verifier checks exact per-mode compiler flags.

The fixed benchmark policy keeps nine small/five large pairs plus one warmup,
normal runtime settings and RSS gates. Two independent confirmations are required
only after a passing screen. No timing before all correctness gates/readback.

The first root-suite invocation failed because -trimpath is unsupported by the
source-fixture test harness (internal/repo/paths.go explicitly panics; bundled
TestingLibPath uses runtime.Caller). The failed controller/report/logs are
preserved. Remaining root/services/conformance tests omit -trimpath, as in prior
validation, while retaining the exact candidate -l=4 policy. All 30 successful
lifetime results are reused, not rerun. Production and CLI builds keep -trimpath.
No failed test result is counted as passing; the full root phase must pass anew.

All validation gates passed: 30 lifetime cases across normal/race/checkptr,
21,175 root tests, 219 services tests, and 14,915 pinned conformance configurations
(12,789 fully checked, 8 partially checked, 2,118 unsupported, zero failures).
Normal, race, and checkptr CLI runs each passed all 80 cases; API/emit passed 12.
Independent raw archive readback passed. The preserved initial trimpath setup
failure is excluded from these passing counts. The fixed screen is prepared;
no workload speedup has yet been measured for this candidate.
