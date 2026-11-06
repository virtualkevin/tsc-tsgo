import { readFileSync } from 'node:fs';
import { posix } from 'node:path';

// mountinfo escapes whitespace and backslashes in paths with octal escapes.
const unescapePath = (text) => text.replace(/\\([0-7]{3})/g, (_, octal) => String.fromCharCode(parseInt(octal, 8)));
const contains = (root, path) => root === '/' || path === root || path.startsWith(root + '/');
const read = (path, readFile, errors) => {
  try {
    return readFile(path, 'utf8').trim();
  } catch (error) {
    errors.push({ path, code: error.code ?? error.name });
    return null;
  }
};
const parseCpuStat = (text) =>
  text === null
    ? null
    : Object.fromEntries(
        text.split('\n').flatMap((line) => {
          const match = /^(\S+)\s+(\d+)$/.exec(line.trim());
          // Strings preserve counters beyond Number.MAX_SAFE_INTEGER.
          return match ? [[match[1], match[2]]] : [];
        }),
      );

export function readCgroupV2({ readFile = readFileSync } = {}) {
  const errors = [];
  const membership = read('/proc/self/cgroup', readFile, errors);
  const mountinfo = read('/proc/self/mountinfo', readFile, errors);
  const result = { status: 'unavailable', scope: 'visible cgroup v2 hierarchy', errors };
  if (membership === null || mountinfo === null) return result;
  const member = /^0::(\/.*)$/m.exec(membership);
  if (!member) return { ...result, reason: 'No unified cgroup v2 membership' };
  // Membership outside the process's cgroup namespace can contain /../.
  // Normalizing it would incorrectly turn an invisible hierarchy into root.
  if (member[1].split('/').includes('..'))
    return { ...result, membershipPath: member[1], reason: 'Membership lies outside the visible cgroup namespace' };
  const membershipPath = posix.normalize(member[1]);
  const mounts = mountinfo.split('\n').flatMap((line) => {
    const fields = line.split(' ');
    const separator = fields.indexOf('-');
    if (separator < 6 || fields[separator + 1] !== 'cgroup2') return [];
    const rawRoot = unescapePath(fields[3]);
    if (rawRoot.split('/').includes('..')) return [];
    const root = posix.normalize(rawRoot);
    const point = posix.normalize(unescapePath(fields[4]));
    return root.startsWith('/') && point.startsWith('/') && contains(root, membershipPath) ? [{ root, point }] : [];
  });
  // Prefer the broadest visible hierarchy, so a nested bind mount cannot hide
  // an accessible ancestor quota. A non-root mount still needs its root prefix
  // removed when translating the membership path to a filesystem path.
  mounts.sort((a, b) => a.root.length - b.root.length || a.point.length - b.point.length);
  if (!mounts.length) return { ...result, membershipPath, reason: 'No cgroup2 mount contains the reported membership' };
  const mount = mounts[0];
  const ownPath = posix.join(mount.point, posix.relative(mount.root, membershipPath));
  const ancestors = [];
  for (let path = ownPath; ; path = posix.dirname(path)) {
    const entryErrors = [];
    const get = (name) => read(posix.join(path, name), readFile, entryErrors);
    ancestors.push({
      path,
      cpuMax: get('cpu.max'),
      memoryMax: get('memory.max'),
      cpusetCpus: get('cpuset.cpus'),
      cpusetCpusEffective: get('cpuset.cpus.effective'),
      cpuStat: parseCpuStat(get('cpu.stat')),
      errors: entryErrors,
    });
    if (path === mount.point) break;
  }
  const cpuLimits = ancestors.flatMap(({ cpuMax }) => {
    const match = /^(\d+)\s+(\d+)$/.exec(cpuMax ?? '');
    if (!match || Number(match[2]) <= 0) return [];
    const ratio = Number(match[1]) / Number(match[2]);
    return Number.isFinite(ratio) ? [ratio] : [];
  });
  const memoryLimits = ancestors
    .filter(({ memoryMax }) => /^\d+$/.test(memoryMax ?? ''))
    .map(({ memoryMax }) => BigInt(memoryMax));
  return {
    ...result,
    status: 'available',
    membershipPath,
    mountRoot: mount.root,
    mountPoint: mount.point,
    ancestors,
    minimumVisibleCpuQuotaCpus: cpuLimits.length ? Math.min(...cpuLimits) : null,
    minimumVisibleMemoryMaxBytes: memoryLimits.length
      ? memoryLimits.reduce((a, b) => (a < b ? a : b)).toString()
      : null,
    cpuQuotaReadComplete: ancestors.every(({ cpuMax }) => /^(?:max|\d+)\s+[1-9]\d*$/.test(cpuMax ?? '')),
    memoryLimitReadComplete: ancestors.every(({ memoryMax }) => /^(?:max|\d+)$/.test(memoryMax ?? '')),
  };
}

// Read outside the timed compiler invocation. Ancestor counters include sibling
// tasks and therefore describe shared throttling pressure, not compiler CPU use.
export function readCgroupCpuStats(cgroup, { readFile = readFileSync } = {}) {
  return {
    capturedAt: new Date().toISOString(),
    ancestors: (cgroup.ancestors ?? []).map(({ path }) => {
      const errors = [];
      return { path, cpuStat: parseCpuStat(read(posix.join(path, 'cpu.stat'), readFile, errors)), errors };
    }),
  };
}
