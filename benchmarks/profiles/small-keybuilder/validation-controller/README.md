Prepared only. No tests or compiler builds were launched while preparing this controller. It never edits main, applies patches, builds release binaries, publishes reports, or commits. Previous numeric validation controllers remain unchanged.

After explicit parent release, run from an escalated tool context:

```sh
python3 /tmp/tsc-small-keybuilder-validation/validate.py --output /tmp/small-keybuilder-validation-main --expected-source 4937cfc277515b8b566162d078dd493524d406de94ced593a78f38bbd6c7aa5d
```

Output must be a fresh directory below /tmp. The expected full-source digest is required, never inferred. Reviewed SHA256 values for checker.go, keybuilder.go, keybuilder_test.go, unchanged relater.go and retained relation_keys_api_test.go are also enforced. Numeric relation production/test residue is rejected. Source and HEAD are captured before execution, after every stage, and at termination; any change aborts subsequent stages. Fixture revision identities are checked before and after; fixture-tree bytes are not independently hashed here.

Strictly sequential stages:

1. Normal focused checker tests using `-run '^(TestBuffered|TestRelationKeys)' -count=1`.
2. The same focused tests with `-race`.
3. The same focused tests with `-gcflags=all=-d=checkptr=2`.
4. Root `npm test`, with `GOFLAGS='-json -count=1'` to force all ten package suites uncached.
5. Full pinned `TestSubmodule` conformance, `-parallel 4 -count=1 -timeout 30m`.

Every focused stage requires exactly the nine expected top-level test names and 255 passing test records: nine top-level + 24 lengths × ten chunks + four alias/type cases + two cold-order cases. No focused skips/failures are permitted. Root ten-package terminal statuses must all pass. Conformance records fully checked, partially checked and unsupported source/configuration cases separately; a package-level pass alone is insufficient.

The pinned Go 1.26.9 toolchain is used without trimpath so fixture lookup remains valid. Experimental TSC variables and GC/profile/runtime overrides are cleared by name without recording secret values; explicit validation environment is recorded. Each command writes stdout/stderr, exit status and hashes. `validation.json` contains commands, suite scope, source identities, pins, outcomes and limitations. Stages stop at their first command, parsing, scope, or immutability failure. Children get dedicated process groups with TERM/KILL cleanup on completion, timeout, or SIGINT/SIGTERM. No performance interpretation of these validation durations is valid.

Native parity/API/parallel-emit validation is separately owned by root. The separately preserved production binary is not exercised by this controller; `go test` builds the normal/race/checkptr test binaries from the captured source.
