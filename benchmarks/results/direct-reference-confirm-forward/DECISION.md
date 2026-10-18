# Rejected after completed workload-floor failures

Capture aa52ab0. Confirmation session5525 was interrupted bySIGTERM after roughly470seconds. Supervisor identifies PID3841/UID1000/comm codex as the sender; the cause is unknown. Cancellation was forwarded immediately, and the runner reported zero leftover marked processes. This is an incomplete confirmation, not a completed four-workload result.

Before interruption, TypeORM and tRPC each completed all19prespecified pairs. Independent recorder3312 checked unchanged source/binary/controller/input hashes, raw samples, RSS and pair normalization. Both fail both required0.98workload floors:

| Workload | Baseline median ms | Candidate median ms | Ratio of medians | Median paired ratio |
|---|---:|---:|---:|---:|
|TypeORM|2522.315139|2593.608250|0.9725119971|0.9764868861|
|tRPC|499.577639|514.582674|0.9708403805|0.9784708477|

Each confirmation must pass every workload floor. These completed failures are sufficient to reject; no unfinished large-workload result could rescue them. No four-workload aggregate is computed, and no values from the incomplete large report are added to PERF.md. The complete passing screen stays separate. No replacement confirmation, reversed-role confirmation, extra samples, retuning or promotion.

Production source216d40c7 and default binary8fe4bd80 remain unchanged. Preserved candidate25f46474 remains available as experiment evidence. The original-native10×goal is still unmet. This result establishes a failed acceptance gate on these samples, not a universal performance regression or a diagnosis of its cause.

All raw reports are retained, including the incomplete large report. Twelve execution files were copied with hash readback, including supervisor, policy, controllers, config, statistics and interrupted-result recorder. Two completed19pair rows were appended to the table-only PERF.md.
