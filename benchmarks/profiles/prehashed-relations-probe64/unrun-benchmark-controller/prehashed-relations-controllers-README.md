# Prehashed relation validation and A/B: prepared, final identities verified

Separate controllers/common/recorder under /tmp. No compiler, test, workload or measurement has been launched. No repository files or prior controllers were modified. Syntax checks passed. Final preserved binary/source/sidecar hashes are explicitly pinned and read-only common capture verification passed. Execution still requires parent release.

Native validation, only after final identities and source freeze:

```sh
node /tmp/run-prehashed-relations-native.mjs /tmp/prehashed-relations-native-validation
```

A new /tmp output directory is required. It verifies the candidate against explicit hashes, complete source capture and three-file delta against saturated; verifies original native and pinned-Go oracle hashes; requires exactly one scriptc platform package; clears SHOW_FAILURES and runtime/experimental overrides; runs80 differential parity tests and12 actual-Go API/emit/project integrations sequentially. Zero skips/failures/cancelled/todo permitted. Full source/HEAD, binary/sidecar/comparator identities must remain unchanged. Commands, logs, numeric exits/counts and provenance are written only under /tmp. Output limit, timeout and signal handling terminate the detached test process group. Root owns any eventual report preservation in the repository.

A/B, only after all validation is terminal and root releases a quiet window:

```sh
node /tmp/run-prehashed-relations-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/prehashed-relations-default-rss
```

Fresh results directory only. Baseline is preserved saturated-keybuilder binary2bdcca53f630535846054eada84cae8afaa32b4faab21de029eca41c79e26303, source78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337, sidecarc398c606655dcc0a59c8f0167014380bbf77a836866ef1bad81422516d08de8d. This is NOT the older pointer baseline. Candidate is packages/tsc-go/dist/tsc-go-prehashed-relations, binary4b7a58bac052c7c474bde440fa43bd5866aa4cfd57284c78d3fe88e6b5a6e838, sourcef5e6e4418b084a529efbf62506a0639bedfe3b555816ade86c06c5a3f0fb54d4, sidecar488a3476e97301565e6d1402dee7973d08bfcfae58d720091d2555c892be11a5; buildbasec7ceb93131606b0b0809118a7e111de00856cdd8 dirty.

The full source-manifest difference must be exactly relater.go modified, relation_results.go added, relation_results_test.go added; strengthened patch96999bd26b5a9443bb5e1546f13fb94a19dbb91a7015b5e20d27dbdbeaa7d60e hashes are pinned. Saturated key generation and original declaration transformer remain identical. Expected source count5155 versus5153 baseline. Full build settings must match normal Go1.26.9 linux/amd64 v1 CGO1 -trimpath without PGO/extra flags.

Same default GC, default/unset round-robin scheduling and default checker count, no asymmetric overrides, symmetric GNU-time RSS. Seven alternating pairs each TypeORM/tRPC, three each VSCode/Sentry, one warmup each. Dynamic launchHEAD pinned throughout. Existing exact args/env/input/diagnostic/exit/order/resource/median/provenance gates and bounded process cleanup remain. Ratio>1 favors prehashed candidate. This isolates storage integration+new cache, with unchanged128-bit keys and key construction. No performance benefit is assumed; monolithic growth/fallback can increase peak RSS.

After completed A/B:

```sh
node /tmp/record-prehashed-relations-ab.mjs /home/dev/tssss/tsc-tsgo/benchmarks/results/prehashed-relations-default-rss /tmp/prehashed-relations-ab-proposal
```

Recorder writes only four proposed PERF rows, NOTES entry and proposal.json below a fresh /tmp directory. Both expected/actual controller filename lists are sorted. It distinguishes build provenance/captureHEAD, uses saturated baseline labels, and rejects duplicate documentation markers.

Direct Go/Go comparison, not the native target or proof of10×. GNU-time-wrapped timing cannot compare with historical unwrapped measurements. RSS is command peak, not heap or aggregate tree. Correctness requires separately completed Go/race/checkptr/conformance/native gates. Build provenance does not independently hash external module-cache/toolchain contents. Timed diagnostics are enforced by the hashed runner rather than stored raw per sample.
