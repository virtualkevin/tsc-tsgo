Prepared only; no Go commands have been run. Apply reviewed relation patch through parent first, freeze main, then obtain explicit parent release and source digest.

Run from escalated tool context after release:

```
python3 /tmp/tsc-numeric-relation-validation/validate.py --output /tmp/numeric-relation-validation-main --expected-source PARENT_SUPPLIED_COMPLETE_SHA256
```

Output directory must be fresh and beneath /tmp. Controller checks production representation and test presence, verifies both pinned upstream revisions, captures complete source manifest, and aborts before tests if its digest does not equal the explicit supplied digest. No default digest is baked in. Test errors abort subsequent stages; all child numeric exits/stdout+stderr hashes are recorded. Finally captures source again. Never edits main or applies a patch.

Sequence: focused normal, then race/checkptr concurrently (max2 children), then root npm10packages/full pinned TestSubmodule concurrently (max2 children). Existing focused test scope is7top-level tests/9passrecords including2cold-direction subtests, expected1checkerpackage. Rootalias verifies10package terminal records. Full conformance reports unsupported and partially checked cases separately.

After manual review of successful captures/results, publish compact reports outside captured source:

```
python3 /tmp/tsc-numeric-relation-validation/publish.py --output /tmp/numeric-relation-validation-main
```

Publisher produces benchmarks/validation/numeric-relation-focused.json and numeric-relation-conformance.json. Exact commands/environment/logs/pins/scope in controller report. No race validation of simultaneous unsynchronized interner writes, no proof of exact recursive reentry count, no actual overflow-generation coverage, and no speed claim are implied by the focused tests.
