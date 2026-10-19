# Paired union/intersection property-cache prototype

Isolated Go overlay on retained production at `7f654d8`; no production application
or performance claim. This is a storage change, not reuse across containing types,
checker instances, names, or augmentation modes. The earlier rejected cache-sharing
experiment remains rejected.

## Mapping and update contract

For each exact containing Type pointer and exact name, an entry holds two symbol
pointers: augmented and non-augmented. They correspond to the old independent map
values. The map remains stored on the type, preserving lookup through another
checker receiver and the existing granularity of mutable ownership. No global or
checker-wide pool, IDs, locks, pointer reconstruction, or additional semantic
queries are introduced. Symbol pointers remain typed GC roots.

A lookup returns the selected nonnil slot. On a miss the existing synthesis runs
in the existing order. A nil result does not add an entry and can be retried after
members change. A nonnil result overwrites the requested slot. A complete
non-augmented result fills the augmented slot only if that slot is still nil.
The pair must be reread after synthesis: recursive work can have published the
other slot, including a distinct augmented winner. No pointer to a map element is
kept across recursive work or map growth.

The old two map-header fields become one map-header field. The pair value grows
from one pointer to two, and one-sided entries pay for an empty slot. Names common
to both namespaces need only one stored key. The cache map is created before
synthesis as before, but separate empty-map allocation states no longer exist.
Neither nominal header savings nor fewer maps proves lower RSS or faster lookup.

## Validation scope

Ten focused tests passed in normal/race/checkptr modes (independent raw-log
readback passed): seven existing
stateful union-cache tests, the existing lazy unmatched-property regression, and
two new ownership/history tests. The original semantic assertions are retained.
Representation-facing test reads decode the appropriate slot; a test-only
snapshot exposes populated entries for the existing length/identity assertions.
Its nil result means no populated entries, not a claim about old empty-map
allocation identity. Recursive winner, late mutation, partial-result isolation,
missing-member retry, distinct type ownership, and same-symbol identity are covered.

Broader units/conformance and CLI validation are running. Remaining requirements:
CLI/API/emit parity, race/checkptr integration, normal production-build provenance,
then the established frozen workload screen and independent confirmations. No
benchmark should start until correctness and build checks pass. The 10× original
native target remains unmet.

## Prepared measurement commands (not executed)

After both correctness controllers complete, run `verify.py` and the guarded
`build-production.py`; the latter builds through the normal repository build and
restores retained production source/default artifacts even after failure. Its
restore checks permit either the frozen original or staged bytes so interruption
partway through applying the overlay is recoverable; unexpected edits are refused.
Then run `prepare-screen.py` to derive the exact five-file delta from provenance.

The Node preflight and runner require the config as argv[3]:

```
node benchmarks/profiles/paired-property-cache/preflight-screen.mjs unused benchmarks/profiles/paired-property-cache/screen.json
node benchmarks/profiles/paired-property-cache/run-screen.mjs benchmarks/results/paired-property-cache-screen benchmarks/profiles/paired-property-cache/screen.json
node benchmarks/profiles/paired-property-cache/record-screen.mjs benchmarks/results/paired-property-cache-screen benchmarks/profiles/paired-property-cache/screen.json
```

Run timing under the existing signal supervisor, logging to
`/tmp/tsc-paired-property-cache-screen-supervisor.jsonl`. No concurrent build,
validation, profiling, or Git activity is permitted during timing. The recorder
checks a complete successful capture; it does not turn a failed gate into acceptance.
`archive-screen.py` archives execution provenance and appends only measured rows to
PERF.md after independent recording. Interrupted captures require separate review
and preservation, not overwriting or blindly restarting the performance experiment.

## Interrupted CLI validation

The first CLI controller completed normal parity (80) and API/emit/project checks
(12), then received SIGTERM during race CLI validation. The signal supervisor
records Codex PID 3841 / UID 1000 as sender; the reason is unknown. The controller
exited 1 with `KeyboardInterrupt('15')`, not a reported test failure. Its original
`final-cli.json`, signal log, and interrupted build/test output are preserved.

`validate-cli-remaining.py` resumes only race/checkptr in new output paths. It
requires unchanged source, HEAD, comparators, normal build and completed prefix.
It rebuilds instrumented binaries with the same flags and writes separately named
archives. `final-cli-resumed.json` includes the unchanged two completed records;
the verifier checks both controller/report hashes and that prefix. No failed or
interrupted report is overwritten or treated as passed.

The resumed controller subsequently completed all 80 race parity cases, then was
also interrupted by SIGTERM during checkptr CLI testing. Its report remains failed
and records the same Codex sender with unknown reason. `interrupted-checkptr/`
preserves that unfinished output. `validate-cli-checkptr.py` runs only checkptr in
fresh paths; `final-cli-completed.json` carries the unchanged three passing records.
The verifier checks the complete chain of original, resumed, and final reports,
controller hashes, and unchanged prefixes. No completed phase is rerun.

## Completed correctness evidence

All ten focused tests passed in normal, race and checkptr modes. Root units passed
21,177 test records; services passed 219. Pinned conformance completed 14,915
configurations: 12,789 fully checked, 8 partially checked with inherited skips,
2,118 unsupported, and zero failures. CLI parity passed 80 cases in each of normal,
race and checkptr modes; API/emit/project integration passed all 12 cases.

`verify.py` independently read and checked the raw archives, counts, source hashes,
and unchanged prefixes through both interrupted reports. `readback.json` records
success. These are executed-path compatibility checks, not a general correctness
proof or a speedup. The guarded normal production build is now running; the
candidate remains unpromoted and no workload timings have been taken.

The normal build completed successfully and exactly matched the validated overlay
binary (`e2eefe22…`). Its source digest is `26786e64…`, with five changed/added files
and 5,155 candidate source files versus 5,154 retained. Build settings match the
retained comparator. Source and default binary/provenance were restored and verified.
The preserved candidate is `packages/tsc-go/dist/tsc-go-paired-property-cache`.
Workload performance remains unmeasured pending the frozen screen.

## Performance decision

The complete screen was independently verified and rejected. Aggregate ratios
0.990758/0.969772 fail 1.01, and several workload floors fail. No confirmations or
promotion. See `DECISION.md` and the preserved raw reports; production remains
unchanged. Four measured rows are recorded in PERF.md.
