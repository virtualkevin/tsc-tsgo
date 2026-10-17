# TypeData code generation audit

The approved non-PGO candidate was inspected without rebuilding the compiler. All inspection processes are terminal. Exact binary/source/toolchain hashes, commands, small DWARF readers and raw results are in summary.json and the neighboring files. Assembly retains source lines/instructions; trailing display whitespace was removed.

Candidate binary: cae2e8b37bddc0ebd69a6f5b169a4623cddb65342a59ab692445e4a9b85ff20a. Source: 9c86a02c17a5d2c6892ae925667031b33ae16027c1d0338430a46df5a28b97b7. Its build metadata records no PGO and no extra GOFLAGS. Reference is the preserved lazy binary, whose full hashes are recorded; it is an older source revision, so this is a representation/codegen comparison, not an isolated performance experiment.

## Inlining and dispatch

| Type accessor | Candidate DWARF inline sites | Reference inline sites |
| --- | ---: | ---: |
| AsConstrainedType | 2 | 2 |
| AsStructuredType | 13 | 13 |
| AsObjectType | 16 | 16 |
| AsTypeReference | 130 | 130 |
| AsInterfaceType | 60 | 60 |
| AsUnionOrIntersectionType | 196 | 7 |

All six candidate accessors have actual DWARF inline-subroutine instances. No standalone symbol matching any of the six candidate methods remains in `go tool nm`; the filtering command therefore returns the expected no-match status 1. This is not a failed build. The old wrappers also inline: the meaningful difference is that their inlined bodies retain interface dispatch. For example, reference typeResolutionHasProperty loads the interface table/data at offsets 40/48, loads its method pointer, then CALL CX. The candidate instead loads the immutable byte at offset12, tests zero, performs byte subtraction/range comparison, then loads the retained allocation pointer at offset40. Source-tagged snippets are in candidate-selected.asm and reference-selected.asm. The candidate does not need an interface call for this access.

The union/intersection accessor has more recorded inline sites in the candidate, including through Type.Types. Counts reflect emitted static debug information, not invocation frequency, and cannot establish a wall-time improvement.

## Constructors and escape

newType and newObjectType have zero DWARF inline instances in both binaries. newIntrinsicTypeEx has26 in each. Candidate newType's symbol is283 bytes versus345 in the reference, and newObjectType390 versus411. These are symbol sizes, not speed estimates.

Reference newType performs an indirect CALL CX for TypeData.AsType before header initialization. Candidate newType accepts the original allocation directly and initializes its Type prefix without that call or a concrete-type switch. It stores the retained allocation at offset40 and immutable kind at offset12 before tracing. Its tracer branch still contains its own unrelated interface call.

Every one of the eight newObjectType branches still calls runtime.newobject with a concrete type descriptor; the pointer therefore still escapes to the typed heap rather than becoming stack or untyped storage. The merge path passes that allocated pointer and a constant kind to newType. The initialized checker/self pointer writes have runtime.writeBarrier checks and gcWriteBarrier4 on the slow path. No claim of allocation elimination is supported by the generated code.

## Layout and invariant review

DWARF confirms all24 concrete/base shapes plus Type. Type is48 bytes versus56 in the reference. The kind occupies offset12, existing pointer fields retain offsets16/24/32, and the allocation pointer occupies offset40. Every concrete shape's nominal size is eight bytes smaller; every immediate embedded-base field is at offset0. The production compile-time assertions independently check offset0, sufficient size, and matching alignment for all24 edges.

The source conversion always starts from the retained original complete allocation pointer. Exact accessors restore that type; base accessors narrow to an actual smaller zero-offset embedded prefix. Neither accessor reconstructs a larger allocation from the receiver's Type prefix. That matches the local unsafe.Pointer smaller/equivalent-layout rule. Ordinary typed allocation and write barriers remain in machine code. A copied Type header continues retaining and selecting the original allocation, rather than treating the detached copy as a derived object.

The remaining invariant hazard is a fabricated or mismatched private pointer/kind pair, or a future type inserted outside its DFS family range. Construction/layout/accessor tests and review must cover new shapes. Nil/zero Type panic behavior and exact mismatch rejection remain explicit; mismatch panic strings/types differ from the old runtime TypeAssertionError as already documented. Codegen inspection does not replace runtime validation. Nominal byte reductions are not allocator/RSS measurements.

## Existing pointer-store screen

pointer-linkstore-screen/ preserves a separate earlier synthetic experiment in about48KB: summary, raw hit/allocation logs, two benchmark-order sources and isolated prototype. All72 hit samples reported zero allocation and favored the prototype in both ordering screens, but no construction or whole-compiler improvement was measured. These results were not rerun during this audit. Their scope and source/provenance limitations are recorded separately; they do not validate TypeData performance.

## Parent manifest comparison

The older reference revision was additionally checked against the candidate using their complete recorded source manifests. `source-comparison.json` shows that the only non-test file differences are the five production files implementing this Type representation change; the remaining differences are regression tests. Build settings match exactly and neither build uses PGO or extra GOFLAGS. This strengthens attribution of the paired workload comparison, while the static codegen observations themselves still establish no speed or memory gain.
