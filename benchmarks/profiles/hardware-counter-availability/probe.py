from pathlib import Path
import subprocess,json,hashlib
out=Path(__file__).resolve().parent
commands=[['perf','stat','-e','cycles,instructions,cache-references,cache-misses','--','/usr/bin/true'],['sudo','-n','perf','stat','-e','cycles,instructions,cache-references,cache-misses','--','/usr/bin/true']]
report={'scope':'Read-only hardware counter availability probe; not compiler performance data. No kernel setting changes.','perfEventParanoid':Path('/proc/sys/kernel/perf_event_paranoid').read_text().strip(),'runs':[]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for i,command in enumerate(commands):
 p=subprocess.run(command,capture_output=True,text=True,timeout=15)
 stdout=out/f'{i}.stdout';stderr=out/f'{i}.stderr';stdout.write_text(p.stdout);stderr.write_text(p.stderr)
 report['runs'].append({'command':command,'exitCode':p.returncode,'stdoutSha256':sha(stdout),'stderrSha256':sha(stderr),'unsupportedMarkers':p.stderr.count('<not supported>')})
report['requestedHardwareCountersAvailable']=report['runs'][1]['exitCode']==0 and report['runs'][1]['unsupportedMarkers']==0
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
