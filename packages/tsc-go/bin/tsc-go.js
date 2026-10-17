#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const executable = resolve(dirname(fileURLToPath(import.meta.url)), '../dist', process.platform === 'win32' ? 'tsc-go.exe' : 'tsc-go');
const result = spawnSync(executable, process.argv.slice(2), { stdio: 'inherit' });
if (result.error) {
  process.stderr.write(`tsc-go: ${result.error.message}; run npm run build -w @tsc-ts/go first\n`);
} else if (result.signal) {
  process.kill(process.pid, result.signal);
}
process.exitCode = result.status ?? 1;
