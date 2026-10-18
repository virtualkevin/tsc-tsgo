// Fresh-process, paired, end-to-end typechecking benchmark. Node 24+, no dependencies.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { availableParallelism, cpus, platform, release, totalmem } from 'node:os';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { inspectResourceWrapper, assertResourceWrapperUnchanged, runWithResources } from './resource-run.mjs';
import { readCgroupCpuStats, readCgroupV2 } from './cgroup.mjs';
import { readBuildProvenance } from '../scripts/build-provenance.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
// Both native builds support the same physical declaration-library override.
const libraryDirectory = resolve(
  process.env.TSC_TS_LIB_DIR ?? resolve(root, 'upstream/typescript-go/internal/bundled/libs'),
);
const compilerEnv = { ...process.env, TSC_TS_LIB_DIR: libraryDirectory };
const { values } = parseArgs({
  options: {
    baseline: { type: 'string' },
    candidate: { type: 'string' },
    'measure-rss': { type: 'boolean', default: false },
    'candidate-checkers': { type: 'string' },
    'candidate-env': { type: 'string', multiple: true },
    'unset-env': { type: 'string', multiple: true },
    manifest: { type: 'string', default: 'benchmarks/workloads.json' },
    projects: { type: 'string' },
    runs: { type: 'string', default: '7' },
    warmups: { type: 'string', default: '1' },
    timeout: { type: 'string', default: '600000' },
    output: { type: 'string', default: 'benchmarks/results/latest.json' },
    help: { type: 'boolean' },
  },
});
if (values.help) {
  console.log(
    'node benchmarks/run.mjs --baseline PATH --candidate PATH [--candidate-checkers N] [--candidate-env NAME=VALUE] [--measure-rss] [--unset-env NAME] [--projects typeorm,trpc] [--runs 7] [--warmups 1] [--manifest PATH] [--output PATH]',
  );
  process.exit(0);
}
const unsetEnvironment = [...new Set(values['unset-env'] ?? [])];
for (const name of unsetEnvironment) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) || name === 'TSC_TS_LIB_DIR')
    throw new Error('--unset-env requires an environment name other than mandatory TSC_TS_LIB_DIR');
  delete compilerEnv[name];
}
// Only runtime/scheduler controls may differ; semantic inputs (including the
// declaration libraries) remain shared. Apply overrides after shared removals.
const candidateEnvironmentOverrides = {};
const candidateEnvironmentNames = new Set([
  'GOGC',
  'GOMEMLIMIT',
  'GOMAXPROCS',
  'GODEBUG',
  'TSC_GO_SCHEDULER',
  'TSC_GO_SHARED_GLOBALS',
]);
for (const assignment of values['candidate-env'] ?? []) {
  const separator = assignment.indexOf('=');
  const name = assignment.slice(0, separator);
  if (separator < 1 || !candidateEnvironmentNames.has(name))
    throw new Error(
      '--candidate-env requires NAME=VALUE for an allowed runtime/scheduler control; TSC_TS_LIB_DIR and other input controls are forbidden',
    );
  if (Object.hasOwn(candidateEnvironmentOverrides, name))
    throw new Error(`--candidate-env repeats ${name}; supply each control once`);
  candidateEnvironmentOverrides[name] = assignment.slice(separator + 1);
}
const compilerEnvironments = {
  baseline: compilerEnv,
  candidate: { ...compilerEnv, ...candidateEnvironmentOverrides },
};
const count = (name, min) => {
  const n = Number(values[name]);
  if (!Number.isSafeInteger(n) || n < min) throw new Error(`--${name} must be an integer >= ${min}`);
  return n;
};
const runs = count('runs', 1),
  warmups = count('warmups', 0),
  timeout = count('timeout', 1);
const candidateCheckers = values['candidate-checkers'] === undefined ? null : Number(values['candidate-checkers']);
if (
  candidateCheckers !== null &&
  (!/^\d+$/.test(values['candidate-checkers']) ||
    !Number.isSafeInteger(candidateCheckers) ||
    candidateCheckers < 1 ||
    candidateCheckers > 256)
)
  throw new Error('--candidate-checkers must be an integer from 1 to 256');
