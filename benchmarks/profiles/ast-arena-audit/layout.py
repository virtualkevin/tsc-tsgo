from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[3];here=Path(__file__).resolve().parent
p=root/'packages/tsc-go/internal/ast/storage_layout_audit_test.go';assert not p.exists()
data=(here/'layout_test.go.txt').read_bytes();p.write_bytes(data)
env=os.environ.copy();env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
for k in ['GOFLAGS','GOEXPERIMENT']:env.pop(k,None)
command=['/tmp/tsc-toolchains/go/bin/go','test','-json','./internal/ast','-run','^TestStorageLayoutAudit$','-count=1']
try:
 r=subprocess.run(command,cwd=root/'packages/tsc-go',env=env,capture_output=True,timeout=600)
 (here/'layout.stdout').write_bytes(r.stdout);(here/'layout.stderr').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
 events=[json.loads(x) for x in r.stdout.splitlines()];lines=[line.split('LAYOUT_JSON ',1)[1].strip() for line in ''.join(e.get('Output','') for e in events).splitlines() if 'LAYOUT_JSON ' in line];assert len(lines)==1
 records=json.loads(lines[0]);(here/'layout.json').write_text(json.dumps({'command':command,'harnessSha256':hashlib.sha256(data).hexdigest(),'layouts':records},indent=2)+'\n');print([(r['Name'],r['Size']) for r in records])
finally:
 assert p.read_bytes()==data;p.unlink()
