# Rejected sparse filter: code-generation audit

Pinned Go1.26.9 objdump of retained8fe4bd80 and rejected4ce3c7ed. Raw assembly, exact commands, tool/binary/output hashes and a reproducer are included. Run `python3 benchmarks/profiles/sparse-filter-codegen/reproduce.py`.

| propertiesRelatedTo | Retained | Rejected filter |
|---|---:|---:|
| Entry stack reservation, bytes | 368 | 440 |
| Encoded instruction bytes | 6318 | 6734 |
| Disassembled instruction rows | 1312 | 1399 |

The candidate's32-byte filter is zeroed at relater.go:4280 by two MOVUPS before the target-size comparison at relater.go:4278 (CMPQ $0x100). The frame reservation applies at function entry, including identity/tuple paths that never use the filter. These are static facts, not executed-instruction counts, CPU attribution, total-stack measurements, or proof that code layout caused the failed tRPC result.

This supports a distinct execution-structure experiment: put the unchanged wide-target filtered loop into a helper dispatched only for target property counts≥256, preserving the ordinary loop and avoiding local filter storage in the common caller. Keep the filter hash/size/eligibility and target order/rebuild behavior unchanged. Verify generated caller frame and initialization before timing; a new candidate must independently pass the same correctness and frozen screen/confirmation gates. Do not pool results with the rejected screen or reinterpret its outcome.
