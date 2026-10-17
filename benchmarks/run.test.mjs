import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

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
    run(candidate, extra = []) {
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
        { encoding: 'utf8' },
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
  assert.deepEqual(r.report.projects[0].compilerArgs.baseline, r.report.projects[0].compilerArgs.candidate);
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
