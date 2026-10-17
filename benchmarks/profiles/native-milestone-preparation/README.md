# Direct native milestone — preparation only

Prepared during the first indexed-storage confirmation. All four controller syntax checks passed after the quiet timing window closed (see syntax-checks.json). They have not been preflighted or executed; no performance result is implied. Preflight remains gated on both confirmation records and the retained source.

The runner preserves the existing alternating-pair workload harness, GNU time/RSS wrapper, identical physical library and project settings, diagnostic/input gates, frozen binary identities and process cleanup. It uses nine pairs for TypeORM/tRPC and five for VS Code/Sentry, one warmup each, with a 90-minute overall bound and 180-second invocation bound. Default native worker count is not assumed equal to Go.

Two mutually exclusive configurations are prepared. `common-native.mjs` requires the two prescribed indexed-storage confirmation records before choosing indexed or restored saturated Go. It requires the current Go source to match the selected compiler. Do not run both alternatives or use these measurements to rescue a failed storage confirmation.

Original native executable SHA256 is `525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4`. Its historical build sidecar is absent. Current tracked native source is separately pinned (228 files, SHA256 `c8fda9057fe820236882146736f5ecbd28fb84a8875e283dc1fbeaa8a196b1dd`); it has no tracked diff against initial revision d3e96c17c42be94d8cc3b842174376ddc5a558c0. This does not reconstruct historical binary build provenance. The Go compiler retains verified local build metadata; no assertion equates native and Go build settings.

Planned invocation uses original files under `/tmp/tsc-native-milestone/`: `node run-native.mjs NEW_RESULT_DIRECTORY CONFIG_PATH`; postprocess with `node record-native.mjs RESULT_DIRECTORY CONFIG_PATH`. Run only after review, syntax checks, source restoration if required, and successful preflight. Keep source, HEAD, scripts and binaries unchanged through measurement and recording.

Report all four direct native/Go ratios, paired medians, samples and peak RSS. Never multiply prior Go/Go ratios. The observed 10× field is a finite measurement check, not a declaration that the full correctness/performance goal is complete.
