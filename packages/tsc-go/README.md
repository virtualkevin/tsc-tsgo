# Go compiler

This package contains the complete Go compiler source at the exact upstream revision from which tsc-ts was ported. It is a maintained source fork, with optimizations applied to Go directly. `UPSTREAM.json` records its provenance; `LICENSE` and `NOTICE.txt` retain the upstream licensing information. The canonical Go module path is retained because the compiler uses internal imports.

```sh
npm run build -w @tsc-ts/go
packages/tsc-go/dist/tsc-go --noEmit -p path/to/tsconfig.json
npm test -w @tsc-ts/go
```

Building requires Go 1.26 or newer. Set `GO` to a Go executable when it is not on `PATH`. The build embeds the standard library declaration files, so the executable can be moved without sibling data files. `TSC_TS_LIB_DIR` overrides their directory, including in API and language-server modes, matching the tsc-ts test configuration. The local `tsc-go` npm command launches this executable after building. `TSC_GO_PGO` optionally selects a CPU profile for a profile-guided build.

The existing TypeScript implementation remains available as the performance and compatibility baseline. The Go CLI, API server, incremental compiler, watch mode, emitters, and language server come from the pinned upstream source. The original internal Go tests are retained. Tests requiring the upstream TypeScript submodule or baseline fixtures need those fixtures separately; the workspace test command runs the compiler unit suites that do not require them.

`TSC_GO_SCHEDULER=balanced` enables an experimental checker assignment that balances estimated work using checked source-file lengths. It keeps each file assigned to one checker for the program's lifetime and preserves processing order within each checker. Files skipped by type checking retain their original assignment and do not count toward semantic work. The default remains the upstream round-robin assignment until representative measurements justify a change.

`TSC_GO_SCHEDULER=dependency` adds bounded groups of checked files and their importers to that balancing policy. It uses the program's completed module resolutions, keeps groups on one checker, and preserves the same fixed ownership and processing order. Both alternative schedulers are experiments; see the root `PERF.md` for measured results.

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

Do not add `-trimpath` to these test builds: the runner locates fixtures using its source path. The regular compiler build still uses `-trimpath`. Add `-json` to capture individual passes, failures, and skips; unsupported options such as ES5, AMD, and `outFile` are explicitly skipped by the upstream runner and are not passing cases.
