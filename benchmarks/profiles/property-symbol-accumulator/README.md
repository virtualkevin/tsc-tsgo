# Append-only property symbol accumulator

Isolated overlay on retained source at `fe0b6cb`. Reuses the existing checker
orderedSet implementation in createUnionOrIntersectionProperty. It is distinct
from the rejected paired-cache layout and from the earlier small-pair intersection
reduction algorithm. No property-result cache or compiler lifetime is changed.

The local set only adds exact symbol pointers, then reads their insertion order.
It is not exposed to synthesis callbacks. The general collections.OrderedSet stores
both an ordered key slice and a map for every populated set. The checker orderedSet
already uses linear membership for up to 16 values and creates a map above that
threshold. This prototype uses that existing threshold without tuning it.

Every formerly unconditional Add of an arbitrary symbol now checks contains first;
the initial singleProp is inserted only into an empty accumulator. Thus duplicates
remain excluded by pointer identity and first-occurrence order is preserved. Both
the semantic-query loop and hasCommonDeclaration consume the ordered slice after
collection is complete. Common-declaration intersection logic and all semantic
query sites remain unchanged. No fixed stack buffer or wider eligibility rule is
introduced. Larger-set membership remains hash-based after promotion.

The new integration fixture checks observed type-mapper query order with repeated
exact symbols and widths 1, 2, 3, 16, 17 and 32, plus cached identity across the two
augmentation modes. It runs against both retained and candidate source alongside
all seven existing stateful union-cache tests, normally and with race/checkptr.
All six focused runs passed (baseline and candidate, each normal/race/checkptr;
eight tests per run). Full correctness and normal build provenance must
precede the established workload screen; no timing or speedup is claimed.

This tests a limited allocation mechanism within a broader optimization goal. It
is not an established path to 10×. Whole-graph compact handles remain unimplemented:
a checker-owned table would need a credible lifetime model that does not keep all
temporary types alive merely because persistent graph edges use numeric handles.

Full overlay validation passed: 21,176 root test records, 219 services records,
and 14,915 conformance configurations (12,789 fully checked, 8 partially checked,
2,118 unsupported/skipped, zero failures). Normal CLI parity passed 80 tests and
API/emit integration passed 12. An external SIGTERM interrupted the first race
CLI run; the original report and raw logs are retained. The resumed run preserves
the successful prefix and identical source/comparator hashes; all 80 race CLI
checks passed. All 80 checkptr CLI tests also passed; the resumed process completed successfully. These are tested domains, not a
whole-compiler equivalence proof or performance evidence.

Independent raw-evidence readback passed. The standard production build generated
binary `d463cf16ee13654ced8ab6f8c23d5f5e09609ae5b2f6117d007d55c9e16c9371`,
source `fe85ceeeecd9525e78a89e2309d456476cd87f83029ec72d7d65b4f247bc8e0d`,
and provenance sidecar `f8e562075d1f26d82ffeaeeb4f06e01009e2675b0668b04b301ffd2450fb3986`.
The binary matches the tested normal overlay build. Only checker.go and the new
query-order test differ from retained source. Retained source, default binary,
and default sidecar were restored and verified. The workload screen is pending.
