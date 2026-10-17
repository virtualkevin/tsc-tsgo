import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync, readlinkSync, renameSync, writeFileSync } from 'node:fs';
import { join, relative, resolve, sep } from 'node:path';

export const sha256 = (content) => createHash('sha256').update(content).digest('hex');
export const hashFile = (path) => sha256(readFileSync(path));
export const sidecarPath = (binary) => `${binary}.provenance.json`;
const slash = (path) => path.split(sep).join('/');

function git(root, args) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  if (result.error || result.status !== 0)
    throw new Error(`Cannot capture Git build provenance: ${result.error?.code ?? result.status}`);
  return result.stdout;
}

// Hash the complete local compiler source trees, including ignored/untracked
// files and embedded declarations. This intentionally includes tests too. Module
// dependencies and the toolchain are identified separately; this is not a
// hermetic build attestation or a hash of the entire external dependency cache.
export function captureGoSources(packageRoot) {
  const repositoryRoot = git(packageRoot, ['rev-parse', '--show-toplevel']).trim();
  const roots = ['cmd', 'internal', 'scripts', 'go.mod', 'go.sum', 'package.json'].map((path) =>
    resolve(packageRoot, path),
  );
  roots.push(resolve(repositoryRoot, 'scripts/build-provenance.mjs'));
  const files = [];
  const visit = (path) => {
    const stat = lstatSync(path);
    if (stat.isDirectory()) {
      for (const entry of readdirSync(path).sort()) visit(join(path, entry));
    } else if (stat.isFile()) {
      files.push({
        path: slash(relative(repositoryRoot, path)),
        sha256: hashFile(path),
        executable: (stat.mode & 0o111) !== 0,
      });
    } else if (stat.isSymbolicLink()) {
      // Go rejects symlinked embedded files; reject source symlinks here as well
      // rather than claiming to have captured an external mutable source tree.
      throw new Error(
        `Cannot capture symlinked compiler source: ${slash(relative(repositoryRoot, path))} -> ${readlinkSync(path)}`,
      );
    } else {
      throw new Error(`Cannot capture non-file compiler source: ${slash(relative(repositoryRoot, path))}`);
    }
  };
  for (const path of roots) visit(path);
  files.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  const pathspecs = roots.map((path) => slash(relative(repositoryRoot, path)));
  const changes = git(repositoryRoot, [
    'status',
    '--porcelain=v1',
    '-z',
    '--no-renames',
    '--untracked-files=all',
    '--',
    ...pathspecs,
  ])
    .split('\0')
    .filter(Boolean);
  const ignoredSources = git(repositoryRoot, [
    'ls-files',
    '-z',
    '--others',
    '--ignored',
    '--exclude-standard',
    '--',
    ...pathspecs,
  ])
    .split('\0')
    .filter(Boolean);
  return {
    revision: git(repositoryRoot, ['rev-parse', 'HEAD']).trim(),
    dirty: changes.length !== 0 || ignoredSources.length !== 0,
    changes,
    ignoredSources,
    digestAlgorithm: 'sha256(JSON.stringify(sorted local source manifest))',
    sha256: sha256(JSON.stringify(files)),
    files,
  };
}

export function assertSameGoSources(before, after) {
  if (JSON.stringify(before) !== JSON.stringify(after))
    throw new Error('Compiler sources or Git state changed during build; refusing to publish provenance');
}

// Never serialize arbitrary environment variables, linker flags, or `go version
// -m` output: these can contain credentials passed with -ldflags/-X. GOFLAGS is
// identified by its hash, while these fixed toolchain settings are safe values.
export function describeGoBuild(go, args, packageRoot, profile = null) {
  const keys = [
    'GOVERSION',
    'GOOS',
    'GOARCH',
    'GOAMD64',
    'GOARM',
    'GOARM64',
    'GO386',
    'GOMIPS',
    'GOMIPS64',
    'GOPPC64',
    'GORISCV64',
    'CGO_ENABLED',
    'GOEXPERIMENT',
    'GOFLAGS',
  ];
  const result = spawnSync(go, ['env', '-json', ...keys], { cwd: packageRoot, encoding: 'utf8' });
  if (result.error || result.status !== 0) throw new Error('Cannot capture Go toolchain settings');
  const settings = JSON.parse(result.stdout);
  const flags = settings.GOFLAGS ?? '';
  delete settings.GOFLAGS;
  return {
    toolchain: settings,
    arguments: args.map((argument, index) =>
      args[index - 1] === '-o' ? '<binary>' : argument.startsWith('-pgo=') ? '-pgo=<profile>' : argument,
    ),
    extraFlagsPresent: flags !== '',
    extraFlagsSha256: sha256(flags),
    profile: profile ? { sha256: hashFile(profile) } : null,
    dependencyScope:
      'Local sources and go.mod/go.sum are hashed; external module-cache contents and toolchain files are not hashed',
  };
}

export function publishBuildProvenance(binary, source, build) {
  const metadata = {
    schemaVersion: 1,
    producer: 'tsc-go-build',
    builtAt: new Date().toISOString(),
    binary: { sha256: hashFile(binary) },
    source,
    build,
  };
  const path = sidecarPath(binary);
  const temporary = `${path}.${process.pid}.tmp`;
  writeFileSync(temporary, JSON.stringify(metadata, null, 2) + '\n');
  renameSync(temporary, path);
  return metadata;
}

export function readBuildProvenance(binary, binarySha256 = hashFile(binary)) {
  const path = sidecarPath(binary);
  let content;
  try {
    content = readFileSync(path, 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') return { status: 'absent', path };
    throw new Error(`Cannot read binary provenance sidecar: ${path} (${error.code})`);
  }
  let metadata;
  try {
    metadata = JSON.parse(content);
  } catch {
    throw new Error(`Invalid binary provenance JSON: ${path}`);
  }
  if (
    metadata?.schemaVersion !== 1 ||
    metadata.producer !== 'tsc-go-build' ||
    !/^[a-f0-9]{64}$/.test(metadata.source?.sha256 ?? '') ||
    !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(metadata.source?.revision ?? '') ||
    typeof metadata.source?.dirty !== 'boolean' ||
    !Array.isArray(metadata.source?.files) ||
    !metadata.source.files.every(
      (file) =>
        typeof file?.path === 'string' &&
        /^[a-f0-9]{64}$/.test(file.sha256 ?? '') &&
        typeof file.executable === 'boolean',
    ) ||
    !metadata.build?.toolchain ||
    !Array.isArray(metadata.build?.arguments)
  )
    throw new Error(`Unsupported or incomplete binary provenance: ${path}`);
  if (metadata.binary?.sha256 !== binarySha256) throw new Error(`Binary provenance SHA-256 mismatch: ${path}`);
  if (sha256(JSON.stringify(metadata.source.files)) !== metadata.source.sha256)
    throw new Error(`Source manifest SHA-256 mismatch in binary provenance: ${path}`);
  return { status: 'verified', path, sidecarSha256: sha256(content), metadata };
}
