import assert from 'node:assert/strict';
import test from 'node:test';
import { readCgroupCpuStats, readCgroupV2 } from './cgroup.mjs';

const mount = (root, point) => `36 25 0:32 ${root} ${point} rw - cgroup2 cgroup rw`;
const node = (path, cpuMax = 'max 100000', memoryMax = 'max') => ({
  [`${path}/cpu.max`]: cpuMax,
  [`${path}/memory.max`]: memoryMax,
  [`${path}/cpuset.cpus`]: '',
  [`${path}/cpuset.cpus.effective`]: '0-7',
  [`${path}/cpu.stat`]: 'usage_usec 9007199254740993\nnr_periods 20\nnr_throttled 4\nthrottled_usec 1234',
});
const reader =
  (files, calls = []) =>
  (path) => {
    calls.push(path);
    if (files[path] instanceof Error) throw files[path];
    if (!(path in files)) throw Object.assign(new Error('missing'), { code: 'ENOENT' });
    return files[path];
  };

test('finds nested ancestor quota when process and mount-root limits are unlimited', () => {
  const files = {
    '/proc/self/cgroup': '0::/user.slice/user-1000.slice/session-6.scope',
    '/proc/self/mountinfo': mount('/', '/sys/fs/cgroup'),
    ...node('/sys/fs/cgroup'),
    ...node('/sys/fs/cgroup/user.slice'),
    ...node('/sys/fs/cgroup/user.slice/user-1000.slice', '560000 100000', '18446744073709550000'),
    ...node('/sys/fs/cgroup/user.slice/user-1000.slice/session-6.scope'),
  };
  const result = readCgroupV2({ readFile: reader(files) });
  assert.equal(result.minimumVisibleCpuQuotaCpus, 5.6);
  assert.equal(result.minimumVisibleMemoryMaxBytes, '18446744073709550000');
  assert.equal(result.cpuQuotaReadComplete, true);
  assert.equal(result.ancestors.length, 4);
  assert.equal(result.ancestors[0].cpuMax, 'max 100000');
  assert.equal(result.ancestors[0].cpusetCpusEffective, '0-7');
  assert.equal(result.ancestors[0].cpuStat.usage_usec, '9007199254740993');
  files['/sys/fs/cgroup/user.slice/user-1000.slice/session-6.scope/cpu.max'] = '200000 100000';
  assert.equal(readCgroupV2({ readFile: reader(files) }).minimumVisibleCpuQuotaCpus, 2);
});

test('maps non-root cgroup mounts and escaped mountpoints without walking above the mount', () => {
  const calls = [];
  const files = {
    '/proc/self/cgroup': '0::/tenant/workers/job',
    '/proc/self/mountinfo': mount('/tenant', '/sys/cgroup\\040space'),
    ...node('/sys/cgroup space', '250000 100000'),
    ...node('/sys/cgroup space/workers'),
    ...node('/sys/cgroup space/workers/job'),
  };
  const result = readCgroupV2({ readFile: reader(files, calls) });
  assert.equal(result.mountRoot, '/tenant');
  assert.equal(result.mountPoint, '/sys/cgroup space');
  assert.equal(result.minimumVisibleCpuQuotaCpus, 2.5);
  assert.deepEqual(
    result.ancestors.map((entry) => entry.path),
    ['/sys/cgroup space/workers/job', '/sys/cgroup space/workers', '/sys/cgroup space'],
  );
  assert.ok(!calls.includes('/sys/cpu.max'));
  // In a cgroup namespace the visible membership and mount root may both be /.
  files['/proc/self/cgroup'] = '0::/';
  files['/proc/self/mountinfo'] = mount('/', '/sys/cgroup\\040space');
  assert.equal(readCgroupV2({ readFile: reader(files) }).ancestors.length, 1);
});

test('uses the broadest visible hierarchy instead of a bind mount hiding an ancestor quota', () => {
  const files = {
    '/proc/self/cgroup': '0::/tenant/job',
    '/proc/self/mountinfo': [mount('/tenant/job', '/bound'), mount('/', '/all')].join('\n'),
    ...node('/all', '100000 100000'),
    ...node('/all/tenant'),
    ...node('/all/tenant/job'),
    ...node('/bound'),
  };
  const result = readCgroupV2({ readFile: reader(files) });
  assert.equal(result.mountPoint, '/all');
  assert.equal(result.minimumVisibleCpuQuotaCpus, 1);
  // Prefix similarity does not make a mount an ancestor.
  files['/proc/self/mountinfo'] = mount('/tenant-other', '/bound');
  assert.equal(readCgroupV2({ readFile: reader(files) }).status, 'unavailable');
  files['/proc/self/cgroup'] = '0::/../outside';
  files['/proc/self/mountinfo'] = mount('/', '/all');
  assert.equal(readCgroupV2({ readFile: reader(files) }).status, 'unavailable');
});

test('missing or inaccessible metadata remains unknown rather than falsely unlimited', () => {
  const denied = Object.assign(new Error('denied'), { code: 'EACCES' });
  assert.equal(readCgroupV2({ readFile: reader({ '/proc/self/cgroup': denied }) }).status, 'unavailable');
  const files = {
    '/proc/self/cgroup': '0::/job',
    '/proc/self/mountinfo': mount('/', '/cg'),
    ...node('/cg', '560000 100000'),
    ...node('/cg/job'),
    '/cg/job/cpu.max': denied,
  };
  delete files['/cg/job/memory.max'];
  const result = readCgroupV2({ readFile: reader(files) });
  assert.equal(result.minimumVisibleCpuQuotaCpus, 5.6);
  assert.equal(result.cpuQuotaReadComplete, false);
  assert.equal(result.memoryLimitReadComplete, false);
  assert.equal(result.ancestors[0].cpuMax, null);
  assert.deepEqual(result.ancestors[0].errors, [
    { path: '/cg/job/cpu.max', code: 'EACCES' },
    { path: '/cg/job/memory.max', code: 'ENOENT' },
  ]);
});

test('per-invocation snapshots read only ancestor CPU counters and retain counter changes', () => {
  const files = {
    '/proc/self/cgroup': '0::/job',
    '/proc/self/mountinfo': mount('/', '/cg'),
    ...node('/cg'),
    ...node('/cg/job'),
  };
  const cgroup = readCgroupV2({ readFile: reader(files) });
  const calls = [];
  const before = readCgroupCpuStats(cgroup, { readFile: reader(files, calls) });
  files['/cg/cpu.stat'] = 'nr_throttled 6\nthrottled_usec 4321';
  const after = readCgroupCpuStats(cgroup, { readFile: reader(files, calls) });
  assert.equal(before.ancestors[1].cpuStat.nr_throttled, '4');
  assert.equal(after.ancestors[1].cpuStat.nr_throttled, '6');
  assert.deepEqual(calls, ['/cg/job/cpu.stat', '/cg/cpu.stat', '/cg/job/cpu.stat', '/cg/cpu.stat']);
});
