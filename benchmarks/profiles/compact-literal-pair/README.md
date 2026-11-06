# Compact literal-pair candidate

An isolated five-file Go overlay reduces LiteralType from 88 to 80 bytes while Type stays 56 bytes on the current amd64 toolchain. One partner pointer plus private state in header padding replaces the two freshness pointers. Public flags, value, type ID/allocation order and canonical pointer identity remain unchanged by the intended contract. Accessors resolve implicit self through the original TypeData, preserving copied-value behavior. See CONTRACT.md for states and limits.

Candidate and retained representation passed three focused tests each in normal, race and checkptr modes (18 raw outcomes verified by verify-focused.py). Tests cover zero/allocated/linked states, copied exported payloads and headers, interning, counter preservation, repeated GC and layout. source-audit.py reverses the specified substitutions and matches all three original production files exactly. An initial audit-script formatting mismatch is preserved; no candidate code changed to resolve it.

Full units/services/pinned conformance completed (resumed session90584): root21,178 tests across14packages; services219; pinned14,915 cases with12,789fully checked,8partially checked,2,118unsupported skips and0failures. Independent full raw readback1511 passed. The initial full controller21274 rejected an incorrect expected root count despite Go exit0; initial controller/report and exact prior/current test-name delta are preserved. The resumed controller reused verified root evidence, then ran services and conformance.

CLI validation27490 completed: normal80, API/emit/project12, race80 and checkptr80 all pass. Independent complete raw-evidence verifier7067 passed. Normal provenance build50227 passed: binaryd9252a12, source35b57efd,5156source files and exactlyfive source changes. Retained production source/default executable were restored and verified. Duplicate raw logs were removed only after exact gzip readback; raw-compression.json preserves their hashes.

Validation/build ran with HEAD8b1d1fe and fixed overlay sources. All correctness gates required for screening passed. This remains an unpromoted performance candidate; no timing or speedup result exists yet. Benchmark policy and finalized identities are in COMPARISON_POLICY.md and screen.json.

The memory saving may lose to added accessor branches and dispatch. Full correctness gates, normal provenance build, and the existing matched four-workload screening/confirmation policy are required before any promotion. PERF.md remains unchanged until actual compiler workload timing.
