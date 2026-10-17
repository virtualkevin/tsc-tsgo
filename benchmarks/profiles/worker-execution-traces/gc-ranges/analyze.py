"""Pinned Go1.26 parsed trace ranges: wall intervals, never CPU accounting."""
import json,re,sys
from collections import Counter,defaultdict
HEADER=re.compile(r'^M=(-?\d+) P=(-?\d+) G=(-?\d+) (\w+) Time=(\d+)(.*)$')
RANGE=re.compile(r' Name=("[^"]*") Scope=(\S+)')
REGION=re.compile(r' Task=(\d+) Type="checker.files"$')
LOG=re.compile(r' Task=(\d+) Category="checker.index" Message="(\d+)"$')

def union_ns(intervals):
    end=None;total=0
    for a,b in sorted(intervals):
        if b<a:raise ValueError('Negative interval')
        total+=max(0,b-max(a,end if end is not None else a));end=max(b,end if end is not None else b)
    return total

def overlap(intervals,a,b):
    return union_ns((max(x,a),min(y,b)) for x,y in intervals if x<b and y>a)

def analyze(lines):
    opened={};spans=defaultdict(list);workers={};indices={};partial=[];first=last=None;counts=Counter()
    for line in lines:
        h=HEADER.match(line.rstrip('\n'))
        if not h:continue
        _,_,gid,kind,now,fields=h.groups();gid=int(gid);now=int(now)
        if last is not None and now<last:raise ValueError('Non-monotonic trace')
        if first is None:first=now
        last=now
        if kind in ('RangeBegin','RangeActive','RangeEnd'):
            m=RANGE.match(fields)
            if not m:raise ValueError('Malformed range')
            name,scope=m.groups();name=json.loads(name)
            if name not in ('GC mark assist','GC concurrent mark phase') and not name.startswith('stop-the-world ('):continue
            key=(name,scope);counts[kind]+=1
            if kind=='RangeBegin':
                if key in opened:raise ValueError('Duplicate range begin')
                opened[key]=now
            elif kind=='RangeActive':
                # Go generation boundaries repeat active range metadata.
                if key not in opened:opened[key]=None
            else:
                if key not in opened:raise ValueError('Range end without begin or active marker')
                begin=opened.pop(key)
                if begin is None:partial.append(dict(name=name,scope=scope,end=now,reason='start outside capture'))
                else:spans[key].append((begin,now))
        elif kind=='Log':
            m=LOG.fullmatch(fields)
            if m:indices[int(m[1])]=int(m[2])
        elif kind in ('RegionBegin','RegionEnd'):
            m=REGION.fullmatch(fields)
            if not m:continue
            task=int(m[1])
            if kind=='RegionBegin':
                if task in workers:raise ValueError('Repeated worker region')
                workers[task]=dict(gid=gid,start=now)
            else:
                w=workers[task]
                if w['gid']!=gid or 'end' in w:raise ValueError('Mismatched region end')
                w['end']=now
    if first is None or not workers:raise ValueError('No worker trace')
    for (name,scope),begin in opened.items():partial.append(dict(name=name,scope=scope,start=begin,reason='end outside capture'))
    stw=[i for (name,_),intervals in spans.items() if name.startswith('stop-the-world (') for i in intervals]
    gc=[i for (name,_),intervals in spans.items() if name=='GC concurrent mark phase' for i in intervals]
    results=[]
    for task,w in workers.items():
        if 'end' not in w:raise ValueError('Incomplete worker')
        a,b=w['start'],w['end'];scope=f"Goroutine({w['gid']})"
        for p in partial:
            if p['name']=='GC mark assist' and p['scope']==scope:
                lo=p.get('start');lo=first if lo is None else lo;hi=p.get('end',last)
                if lo<b and hi>a:raise ValueError('Incomplete assist overlapping worker')
        assist=overlap(spans[('GC mark assist',scope)],a,b)
        results.append(dict(task=task,checker=indices[task],filesMs=(b-a)/1e6,assistWallMs=assist/1e6,assistWallFraction=assist/(b-a) if b>a else 0,stwOverlapMs=overlap(stw,a,b)/1e6,concurrentMarkOverlapMs=overlap(gc,a,b)/1e6))
    start=min(w['start'] for w in workers.values());end=max(w['end'] for w in workers.values())
    phases={name:dict(wallMs=(b-a)/1e6,stwUnionMs=overlap(stw,a,b)/1e6,concurrentMarkUnionMs=overlap(gc,a,b)/1e6) for name,a,b in [('beforeWorkers',first,start),('workers',start,end),('afterWorkers',end,last)]}
    return dict(status='analyzed',phaseWindows=phases,workerRanges=results,rangeCounts=dict(counts),incompleteRanges=partial,totalTraceWallMs=(last-first)/1e6,stwUnionMs=union_ns(stw)/1e6,concurrentMarkUnionMs=union_ns(gc)/1e6,limitations=['Assist wall ranges may include waiting/descheduling and are not GC CPU costs.','STW/mark/assist intervals overlap and must not be added.','Concurrent mark overlap does not mean the worker stops computing.','Only complete ranges contribute; incomplete capture-boundary ranges are listed.','Single instrumented traces do not establish achievable speedups.','These extendedDiagnostics runs force two final collections; after-worker GC is not representative of benchmark flags.'])

if __name__=='__main__':
    with open(sys.argv[1]) as f:r=analyze(f)
    with open(sys.argv[2],'x') as f:json.dump(r,f,indent=2);f.write('\n')
