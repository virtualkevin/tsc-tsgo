// Fresh-process, paired, end-to-end typechecking benchmark. Node 24+, no dependencies.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { availableParallelism, cpus, platform, release, totalmem } from 'node:os';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

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
    'node benchmarks/run.mjs --baseline PATH --candidate PATH [--projects typeorm,trpc] [--runs 7] [--warmups 1] [--manifest PATH] [--output PATH]',
  );
  process.exit(0);
}
const count = (name, min) => {
  const n = Number(values[name]);
  if (!Number.isSafeInteger(n) || n < min) throw new Error(`--${name} must be an integer >= ${min}`);
  return n;
};
const runs = count('runs', 1),
  warmups = count('warmups', 0),
  timeout = count('timeout', 1);
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
const run = (command, args, cwd = root) => {
  const start = process.hrtime.bigint();
  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    timeout,
    env: compilerEnv,
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
const report = {
  schemaVersion: 1,
  startedAt: new Date().toISOString(),
  status: 'running',
  methodology:
    'Fresh process for every invocation; warmed filesystem cache; alternating baseline/candidate order; no incremental cache; typechecking enabled; timings include process startup and diagnostic output capture. All measured commands must match the approved exit code and diagnostics; nonzero semantic diagnostics require an explicit manifest fingerprint.',
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
    compilerEnvironment: Object.fromEntries(
      ['GOMAXPROCS', 'GOGC', 'GOMEMLIMIT', 'TSC_TS_LIB_DIR', 'NODE_OPTIONS']
        .filter((k) => compilerEnv[k] !== undefined)
        .map((k) => [k, compilerEnv[k]]),
    ),
    cpuMax: existsSync('/sys/fs/cgroup/cpu.max') ? readFileSync('/sys/fs/cgroup/cpu.max', 'utf8').trim() : null,
    memoryMax: existsSync('/sys/fs/cgroup/memory.max')
      ? readFileSync('/sys/fs/cgroup/memory.max', 'utf8').trim()
      : null,
  },
  repositoryCommit: git(root, 'rev-parse', 'HEAD'),
  repositoryDirty: git(root, 'status', '--porcelain', '--untracked-files=no') !== '',
  binaries: Object.fromEntries(Object.entries(binaries).map(([k, path]) => [k, { path, sha256: hashFile(path) }])),
  runs,
  warmups,
  timeoutMs: timeout,
  projects: [],
};
const save = () => writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
try {
  for (const p of projects) {
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
      expectedExit,
      diagnosticCount: p.diagnosticCount ?? 0,
      diagnosticsSha256: p.diagnosticsSha256 ?? null,
      configSha256: hashFile(resolve(cwd, p.project)),
      lockfileSha256: hashFile(resolve(cwd, p.lockfile)),
      preflight: {},
      pairs: [],
      status: 'running',
    };
    report.projects.push(entry);
    save();
    const canonicalFile = (file) => relative(cwd, resolve(cwd, file));
    let expectedFiles, expectedOutput, expectedInputs;
    for (const [name, binary] of Object.entries(binaries)) {
      const files = requireSuccess(run(binary, [...args, '--listFilesOnly'], cwd), `${p.name} ${name} file discovery`);
      const paths = files.stdout.trim().split('\n').filter(Boolean);
      if (!paths.length || files.stderr)
        throw new Error(`${p.name} ${name}: empty source set or file discovery errors`);
      const canonical = paths.map(canonicalFile).sort();
      if (expectedFiles && JSON.stringify(expectedFiles) !== JSON.stringify(canonical))
        throw new Error(`${p.name}: compilers read different file sets`);
      expectedFiles = canonical;
      const check = requireOutcome(run(binary, args, cwd), `${p.name} ${name} preflight`);
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
      };
    }
    const sample = (name) => {
      const result = requireOutcome(run(binaries[name], args, cwd), `${p.name} ${name}`);
      if (outputSignature(result) !== expectedOutput)
        throw new Error(`${p.name} ${name}: output changed during timing`);
      return result.ms;
    };
    for (let i = 0; i < warmups; i++) {
      sample('baseline');
      sample('candidate');
    }
    for (let i = 0; i < runs; i++) {
      const order = i % 2 ? ['candidate', 'baseline'] : ['baseline', 'candidate'];
      const pair = { order };
      for (const name of order) pair[name] = sample(name);
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
    for (const [name, path] of Object.entries(binaries))
      if (hashFile(path) !== report.binaries[name].sha256) throw new Error(`${name}: binary changed during timing`);
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
  save();
  console.error(error.message);
  process.exitCode = 1;
}
