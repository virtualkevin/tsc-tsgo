"""Offline union-construction budget from hash-checked retained profiles."""
from pathlib import Path
import hashlib, importlib.util, json, re, subprocess, sys, tarfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = 'github.com/microsoft/typescript-go/internal/checker.(*Checker).'
TARGET = PREFIX + 'addTypesToUnion'
BASE = HERE.parent / 'node-pointer-normal'
HEAPS = HERE.parent / 'ast-arena-audit'
sha = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location('heap_parser', HEAPS / 'analyze.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
manifest = json.loads((BASE / 'manifest.json').read_text())
assert sha((BASE / 'profiles.tar.gz').read_bytes()) == manifest['archiveSha256']
heap_inputs = {x['project']: x for x in json.loads((HEAPS / 'inputs.json').read_text())}
report = {'scope': 'Historical sampled CPU and allocation attribution, not new timing, wall-time savings, peak RSS or final-GC liveness. CPU percentages are pprof-rounded inclusive sample fractions. Recursive appearances counted once by pprof and allocation stack membership.', 'projects': []}
with tarfile.open(BASE / 'profiles.tar.gz') as cpus, tarfile.open(HEAPS / 'raw-heaps.tar.gz') as heaps:
    for project in ['typeorm', 'trpc', 'vscode', 'sentry']:
        name = next(k for k in manifest['files'] if k.startswith(project + '/') and k.endswith('-cpuprofile.pb.gz'))
        member = next(m for m in cpus.getmembers() if m.name.removeprefix('./') == 'node-pointer-normal/' + name)
        data = cpus.extractfile(member).read()
        assert sha(data) == manifest['files'][name]
        profile = HERE / (project + '.pb.gz')
        profile.write_bytes(data)
        command = ['/tmp/tsc-toolchains/go/bin/go', 'tool', 'pprof', '-top', '-nodefraction=0', '-nodecount=0', '-focus=addTypesToUnion|addTypeToUnion', str(profile)]
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        (HERE / (project + '.cpu.txt')).write_text(result.stdout)
        (HERE / (project + '.stderr')).write_text(result.stderr)
        line = next(l for l in result.stdout.splitlines() if l.endswith(TARGET))
        columns = line.split()
        cpu_pct = float(columns[-2].rstrip('%'))
        raw = heaps.extractfile(project + '.raw.txt').read()
        assert sha(raw) == heap_inputs[project]['rawSha256']
        total = [0]*4; selected = [0]*4; insertion = [0]*4
        for values, frames in parser.parse(raw.decode()):
            total = [a+b for a,b in zip(total, values)]
            if TARGET not in frames: continue
            selected = [a+b for a,b in zip(selected, values)]
            if frames[0].startswith('slices.Insert['):
                insertion = [a+b for a,b in zip(insertion, values)]
        report['projects'].append({'project': project, 'cpuProfileSha256': sha(data), 'cpuInclusivePercentRounded': cpu_pct,
            'heapRawSha256': sha(raw), 'heapMetrics': parser.METRICS, 'heapTotal': total, 'unionInclusiveHeap': selected,
            'unionDirectInsertHeap': insertion, 'unionInclusiveAllocBytesPercent': 100*selected[1]/total[1],
            'unionDirectInsertAllocBytesPercent': 100*insertion[1]/total[1], 'command': command})
report['sourceHashes'] = {name: sha((ROOT/name).read_bytes()) for name in ['packages/tsc-go/internal/checker/checker.go','packages/tsc-go/internal/checker/utilities.go']}
text = json.dumps(report, indent=2)+'\n'
if '--write' in sys.argv: (HERE/'report.json').write_text(text)
else: assert (HERE/'report.json').read_text() == text
for p in report['projects']:
    print(p['project'], p['cpuInclusivePercentRounded'], p['unionInclusiveAllocBytesPercent'], p['unionDirectInsertAllocBytesPercent'])