if (!values.baseline || !values.candidate) throw new Error('--baseline and --candidate executable paths are required');
const binaries = { baseline: resolve(values.baseline), candidate: resolve(values.candidate) };
const manifestPath = resolve(root, values.manifest);
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
if (manifest.schemaVersion !== 1) throw new Error('Unsupported manifest schema');
const selected = values.projects?.split(',');
const projects = manifest.projects.filter((p) => !selected || selected.includes(p.name));
if (!projects.length || selected?.some((name) => !projects.some((p) => p.name === name)))
  throw new Error('Unknown or empty project selection');
const output = resolve(root, values.output);
mkdirSync(dirname(output), { recursive: true });
const hash = (data) => createHash('sha256').update(data).digest('hex');
const hashFile = (path) => hash(readFileSync(path));
const run = (command, args, cwd = root, env = compilerEnv) => {
  const start = process.hrtime.bigint();
  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    timeout,
    env,
    maxBuffer: 128 * 1024 * 1024,
  });
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  if (result.error || result.signal) throw new Error(`${command} failed: ${result.error?.message ?? result.signal}`);
  return {
    status: result.status,
    stdout: result.stdout.replaceAll('\r\n', '\n'),
    stderr: result.stderr.replaceAll('\r\n', '\n'),
    ms,
  };
};
let resourceWrapper;
// Select the comparison side explicitly: both sides may use the same executable.
const runCompiler = (name, args, cwd) =>
  resourceWrapper
    ? runWithResources(resourceWrapper, binaries[name], args, { cwd, env: compilerEnvironments[name], timeout })
    : run(binaries[name], args, cwd, compilerEnvironments[name]);
const requireSuccess = (result, label) => {
  if (result.status !== 0)
    throw new Error(`${label} exited ${result.status}; no timing accepted.\n${result.stdout}\n${result.stderr}`);
  return result;
};
const git = (cwd, ...args) => requireSuccess(run('git', args, cwd), 'git').stdout.trim();
const median = (ns) => {
  const a = [...ns].sort((a, b) => a - b),
    m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};
const summarize = (ns) => ({ medianMs: median(ns), minMs: Math.min(...ns), maxMs: Math.max(...ns), samplesMs: ns });
const cgroupV2 = readCgroupV2();
const recordedCompilerEnvironment = (env) =>
  Object.fromEntries(
    [
      'GOMAXPROCS',
      'GOGC',
      'GOMEMLIMIT',
      'GODEBUG',
      'TSC_GO_SCHEDULER',
      'TSC_GO_SHARED_GLOBALS',
      'TSC_TS_LIB_DIR',
      'TSC_TS_CHECKERS',
      'TSC_TS_CHECKERS_TRACE',
      'TSC_TS_REGION',
      'TSC_TS_RECYCLE',
      'TSC_TS_SIDE_STATE',
      'TSC_TS_ID_ORDER',
      'TSC_TS_TIMELINE',
      'TSC_TS_SMAPS',
      'NODE_OPTIONS',
    ]
      .filter((k) => env[k] !== undefined)
      .map((k) => [k, env[k]]),
  );
