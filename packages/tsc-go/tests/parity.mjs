// Compare the original native TypeScript implementation with the Go executable.
// Build both first; missing binaries are an error, never a skipped success.
// Run: node --test packages/tsc-go/tests/parity.mjs
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { cases as checkerCases } from '../../tsc-ts/tests/checker-cases.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const baseline = resolve(root, process.env.TSC_GO_BASELINE ?? 'packages/tsc-ts/dist/tsc');
const candidate = resolve(root, process.env.TSC_GO_CANDIDATE ?? 'packages/tsc-go/dist/tsc-go');
const libs = resolve(root, 'upstream/typescript-go/internal/bundled/libs');
for (const path of [baseline, candidate, libs]) {
  assert.ok(existsSync(path), `Required parity input is missing: ${path}`);
}

const fixtures = [
  {
    name: 'generics, conditional types, classes, and declarations',
    files: {
      'types.ts':
        'export type Unwrap<T> = T extends Promise<infer V> ? V : T;\nexport interface Box<T> { value: T }\nexport function box<T>(value: T): Box<T> { return { value }; }\n',
      'main.ts':
        'import { box, type Unwrap } from "./types.js";\nexport class Store<T> { constructor(public value: T) {} get(): T { return this.value; } }\nexport const data = box({ name: "caf\u00e9", count: 1 });\nexport const n: Unwrap<Promise<number>> = 42;\n',
    },
  },
  {
    name: 'semantic errors with Unicode positions',
    diagnostic: 'TS2322',
    files: {
      'main.ts':
        '// caf\u00e9 \u2014 \u{1f600}\nexport const x: string = 123;\nexport function twice(n: number): number { return n * 2; }\ntwice("wrong");\nexport const missing = unknownName;\n',
    },
  },
  {
    name: 'syntax errors',
    diagnostic: 'TS1110',
    files: { 'main.ts': 'export const x: = 3;\nexport function f( { return 1; }\n' },
  },
  {
    name: 'JSX preserve and namespace declarations',
    options: { jsx: 'preserve' },
    files: {
      'main.tsx':
        'declare global { namespace JSX { interface IntrinsicElements { div: { title?: string; children?: unknown } } } }\nexport namespace Shapes { export interface Point { x: number; y: number } }\nexport const view = <div title="hello">world</div>;\n',
    },
  },
  {
    name: 'checked JavaScript and JSON module resolution',
    diagnostic: 'TS2322',
    options: { allowJs: true, checkJs: true, resolveJsonModule: true },
    files: {
      'data.json': '{"label":"hello","count":2}\n',
      'helper.js': '/** @param {number} n */\nexport const twice = (n) => n * 2;\n',
      'main.ts':
        'import { twice } from "./helper.js";\nimport data from "./data.json";\nexport const n = twice(data.count);\nexport const bad: number = data.label;\n',
    },
  },
  {
    name: 'mapped union declaration order across checker histories',
    files: {
      'view.ts': 'export function view<F>(fields: F): { readonly [K in keyof F]: F[K] } { return fields; }\n',
      'defs.ts':
        'import { view } from "./view.js";\nexport const a = view({ kind: "a" as const, x: 1 });\nexport const b = view({ kind: "b" as const, y: "s" });\n',
      'main.ts':
        'import { a, b } from "./defs.js";\nexport const first = b;\nexport const pick = Math.random() > 0.5 ? a : b;\n',
    },
  },
];

// These cases deliberately cross the flow-walk memoization threshold and cover
// loop/reduce-label contexts, aliases, reference-key collisions, and generic
// types whose narrowing depends on the source position.
fixtures.push(
  ...checkerCases
    .filter(({ name }) => name.startsWith('flow analysis'))
    .map(({ name, source }) => ({
      name,
      diagnostic: 'TS2322',
      files: { 'main.ts': source.join('\n') + '\n' },
    })),
);

const variants = [
  ['check', ['--noEmit']],
  ['emit', []],
  ['declarations and source maps', ['--declaration', '--declarationMap', '--sourceMap']],
  ['declarations only', ['--declaration', '--emitDeclarationOnly']],
  ['no emit on error', ['--declaration', '--noEmitOnError']],
];

function emitted(dir, base = dir, output = {}) {
  if (!existsSync(dir)) return output;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) emitted(path, base, output);
    else output[relative(base, path)] = readFileSync(path).toString('base64');
  }
  return output;
}

function run(binary, cwd, args) {
  rmSync(join(cwd, 'out'), { recursive: true, force: true });
  const result = spawnSync(binary, ['-p', '.', '--pretty', 'false', ...args], {
    cwd,
    env: { ...process.env, TSC_TS_LIB_DIR: libs, NO_COLOR: '1' },
    encoding: 'utf8',
    timeout: 60_000,
    maxBuffer: 16 * 1024 * 1024,
  });
  assert.ifError(result.error);
  assert.equal(result.signal, null, `${binary} terminated by a signal`);
  return { status: result.status, stdout: result.stdout, stderr: result.stderr, files: emitted(join(cwd, 'out')) };
}

for (const fixture of fixtures) {
  for (const [name, args] of variants) {
    test(`${fixture.name}: ${name}`, () => {
      const cwd = mkdtempSync(join(tmpdir(), 'tsc-go-parity-'));
      try {
        for (const [file, content] of Object.entries(fixture.files)) {
          mkdirSync(dirname(join(cwd, file)), { recursive: true });
          writeFileSync(join(cwd, file), content);
        }
        writeFileSync(join(cwd, 'package.json'), '{"type":"module"}\n');
        writeFileSync(
          join(cwd, 'tsconfig.json'),
          JSON.stringify({
            compilerOptions: {
              target: 'ES2022',
              module: 'ESNext',
              moduleResolution: 'Bundler',
              strict: true,
              types: [],
              rootDir: '.',
              outDir: 'out',
              ...fixture.options,
            },
            include: ['*.ts', '*.tsx', '*.js'],
            exclude: ['out'],
          }),
        );
        const expected = run(baseline, cwd, args);
        assert.equal(expected.stderr, '', 'the baseline must complete without runtime errors');
        if (fixture.diagnostic) {
          assert.notEqual(expected.status, 0, 'the baseline must reject invalid source');
          assert.ok(expected.stdout.includes(fixture.diagnostic), `expected ${fixture.diagnostic}`);
        } else {
          assert.equal(expected.status, 0, expected.stdout);
          if (name !== 'check') assert.ok(Object.keys(expected.files).length > 0, 'the baseline must emit files');
        }
        const actual = run(candidate, cwd, args);
        assert.deepEqual(actual, expected);
      } finally {
        rmSync(cwd, { recursive: true, force: true });
      }
    });
  }
}
