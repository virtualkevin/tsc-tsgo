# Superseded before performance testing

Focused normal/race/checkptr, root/services, pinned conformance and normal CLI/API
checks passed. A separate stateful audit then demonstrated a metadata snapshot
difference: presence lookup materializes the old symbol and captures nameType,
whereas this view version captured it only at the later type query. The reference
history passed and the view history failed. See snapshot-audit/decision.json and
its preserved raw output. This is a component counterexample; it does not claim a
known end-user program currently triggers the source-link mutation.

Remaining CLI validation was intentionally terminated after confirmation. Its
KeyboardInterrupt report is preserved, not presented as a test pass. No workload
timing, standard production build or promotion was performed. Production remains
unchanged. Corrected source is isolated in property-relation-view-snapshot and
requires fresh validation. Earlier passing suites cannot validate that new source.
