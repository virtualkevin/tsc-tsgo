# End-to-end compiler benchmarks

`workloads.json` pins representative snapshots of the four repositories named in
the supplied tweet. These snapshots and configurations were selected independently:
the screenshots give no commit IDs, commands, dependency versions, hardware,
sample counts, or cache settings. In particular, `trpc` currently means its server
package. Results must not be described as reproducing the tweet's exact experiment.

Fetch and install the smaller projects first:

```sh
node benchmarks/prepare.mjs --projects typeorm,trpc --install
```

The manifest records the exact install commands. pnpm uses the `packageManager`
version in each pinned repository through Corepack. Install scripts are disabled;
native database bindings are unnecessary for typechecking. The manifest's `prepare` command builds Sentry's referenced icons and scraps
declarations using its lockfile-pinned `typescript-7` installation and fetches
VS Code's Electron declarations with its checksum-verified setup script. Setup is
excluded from timed runs. Other generated inputs must also exist before measuring. An unexpected failed compiler invocation is never accepted as a performance result.

Build both native compilers, then run from the repository root:

```sh
TSC_TS_LIB_DIR="$PWD/upstream/typescript-go/internal/bundled/libs" \
  node benchmarks/run.mjs \
  --baseline packages/tsc-ts/dist/tsc \
  --candidate packages/tsc-go/dist/tsc-go \
  --projects typeorm,trpc --runs 7 --warmups 1 \
  --output benchmarks/results/comparison.json
```

TypeORM uses identical `--module node20 --moduleResolution node16` overrides
for both compilers because its original `node10` resolution was removed in TS7.
The package's complete source and test scope is retained.

Both executables get the same project and semantic flags. Optional
`--candidate-checkers N` (an integer from 1 through 256) passes `--checkers N`
only to the Go candidate, preserving the original baseline's scheduling. This
applies consistently to file discovery, preflight, warmup, and timed runs.
JSON records `candidateCheckers` and each project's actual `compilerArgs` and
`fileDiscoveryArgs` arrays for both executables. Without the option both receive
identical flags.

The runner disables emit,
incremental checking, composite mode, and `noCheck`; it preserves the project's
other settings, including `skipLibCheck`. Every invocation starts a fresh process.
Warmup and source discovery leave the filesystem cache warm; these are not cold
disk measurements or persistent compiler-server measurements. Timed runs alternate
execution order and capture all compiler output. Approved preflight exit status, equal input
file sets, equal diagnostics, and stable output on every measured run
are required. Success is the default. A workload with known semantic errors may
explicitly set `expectedExit`, `diagnosticsSha256`, and `diagnosticCount` in its
manifest; these must be reviewed from the original native tsc-ts baseline. The
fingerprint hashes the JSON array `[stdout, stderr]`, replacing the absolute
workload and library paths with `<workload>` and `<typescript-libs>`. Configuration
errors and missing files/dependencies are rejected even if fingerprinted. Such
results must be labeled as checking a workload with diagnostics. Per-project
`args` record identical compatibility overrides for both compilers. The runner forces both compilers to use the same physical declaration libraries
through an absolute `TSC_TS_LIB_DIR` (the pinned upstream libraries by default).
Input paths and content hashes must match, and input contents and executable
hashes are checked again after timing. Unreadable or virtual-only inputs fail.
A broader correctness suite is still
required before claiming compiler equivalence.

JSON results preserve raw times, paired order, medians, ranges, compiler SHA-256s,
configuration and dependency-lock hashes, workload commits, input file hashes,
CPU/OS/Node information, cgroup limits, and relevant compiler environment variables.
The runner rejects changed tracked workload files and mismatched commits. Generated
or installed files are fingerprinted through the compiler's actual input list.
Keep the same installed dependency tree and library version for both executables.
Do not run other CPU-intensive builds or benchmarks at the same time.

The old `packages/tsc-ts/scripts/bench.mjs` is a separate scanner/self-check
microbenchmark. Its whole-project loop ignores exit status and does not measure
native tsc-ts, so it must not supply the end-to-end comparison for this project.

The pinned upstream source configurations are available at:

- [VS Code client](https://github.com/microsoft/vscode/blob/51266f6f4a66a9519a8b4974fe60365cd9b49eac/src/tsconfig.json)
- [Sentry frontend](https://github.com/getsentry/sentry/blob/624fb343cb8e0f9c1b852e6860c426fb7804b739/tsconfig.json)
- [TypeORM package](https://github.com/typeorm/typeorm/blob/fe92394287516feeada6e9c308ebe22deca2458e/packages/typeorm/tsconfig.json)
- [tRPC server](https://github.com/trpc/trpc/blob/10e2ef98f7842b94eb3026e4f9bcfe62cc39b088/packages/server/tsconfig.json)
