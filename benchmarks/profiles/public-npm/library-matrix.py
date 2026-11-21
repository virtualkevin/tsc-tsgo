"""Separate compiler and standard-library changes on the two failing release checks."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]
frozen=json.loads(gzip.decompress((here.parent/'literal-union-intersection/native.json.gz').read_bytes()))
public=Path(sys.argv[1]).resolve()
launcher=public/'node_modules/tsc-ts/bin/tsc-ts.js'
release_lib=public/'node_modules/@tsc-ts/linux-x64-gnu/lib'
old_lib=Path(frozen['environment']['compilerEnvironment']['TSC_TS_LIB_DIR']).resolve()
go=Path(frozen['binaries']['candidate']['path'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release=json.loads((here/'releases.json').read_text())['releases']['0.1.5']
assert sha(launcher)==release['launcherSha256'] and sha(release_lib/'tsc-ts')==release['linuxGnuBinarySha256']
assert sha(go)==frozen['binaries']['candidate']['sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_', 'SCRIPTC_'))}
report={'publicVersion':'0.1.5','goSha256':sha(go),'projects':{}}
for p in frozen['projects']:
    if p['name'] not in ('vscode','sentry'):continue
    cwd=Path(p['cwd'])
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip()==p['commit']
    results={}
    for label,lib in [('originalLibraries',old_lib),('publicLibraries',release_lib)]:
        observed=[]
        for role,binary in [('public',launcher),('go',go)]:
            check_env=dict(env,TSC_TS_LIB_DIR=str(lib))
            def run(args):
                return subprocess.run([binary,*args],cwd=cwd,env=check_env,capture_output=True,text=True,timeout=480)
            files=run(p['fileDiscoveryArgs']['candidate'])
            assert files.returncode==0 and not files.stderr
            sources={}
            for name in files.stdout.splitlines():
                f=(cwd/name).resolve()
                key='library/'+f.relative_to(lib).as_posix() if f.is_relative_to(lib) else 'project/'+os.path.relpath(f,cwd)
                assert key not in sources
                sources[key]=sha(f)
            prior={}
            for item in p['preflight']['candidate']['inputs']:
                f=(cwd/item['file']).resolve()
                key='library/'+f.relative_to(old_lib).as_posix() if f.is_relative_to(old_lib) else 'project/'+os.path.relpath(f,cwd)
                prior[key]=item['sha256']
            # Report any divergence; membership and bytes must agree for workload comparisons.
            differences=[k for k in sorted(set(sources)|set(prior)) if sources.get(k)!=prior.get(k)]

            r=run(p['compilerArgs']['candidate'])
            assert r.returncode in (0,1,2) and not r.stderr
            assert r.returncode==0 or 'error TS' in r.stdout
            inputs=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
            observed.append(dict(role=role,inputsSha256=inputs,inputCount=len(sources),inputDifferencesFromOriginal=differences,
                                 exit=r.returncode,diagnostics=r.stdout.splitlines()))
            print(p['name'],label,role,r.returncode,sum('error TS' in l for l in r.stdout.splitlines()),flush=True)
        # Preserve divergent dependency selections as evidence about comparability.
        results[label]=observed
    report['projects'][p['name']]={'commit':p['commit'],'matrix':results}
(here/'0.1.5-library-matrix.json.gz').write_bytes(gzip.compress((json.dumps(report,indent=2)+'\n').encode(),mtime=0))
