# Mapper pair allocation experiment

Retained normal-flag profiles attribute 589,829 sampled allocation objects to appendTypeMapping and 458,756 to prependTypeMapping on Sentry (4.52% of 23,225,216 total). VS Code estimates are 16,384 and 49,152 (0.38% of 17,402,575). These are cumulative sampled allocation estimates, not exact counts, live heap, CPU removal budgets, or runtime predictions. Raw profile hashes match the prior retained-profile audit. Source-correct pprof commands, line decodes, caller decodes and source hash are retained here.

When the existing mapper is nonnil, each operation constructs a simple mapper and a merged mapper. The candidate coallocates those two existing concrete representations in one typed Go object. It preserves interface dispatch, concrete type assertions, mapper order/comparison, callbacks, and distinct published identities. It adds no shared cache, unsafe pointer conversion, pool, or reset. Nil mapper paths are unchanged.

The total payload is unchanged; one allocation replaces two. An independently escaped child now retains the whole pair, potentially retaining the sibling graph longer. This requires RSS and full compiler correctness validation. This is not the earlier unrelated-object slab experiment: the two objects already form an ownership edge when created.

All three focused tests and full compiler correctness validation passed; see the sibling mapper-pair directory for raw evidence and restoration proof. Performance remains unverified. Production source and default executable have been restored to the retained baseline.
