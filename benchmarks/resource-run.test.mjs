import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { chmodSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';
import {
  inspectResourceWrapper,
  assertResourceWrapperUnchanged,
  parseResourceResult,
  runWithResources,
} from './resource-run.mjs';

// Availability is required on Linux; only unsupported platforms skip integration.
const linuxOnly = { skip: process.platform !== 'linux' && 'RSS integration requires Linux GNU time and /proc' };

function fixture(t) {
  const directory = mkdtempSync(join(tmpdir(), 'rss-test-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const script = (name, code) => {
    const path = join(directory, name);
    writeFileSync(path, `#!${process.execPath}\n${code}\n`);
    chmodSync(path, 0o755);
    return path;
  };
  return { directory, script, options: { cwd: directory, env: process.env, timeout: 10000 } };
}

test('requires exact complete integer resource output and matching exit status', () => {
  assert.deepEqual(parseResourceResult('{"peakRssKiB":123,"exitStatus":1}\n', 1), { peakRssKiB: 123, exitStatus: 1 });
  for (const text of [
    '',
    '{}',
    '{"peakRssKiB":1,"exitStatus":0}\nnoise',
    '{"peakRssKiB":1,"peakRssKiB":2,"exitStatus":0}',
    '{"peakRssKiB":-1,"exitStatus":0}',
    '{"peakRssKiB":1.5,"exitStatus":0}',
    '{"peakRssKiB":9007199254740992,"exitStatus":0}',
    '{"peakRssKiB":1,"exitStatus":256}',
    '{"peakRssKiB":1,"exitStatus":1}',
    '{"peakRssKiB":1,"exitStatus":0,"extra":1}',
  ]) {
    assert.throws(() => parseResourceResult(text, 0), /resource/);
  }
});

test('GNU time preserves diagnostic streams and approved nonzero command status', linuxOnly, async (t) => {
  const f = fixture(t);
  const binary = f.script(
    'compiler',
    "process.stdout.write('out\\r\\n');process.stderr.write('diagnostic\\r\\n');process.exit(2);",
  );
  const wrapper = inspectResourceWrapper();
  const result = await runWithResources(wrapper, binary, [], f.options);
  assert.equal(result.status, 2);
  assert.equal(result.stdout, 'out\n');
  assert.equal(result.stderr, 'diagnostic\n');
  assert.equal(result.resources.exitStatus, 2);
  assert.ok(result.resources.peakRssKiB > 0);
  assert.ok(result.ms > 0);
  assertResourceWrapperUnchanged(wrapper);
});

test('rejects missing/malformed metrics, wrapper status disagreement and changed wrapper', linuxOnly, async (t) => {
  const f = fixture(t);
  for (const [name, code, pattern] of [
    ['failed', 'process.exit(127)', /ENOENT/],
    [
      'malformed',
      "require('node:fs').writeFileSync(process.argv[process.argv.indexOf('--output')+1], 'noise');",
      /malformed/,
    ],
    [
      'disagree',
      `require('node:fs').writeFileSync(process.argv[process.argv.indexOf('--output')+1], '{"peakRssKiB":1,"exitStatus":0}');process.exit(2);`,
      /disagreement/,
    ],
  ]) {
    const wrapper = { path: f.script(name, code) };
    await assert.rejects(runWithResources(wrapper, process.execPath, ['-e', ''], f.options), pattern);
  }
  const path = f.script('version', "console.log('GNU Time fixture');");
  const inspected = inspectResourceWrapper(path);
  writeFileSync(path, '# changed');
  assert.throws(() => assertResourceWrapperUnchanged(inspected), /wrapper changed/);
});

const live = (pid) => {
  try {
    // A killed process can remain a zombie briefly until its parent/init reaps it.
    const stat = readFileSync(`/proc/${pid}/stat`, 'utf8');
    return stat.slice(stat.lastIndexOf(')') + 2, stat.lastIndexOf(')') + 3) !== 'Z';
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
};
async function until(predicate, label) {
  const deadline = Date.now() + 10000;
  while (!predicate()) {
    if (Date.now() > deadline) throw new Error(`Timed out waiting for ${label}`);
    await delay(20);
  }
}

for (const mode of ['timeout', 'SIGINT', 'SIGTERM', 'overflow', 'wrapper-exit']) {
  test(
    `${mode} cleans up compiler descendants and temporary resources`,
    { ...linuxOnly, timeout: 20000 },
    async (t) => {
      const f = fixture(t);
      const pidFile = join(f.directory, 'pids.json');
      const binary = f.script(
        'compiler',
        `
      const {spawn}=require('node:child_process');
      const child=spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{stdio:'inherit'});
      require('node:fs').writeFileSync(${JSON.stringify(pidFile)},JSON.stringify([process.pid,child.pid]));
      ${mode === 'overflow' ? "process.stdout.write('x'.repeat(16384));" : ''}
      setInterval(()=>{},1000);
    `,
      );
      const wrapper =
        mode === 'wrapper-exit'
          ? {
              path: f.script(
                'early-wrapper',
                `
          const {spawn}=require('node:child_process');
          spawn(${JSON.stringify(binary)},[],{stdio:'inherit'});
          const fs=require('node:fs');
          const wait=setInterval(()=>{if(fs.existsSync(${JSON.stringify(pidFile)})){clearInterval(wait);process.exit(2);}},10);
        `,
              ),
            }
          : inspectResourceWrapper();
      const driver = join(f.directory, 'driver.mjs');
      writeFileSync(
        driver,
        `
      import {runWithResources} from ${JSON.stringify(new URL('./resource-run.mjs', import.meta.url).href)};
      try {
        await runWithResources(${JSON.stringify(wrapper)},${JSON.stringify(binary)},[],{
          cwd:${JSON.stringify(f.directory)},env:{...process.env,TMPDIR:${JSON.stringify(f.directory)}},
          timeout:${mode === 'timeout' ? 2000 : 10000},maxBuffer:${mode === 'overflow' ? 1024 : 1048576}
        });
        process.exitCode=99;
      } catch(error) { console.error(error.message); }
    `,
      );
      // tmpdir() reads TMPDIR in the driver, not the child compiler's env argument.
      const child = spawn(process.execPath, [driver], {
        env: { ...process.env, TMPDIR: f.directory },
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      let stderr = '';
      child.stderr.on('data', (data) => {
        stderr += data;
      });
      child.stdout.resume();
      const closed = new Promise((resolve, reject) => {
        child.once('error', reject);
        child.once('close', (status, signal) => resolve({ status, signal }));
      });
      t.after(() => {
        if (child.exitCode === null) child.kill('SIGKILL');
      });
      await until(() => existsSync(pidFile), 'descendant startup');
      const pids = JSON.parse(readFileSync(pidFile));
      t.after(() => {
        for (const pid of pids) {
          try {
            process.kill(pid, 'SIGKILL');
          } catch {}
        }
      });
      if (mode === 'SIGINT' || mode === 'SIGTERM') child.kill(mode);
      const result = await closed;
      assert.deepEqual(result, { status: 0, signal: null }, stderr);
      assert.match(
        stderr,
        mode === 'timeout'
          ? /timeout/
          : mode === 'SIGINT' || mode === 'SIGTERM'
            ? new RegExp(mode)
            : mode === 'overflow'
              ? /buffer limit/
              : /ENOENT/,
      );
      await until(() => pids.every((pid) => !live(pid)), 'descendant cleanup');
      const { readdirSync } = await import('node:fs');
      assert.equal(
        readdirSync(f.directory).some((name) => name.startsWith('tsc-rss-')),
        false,
      );
    },
  );
}

test('rejects spawn failure and compiler signals without leaking cancellation handlers', linuxOnly, async (t) => {
  const f = fixture(t);
  const interrupts = process.listenerCount('SIGINT');
  const terminations = process.listenerCount('SIGTERM');
  await assert.rejects(
    runWithResources({ path: join(f.directory, 'missing-wrapper') }, process.execPath, [], f.options),
    /ENOENT/,
  );
  const binary = f.script('signaled', "process.kill(process.pid, 'SIGTERM');");
  await assert.rejects(runWithResources(inspectResourceWrapper(), binary, [], f.options), /disagreement|terminated/);
  assert.equal(process.listenerCount('SIGINT'), interrupts);
  assert.equal(process.listenerCount('SIGTERM'), terminations);
});
