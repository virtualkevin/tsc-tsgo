"""Analyze pinned Go 1.26 parsed execution traces; diagnostic wall times only."""
import argparse
import collections
import json
import re

HEADER = re.compile(r'^M=(-?\d+) P=(-?\d+) G=(-?\d+) (\w+) Time=(\d+)(.*)$')
TASK = re.compile(r' ID=(\d+) Parent=(\d+) Type=("[^"\n]*")$')
REGION = re.compile(r' Task=(\d+) Type=("[^"\n]*")$')
LOG = re.compile(r' Task=(\d+) Category=("[^"\n]*") Message=("[^"\n]*")$')
STATE = re.compile(r' GoID=(\d+) (\w+)->(\w+)(?: |$)')


def analyze(lines):
    states, tasks, active = {}, {}, {}
    counts = collections.Counter()
    previous = None

    def settle(gid, now):
        if gid in active:
            region = active[gid]
            state = states.get(gid)
            if state is None:
                raise ValueError(f'Unknown goroutine state for worker {gid}')
            region['stateNs'][state] += now - region['cursor']
            region['cursor'] = now

    for line in lines:
        m = HEADER.match(line.rstrip('\n'))
        if not m:
            if line.startswith('M='):
                raise ValueError('Malformed event header')
            continue  # Go decoder emits indented stacks and stack headings.
        _, _, gid, kind, now, fields = m.groups()
        gid, now = int(gid), int(now)
        if previous is not None and now < previous:
            raise ValueError('Non-monotonic event times')
        previous = now
        counts[kind] += 1
        if kind == 'StateTransition':
            m = STATE.match(fields)
            if not m:
                if ' ProcID=' in fields:
                    continue
                raise ValueError('Unknown transition resource')
            target, old, new = m.groups()
            target = int(target)
            if target in states and states[target] != old:
                raise ValueError(f'Inconsistent state for goroutine {target}')
            settle(target, now)
            states[target] = new
        elif kind in ('TaskBegin', 'TaskEnd'):
            m = TASK.fullmatch(fields)
            if not m:
                raise ValueError('Malformed task event')
            taskid, parent, name = m.groups()
            taskid, parent, name = int(taskid), int(parent), json.loads(name)
            if name not in ('checker.batch', 'checker.group'):
                continue
            if kind == 'TaskBegin':
                if taskid in tasks:
                    raise ValueError('Duplicate task')
                tasks[taskid] = dict(id=taskid, parent=parent, name=name,
                    gid=gid, start=now, regions={}, logs={})
            else:
                t = tasks[taskid]
                if 'end' in t or t['parent'] != parent or t['gid'] != gid:
                    raise ValueError('Mismatched task end')
                t['end'] = now
        elif kind in ('RegionBegin', 'RegionEnd'):
            m = REGION.fullmatch(fields)
            if not m:
                raise ValueError('Malformed region event')
            taskid, name = m.groups()
            taskid, name = int(taskid), json.loads(name)
            if taskid not in tasks:
                continue
            t = tasks[taskid]
            if t['gid'] != gid or 'end' in t:
                raise ValueError('Region outside task ownership')
            if kind == 'RegionBegin':
                if name in t['regions']:
                    raise ValueError('Repeated named region')
                r = dict(start=now)
                t['regions'][name] = r
                if name == 'checker.files':
                    if gid in active:
                        raise ValueError('Nested worker file regions')
                    r.update(cursor=now, stateNs=collections.Counter())
                    active[gid] = r
            else:
                r = t['regions'][name]
                if 'end' in r:
                    raise ValueError('Duplicate region end')
                if name == 'checker.files':
                    if active.get(gid) is not r:
                        raise ValueError('Mismatched active file region')
                    settle(gid, now)
                    del active[gid]
                    del r['cursor']
                    if sum(r['stateNs'].values()) != now - r['start']:
                        raise ValueError('Incomplete worker state accounting')
                r['end'] = now
        elif kind == 'Log':
            m = LOG.fullmatch(fields)
            if not m:
                raise ValueError('Malformed log event')
            taskid, category, message = m.groups()
            taskid = int(taskid)
            if taskid in tasks:
                category, message = json.loads(category), json.loads(message)
                if category in tasks[taskid]['logs']:
                    raise ValueError('Repeated metadata')
                tasks[taskid]['logs'][category] = message
    if active or not tasks:
        raise ValueError('Incomplete or absent worker tasks')
    for t in tasks.values():
        if 'end' not in t:
            raise ValueError('Incomplete task')
        for r in t['regions'].values():
            if 'end' not in r or r['start'] < t['start'] or r['end'] > t['end']:
                raise ValueError('Incomplete or out-of-task region')
        if t['name'] == 'checker.group':
            if tasks[t['parent']]['name'] != 'checker.batch':
                raise ValueError('Worker lacks batch parent')
            if set(t['regions']) != {'checker.lock', 'checker.files'}:
                raise ValueError('Missing worker regions')
    batches = []
    for t in tasks.values():
        if t['name'] != 'checker.batch':
            continue
        workers = [w for w in tasks.values() if w['parent'] == t['id']]
        if not workers or set(t['regions']) != {'checker.initialize'}:
            raise ValueError('Incomplete checker batch')
        indices = [int(w['logs']['checker.index']) for w in workers]
        if sorted(indices) != list(range(len(workers))):
            raise ValueError('Missing or duplicate checker index')
        files = [w['regions']['checker.files'] for w in workers]
        ends = sorted(r['end'] for r in files)
        starts = [r['start'] for r in files]
        batches.append(dict(taskId=t['id'], fileCount=int(t['logs']['file.count']),
            durationMs=(t['end']-t['start'])/1e6,
            startSkewMs=(max(starts)-min(starts))/1e6,
            finishSpreadMs=(ends[-1]-ends[0])/1e6,
            lastWorkerOnlyMs=(ends[-1]-ends[-2])/1e6 if len(ends)>1 else None,
            workers=[dict(checker=int(w['logs']['checker.index']),
                lockMs=(w['regions']['checker.lock']['end']-w['regions']['checker.lock']['start'])/1e6,
                filesMs=(w['regions']['checker.files']['end']-w['regions']['checker.files']['start'])/1e6,
                stateMs={s:v/1e6 for s,v in w['regions']['checker.files']['stateNs'].items()}) for w in workers]))
    return dict(status='parsed', eventCounts=dict(counts), batches=batches,
        limitations=['Diagnostic traced runs are not optimization timings.',
        'Running includes runtime/GC work, not just semantic computation.',
        'Worker state durations overlap across workers; do not sum as elapsed time.',
        'Completion tails are observations, not achievable scheduling gains.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('parsed_trace')
    parser.add_argument('output')
    args = parser.parse_args()
    with open(args.parsed_trace) as f:
        report = analyze(f)
    with open(args.output, 'x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
