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

Both executables inherit the same environment. Repeatable `--unset-env NAME`
removes an inherited setting from all discovery, preflight, warmup and timed
subprocesses, for example `--unset-env TSC_TS_CHECKERS --unset-env TSC_GO_SCHEDULER`.
The mandatory physical-library override `TSC_TS_LIB_DIR` cannot be unset.
JSON records removals and the effective runtime/scheduler settings, including
`TSC_GO_SHARED_GLOBALS` and the native baseline's `TSC_TS_CHECKERS`, `TSC_TS_REGION`,
`TSC_TS_RECYCLE` and `TSC_TS_SIDE_STATE`. Clear experimental baseline controls when
measuring its default policy.

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

New Go builds write `<binary>.provenance.json` after a successful build. The
sidecar records the binary SHA-256, Git revision, source dirty state (including
untracked and ignored source files), a content-hashed local source manifest,
toolchain settings, build options, and an explicit PGO profile hash when used.
Sources and settings are checked before and after building; changes prevent
publication. Arbitrary `GOFLAGS` values are hashed, since linker flags may contain
secrets. Local source hashing includes `cmd`, `internal` (including embedded
libraries), build scripts, and module files. External dependency/toolchain files
and external inputs selected through arbitrary `GOFLAGS` are not content-hashed;
this is build metadata with integrity checks, not a hermetic or signed attestation.

The runner checks each optional sidecar against the actual binary and source
manifest hashes, records `buildProvenance.status: "verified"`, and rejects
sidecar changes during measurement. Historical binaries without sidecars remain
usable with explicit `"absent"` provenance; the measurement checkout's commit
does not identify their build source. When preserving or renaming a binary,
copy its sidecar alongside it as `<new-binary>.provenance.json`. Do not generate
sidecars retroactively from the current checkout for previously built binaries.

Cgroup v2 metadata resolves the process membership using `/proc/self/cgroup` and
`/proc/self/mountinfo`, then records each visible ancestor's CPU quota, memory
limit, configured/effective CPU set, and CPU counters. Minimum quota ratios
include parent limits even when the leaf and mount root say `max`. Missing or
unreadable limits are recorded as unknown, with completeness flags; limits
outside the visible cgroup namespace cannot be inferred. Each timed sample also
records ancestor CPU counters immediately before and after invocation, outside
the timer. These counters include sibling tasks, so throttling changes describe
shared cgroup pressure, not CPU time attributable solely to the compiler.

The old `packages/tsc-ts/scripts/bench.mjs` is a separate scanner/self-check
microbenchmark. Its whole-project loop ignores exit status and does not measure
native tsc-ts, so it must not supply the end-to-end comparison for this project.

The pinned upstream source configurations are available at:

- [VS Code client](https://github.com/microsoft/vscode/blob/51266f6f4a66a9519a8b4974fe60365cd9b49eac/src/tsconfig.json)
- [Sentry frontend](https://github.com/getsentry/sentry/blob/624fb343cb8e0f9c1b852e6860c426fb7804b739/tsconfig.json)
- [TypeORM package](https://github.com/typeorm/typeorm/blob/fe92394287516feeada6e9c308ebe22deca2458e/packages/typeorm/tsconfig.json)
- [tRPC server](https://github.com/trpc/trpc/blob/10e2ef98f7842b94eb3026e4f9bcfe62cc39b088/packages/server/tsconfig.json)

Optional `--measure-rss` requires Linux and GNU `/usr/bin/time`. It wraps both
compilers symmetrically in discovery, preflight, warmups and timed samples,
writing resource metrics to a separate temporary file. Compiler stdout/stderr,
approved diagnostic fingerprints and real binary provenance retain their existing
checks. Reports record the wrapper path, version, SHA-256, normalized invocation
arguments and per-invocation peak RSS in KiB; wrapper hashes are checked before
and after each project. RSS summaries are separate from wall-time summaries.

Wrapped wall times include GNU time startup, waiting and writing its resource
file, and are **not comparable with historical unwrapped timings**. Temporary
file setup, metric parsing and cleanup happen outside the timer for both
compilers. Peak RSS is an OS command maximum, not Go heap size, total allocated
bytes, or an aggregate process-tree/cgroup memory peak. Pair fresh wrapped
baseline and candidate measurements for GC/memory comparisons. The default mode
remains unwrapped.

In RSS mode, timeout, SIGINT/SIGTERM, output overflow and wrapper termination
kill the compiler's Linux process group. This covers the native compilers and
ordinary descendants; processes deliberately creating separate sessions are
outside this cleanup contract. Missing/malformed metrics and mismatched wrapper
exit status fail the run. Test the resource adapter and full mock harness with
`node --test benchmarks/resource-run.test.mjs benchmarks/run.test.mjs`.
