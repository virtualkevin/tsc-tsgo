import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { compileSources } from './temp.mjs';
import { cases } from './checker-cases.mjs';

const root = resolve(import.meta.dirname, '..');
const repo = resolve(root, '../..');
const libs = join(repo, 'upstream/typescript-go/internal/bundled/libs');
const oracle = join(repo, 'packages/tsgo/dist/check-oracle');

test(
  'checker matches tsgo on small cases',
  { skip: !existsSync(libs) && 'needs upstream sources', timeout: 300_000 },
  () => {
    const out = compileSources('tsc-ts-check-', ['drivers/check.ts']);
    for (const { name, file: fileName = 'input.ts', source, expected } of cases) {
      const file = join(out, fileName);
      writeFileSync(file, source.join('\n') + '\n');
      const actual = execFileSync(process.execPath, ['--stack-size=16000', join(out, 'drivers/check.js'), file, libs], {
        encoding: 'utf8',
      });
      const lines = actual.split('\n').filter((l) => l !== '');
      assert.deepEqual(lines, expected, name);
      if (existsSync(oracle)) {
        const reference = execFileSync(oracle, [file, libs], { encoding: 'utf8' })
          .split('\n')
          .filter((l) => l !== '');
        assert.deepEqual(lines, reference, name + ' (oracle)');
      }
    }
  },
);
