import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { publishBuildProvenance } from '../scripts/build-provenance.mjs';

const runner = resolve(dirname(fileURLToPath(import.meta.url)), 'run.mjs');
function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'compiler-bench-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const git = (...args) => {
    const r = spawnSync('git', args, { cwd: dir, encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
    return r.stdout.trim();
  };
  writeFileSync(join(dir, 'tsconfig.json'), '{}');
  writeFileSync(join(dir, 'package-lock.json'), '{}');
  writeFileSync(join(dir, 'input.ts'), 'export const x = 1;');
  git('init', '-q');
  git('add', '.');
  git('-c', 'user.name=Benchmark Test', '-c', 'user.email=benchmark@example.invalid', 'commit', '-qm', 'fixture');
  writeFileSync(
    join(dir, 'manifest.json'),
    JSON.stringify({
      schemaVersion: 1,
      projects: [
        {
          name: 'fixture',
          directory: dir,
          commit: git('rev-parse', 'HEAD'),
          project: 'tsconfig.json',
          lockfile: 'package-lock.json',
        },
      ],
    }),
  );
  const compiler = (name, code) => {
    const path = join(dir, name);
    writeFileSync(path, `#!${process.execPath}\n${code}\n`);
    chmodSync(path, 0o755);
    return path;
  };
  const baseline = compiler(
    'baseline',
    "if(process.argv.includes('--listFilesOnly'))console.log(process.cwd()+'/input.ts');",
  );
  return {
    dir,
    compiler,
    run(candidate, extra = [], env = process.env) {
      const output = join(dir, 'result.json');
      const r = spawnSync(
        process.execPath,
        [
          runner,
          '--manifest',
          join(dir, 'manifest.json'),
          '--baseline',
          baseline,
          '--candidate',
          candidate,
          '--runs',
          '2',
          '--warmups',
          '0',
          '--output',
          output,
          ...extra,
        ],
        { encoding: 'utf8', env },
      );
      assert.equal(r.error, undefined);
      let report;
      try {
        report = JSON.parse(readFileSync(output, 'utf8'));
      } catch {
        throw new Error(r.stderr || r.stdout || 'No report');
      }
      return { ...r, report };
    },
    baseline,
  };
}
test('records paired successful samples and provenance', (t) => {
  const f = fixture(t),
    r = f.run(f.baseline);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.report.status, 'passed');
  assert.equal(r.report.projects[0].pairs.length, 2);
  assert.deepEqual(r.report.projects[0].pairs[1].order, ['candidate', 'baseline']);
  assert.equal(r.report.projects[0].preflight.baseline.fileCount, 1);
  assert.match(r.report.projects[0].preflight.baseline.inputs[0].sha256, /^[a-f0-9]{64}$/);
  assert.equal(r.report.candidateCheckers, null);
  assert.deepEqual(r.report.environment.candidateEnvironmentOverrides, {});
  assert.deepEqual(r.report.environment.compilerEnvironments.baseline, r.report.environment.compilerEnvironment);
  assert.deepEqual(r.report.environment.compilerEnvironments.candidate, r.report.environment.compilerEnvironment);
  assert.equal(r.report.binaries.baseline.buildProvenance.status, 'absent');
  assert.deepEqual(r.report.projects[0].compilerArgs.baseline, r.report.projects[0].compilerArgs.candidate);
});
test('records verified build provenance and rejects a sidecar changed during measurement', (t) => {
  const f = fixture(t);
  const source = {
    revision: 'a'.repeat(40),
    dirty: true,
    files: [],
    sha256: createHash('sha256').update('[]').digest('hex'),
  };
  const build = { toolchain: { GOVERSION: 'fixture' }, arguments: ['fixture'] };
  publishBuildProvenance(f.baseline, source, build);
  const passed = f.run(f.baseline);
  assert.equal(passed.status, 0, passed.stderr);
  assert.equal(passed.report.binaries.candidate.buildProvenance.status, 'verified');
  assert.equal(passed.report.binaries.candidate.buildProvenance.metadata.source.dirty, true);
  const candidate = f.compiler(
    'changing-provenance',
    `
    const fs = process.getBuiltinModule('fs');
    if (process.argv.includes('--listFilesOnly')) console.log(process.cwd()+'/input.ts');
    else fs.appendFileSync(process.argv[1]+'.provenance.json', ' ');
  `,
  );
  publishBuildProvenance(candidate, source, build);
  const rejected = f.run(candidate);
  assert.equal(rejected.status, 1);
  assert.match(rejected.stderr, /binary build provenance changed during timing/);
});
test('candidate checker count is recorded and used only for every candidate invocation', (t) => {
  const f = fixture(t);
  const code = (name) => `
    const fs = process.getBuiltinModule('fs');
    const args = process.argv.slice(2);
    fs.appendFileSync(${JSON.stringify(join(f.dir, 'invocations.jsonl'))}, JSON.stringify({name:${JSON.stringify(name)},args})+'\\n');
    if (args.includes('--listFilesOnly')) console.log(process.cwd()+'/input.ts');
  `;
  f.compiler('baseline', code('baseline'));
  const candidate = f.compiler('candidate', code('candidate'));
  const r = f.run(candidate, ['--candidate-checkers', '3', '--warmups', '1']);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.report.candidateCheckers, 3);
  const entry = r.report.projects[0];
  assert.deepEqual(entry.compilerArgs.baseline, entry.args);
  assert.deepEqual(entry.compilerArgs.candidate, [...entry.args, '--checkers', '3']);
  const calls = readFileSync(join(f.dir, 'invocations.jsonl'), 'utf8')
    .trim()
    .split('\n')
    .map((line) => JSON.parse(line));
  for (const name of ['baseline', 'candidate']) {
    const ownCalls = calls.filter((call) => call.name === name);
    assert.equal(ownCalls.length, 5); // file discovery, preflight, warmup, two timed runs
    assert.deepEqual(ownCalls[0].args, entry.fileDiscoveryArgs[name]);
    assert.deepEqual(entry.fileDiscoveryArgs[name], [...entry.compilerArgs[name], '--listFilesOnly']);
    for (const call of ownCalls.slice(1)) assert.deepEqual(call.args, entry.compilerArgs[name]);
  }
});
test('rejects candidate checker counts outside integer range 1..256 before running compilers', () => {
  for (const value of ['0', '257', '-1', '1.5', 'NaN', '1e2', '']) {
    const r = spawnSync(process.execPath, [runner, `--candidate-checkers=${value}`], { encoding: 'utf8' });
    assert.equal(r.status, 1);
    assert.match(r.stderr, /--candidate-checkers must be an integer from 1 to 256/);
  }
});
test('removes inherited scheduler controls consistently from every compiler invocation', (t) => {
  const f = fixture(t);
  const code = `
    if ('TSC_TS_CHECKERS' in process.env || 'TSC_GO_SCHEDULER' in process.env) process.exit(99);
    if (process.env.TSC_GO_SHARED_GLOBALS !== '1') process.exit(98);
    if (!process.env.TSC_TS_LIB_DIR) process.exit(97);
    if (process.argv.includes('--listFilesOnly')) console.log(process.cwd()+'/input.ts');
  `;
  f.compiler('baseline', code);
  const candidate = f.compiler('candidate', code);
  const r = f.run(candidate, ['--unset-env', 'TSC_TS_CHECKERS', '--unset-env', 'TSC_GO_SCHEDULER', '--warmups', '1'], {
    ...process.env,
    TSC_TS_CHECKERS: 'fixed',
    TSC_GO_SCHEDULER: 'dependency',
    TSC_GO_SHARED_GLOBALS: '1',
  });
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.report.environment.compilerEnvironment.TSC_TS_CHECKERS, undefined);
  assert.equal(r.report.environment.compilerEnvironment.TSC_GO_SCHEDULER, undefined);
  assert.equal(r.report.environment.compilerEnvironment.TSC_GO_SHARED_GLOBALS, '1');
  assert.deepEqual(r.report.environment.unsetEnvironment, ['TSC_TS_CHECKERS', 'TSC_GO_SCHEDULER']);
});
test('rejects compiler errors instead of timing a fast failure', (t) => {
  const f = fixture(t),
    bad = f.compiler('bad', 'console.error("missing dependency");process.exit(2);');
  const r = f.run(bad);
  assert.equal(r.status, 1);
  assert.equal(r.report.status, 'failed');
  assert.match(r.stderr, /exited 2/);
  assert.equal(r.report.projects[0].pairs.length, 0);
});
test('rejects a no-op compiler and mismatched diagnostic output', (t) => {
  const f = fixture(t);
  assert.match(f.run(f.compiler('noop', '')).stderr, /empty source set/);
  const bad = f.compiler(
    'different',
    "if(process.argv.includes('--listFilesOnly'))console.log(process.cwd()+'/input.ts');else console.log('ignored error');",
  );
  assert.match(f.run(bad).stderr, /diagnostics differ/);
});
test('rejects mismatched file sets and tracked workload edits', (t) => {
  const f = fixture(t);
  assert.match(
    f.run(f.compiler('wrong-file', "console.log(process.cwd()+'/other.ts');")).stderr,
    /different file sets/,
  );
  writeFileSync(join(f.dir, 'input.ts'), 'export const x = 2;');
  assert.match(f.run(f.baseline).stderr, /tracked workload files are modified/);
});
test('only accepts explicitly fingerprinted semantic diagnostics, never setup failures', (t) => {
  const f = fixture(t);
  const diagnostic = 'input.ts(1,1): error TS2322: Type number is not assignable to string.\n';
  const compilerCode = `if(process.argv.includes('--listFilesOnly'))console.log(process.cwd()+'/input.ts');else{process.stdout.write(${JSON.stringify(diagnostic)});process.exit(1);}`;
  f.compiler('baseline', compilerCode);
  const path = join(f.dir, 'manifest.json');
  const manifest = JSON.parse(readFileSync(path, 'utf8'));
  manifest.projects[0].expectedExit = 1;
  writeFileSync(path, JSON.stringify(manifest));
  assert.match(f.run(f.baseline).stderr, /explicitly approved/);
  manifest.projects[0].diagnosticsSha256 = createHash('sha256')
    .update(JSON.stringify([diagnostic, '']))
    .digest('hex');
  manifest.projects[0].diagnosticCount = 1;
  writeFileSync(path, JSON.stringify(manifest));
  const passed = f.run(f.baseline);
  assert.equal(passed.status, 0, passed.stderr);
  const setup = 'input.ts(1,1): error TS2307: Cannot find module missing.\n';
  f.compiler('baseline', compilerCode.replace(JSON.stringify(diagnostic), JSON.stringify(setup)));
  manifest.projects[0].diagnosticsSha256 = createHash('sha256')
    .update(JSON.stringify([setup, '']))
    .digest('hex');
  writeFileSync(path, JSON.stringify(manifest));
  assert.match(f.run(f.baseline).stderr, /setup diagnostic TS2307/);
});

