# Indexed lookup versus handle-only control

Completed third frozen screening comparison: both binaries have identical allocation handles and symbol layout, while ValueSymbolLinks uses PointerLinkStore in the reference and sparse indexed storage in the candidate. This measures the combined storage/lookup/growth change; it does not isolate one machine instruction or prove a causal explanation for timing variation.

The9/5-pair screen passes all integrity checks, with every sample retained. Ratio-of-medians results are1.041/0.979/1.015/1.028; paired medians1.015/0.992/1.015/1.037 for TypeORM/tRPC/VSCode/Sentry. Aggregate geometric means1.0153/1.0145 are modest and tRPC is slower in this run. RSS ratios stay within the frozen5%guard. Complete samples, both declared summaries and all memory numbers are in recording/proposal.json and the raw group reports.

This is attribution evidence. indexedVsUnchangedQualifiesForConfirmation is null because this comparison is not the adoption reference. Its generic per-workload threshold fails on tRPC, but it does not replace the separate unchanged-baseline qualification established by the frozen policy. Do not multiply these ratios with the handle-only results or subtract A/A variation. Promotion still requires both independent confirmations against unchanged Go, followed by direct native target accounting.

Executed controllers/configuration and the recorder are preserved with original paths and hashes. No candidate code or runtime settings changed during the run. No subagents were used.
