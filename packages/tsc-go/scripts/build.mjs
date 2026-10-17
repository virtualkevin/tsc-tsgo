import { spawnSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
mkdirSync(join(root, 'dist'), { recursive: true });
const executable = join(root, 'dist', process.platform === 'win32' ? 'tsc-go.exe' : 'tsc-go');
const args = ['build', '-trimpath', '-o', executable];
if (process.env.TSC_GO_PGO) args.push(`-pgo=${resolve(process.env.TSC_GO_PGO)}`);
args.push('./cmd/tsgo');
const result = spawnSync(process.env.GO ?? 'go', args, { cwd: root, stdio: 'inherit' });
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
