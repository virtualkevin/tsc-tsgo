# Go compiler

This package contains the complete Go compiler source at the exact upstream revision from which tsc-ts was ported. It is a maintained source fork, with optimizations applied to Go directly. `UPSTREAM.json` records its provenance; `LICENSE` and `NOTICE.txt` retain the upstream licensing information. The canonical Go module path is retained because the compiler uses internal imports.

```sh
npm run build -w @tsc-ts/go
packages/tsc-go/dist/tsc-go --noEmit -p path/to/tsconfig.json
npm test -w @tsc-ts/go
```

Building requires Go 1.26 or newer. Set `GO` to a Go executable when it is not on `PATH`. The build embeds the standard library declaration files, so the executable can be moved without sibling data files. `TSC_TS_LIB_DIR` overrides their directory, including in API and language-server modes, matching the tsc-ts test configuration. The local `tsc-go` npm command launches this executable after building. `TSC_GO_PGO` optionally selects a CPU profile for a profile-guided build.

The existing TypeScript implementation remains available as the performance and compatibility baseline. The Go CLI, API server, incremental compiler, watch mode, emitters, and language server come from the pinned upstream source. The original internal Go tests are retained. Tests requiring the upstream TypeScript submodule or baseline fixtures need those fixtures separately; the workspace test command runs the compiler unit suites that do not require them.
