# Direct member materialization confirmations

The unchanged candidate passed the screen at capture 594c813, archived in commit 49ef6c8. These two independent confirmations follow the original frozen policy in ../direct-member-materialization/COMPARISON_POLICY.md. Each uses 19 TypeORM/tRPC pairs and 11 VS Code/Sentry pairs, with one warmup. The reverse confirmation exchanges raw binary roles and normalizes each pair before calculating summaries. Both must independently pass every gate; no pooling or extra samples.

The recorder is adapted from the node-pointer confirmation with exact binary identities updated. Common provenance checks come from this candidate’s screen, including unchanged declaration transformation and key construction. Reverse configuration reverses source deltas and counts too. Production source remains the retained baseline. No candidate code or build changes are made.

Run `node run-confirm.mjs RESULT_DIRECTORY CONFIG` from the repository root using full profile-relative paths; record with `node record-confirm.mjs RESULT_DIRECTORY CONFIG` before changing the capture HEAD. Do not overlap builds, tests, Git, profiles or other benchmarks with timing.

Candidate rejected: the replacement forward confirmation completed 19 tRPC pairs with a ratio-of-medians below the frozen 0.98 floor. The large stage was interrupted by SIGTERM; no full-suite aggregate is claimed. See ../../results/direct-member-confirm-forward-retry/partial-decision.json for independently verified completed measurements. No reverse run or further rescue samples will be taken. Production remains unchanged.
