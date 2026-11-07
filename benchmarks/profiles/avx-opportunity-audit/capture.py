"""Offline SIMD opportunity audit of retained production profiles and executable."""
from pathlib import Path
import gzip, hashlib, importlib.util, json, re, subprocess, tarfile, tempfile
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
PRIOR=HERE.parent/'project-inlining-normal'
BINARY=ROOT/'packages/tsc-go/dist/tsc-go'; GO=Path('/tmp/tsc-toolchains/go/bin/go')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BINARY)=='9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a'
assert sha(GO)=='e90c4e12df236ea0c2e7536fd68da8a47fc0b585c19588bf6c1a70cfc296a0f9'
assert not (HERE/'report.json').exists()
manifest=json.loads((PRIOR/'manifest.json').read_text()); expected={f['path']:f['sha256'] for f in manifest['files']}
parser=HERE.parent/'property-work-budget/analyze.py'
spec=importlib.util.spec_from_file_location('budget',parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.PATTERNS={
 'scanner':r'/scanner\.',
 'byte_search_compare':r'^(?:indexbytebody|memeqbody|cmpbody|internal/bytealg\.|strings\.(?:Index|Compare|Equal)|bytes\.(?:Index|Compare|Equal))',
 'memory_copy_clear':r'^runtime\.(?:memmove|memclrNoHeapPointers)$',
 'map_control_match':r'^internal/runtime/maps\.ctrlGroup\.match',
 'hashing':r'^(?:aeshashbody|runtime\.(?:memhash|strhash)|internal/runtime/maps\.h[12]$)',
 'slice_search':r'^slices\.(?:Contains|Index)',
}
rows=[]
with tarfile.open(PRIOR/'profiles.tar.gz') as archive, tempfile.TemporaryDirectory(prefix='avx-profile-audit-') as temporary:
 for workload in ['typeorm','trpc','vscode','sentry']:
  member=next(x for x in archive.getmembers() if x.name.startswith(workload+'/') and x.name.endswith('-cpuprofile.pb.gz'))
  data=archive.extractfile(member).read();digest=hashlib.sha256(data).hexdigest();assert digest==expected[member.name]
  profile=Path(temporary)/Path(member.name).name;profile.write_bytes(data)
  cmd=[str(GO),'tool','pprof','-raw',str(BINARY),str(profile)]
  result=subprocess.run(cmd,capture_output=True,check=True)
  raw=result.stdout.decode();analysis=mod.analyze(raw);analysis.pop('propertyUnionPercent')
  dest=HERE/(workload+'.raw.gz');dest.write_bytes(gzip.compress(result.stdout,mtime=0));assert gzip.decompress(dest.read_bytes())==result.stdout
  rows.append({'workload':workload,'profile':member.name,'profileSha256':digest,'rawSha256':hashlib.sha256(result.stdout).hexdigest(),'archiveSha256':sha(dest),'command':cmd,'stderr':result.stderr.decode(),**analysis})
  print(workload,analysis['inclusivePercent'],flush=True)
assembly=[]
for symbol in ['runtime.memclrNoHeapPointers','runtime.memmove','memeqbody','indexbytebody']:
 cmd=['/usr/bin/objdump','-d','--disassemble='+symbol,str(BINARY)]
 r=subprocess.run(cmd,capture_output=True,check=True,text=True);assert '<'+symbol+'>:' in r.stdout
 file=HERE/(symbol+'.asm');file.write_text(r.stdout)
 assembly.append({'symbol':symbol,'command':cmd,'sha256':sha(file),'vectorInstructionLines':[line for line in r.stdout.splitlines() if re.search(r'\b(?:v[a-z0-9]+|pcmpeqb|pmovmskb)\s',line)]})
cpu=Path('/proc/cpuinfo').read_text().split('\n\n')[0]
model=next(line.split(':',1)[1].strip() for line in cpu.splitlines() if line.startswith('model name'))
flags=next(line.split(':',1)[1].split() for line in cpu.splitlines() if line.startswith('flags'))
features=sorted(x for x in flags if x.startswith(('avx','sse','xsave')) or x in ['aes','osxsave'])
sources=['runtime/memclr_amd64.s','runtime/memmove_amd64.s','internal/bytealg/equal_amd64.s','internal/bytealg/indexbyte_amd64.s','internal/runtime/maps/group.go','internal/cpu/cpu_x86.go']
report={'scope':'Offline historical production CPU samples; inclusive categories overlap and include callees. Not removable wall time, SIMD eligibility proof, or speedup. Assembly proves available code paths, not dynamic execution frequency. CPU flags are kernel-advertised; runtime dispatch remains required.','controllerSha256':sha(__file__),'parserSha256':sha(parser),'binarySha256':sha(BINARY),'goSha256':sha(GO),'objdumpSha256':sha('/usr/bin/objdump'),'priorManifestSha256':sha(PRIOR/'manifest.json'),'priorArchiveSha256':sha(PRIOR/'profiles.tar.gz'),'cpuModel':model,'advertisedFeatures':features,'patterns':mod.PATTERNS,'projects':rows,'assembly':assembly,'runtimeSources':{s:sha(GO.parent.parent/'src'/s) for s in sources}}
(HERE/'report.json').write_text(json.dumps(report,indent=2)+'\n')
