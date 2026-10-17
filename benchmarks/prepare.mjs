// Fetch only the declared commit. Dependency installation is a separate explicit step.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({
  options: {
    projects: { type: 'string' },
    install: { type: 'boolean' },
    help: { type: 'boolean' },
  },
});
if (values.help) {
  console.log('node benchmarks/prepare.mjs [--projects typeorm,trpc] [--install]');
  process.exit(0);
}
const manifest = JSON.parse(readFileSync(resolve(root, 'benchmarks/workloads.json'), 'utf8'));
const names = values.projects?.split(',');
if (names?.some((name) => !manifest.projects.some((p) => p.name === name))) throw new Error('Unknown project');
function run(command, args, cwd) {
  const r = spawnSync(command, args, { cwd, stdio: 'inherit' });
  if (r.error || r.status !== 0) throw new Error(`${command} failed: ${r.error?.message ?? r.status}`);
}
for (const p of manifest.projects.filter((p) => !names || names.includes(p.name))) {
  const cwd = resolve(root, p.directory);
  mkdirSync(cwd, { recursive: true });
  if (!existsSync(resolve(cwd, '.git'))) {
    run('git', ['init', '-q'], cwd);
    run('git', ['remote', 'add', 'origin', p.repository], cwd);
  }
  const dirty = spawnSync('git', ['status', '--porcelain'], { cwd, encoding: 'utf8' });
  if (dirty.status !== 0 || dirty.stdout.trim())
    throw new Error(`${p.name}: checkout is not clean; refusing to change it`);
  run('git', ['fetch', '--depth=1', 'origin', p.commit], cwd);
  run('git', ['checkout', '--detach', p.commit], cwd);
  if (values.install) {
    run(p.install[0], p.install.slice(1), cwd);
    if (p.prepare) run(p.prepare[0], p.prepare.slice(1), cwd);
  }
  console.log(`${p.name}: ${p.scope}`);
}
