# Go compiler

This package is the primary compiler implementation for this fork. It starts from the exact upstream Go revision from which tsc-ts was ported and applies optimizations and compatibility fixes to the maintained Go source. `UPSTREAM.json` records its provenance; `LICENSE` and `NOTICE.txt` retain the upstream licensing information. The canonical Go module path is retained because the compiler uses internal imports.

```sh
npm ci
npm run build
node packages/tsc-go/bin/tsc-go.js --noEmit -p path/to/tsconfig.json
npm test
```

Run these commands from the repository root with Node.js 24+, npm, and Go 1.26 or newer. The root build and test commands target this workspace; `build:go` and `test:go` remain aliases. Set `GO` to a Go executable for the build when it is not on `PATH`; the unit-test command requires `go` on `PATH`. The build embeds the standard library declaration files, so the executable can be moved without sibling data files. `TSC_TS_LIB_DIR` overrides their directory, including in API and language-server modes, matching the tsc-ts test configuration. The local `tsc-go` npm command launches the existing executable and does not build automatically. Windows builds use `dist/tsc-go.exe`. `TSC_GO_PGO` optionally selects a CPU profile for a profile-guided build.

The existing TypeScript implementation remains available as the performance and compatibility baseline. The Go CLI, API server, incremental compiler, watch mode, emitters, and language server come from the pinned upstream source. The original internal Go tests are retained. Tests requiring the upstream TypeScript submodule or baseline fixtures need those fixtures separately; the workspace test command runs the compiler, CLI lifecycle, and watch unit suites that do not require them.

`TSC_GO_SCHEDULER=balanced` enables an experimental checker assignment that balances estimated work using checked source-file lengths. It keeps each file assigned to one checker for the program's lifetime and preserves processing order within each checker. Files skipped by type checking retain their original assignment and do not count toward semantic work. The default remains the upstream round-robin assignment until representative measurements justify a change.

`TSC_GO_SCHEDULER=dependency` adds bounded groups of checked files and their importers to that balancing policy. It uses the program's completed module resolutions, keeps groups on one checker, and preserves the same fixed ownership and processing order. Both alternative schedulers are experiments; see the root `PERF.md` for measured results.

Native watch mode uses the same `TSC_TS_WATCH_MEMORY` policy as tsc-ts: the exact value `0` disables worker replacement; a positive numeric value sets a limit in MiB; otherwise the limit is 2.5 times resident memory after the first build. A worker above that limit is replaced before a relevant rebuild. Ordinary watch retains its last valid configuration after a failed reread and waits for successful configuration recovery before allowing replacement.

## Native reference parity

The focused parity suite compares diagnostics and emitted output from the Go
compiler with the original native TypeScript implementation. From the repository
root, prepare its inputs explicitly:

```sh
npm run fetch:upstream
npm run build
npm run build:reference:native
npm run test:parity
```

The native reference build needs the pinned scriptc toolchain and `clang`.
The parity suite requires the fetched upstream library declarations and both
executables; missing inputs fail the suite. It defaults to
`packages/tsc-ts/dist/tsc` and `packages/tsc-go/dist/tsc-go`. Set `TSC_GO_BASELINE`
and `TSC_GO_CANDIDATE` to select preserved binaries (paths are resolved from the
repository root); on Windows select the candidate's `.exe` path explicitly.
The native reference build overwrites `packages/tsc-ts/dist/tsc`, so preserve any
baseline binary and any provenance sidecar before rebuilding it for a comparison.

This focused suite supplements the local Go tests and the upstream conformance
corpus below. A shared defect in both implementations can pass differential
checks, so native parity alone is not proof of correctness. The root
`test:reference` and `test:all` commands retain the broader original workspace
test workflows; neither replaces the Go corpus command below.

## Upstream conformance fixtures

From the repository root, fetch the pinned checkouts and extend their sparse paths with the reference snapshots and auxiliary declarations used by the Go test runner:

```sh
node scripts/fetch-upstream.mjs
git -C upstream/typescript-go sparse-checkout add testdata
git -C upstream/TypeScript sparse-checkout add tests/baselines/reference tests/lib
mkdir -p packages/tsc-go/_submodules
ln -sfn ../../upstream/typescript-go/testdata packages/tsc-go/testdata
ln -sfn ../../../upstream/TypeScript packages/tsc-go/_submodules/TypeScript
```

These symlinks and generated local test output are ignored by Git. Rerunning `fetch-upstream.mjs` resets the sparse paths, so repeat both `sparse-checkout add` commands afterward. The runner compares results with the pinned snapshots and writes actual output under `upstream/typescript-go/testdata/baselines/local`; it does not accept changed reference snapshots automatically.

Run a focused check, then the broader generic and union subset:

```sh
cd packages/tsc-go
go test ./internal/testrunner -run 'TestSubmodule/(mappedTypes[12]|unionTypePropertyAccessibility|unionTypeIndexSignature|contextualTypeWithUnionTypeMembers|typeArgumentInferenceWithObjectLiteral|typeArgumentInferenceWithConstraints)\.ts' -parallel 4 -timeout 15m
go test ./internal/testrunner -run 'TestSubmodule/(?i)(mappedType|union|intersection|generic|typeArgument|contextualType)' -parallel 4 -timeout 20m
```

Run the complete pinned conformance corpus with:

```sh
go test ./internal/testrunner -run '^TestSubmodule$' -parallel 4 -timeout 30m
```

Do not add `-trimpath` to these test builds: the runner locates fixtures using its source path. The regular compiler build still uses `-trimpath`. Add `-json` to capture individual passes, failures, and skips; unsupported options such as ES5, AMD, and `outFile` are explicitly skipped by the upstream runner and are not passing cases.
