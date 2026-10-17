import { spawnSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  assertSameGoSources,
  captureGoSources,
  describeGoBuild,
  publishBuildProvenance,
  sidecarPath,
} from '../../../scripts/build-provenance.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
mkdirSync(join(root, 'dist'), { recursive: true });
const executable = join(root, 'dist', process.platform === 'win32' ? 'tsc-go.exe' : 'tsc-go');
const go = process.env.GO ?? 'go';
const profile = process.env.TSC_GO_PGO ? resolve(process.env.TSC_GO_PGO) : null;
const args = ['build', '-trimpath', '-o', executable];
if (profile) args.push(`-pgo=${profile}`);
args.push('./cmd/tsgo');
const source = captureGoSources(root);
const build = describeGoBuild(go, args, root, profile);
// A failed/interrupted build must not leave a stale sidecar next to its output.
rmSync(sidecarPath(executable), { force: true });
const result = spawnSync(go, args, { cwd: root, stdio: 'inherit' });
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
if (result.status === 0) {
  assertSameGoSources(source, captureGoSources(root));
  if (JSON.stringify(build) !== JSON.stringify(describeGoBuild(go, args, root, profile)))
    throw new Error('Go toolchain settings or PGO profile changed during build; refusing to publish provenance');
  publishBuildProvenance(executable, source, build);
}
