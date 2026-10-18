import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const format = '{"peakRssKiB":%M,"exitStatus":%x}';
const sha256 = (data) => createHash('sha256').update(data).digest('hex');

export function inspectResourceWrapper(path = '/usr/bin/time', env = process.env) {
  if (process.platform !== 'linux') throw new Error('RSS wrapper mode currently requires Linux GNU time');
  path = realpathSync(path);
  const before = sha256(readFileSync(path));
  const result = spawnSync(path, ['--version'], { encoding: 'utf8', timeout: 5000, env });
  if (result.error || result.signal || result.status !== 0 || !/GNU [Tt]ime/.test(result.stdout))
    throw new Error('RSS wrapper must be a working GNU time executable');
  if (sha256(readFileSync(path)) !== before) throw new Error('RSS wrapper changed during inspection');
  return {
    path,
    sha256: before,
    version: result.stdout.trim(),
    format,
    methodology:
      'GNU time maximum resident set size in KiB for the command; not Go heap size, allocated bytes, or a process-tree/cgroup peak. Wrapped wall time includes wrapper launch/wait and resource-file output.',
  };
}

export function assertResourceWrapperUnchanged(wrapper) {
  if (sha256(readFileSync(wrapper.path)) !== wrapper.sha256) throw new Error('RSS wrapper changed during measurement');
}

export function parseResourceResult(text, status) {
  // GNU time uses this exact integer-only format. Reject duplicate keys/records,
  // trailing messages and JSON coercions instead of trusting partial metrics.
  if (!/^\{"peakRssKiB":\d+,"exitStatus":\d+\}\n?$/.test(text))
    throw new Error('Missing or malformed GNU time resource output');
  let result;
  try {
    result = JSON.parse(text);
  } catch {
    throw new Error('Missing or malformed GNU time resource output');
  }
  if (
    !result ||
    typeof result !== 'object' ||
    Array.isArray(result) ||
    Object.keys(result).sort().join(',') !== 'exitStatus,peakRssKiB' ||
    !Number.isSafeInteger(result.peakRssKiB) ||
    result.peakRssKiB < 0 ||
    !Number.isInteger(result.exitStatus) ||
    result.exitStatus < 0 ||
    result.exitStatus > 255 ||
    result.exitStatus !== status
  )
    throw new Error('Invalid GNU time resource values or wrapper/command status disagreement');
  return result;
}

// Call for both baseline and candidate in discovery, preflight, warmups and
// timed samples. The existing semantic outcome/output checks must still run.
export async function runWithResources(wrapper, binary, args, { cwd, env, timeout, maxBuffer = 128 * 1024 * 1024 }) {
  // Temporary-directory setup and parsing/cleanup happen outside the wall clock.
  const directory = mkdtempSync(join(tmpdir(), 'tsc-rss-'));
  const output = join(directory, 'resources.json');
  const wrapperArgs = ['--quiet', '--output', output, '--format', format, '--', binary, ...args];
  try {
    const result = await new Promise((resolve, reject) => {
      const stdout = [],
        stderr = [];
      let bytes = 0,
        failure,
        child,
        timer;
      const start = process.hrtime.bigint();
      const killGroup = () => {
        if (!child?.pid) return;
        try {
          process.kill(-child.pid, 'SIGKILL');
        } catch (error) {
          if (error.code !== 'ESRCH') failure ??= error;
        }
      };
      const cancel = (reason) => {
        failure ??= new Error(reason);
        killGroup();
      };
      const onInterrupt = () => cancel('Resource measurement interrupted by SIGINT');
      const onTerminate = () => cancel('Resource measurement interrupted by SIGTERM');
      const cleanHandlers = () => {
        clearTimeout(timer);
        process.removeListener('SIGINT', onInterrupt);
        process.removeListener('SIGTERM', onTerminate);
      };
      try {
        child = spawn(wrapper.path, wrapperArgs, { cwd, env, detached: true, stdio: ['ignore', 'pipe', 'pipe'] });
      } catch (error) {
        reject(error);
        return;
      }
      process.on('SIGINT', onInterrupt);
      process.on('SIGTERM', onTerminate);
      timer = setTimeout(() => cancel('Resource measurement exceeded timeout'), timeout);
      const collect = (chunks, data) => {
        if (failure) return;
        bytes += data.length;
        if (bytes > maxBuffer) {
          cancel('Resource measurement exceeded output buffer limit');
          return;
        }
        chunks.push(data);
      };
      child.stdout.on('data', (data) => collect(stdout, data));
      child.stderr.on('data', (data) => collect(stderr, data));
      child.once('exit', killGroup);
      child.once('error', (error) => {
        failure ??= error;
        killGroup();
      });
      child.once('close', (status, signal) => {
        const ms = Number(process.hrtime.bigint() - start) / 1e6;
        // Kill any remaining members even if the wrapper exited unexpectedly.
        // The real compiler invocations do not create separate sessions.
        killGroup();
        cleanHandlers();
        if (failure || signal || status === null) {
          reject(failure ?? new Error(`Resource wrapper terminated: ${signal}`));
          return;
        }
        resolve({
          status,
          stdout: Buffer.concat(stdout).toString('utf8').replaceAll('\r\n', '\n'),
          stderr: Buffer.concat(stderr).toString('utf8').replaceAll('\r\n', '\n'),
          ms,
        });
      });
    });
    const resources = parseResourceResult(readFileSync(output, 'utf8'), result.status);
    return { ...result, resources };
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
}