test(
  'RSS mode preserves approved diagnostics, real compiler provenance and every phase resource sample',
  { skip: process.platform !== 'linux' && 'RSS integration requires Linux GNU time' },
  (t) => {
    const f = fixture(t);
    const diagnostic = 'input.ts(1,1): error TS2322: Type number is not assignable to string.\n';
    const stderr = 'fixture diagnostic context\n';
    const code = `if(process.argv.includes('--listFilesOnly'))console.log(process.cwd()+'/input.ts');else{process.stdout.write(${JSON.stringify(diagnostic)});process.stderr.write(${JSON.stringify(stderr)});process.exit(1);}`;
    f.compiler('baseline', code);
    const candidate = f.compiler('candidate', code);
    const manifestPath = join(f.dir, 'manifest.json');
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    Object.assign(manifest.projects[0], {
      expectedExit: 1,
      diagnosticCount: 1,
      diagnosticsSha256: createHash('sha256')
        .update(JSON.stringify([diagnostic, stderr]))
        .digest('hex'),
    });
    writeFileSync(manifestPath, JSON.stringify(manifest));
    const plain = f.run(candidate);
    assert.equal(plain.status, 0, plain.stderr);
    const wrapped = f.run(candidate, ['--measure-rss', '--warmups', '1']);
    assert.equal(wrapped.status, 0, wrapped.stderr);
    const report = wrapped.report,
      project = report.projects[0];
    assert.equal(report.resourceMeasurement.enabled, true);
    assert.equal(report.resourceMeasurement.timingComparableToUnwrapped, false);
    assert.match(report.methodology, /not comparable to historical unwrapped/);
    assert.match(report.resourceMeasurement.wrapper.sha256, /^[a-f0-9]{64}$/);
    assert.deepEqual(report.binaries, plain.report.binaries);
    assert.equal(project.warmupResources.length, 1);
    for (const name of ['baseline', 'candidate']) {
      assert.deepEqual(project.compilerArgs[name], plain.report.projects[0].compilerArgs[name]);
      assert.equal(project.preflight[name].outputSha256, plain.report.projects[0].preflight[name].outputSha256);
      assert.equal(project.preflight[name].resources.discovery.exitStatus, 0);
      assert.equal(project.preflight[name].resources.check.exitStatus, 1);
      assert.equal(project.warmupResources[0][name].exitStatus, 1);
      assert.equal(project.execution[name].executable, report.resourceMeasurement.wrapper.path);
      assert.equal(project.execution[name].arguments[6], report.binaries[name].path);
      assert.deepEqual(
        project.resources[name].peakRssKiB.samples,
        project.pairs.map((pair) => pair.resources[name].peakRssKiB),
      );
      for (const pair of project.pairs) {
        assert.equal(pair.resources[name].exitStatus, 1);
        assert.ok(pair.resources[name].peakRssKiB > 0);
        assert.equal(typeof pair[name], 'number');
      }
    }
  },
);

