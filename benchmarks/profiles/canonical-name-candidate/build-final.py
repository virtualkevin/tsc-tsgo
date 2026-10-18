from pathlib import Path
import json,subprocess,sys
sys.dont_write_bytecode=True
from final_common import *
verify();OUT.mkdir(parents=True,exist_ok=True)
binary=OUT/'tsc-go'
assert not binary.exists() and not (PROFILE/'final-build.json').exists()
command=[GO,'build','-trimpath','-overlay',str(OVERLAY),'-o',str(binary),'./cmd/tsgo']
with (PROFILE/'final-build.stdout').open('w') as stdout,(PROFILE/'final-build.stderr').open('w') as stderr:
 run=subprocess.run(command,cwd=MODULE,env=ENV,stdout=stdout,stderr=stderr)
report={'scope':'Diagnostic overlay binary and exact staged source metadata; not standard production build-system provenance or a performance comparison.','command':command,'exitCode':run.returncode,'freezeSha256':sha(PROFILE/'final-freeze.json'),'controllerSha256':sha(__file__),'commonSha256':sha(PROFILE/'final_common.py'),'stdoutSha256':sha(PROFILE/'final-build.stdout'),'stderrSha256':sha(PROFILE/'final-build.stderr'),'passed':False}
if run.returncode==0:
 verify();report['binarySha256']=sha(binary)
 info=subprocess.check_output([GO,'version','-m',str(binary)],env=ENV,text=True);(PROFILE/'final-build-info.txt').write_text(info);report['buildInfoSha256']=sha(PROFILE/'final-build-info.txt')
 report['goEnv']=json.loads(subprocess.check_output([GO,'env','-json','GOVERSION','GOOS','GOARCH','GOAMD64','GOEXPERIMENT','CGO_ENABLED','GOFLAGS'],cwd=MODULE,env=ENV,text=True));report['passed']=True
(PROFILE/'final-build.json').write_text(json.dumps(report,indent=2)+'\n')
print('final overlay build',report['passed'],flush=True)
raise SystemExit(0 if report['passed'] else 1)
