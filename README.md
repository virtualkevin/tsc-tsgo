# TypeScript compiler in Go

This fork develops a Go compiler from the pinned TypeScript-Go ancestor of
Vercel's tsc-ts. The maintained implementation is in
[`packages/tsc-go`](packages/tsc-go/README.md); the original TypeScript
implementation remains available as a native performance and compatibility
reference.

## Build and use

Install Node.js 24+, npm, and Go 1.26 or newer, then run from the repository root:

```sh
npm ci
npm run build
node packages/tsc-go/bin/tsc-go.js --noEmit -p path/to/tsconfig.json
npm test
```

`npm run build` produces `packages/tsc-go/dist/tsc-go` (`tsc-go.exe` on Windows)
and a build provenance sidecar. The binary embeds its standard library
declarations and can run directly without Node or sibling data files. The Node
launcher above selects the platform executable; it requires a completed build.
Set `GO` to select a Go executable for building, or put Go on `PATH`. The test
command requires `go` on `PATH` and runs the local Go unit suites.

The Go workspace is private and has no published npm package. Installing the
upstream `tsc-ts` npm package installs the TypeScript reference implementation.
Existing workspace names and package identities are retained in this fork.

## Development commands

| Command                                           | Purpose                                                                                                                                             |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm run build` / `npm run build:go`              | Build the Go compiler.                                                                                                                              |
| `npm test` / `npm run test:go`                    | Run local Go unit suites without upstream conformance fixtures.                                                                                     |
| `npm run test:parity`                             | Compare prepared Go and native TypeScript binaries on focused fixtures; see the [prerequisites](packages/tsc-go/README.md#native-reference-parity). |
| `npm run build:reference`                         | Build the original TypeScript compiler for Node.                                                                                                    |
| `npm run build:reference:native`                  | Build the original TypeScript compiler with scriptc.                                                                                                |
| `npm run test:reference`                          | Run the original TypeScript workspace test task through Turbo.                                                                                      |
| `npm run build:all` / `npm run test:all`          | Run the previous root Turbo tasks across workspaces, including the reference implementation.                                                        |
| `npm run fetch:upstream` / `npm run build:oracle` | Fetch pinned upstream inputs / build the independent Go oracle executables.                                                                         |
| `npm run bench:projects -- --help`                | Show reproducible project benchmark options.                                                                                                        |
| `npm run dev:web` / `npm run build:web`           | Serve / build the retained tsc-ts documentation site.                                                                                               |
| `npm run lint` / `npm run format:check`           | Run the existing JavaScript/TypeScript lint and formatting tools.                                                                                   |

Reference and all-workspace testing need the pinned upstream inputs and oracle
builds. Native reference builds additionally require a scriptc host with `clang`
available for linking; the repository pins scriptc and `@scriptc/threads` to
`0.3.5`. These are not prerequisites for building the Go executable directly
with the Go toolchain. See the [reference package documentation](packages/tsc-ts/README.md)
for its packaging and API instructions.

## Validation and performance

The 10× speedup is an optimization target, not an achieved result. Measurements
are recorded in [`PERF.md`](PERF.md); [`benchmarks/README.md`](benchmarks/README.md)
describes the pinned workloads, commands, and comparison methodology. The
workloads cover tRPC, TypeORM, VS Code, and Sentry; their checked-in revisions and
local measurements should not be treated as a reproduction of the tweet's
unspecified environment.

Local Go tests, focused native parity checks, and upstream conformance tests
provide different coverage. `npm test` does not run all of them. Follow the
[Go package instructions](packages/tsc-go/README.md) to provision and run the
conformance corpus; unsupported upstream test options remain explicit skips.
Recorded results and limitations are in [`benchmarks/validation`](benchmarks/validation).
Passing the available suites is not a claim of complete TypeScript compatibility.
GitHub workflows are disabled for this fork; validation runs locally.

## Repository layout

| Path                                 | Role                                                              |
| ------------------------------------ | ----------------------------------------------------------------- |
| [`packages/tsc-go`](packages/tsc-go) | Primary Go compiler, CLI, API server, language server, and tests. |
| [`packages/tsc-ts`](packages/tsc-ts) | Original TypeScript implementation and reference tests.           |
| [`packages/tsgo`](packages/tsgo)     | Independent pinned upstream oracle builds and stage drivers.      |
| [`benchmarks`](benchmarks)           | Reproducible measurements, profiles, and validation evidence.     |
| [`apps/web`](apps/web/README.md)     | Retained guides for the original tsc-ts implementation.           |

## License

[Apache-2.0](LICENSE). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
and the Go package's `LICENSE`, `NOTICE.txt`, and `UPSTREAM.json` for source
provenance and third-party notices.