for (const wrapped of [false, true]) {
  test(
    `candidate-only environment reaches every phase with the same binary (${wrapped ? 'RSS' : 'plain'})`,
    { skip: wrapped && process.platform !== 'linux' && 'RSS integration requires Linux GNU time' },
    (t) => {
      const f = fixture(t);
      const callsPath = join(f.dir, 'environment-invocations.jsonl');
      const overrides = {
        GOGC: 'off',
        GOMEMLIMIT: '256MiB',
        GOMAXPROCS: '3',
        GODEBUG: 'gcshrinkstackoff=1,madvdontneed=0',
        TSC_GO_SCHEDULER: 'dependency',
        TSC_GO_SHARED_GLOBALS: '',
      };
      const recordedKeys = [...Object.keys(overrides), 'TSC_TS_LIB_DIR', 'TSC_TS_CHECKERS'];
      f.compiler(
        'baseline',
        `
        const fs = process.getBuiltinModule('fs');
        const args = process.argv.slice(2);
        const env = Object.fromEntries(${JSON.stringify(recordedKeys)}.filter(k => process.env[k] !== undefined).map(k => [k, process.env[k]]));
        fs.appendFileSync(${JSON.stringify(callsPath)}, JSON.stringify({args,env})+'\\n');
        if (args.includes('--listFilesOnly')) console.log(process.cwd()+'/input.ts');
      `,
      );
      const inherited = {
        ...process.env,
        GOGC: '37',
        GOMEMLIMIT: '512MiB',
        GOMAXPROCS: '2',
        GODEBUG: 'gcshrinkstackoff=0',
        TSC_GO_SCHEDULER: 'balanced',
        TSC_GO_SHARED_GLOBALS: '1',
        TSC_TS_CHECKERS: 'fixed',
      };
      const extra = Object.entries(overrides).flatMap(([name, value]) => ['--candidate-env', `${name}=${value}`]);
      // Removals appear after overrides on the command line, but take effect first.
      extra.push('--unset-env', 'GOGC', '--unset-env', 'TSC_GO_SCHEDULER', '--warmups', '1');
      if (wrapped) extra.push('--measure-rss');
      const result = f.run(f.baseline, extra, inherited);
      assert.equal(result.status, 0, result.stderr);
      const { report } = result;
      assert.equal(report.schemaVersion, 1);
      assert.equal(report.binaries.baseline.path, report.binaries.candidate.path);
      assert.deepEqual(report.environment.candidateEnvironmentOverrides, overrides);
      const common = report.environment.compilerEnvironment;
      assert.equal(common.GOGC, undefined);
      assert.equal(common.TSC_GO_SCHEDULER, undefined);
      assert.equal(common.GOMEMLIMIT, '512MiB');
      assert.equal(common.TSC_TS_CHECKERS, 'fixed');
      assert.deepEqual(report.environment.compilerEnvironments.baseline, common);
      assert.deepEqual(report.environment.compilerEnvironments.candidate, { ...common, ...overrides });
      const calls = readFileSync(callsPath, 'utf8').trim().split('\n').map(JSON.parse);
      // Baseline discovery/preflight, candidate discovery/preflight, warmups,
      // first pair baseline/candidate, second pair candidate/baseline.
      const sides = [
        'baseline',
        'baseline',
        'candidate',
        'candidate',
        'baseline',
        'candidate',
        'baseline',
        'candidate',
        'candidate',
        'baseline',
      ];
      assert.equal(calls.length, sides.length);
      for (let i = 0; i < calls.length; i++) {
        const side = sides[i];
        const expected = report.environment.compilerEnvironments[side];
        assert.deepEqual(
          calls[i].env,
          Object.fromEntries(recordedKeys.filter((k) => expected[k] !== undefined).map((k) => [k, expected[k]])),
        );
        assert.equal(calls[i].args.includes('--listFilesOnly'), i === 0 || i === 2);
        assert.deepEqual(
          calls[i].args,
          i === 0 || i === 2 ? report.projects[0].fileDiscoveryArgs[side] : report.projects[0].compilerArgs[side],
        );
      }
      assert.equal(report.projects[0].pairs.length, 2);
      assert.equal(report.status, 'passed');
    },
  );
}

test('rejects malformed, semantic, and unrestricted candidate environment controls before invocation', () => {
  for (const value of [
    '',
    'GOGC',
    '=off',
    ' GOGC=off',
    'gogc=off',
    'TSC_TS_LIB_DIR=/other/libs',
    'PATH=/other/bin',
    'NODE_OPTIONS=--require=other',
    'TSC_TS_CHECKERS=fixed',
    'TS_NODE_PROJECT=other',
    '__proto__=other',
  ]) {
    const result = spawnSync(process.execPath, [runner, `--candidate-env=${value}`], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.match(result.stderr, /--candidate-env requires NAME=VALUE for an allowed runtime\/scheduler control/);
  }
});

test('rejects duplicate candidate environment controls rather than silently changing the experiment', () => {
  const result = spawnSync(process.execPath, [runner, '--candidate-env', 'GOGC=100', '--candidate-env', 'GOGC=off'], {
    encoding: 'utf8',
  });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /--candidate-env repeats GOGC/);
});