const report = {
  schemaVersion: 1,
  startedAt: new Date().toISOString(),
  status: 'running',
  methodology:
    'Fresh process for every invocation; warmed filesystem cache; alternating baseline/candidate order; no incremental cache; typechecking enabled; timings include process startup and diagnostic output capture. All measured commands must match the approved exit code and diagnostics; nonzero semantic diagnostics require an explicit manifest fingerprint.',
  resourceMeasurement: { enabled: values['measure-rss'], timingComparableToUnwrapped: !values['measure-rss'] },
  manifestSha256: hashFile(manifestPath),
  provenance: manifest.provenance,
  environment: {
    platform: platform(),
    release: release(),
    arch: process.arch,
    node: process.version,
    cpu: cpus()[0]?.model,
    logicalCpus: cpus().length,
    availableParallelism: availableParallelism(),
    totalMemoryBytes: totalmem(),
    // Legacy field is the common environment after shared removals.
    compilerEnvironment: recordedCompilerEnvironment(compilerEnv),
    compilerEnvironments: Object.fromEntries(
      Object.entries(compilerEnvironments).map(([name, env]) => [name, recordedCompilerEnvironment(env)]),
    ),
    candidateEnvironmentOverrides,
    unsetEnvironment,
    cgroupV2,
  },
  repositoryCommit: git(root, 'rev-parse', 'HEAD'),
  repositoryDirty: git(root, 'status', '--porcelain', '--untracked-files=all') !== '',
  binaries: Object.fromEntries(
    Object.entries(binaries).map(([k, path]) => {
      const sha256 = hashFile(path);
      return [k, { path, sha256, buildProvenance: readBuildProvenance(path, sha256) }];
    }),
  ),
  runs,
  warmups,
  candidateCheckers,
  timeoutMs: timeout,
  projects: [],
};
const save = () => writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
try {
  if (values['measure-rss']) {
    resourceWrapper = inspectResourceWrapper('/usr/bin/time', compilerEnv);
    report.resourceMeasurement.wrapper = resourceWrapper;
    report.methodology +=
      ' GNU time wraps both compilers for discovery, preflight, warmups and samples. Wrapped wall times include wrapper launch/wait and resource-file output and are not comparable to historical unwrapped timings. Temporary-directory setup, resource parsing and cleanup are outside the timer; RSS is recorded separately from diagnostic output.';
  }
  for (const p of projects) {
    if (resourceWrapper) assertResourceWrapperUnchanged(resourceWrapper);
    const cwd = resolve(root, p.directory);
    if (!/^[a-f0-9]{40}$/.test(p.commit)) throw new Error(`${p.name}: full pinned commit required`);
    if (git(cwd, 'rev-parse', 'HEAD') !== p.commit) throw new Error(`${p.name}: checkout does not match pinned commit`);
    if (git(cwd, 'status', '--porcelain', '--untracked-files=no'))
      throw new Error(`${p.name}: tracked workload files are modified`);
    // Force a full typecheck even when the repository enables incremental/noCheck.
    const args = [
      '-p',
      p.project,
      ...(p.args ?? []),
      '--noEmit',
      '--incremental',
      'false',
      '--composite',
      'false',
      '--noCheck',
      'false',
      '--pretty',
      'false',
    ];
    // Checker count changes candidate scheduling only. Keep the original baseline
    // scheduling and every semantic option unchanged.
    const compilerArgs = {
      baseline: args,
      candidate: candidateCheckers === null ? [...args] : [...args, '--checkers', String(candidateCheckers)],
    };
    const fileDiscoveryArgs = Object.fromEntries(
      Object.entries(compilerArgs).map(([name, compilerArgs]) => [name, [...compilerArgs, '--listFilesOnly']]),
    );
    const expectedExit = p.expectedExit ?? 0;
    if (
      expectedExit !== 0 &&
      (!/^[a-f0-9]{64}$/.test(p.diagnosticsSha256 ?? '') ||
        !Number.isSafeInteger(p.diagnosticCount) ||
        p.diagnosticCount < 1)
    )
      throw new Error(
        `${p.name}: nonzero exit requires an explicitly approved native-baseline diagnostics SHA-256 and positive diagnosticCount`,
      );
    const outputSignature = (result) => JSON.stringify([result.stdout, result.stderr]);
    const diagnosticSignature = (result) =>
      outputSignature(result).replaceAll(cwd, '<workload>').replaceAll(libraryDirectory, '<typescript-libs>');
    const requireOutcome = (result, label) => {
      const codes = [...(result.stdout + '\n' + result.stderr).matchAll(/error TS(\d+):/g)].map((m) => Number(m[1]));
      // Missing inputs/dependencies and invalid options must never be timed as useful work.
      const setupError = codes.find(
        (code) => (code >= 5000 && code < 6000) || [2307, 2688, 6053, 6054, 6305, 7016, 18002, 18003].includes(code),
      );
      if (setupError)
        throw new Error(
          `${label}: setup diagnostic TS${setupError}; no timing accepted.\n${result.stdout}\n${result.stderr}`,
        );
      const signature = hash(diagnosticSignature(result));
      if (
        result.status !== expectedExit ||
        (expectedExit !== 0 && (signature !== p.diagnosticsSha256 || codes.length !== p.diagnosticCount))
      )
        throw new Error(
          `${label} exited ${result.status}; no timing accepted. Observed diagnosticsSha256=${signature}, diagnosticCount=${codes.length}.\n${result.stdout}\n${result.stderr}`,
        );
      return result;
    };
    const entry = {
      name: p.name,
      commit: p.commit,
      scope: p.scope,
      cwd,
      args,
      compilerArgs,
      fileDiscoveryArgs,
      expectedExit,
      diagnosticCount: p.diagnosticCount ?? 0,
      diagnosticsSha256: p.diagnosticsSha256 ?? null,
      configSha256: hashFile(resolve(cwd, p.project)),
      lockfileSha256: hashFile(resolve(cwd, p.lockfile)),
      preflight: {},
      pairs: [],
      status: 'running',
    };
    if (resourceWrapper) {
      entry.execution = Object.fromEntries(
        Object.entries(binaries).map(([name, binary]) => [
          name,
          {
            executable: resourceWrapper.path,
            arguments: [
              '--quiet',
              '--output',
              '<unique-resource-output>',
              '--format',
              resourceWrapper.format,
              '--',
              binary,
              ...compilerArgs[name],
            ],
            fileDiscoveryArguments: [
              '--quiet',
              '--output',
              '<unique-resource-output>',
              '--format',
              resourceWrapper.format,
              '--',
              binary,
              ...fileDiscoveryArgs[name],
            ],
            resourceOutputPlaceholder: 'A unique temporary file per invocation; excluded from measured setup time.',
          },
        ]),
      );
      entry.warmupResources = [];
    }
    report.projects.push(entry);
    save();
    const canonicalFile = (file) => relative(cwd, resolve(cwd, file));
    let expectedFiles, expectedOutput, expectedInputs;
    for (const name of Object.keys(binaries)) {
      const files = requireSuccess(
        await runCompiler(name, fileDiscoveryArgs[name], cwd),
        `${p.name} ${name} file discovery`,
      );
      const paths = files.stdout.trim().split('\n').filter(Boolean);
      if (!paths.length || files.stderr)
        throw new Error(`${p.name} ${name}: empty source set or file discovery errors`);
      const canonical = paths.map(canonicalFile).sort();
      if (expectedFiles && JSON.stringify(expectedFiles) !== JSON.stringify(canonical))
        throw new Error(`${p.name}: compilers read different file sets`);
      expectedFiles = canonical;
      const check = requireOutcome(await runCompiler(name, compilerArgs[name], cwd), `${p.name} ${name} preflight`);
      const signature = outputSignature(check);
      if (expectedOutput !== undefined && expectedOutput !== signature)
        throw new Error(`${p.name}: compiler diagnostics differ`);
      expectedOutput = signature;
      const inputs = paths
        .map((file) => ({ file: canonicalFile(file), sha256: hashFile(resolve(cwd, file)) }))
        .sort((a, b) => a.file.localeCompare(b.file));
      if (expectedInputs && JSON.stringify(expectedInputs) !== JSON.stringify(inputs))
        throw new Error(`${p.name}: compiler input contents differ`);
      expectedInputs = inputs;
      entry.preflight[name] = {
        fileCount: paths.length,
        fileListSha256: hash(JSON.stringify(canonical)),
        outputSha256: hash(signature),
        status: check.status,
        inputs,
        ...(resourceWrapper ? { resources: { discovery: files.resources, check: check.resources } } : {}),
      };
    }
    const sample = async (name, cpuCounters) => {
      if (cpuCounters) cpuCounters.before = readCgroupCpuStats(cgroupV2);
      const result = await runCompiler(name, compilerArgs[name], cwd);
      if (cpuCounters) cpuCounters.after = readCgroupCpuStats(cgroupV2);
      requireOutcome(result, `${p.name} ${name}`);
      if (outputSignature(result) !== expectedOutput)
        throw new Error(`${p.name} ${name}: output changed during timing`);
      return result;
    };
    for (let i = 0; i < warmups; i++) {
      const baseline = await sample('baseline');
      const candidate = await sample('candidate');
      if (resourceWrapper) entry.warmupResources.push({ baseline: baseline.resources, candidate: candidate.resources });
    }
    for (let i = 0; i < runs; i++) {
      const order = i % 2 ? ['candidate', 'baseline'] : ['baseline', 'candidate'];
      const pair = { order, cgroupCpu: {} };
      if (resourceWrapper) pair.resources = {};
      for (const name of order) {
        pair.cgroupCpu[name] = {};
        const result = await sample(name, pair.cgroupCpu[name]);
        pair[name] = result.ms;
        if (resourceWrapper) pair.resources[name] = result.resources;
      }
      entry.pairs.push(pair);
      save();
    }
    if (
      hashFile(resolve(cwd, p.project)) !== entry.configSha256 ||
      hashFile(resolve(cwd, p.lockfile)) !== entry.lockfileSha256
    )
      throw new Error(`${p.name}: configuration or lockfile changed during timing`);
    if (git(cwd, 'rev-parse', 'HEAD') !== p.commit || git(cwd, 'status', '--porcelain', '--untracked-files=no'))
      throw new Error(`${p.name}: workload checkout changed during timing`);
    for (const input of expectedInputs)
      if (hashFile(resolve(cwd, input.file)) !== input.sha256)
        throw new Error(`${p.name}: input changed during timing: ${input.file}`);
    for (const [name, path] of Object.entries(binaries)) {
      if (hashFile(path) !== report.binaries[name].sha256) throw new Error(`${name}: binary changed during timing`);
      if (
        JSON.stringify(readBuildProvenance(path, report.binaries[name].sha256)) !==
        JSON.stringify(report.binaries[name].buildProvenance)
      )
        throw new Error(`${name}: binary build provenance changed during timing`);
    }
    if (resourceWrapper) {
      assertResourceWrapperUnchanged(resourceWrapper);
      entry.resourceWrapperVerifiedAfter = true;
      entry.resources = Object.fromEntries(
        Object.keys(binaries).map((name) => {
          const samplesKiB = entry.pairs.map((pair) => pair.resources[name].peakRssKiB);
          return [
            name,
            {
              peakRssKiB: {
                median: median(samplesKiB),
                min: Math.min(...samplesKiB),
                max: Math.max(...samplesKiB),
                samples: samplesKiB,
              },
            },
          ];
        }),
      );
    }
    entry.baseline = summarize(entry.pairs.map((p) => p.baseline));
    entry.candidate = summarize(entry.pairs.map((p) => p.candidate));
    entry.speedup = entry.baseline.medianMs / entry.candidate.medianMs;
    entry.status = 'passed';
    save();
    console.log(
      `${p.name}: ${entry.baseline.medianMs.toFixed(2)} ms -> ${entry.candidate.medianMs.toFixed(2)} ms (${entry.speedup.toFixed(3)}x)`,
    );
  }
  report.status = 'passed';
  report.completedAt = new Date().toISOString();
  save();
  console.log(`Results: ${output}`);
} catch (error) {
  report.status = 'failed';
  report.error = error.message;
  if (resourceWrapper) {
    try {
      assertResourceWrapperUnchanged(resourceWrapper);
      report.resourceMeasurement.wrapperVerifiedAfterFailure = true;
    } catch (integrityError) {
      report.resourceMeasurement.wrapperVerifiedAfterFailure = false;
      report.error += `; ${integrityError.message}`;
    }
  }
  save();
  console.error(report.error);
  process.exitCode = 1;
}
