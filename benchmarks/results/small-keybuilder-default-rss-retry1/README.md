# Short-key buffering: completed comparison

The full retry completed successfully with all provenance, input, diagnostic, order and sample-summary checks passing. Seven alternating pairs for TypeORM/tRPC and three for VS Code/Sentry, one warmup each, symmetric default settings and GNU time RSS. All samples are preserved.

Results are mixed. TypeORM ratio of medians1.016, paired median1.006 (candidate4/7 wins); tRPC0.963, paired median0.962 (candidate2/7); VS Code0.989, paired median1.035 (candidate2/3); Sentry1.045, paired median1.044 (candidate2/3). The conflicting VS Code summaries and small large-project sample counts limit certainty. Median peak RSS rises7575.5→7827.0MiB on VS Code and falls5411.0→5313.4MiB on Sentry; these are total process peaks, not isolated builder allocations.

This candidate is an experimental intermediate. Its source/codegen evidence identifies helper-call and integer-copy overhead that a separately reviewed direct-write refinement will test. These mixed results do not establish an overall improvement or the10× native goal. Future candidates continue to compare against the preserved PointerLinkStore baseline; this result is not reclassified as a universal win.

The first attempt in ../small-keybuilder-default-rss/ terminated on SIGTERM after four TypeORM pairs. Its sender is unknown; no samples are merged with this full retry. All controller/compiler processes were confirmed terminal before retrying.

The initial postprocessing recorder rejected a fixed expected filename list because renaming numeric→small changed lexical sort order. The corrected recorder sorts both exact lists; no measurement or validation requirement changed. Both recorder versions are archived. The corrected recorder completed successfully. controller-design.md is the historical preparation document; completed reports supersede its pending-launch wording.

Scripts retain /tmp paths/imports; reproduce that layout before reuse. Raw reports retain compiler/build/input provenance. No timing here compares with original native tsc-ts or historical unwrapped measurements.
