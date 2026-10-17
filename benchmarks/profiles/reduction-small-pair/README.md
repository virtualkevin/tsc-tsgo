# Bounded small-pair intersection reduction

A distinct candidate after the enlarged-map-value experiment failed screening. For exactly two constituents with a selected skipped side, enumerate the other side once. If it has at most eight properties, snapshot pointers and names, explicitly reject duplicate names, and examine each pair directly. Larger or duplicate-name lists use the original grouping algorithm without repeating enumeration. The bounded uniqueness check does not assume canonical property arrays.

The helper preserves skipped-side lookup before property-type resolution, first/second short-circuit order, same-symbol singleton handling, and property-name snapshots across recursion. It does not change caches, ownership, scheduling or the meaning of intersection reduction.

Normal focused tests pass 128 records across eight top-level tests. New cases compare the frozen original grouping algorithm at widths 0, 1, 2, 8, 9 and 16 across duplicate names, optional tags and conflicting literals, plus shared-symbol singleton non-resolution. Full validation is in progress under the `validate-*.py` controllers.

`codegen.txt` and `baseline-codegen.txt` are pinned Go1.26.9 disassembly. The small helper has no direct allocation calls, and the caller's growslice calls correspond to fallback grouping. Semantic callees can still allocate. The main frame grows from 0x320 (800) to 0x420 (1,056) bytes; the helper has a 0x60 (96) byte frame. This establishes a mechanism and a stack-cost tradeoff, not an end-to-end gain.

The preserved candidate is `packages/tsc-go/dist/tsc-go-reduction-small-pair`; binary/source/sidecar identities and exact two-file delta are in `screen.json` and `build.json`. The frozen policy compares retained node-pointer Go with nine small-workload/five large-workload pairs and requires two independent confirmations plus correctness before retention. No timing has started. The original native-relative 10× goal is not established by a Go/Go screen.

Full validation completed: normal/race/checkptr each pass 128 focused records; root units pass 2,389 records across ten packages; conformance passes 12,789 fully checked and eight partially checked cases, with 2,118 unsupported skips and zero failures; native parity passes 80/80 and actual-Go API/emit/project tests 12/12. The 21 raw evidence files are archived in `validation.tar.gz`, indexed by `validation-archive.json`, with reports in `benchmarks/validation/reduction-small-pair-*.json`.

`restoration.json` verifies production source/default executable are restored to retained node-pointer Go. Candidate code is archived and its binary separately preserved. The screen configuration and preflight verify both artifacts and this restored workspace; this is not promotion.

Screening **failed**: ratio-of-medians aggregate 0.944182 and paired-median aggregate 0.979112 miss 1.01. TypeORM and VS Code also miss the 0.98 workload minimum. RSS passes. The complete result is in `../../results/reduction-small-pair-screen/recording/proposal.json`. No confirmation runs or promotion follow; retained node-pointer Go stays in production. Allocation-call avoidance did not establish an end-to-end benefit.
