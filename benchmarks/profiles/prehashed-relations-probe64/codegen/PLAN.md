# Prepared bounded inspection (not executed)

Wait for parent build99297 terminal and preservation. Baseline: dist/tsc-go-keybuilder-saturated SHA2bdcca53f630535846054eada84cae8afaa32b4faab21de029eca41c79e26303. Future candidate path is supplied to inspect.py only after parent release.

Capture selected relation-cache helpers and three actual semantic callers: Checker.isTypeRelatedTo, Relater.recursiveTypeRelatedTo, Relater.resetMaybeStack. Retain helper assembly, filtered caller excerpts around cache/runtime-map operations, frame prologues, symbol code sizes, exact commands and binary/sidecar/source hashes. Verify source manifest deltas and build settings. No compiler rebuild, giant compiler diagnostics, test, workload or profile.

Questions: do Relation wrappers inline; which new cache boundaries remain calls; is low-bit indexing emitted directly; does full key equality compare both words; how many separate bitmap/key/value memory accesses and bounds branches remain; where do fallback runtime map calls and allocation/growth calls occur; do helper/caller frames grow. Codegen establishes mechanism only, not speed, memory savings or fallback incidence.
