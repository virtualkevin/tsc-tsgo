from pathlib import Path
import hashlib,json,os,subprocess
PROFILE=Path(__file__).resolve().parent
ROOT=PROFILE.parents[2]
MODULE=ROOT/'packages/tsc-go'
OUT=Path('/tmp/tsc-classic-gc-validation')
GO='/tmp/tsc-toolchains/go/bin/go'
BUILD=json.loads((PROFILE/'build.json').read_text());assert BUILD['passed']
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
ENV=os.environ.copy()
for k in list(ENV):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ('GOFLAGS','GOEXPERIMENT','GODEBUG','GOGC','GOMEMLIMIT','GOMAXPROCS','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','NODE_OPTIONS','LD_PRELOAD','SHOW_FAILURES'):ENV.pop(k,None)
ENV.update(GOEXPERIMENT='nogreenteagc',GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local',PATH=str(Path(GO).parent)+':'+ENV.get('PATH',''))
def verify():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
 assert sha(BUILD['binary'])==BUILD['binarySha256']
 assert sha(BUILD['binary']+'.provenance.json')==BUILD['sidecarSha256']
 js='import {captureGoSources} from "./scripts/build-provenance.mjs";const s=captureGoSources(process.cwd()+"/packages/tsc-go");console.log(s.sha256)'
 assert subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,env=ENV,text=True).strip()=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
 assert sha(MODULE/'dist/tsc-go')=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
 assert sha(MODULE/'dist/tsc-go.provenance.json')=='76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'
