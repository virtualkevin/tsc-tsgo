import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  chmodSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { assertSameGoSources, captureGoSources, readBuildProvenance, sidecarPath } from './build-provenance.mjs';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..');
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'build-provenance-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const packageRoot = join(root, 'packages/tsc-go');
  for (const path of ['scripts', 'packages/tsc-go/scripts', 'packages/tsc-go/cmd/tsgo', 'packages/tsc-go/internal'])
    mkdirSync(join(root, path), { recursive: true });
  for (const path of ['scripts/build-provenance.mjs', 'packages/tsc-go/scripts/build.mjs'])
    copyFileSync(join(repository, path), join(root, path));
  writeFileSync(join(root, '.gitignore'), 'dist/\nignored.go\n');
  writeFileSync(join(packageRoot, 'go.mod'), 'module fixture\ngo 1.26\n');
  writeFileSync(join(packageRoot, 'go.sum'), '');
  writeFileSync(join(packageRoot, 'package.json'), '{"type":"module"}');
  writeFileSync(join(packageRoot, 'cmd/tsgo/main.go'), 'package main\nfunc main() {}\n');
  const git = (...args) => {
    const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    return result.stdout.trim();
  };
  git('init', '-q');
  git('add', '.');
  git('-c', 'user.name=Provenance Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture');
  const go = join(root, 'fake-go.mjs');
  writeFileSync(
    go,
    `#!${process.execPath}
import { writeFileSync } from 'node:fs';
const args = process.argv.slice(2);
if (args[0] === 'env') {
  console.log(JSON.stringify({ GOVERSION: 'go1.26.0-fixture', GOOS: 'linux', GOARCH: 'amd64', CGO_ENABLED: '0', GOFLAGS: process.env.GOFLAGS ?? '' }));
} else if (args[0] === 'build') {
  if (process.env.FAKE_BUILD_FAILURE) process.exit(2);
  writeFileSync(args[args.indexOf('-o') + 1], 'fixture binary');
  if (process.env.FAKE_SOURCE_CHANGE) writeFileSync('cmd/tsgo/main.go', 'changed during build');
} else process.exit(3);
`,
  );
  chmodSync(go, 0o755);
  const binary = join(packageRoot, 'dist', process.platform === 'win32' ? 'tsc-go.exe' : 'tsc-go');
  return {
    root,
    packageRoot,
    binary,
    git,
    build(extraEnv = {}) {
      return spawnSync(process.execPath, [join(packageRoot, 'scripts/build.mjs')], {
        cwd: packageRoot,
        encoding: 'utf8',
        env: { ...process.env, GO: go, TSC_GO_PGO: '', ...extraEnv },
      });
    },
  };
}

test('source digest and dirty state include new and ignored compiler source', (t) => {
  const f = fixture(t);
  const initial = captureGoSources(f.packageRoot);
  assert.equal(initial.dirty, false);
  writeFileSync(join(f.packageRoot, 'internal/new.go'), 'package internal\n');
  const untracked = captureGoSources(f.packageRoot);
  assert.equal(untracked.dirty, true);
  assert.notEqual(untracked.sha256, initial.sha256);
  assert.ok(untracked.changes.includes('?? packages/tsc-go/internal/new.go'));
  assert.throws(() => assertSameGoSources(initial, untracked), /changed during build/);
  writeFileSync(join(f.packageRoot, 'internal/ignored.go'), 'package internal\n');
  const ignored = captureGoSources(f.packageRoot);
  assert.notEqual(ignored.sha256, untracked.sha256);
  assert.deepEqual(ignored.ignoredSources, ['packages/tsc-go/internal/ignored.go']);
  assert.ok(ignored.files.some(({ path }) => path.endsWith('/ignored.go')));
});

test('successful build publishes binary-bound source/toolchain/options without flag secrets', (t) => {
  const f = fixture(t);
  const profile = join(f.root, 'fixture.pprof');
  writeFileSync(profile, 'fixture profile');
  const result = f.build({ GOFLAGS: '-ldflags=-X=main.secret=must-not-appear', TSC_GO_PGO: profile });
  assert.equal(result.status, 0, result.stderr);
  const recorded = readBuildProvenance(f.binary);
  assert.equal(recorded.status, 'verified');
  assert.equal(recorded.metadata.source.revision, f.git('rev-parse', 'HEAD'));
  assert.equal(recorded.metadata.source.dirty, false);
  assert.equal(recorded.metadata.build.toolchain.GOVERSION, 'go1.26.0-fixture');
  assert.deepEqual(recorded.metadata.build.arguments, [
    'build',
    '-trimpath',
    '-o',
    '<binary>',
    '-pgo=<profile>',
    './cmd/tsgo',
  ]);
  assert.equal(recorded.metadata.build.extraFlagsPresent, true);
  assert.match(recorded.metadata.build.profile.sha256, /^[a-f0-9]{64}$/);
  assert.ok(!readFileSync(sidecarPath(f.binary), 'utf8').includes('must-not-appear'));
  // Preservation requires copying the sidecar alongside the renamed binary.
  const preserved = join(f.root, 'preserved-binary');
  copyFileSync(f.binary, preserved);
  assert.equal(readBuildProvenance(preserved).status, 'absent');
  copyFileSync(sidecarPath(f.binary), sidecarPath(preserved));
  assert.equal(readBuildProvenance(preserved).status, 'verified');
});

test('failed and source-mutating builds never leave successful provenance', (t) => {
  const f = fixture(t);
  assert.equal(f.build().status, 0);
  assert.equal(f.build({ FAKE_BUILD_FAILURE: '1' }).status, 2);
  assert.equal(existsSync(sidecarPath(f.binary)), false);
  const changed = f.build({ FAKE_SOURCE_CHANGE: '1' });
  assert.equal(changed.status, 1);
  assert.match(changed.stderr, /sources or Git state changed during build/);
  assert.equal(existsSync(sidecarPath(f.binary)), false);
});

test('reader rejects stale binaries, corrupted manifests, and malformed sidecars', (t) => {
  const f = fixture(t);
  assert.equal(f.build().status, 0);
  const path = sidecarPath(f.binary);
  const valid = readFileSync(path, 'utf8');
  writeFileSync(f.binary, 'different binary');
  assert.throws(() => readBuildProvenance(f.binary), /Binary provenance SHA-256 mismatch/);
  writeFileSync(f.binary, 'fixture binary');
  const metadata = JSON.parse(valid);
  metadata.source.files[0].sha256 = '0'.repeat(64);
  writeFileSync(path, JSON.stringify(metadata));
  assert.throws(() => readBuildProvenance(f.binary), /Source manifest SHA-256 mismatch/);
  writeFileSync(path, 'not JSON');
  assert.throws(() => readBuildProvenance(f.binary), /Invalid binary provenance JSON/);
});
