# Prepared inspection, not executed

Wait for parent build37176 terminal and preserved candidate. No main edits or compiler rebuild.

1. Run inspect.py with preserved saturated binary path; compare actual helper symbols/callers against direct baseline61313d4e. Capture keybuilder.go inline instructions in hot caller to avoid losing direct stores. Inspect guards, bounds-check branches, MOVB/MOVL/MOVQ, calls and stack frames.
2. Run exact-source primitive allocation screen (same51cases) with pinned Go; bounded package-only -m=2 for helper eligibility and escape. Verify copied keybuilder source hash against candidate sidecar first.
3. Compare full sidecar source manifests/buildsettings. Preserve binary/profile/source hashes, commands, exact observed assembly and limitations. No compiler workload timings or predicted inlining/speedups.
