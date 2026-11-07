from pathlib import Path
import hashlib,json,os,subprocess
PROFILE=Path(__file__).resolve().parent
ROOT=PROFILE.parents[2]
MODULE=ROOT/'packages/tsc-go'
OUT=Path('/tmp/tsc-reduction-scratch-candidate-validation')
GO='/tmp/tsc-toolchains/go/bin/go'
FREEZE=json.loads((PROFILE/'cli-freeze.json').read_text())
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
ENV=os.environ.copy()
for k in list(ENV):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ('GOFLAGS','GOEXPERIMENT','GODEBUG','GOGC','GOMEMLIMIT','GOMAXPROCS','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','NODE_OPTIONS','LD_PRELOAD','SHOW_FAILURES'):ENV.pop(k,None)
ENV.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local',PATH=str(Path(GO).parent)+':'+ENV.get('PATH',''))
OVERLAY=PROFILE/'overlay.json'
def verify():
 assert sha(OVERLAY)==FREEZE['overlaySha256']
 assert {k:sha(v) for k,v in json.loads(OVERLAY.read_text())['Replace'].items()}==FREEZE['sources']
 assert all(sha(MODULE/k)==v for k,v in FREEZE['base'].items())
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==FREEZE['head']
 js='import {captureGoSources} from "./scripts/build-provenance.mjs";const s=captureGoSources(process.cwd()+"/packages/tsc-go");console.log(s.sha256)'
 assert subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,env=ENV,text=True).strip()=='b50f489f20634bf3570a18d0fcc5cf811036fbcefe2a5ea481b193f848768445'
 assert sha(MODULE/'dist/tsc-go')=='9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a'
 assert sha(MODULE/'dist/tsc-go.provenance.json')=='5164f58805236585d39258604fb12e274475039d04fd3efd5b8572d84c2cf287'
