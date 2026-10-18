"""Shared frozen overlay validation guards; this does not publish production provenance."""
from pathlib import Path
import hashlib,json,os,subprocess
PROFILE=Path(__file__).resolve().parent
ROOT=PROFILE.parents[2]
MODULE=ROOT/'packages/tsc-go'
STAGE=PROFILE/'staged'
OUT=Path('/tmp/tsc-direct-materialization-validation')
GO='/tmp/tsc-toolchains/go/bin/go'
FREEZE=json.loads((PROFILE/'final-freeze.json').read_text())
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
ENV=os.environ.copy()
for key in list(ENV):
 if key.startswith(('TSC_','TS_GO_','SCRIPTC_')) or key in ['GOFLAGS','GOEXPERIMENT','GODEBUG','GOGC','GOMEMLIMIT','GOMAXPROCS','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','NODE_OPTIONS','LD_PRELOAD','SHOW_FAILURES']:
  ENV.pop(key,None)
ENV.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local',PATH=str(Path(GO).parent)+':'+ENV.get('PATH',''))
OVERLAY=PROFILE/'overlay.json'
def verify():
 assert {str(p.relative_to(STAGE)):sha(p) for p in STAGE.rglob('*') if p.is_file()}==FREEZE['sources']
 overlay=json.loads(OVERLAY.read_text())['Replace']
 assert {str(Path(k).relative_to(MODULE)):sha(v) for k,v in overlay.items()}==FREEZE['overlaySources']
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==FREEZE['head']
 js='import {captureGoSources} from "./scripts/build-provenance.mjs";const s=captureGoSources(process.cwd()+"/packages/tsc-go");console.log(JSON.stringify({sha256:s.sha256,revision:s.revision,count:s.files.length}))'
 base=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,env=ENV,text=True))
 assert base=={'sha256':'216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd','revision':FREEZE['head'],'count':5154}
 assert sha(MODULE/'dist/tsc-go')=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
 assert sha(MODULE/'dist/tsc-go.provenance.json')=='76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'
 return base
